import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
from app.crud import warehouse as warehouse_crud
from app.models.user import User
from app.schemas.common import Page
from app.schemas.warehouse import WarehouseCreate, WarehouseOut, WarehouseUpdate

router = APIRouter(prefix="/warehouses", tags=["tires"])


@router.get("", response_model=Page[WarehouseOut])
async def list_warehouses(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("tires", "read")),
) -> Page[WarehouseOut]:
    items, total = await warehouse_crud.list_paginated(
        db, company_id=current_user.company_id, page=page, page_size=page_size
    )
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=WarehouseOut, status_code=status.HTTP_201_CREATED)
async def create_warehouse(
    payload: WarehouseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("tires", "write")),
) -> WarehouseOut:
    if await warehouse_crud.get_by_name(db, current_user.company_id, payload.name) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un almacén con ese nombre")
    return await warehouse_crud.create(db, current_user.company_id, payload)


@router.patch("/{warehouse_id}", response_model=WarehouseOut)
async def update_warehouse(
    warehouse_id: uuid.UUID,
    payload: WarehouseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("tires", "write")),
) -> WarehouseOut:
    warehouse = await warehouse_crud.get(db, warehouse_id, current_user.company_id)
    if warehouse is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Almacén no encontrado")
    if payload.name and payload.name != warehouse.name:
        existing = await warehouse_crud.get_by_name(db, current_user.company_id, payload.name)
        if existing is not None:
            raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un almacén con ese nombre")
    return await warehouse_crud.update(db, warehouse, payload)
