import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
from app.crud import maintenance_task as maintenance_task_crud
from app.crud import tire as tire_crud
from app.crud import vehicle as vehicle_crud
from app.models.user import User
from app.schemas.common import Page
from app.schemas.maintenance import MaintenanceTaskWithRecordsOut
from app.schemas.tire import TireOut
from app.schemas.vehicle import VehicleCreate, VehicleOut, VehicleUpdate

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
    return await vehicle_crud.create(db, current_user.company_id, payload)


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
    return await vehicle_crud.update(db, vehicle, payload)


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
    return await maintenance_task_crud.list_for_vehicle_with_records(db, vehicle_id, current_user.company_id)


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
