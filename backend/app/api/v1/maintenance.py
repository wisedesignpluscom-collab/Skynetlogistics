import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
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

router = APIRouter(prefix="/maintenance-tasks", tags=["maintenance"])


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
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=MaintenanceTaskOut, status_code=status.HTTP_201_CREATED)
async def create_maintenance_task(
    payload: MaintenanceTaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("maintenance", "write")),
) -> MaintenanceTaskOut:
    vehicle = await vehicle_crud.get(db, payload.vehicle_id, current_user.company_id)
    if vehicle is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "El vehículo no pertenece a esta empresa")
    return await maintenance_task_crud.create(db, current_user.company_id, payload)


@router.get("/{task_id}", response_model=MaintenanceTaskOut)
async def get_maintenance_task(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("maintenance", "read")),
) -> MaintenanceTaskOut:
    task = await maintenance_task_crud.get(db, task_id, current_user.company_id)
    if task is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tarea de mantenimiento no encontrada")
    return task


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
    return await maintenance_task_crud.update(db, task, payload)


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
    return await maintenance_task_crud.complete(db, task, payload)
