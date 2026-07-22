import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.custom_fields import validate_entity_custom_data
from app.core.deps import require_permission
from app.crud import maintenance_settings as maintenance_settings_crud
from app.crud import maintenance_task as maintenance_task_crud
from app.crud import vehicle as vehicle_crud
from app.models.user import User
from app.schemas.common import Page
from app.schemas.maintenance import (
    MaintenanceRecordCreate,
    MaintenanceTaskCreate,
    MaintenanceTaskOut,
    MaintenanceTaskUpdate,
)
from app.services.maintenance_status import compute_traffic_light
from app.services.workflows import run_workflows

router = APIRouter(prefix="/maintenance-tasks", tags=["maintenance"])


async def _with_traffic_light(
    db: AsyncSession, company_id: uuid.UUID, tasks: list
) -> list[MaintenanceTaskOut]:
    settings = await maintenance_settings_crud.get_or_create(db, company_id)
    odometers = await vehicle_crud.get_odometers_by_ids(
        db, [task.vehicle_id for task in tasks], company_id
    )
    today = date.today()

    result = []
    for task in tasks:
        out = MaintenanceTaskOut.model_validate(task)
        out.traffic_light = compute_traffic_light(
            status=task.status,
            scheduled_by=task.scheduled_by,
            due_date=task.due_date,
            due_km=task.due_km,
            vehicle_odometer_km=odometers.get(task.vehicle_id),
            today=today,
            warning_days_threshold=settings.warning_days_threshold,
            warning_km_threshold=settings.warning_km_threshold,
        )
        result.append(out)
    return result


@router.get("", response_model=Page[MaintenanceTaskOut])
async def list_maintenance_tasks(
    page: int = 1,
    page_size: int = 20,
    vehicle_id: uuid.UUID | None = None,
    status_filter: str | None = None,
    type: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("maintenance", "read")),
) -> Page[MaintenanceTaskOut]:
    items, total = await maintenance_task_crud.list_paginated(
        db,
        company_id=current_user.company_id,
        page=page,
        page_size=page_size,
        vehicle_id=vehicle_id,
        status=status_filter,
        type=type,
    )
    items_out = await _with_traffic_light(db, current_user.company_id, items)
    return Page(items=items_out, total=total, page=page, page_size=page_size)


@router.post("", response_model=MaintenanceTaskOut, status_code=status.HTTP_201_CREATED)
async def create_maintenance_task(
    payload: MaintenanceTaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("maintenance", "write")),
) -> MaintenanceTaskOut:
    vehicle = await vehicle_crud.get(db, payload.vehicle_id, current_user.company_id)
    if vehicle is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "El vehículo no pertenece a esta empresa")
    payload.custom_data = await validate_entity_custom_data(
        db, current_user.company_id, "maintenance_task", payload.custom_data, payload=payload
    )
    task = await maintenance_task_crud.create(db, current_user.company_id, payload)
    await run_workflows(
        db, company_id=current_user.company_id, entity_type="maintenance_task", event="creado", entity=task
    )
    return task


@router.get("/{task_id}", response_model=MaintenanceTaskOut)
async def get_maintenance_task(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("maintenance", "read")),
) -> MaintenanceTaskOut:
    task = await maintenance_task_crud.get(db, task_id, current_user.company_id)
    if task is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tarea de mantenimiento no encontrada")
    items_out = await _with_traffic_light(db, current_user.company_id, [task])
    return items_out[0]


@router.patch("/{task_id}", response_model=MaintenanceTaskOut)
async def update_maintenance_task(
    task_id: uuid.UUID,
    payload: MaintenanceTaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("maintenance", "write")),
) -> MaintenanceTaskOut:
    task = await maintenance_task_crud.get(db, task_id, current_user.company_id)
    if task is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tarea de mantenimiento no encontrada")
    if payload.custom_data is not None:
        payload.custom_data = await validate_entity_custom_data(
            db, current_user.company_id, "maintenance_task", payload.custom_data, payload=payload
        )
    previous_status = task.status
    updated = await maintenance_task_crud.update(db, task, payload)
    await run_workflows(
        db, company_id=current_user.company_id, entity_type="maintenance_task", event="actualizado", entity=updated
    )
    if payload.status is not None and payload.status != previous_status:
        await run_workflows(
            db, company_id=current_user.company_id, entity_type="maintenance_task", event="cambio_estado",
            entity=updated, previous_status=previous_status,
        )
    return updated


@router.post("/{task_id}/complete", response_model=MaintenanceTaskOut)
async def complete_maintenance_task(
    task_id: uuid.UUID,
    payload: MaintenanceRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("maintenance", "write")),
) -> MaintenanceTaskOut:
    task = await maintenance_task_crud.get(db, task_id, current_user.company_id)
    if task is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tarea de mantenimiento no encontrada")
    if task.status == "completada":
        raise HTTPException(status.HTTP_409_CONFLICT, "La tarea ya está completada")
    previous_status = task.status
    completed = await maintenance_task_crud.complete(db, task, payload)
    await run_workflows(
        db, company_id=current_user.company_id, entity_type="maintenance_task", event="actualizado", entity=completed
    )
    await run_workflows(
        db, company_id=current_user.company_id, entity_type="maintenance_task", event="cambio_estado",
        entity=completed, previous_status=previous_status,
    )
    return completed
