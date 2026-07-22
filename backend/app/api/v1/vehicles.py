import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
from app.crud import maintenance_settings as maintenance_settings_crud
from app.crud import maintenance_task as maintenance_task_crud
from app.crud import tire as tire_crud
from app.crud import vehicle as vehicle_crud
from app.crud import vehicle_document as vehicle_document_crud
from app.crud import vehicle_owner as vehicle_owner_crud
from app.jobs.alerts import run_alert_checks
from app.models.user import User
from app.schemas.common import Page
from app.schemas.maintenance import MaintenanceTaskWithRecordsOut
from app.schemas.tire import TireOut
from app.schemas.vehicle import VehicleCreate, VehicleOut, VehicleUpdate
from app.services.custom_fields import validate_entity_custom_data
from app.schemas.vehicle_document import VehicleDocumentCreate, VehicleDocumentOut
from app.services.maintenance_status import compute_traffic_light
from app.services.workflows import run_workflows

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("", response_model=Page[VehicleOut])
async def list_vehicles(
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    status_filter: str | None = None,
    type: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("vehicles", "read")),
) -> Page[VehicleOut]:
    items, total = await vehicle_crud.list_paginated(
        db,
        company_id=current_user.company_id,
        page=page,
        page_size=page_size,
        search=search,
        status=status_filter,
        type=type,
    )
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=VehicleOut, status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    payload: VehicleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("vehicles", "write")),
) -> VehicleOut:
    if await vehicle_crud.get_by_plate(db, current_user.company_id, payload.plate) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un vehículo con esa placa")
    if payload.owner_id is not None:
        if await vehicle_owner_crud.get(db, payload.owner_id, current_user.company_id) is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Propietario no encontrado")
    payload.custom_data = await validate_entity_custom_data(
        db, current_user.company_id, "vehicle", payload.custom_data, payload=payload
    )
    vehicle = await vehicle_crud.create(db, current_user.company_id, payload)
    await run_workflows(db, company_id=current_user.company_id, entity_type="vehicle", event="creado", entity=vehicle)
    return vehicle


@router.get("/{vehicle_id}", response_model=VehicleOut)
async def get_vehicle(
    vehicle_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("vehicles", "read")),
) -> VehicleOut:
    vehicle = await vehicle_crud.get(db, vehicle_id, current_user.company_id)
    if vehicle is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Vehículo no encontrado")
    return vehicle


@router.patch("/{vehicle_id}", response_model=VehicleOut)
async def update_vehicle(
    vehicle_id: uuid.UUID,
    payload: VehicleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("vehicles", "write")),
) -> VehicleOut:
    vehicle = await vehicle_crud.get(db, vehicle_id, current_user.company_id)
    if vehicle is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Vehículo no encontrado")
    if payload.plate and payload.plate != vehicle.plate:
        existing = await vehicle_crud.get_by_plate(db, current_user.company_id, payload.plate)
        if existing is not None:
            raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un vehículo con esa placa")
    if payload.owner_id is not None:
        if await vehicle_owner_crud.get(db, payload.owner_id, current_user.company_id) is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Propietario no encontrado")
    if payload.custom_data is not None:
        payload.custom_data = await validate_entity_custom_data(
            db, current_user.company_id, "vehicle", payload.custom_data, payload=payload
        )
    previous_status = vehicle.status
    updated = await vehicle_crud.update(db, vehicle, payload)
    await run_workflows(db, company_id=current_user.company_id, entity_type="vehicle", event="actualizado", entity=updated)
    if payload.status is not None and payload.status != previous_status:
        await run_workflows(
            db, company_id=current_user.company_id, entity_type="vehicle", event="cambio_estado",
            entity=updated, previous_status=previous_status,
        )
    return updated


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(
    vehicle_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("vehicles", "delete")),
) -> None:
    vehicle = await vehicle_crud.get(db, vehicle_id, current_user.company_id)
    if vehicle is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Vehículo no encontrado")
    await vehicle_crud.deactivate(db, vehicle)


@router.get("/{vehicle_id}/maintenance", response_model=list[MaintenanceTaskWithRecordsOut])
async def get_vehicle_maintenance_history(
    vehicle_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("vehicles", "read")),
) -> list[MaintenanceTaskWithRecordsOut]:
    vehicle = await vehicle_crud.get(db, vehicle_id, current_user.company_id)
    if vehicle is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Vehículo no encontrado")
    tasks = await maintenance_task_crud.list_for_vehicle_with_records(db, vehicle_id, current_user.company_id)
    settings = await maintenance_settings_crud.get_or_create(db, current_user.company_id)
    today = date.today()

    result = []
    for task in tasks:
        out = MaintenanceTaskWithRecordsOut.model_validate(task)
        out.traffic_light = compute_traffic_light(
            status=task.status,
            scheduled_by=task.scheduled_by,
            due_date=task.due_date,
            due_km=task.due_km,
            vehicle_odometer_km=vehicle.current_odometer_km,
            today=today,
            warning_days_threshold=settings.warning_days_threshold,
            warning_km_threshold=settings.warning_km_threshold,
        )
        result.append(out)
    return result


@router.get("/{vehicle_id}/tires", response_model=list[TireOut])
async def get_vehicle_tires(
    vehicle_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("tires", "read")),
) -> list[TireOut]:
    vehicle = await vehicle_crud.get(db, vehicle_id, current_user.company_id)
    if vehicle is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Vehículo no encontrado")
    return await tire_crud.list_installed_for_vehicle(db, vehicle_id, current_user.company_id)


@router.get("/{vehicle_id}/documents", response_model=list[VehicleDocumentOut])
async def list_vehicle_documents(
    vehicle_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("vehicles", "read")),
) -> list[VehicleDocumentOut]:
    vehicle = await vehicle_crud.get(db, vehicle_id, current_user.company_id)
    if vehicle is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Vehículo no encontrado")
    return await vehicle_document_crud.list_for_vehicle(db, vehicle_id, current_user.company_id)


@router.post(
    "/{vehicle_id}/documents", response_model=VehicleDocumentOut, status_code=status.HTTP_201_CREATED
)
async def create_vehicle_document(
    vehicle_id: uuid.UUID,
    payload: VehicleDocumentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("vehicles", "write")),
) -> VehicleDocumentOut:
    vehicle = await vehicle_crud.get(db, vehicle_id, current_user.company_id)
    if vehicle is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Vehículo no encontrado")
    document = await vehicle_document_crud.create(db, current_user.company_id, vehicle_id, payload)
    if payload.expiry_date is not None:
        await run_alert_checks(db, vehicle_ids=[vehicle_id])
    return document
