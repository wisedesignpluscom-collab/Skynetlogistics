import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
from app.crud import vehicle_owner as vehicle_owner_crud
from app.models.user import User
from app.schemas.common import Page
from app.schemas.vehicle_owner import VehicleOwnerCreate, VehicleOwnerOut, VehicleOwnerUpdate

router = APIRouter(prefix="/vehicle-owners", tags=["vehicles"])


@router.get("", response_model=Page[VehicleOwnerOut])
async def list_vehicle_owners(
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("vehicles", "read")),
) -> Page[VehicleOwnerOut]:
    items, total = await vehicle_owner_crud.list_paginated(
        db, company_id=current_user.company_id, page=page, page_size=page_size, search=search
    )
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=VehicleOwnerOut, status_code=status.HTTP_201_CREATED)
async def create_vehicle_owner(
    payload: VehicleOwnerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("vehicles", "write")),
) -> VehicleOwnerOut:
    return await vehicle_owner_crud.create(db, current_user.company_id, payload)


@router.get("/{owner_id}", response_model=VehicleOwnerOut)
async def get_vehicle_owner(
    owner_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("vehicles", "read")),
) -> VehicleOwnerOut:
    owner = await vehicle_owner_crud.get(db, owner_id, current_user.company_id)
    if owner is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Propietario no encontrado")
    return owner


@router.patch("/{owner_id}", response_model=VehicleOwnerOut)
async def update_vehicle_owner(
    owner_id: uuid.UUID,
    payload: VehicleOwnerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("vehicles", "write")),
) -> VehicleOwnerOut:
    owner = await vehicle_owner_crud.get(db, owner_id, current_user.company_id)
    if owner is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Propietario no encontrado")
    return await vehicle_owner_crud.update(db, owner, payload)


@router.delete("/{owner_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle_owner(
    owner_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("vehicles", "delete")),
) -> None:
    owner = await vehicle_owner_crud.get(db, owner_id, current_user.company_id)
    if owner is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Propietario no encontrado")
    await vehicle_owner_crud.deactivate(db, owner)
