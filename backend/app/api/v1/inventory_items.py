import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
from app.crud import inventory_item as inventory_item_crud
from app.crud import inventory_movement as inventory_movement_crud
from app.crud import warehouse as warehouse_crud
from app.models.user import User
from app.schemas.common import Page
from app.schemas.inventory_item import (
    InventoryItemCreate,
    InventoryItemDetailOut,
    InventoryItemOut,
    InventoryItemUpdate,
)

router = APIRouter(prefix="/inventory-items", tags=["inventory"])


@router.get("", response_model=Page[InventoryItemOut])
async def list_inventory_items(
    page: int = 1,
    page_size: int = 20,
    warehouse_id: uuid.UUID | None = None,
    search: str | None = None,
    low_stock: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("inventory", "read")),
) -> Page[InventoryItemOut]:
    items, total = await inventory_item_crud.list_paginated(
        db,
        company_id=current_user.company_id,
        page=page,
        page_size=page_size,
        warehouse_id=warehouse_id,
        search=search,
        low_stock=low_stock,
    )
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=InventoryItemOut, status_code=status.HTTP_201_CREATED)
async def create_inventory_item(
    payload: InventoryItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("inventory", "write")),
) -> InventoryItemOut:
    if await warehouse_crud.get(db, payload.warehouse_id, current_user.company_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Almacén no encontrado")
    if await inventory_item_crud.get_by_sku(db, current_user.company_id, payload.sku) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un ítem con ese SKU")
    return await inventory_item_crud.create(db, current_user.company_id, payload)


@router.get("/{item_id}", response_model=InventoryItemDetailOut)
async def get_inventory_item(
    item_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("inventory", "read")),
) -> InventoryItemDetailOut:
    item = await inventory_item_crud.get(db, item_id, current_user.company_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ítem de inventario no encontrado")
    movements = await inventory_movement_crud.list_for_item(db, item_id, current_user.company_id)
    return InventoryItemDetailOut(
        **InventoryItemOut.model_validate(item).model_dump(),
        movements=list(reversed(movements)),
    )


@router.patch("/{item_id}", response_model=InventoryItemOut)
async def update_inventory_item(
    item_id: uuid.UUID,
    payload: InventoryItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("inventory", "write")),
) -> InventoryItemOut:
    item = await inventory_item_crud.get(db, item_id, current_user.company_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ítem de inventario no encontrado")
    if payload.warehouse_id is not None:
        if await warehouse_crud.get(db, payload.warehouse_id, current_user.company_id) is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Almacén no encontrado")
    return await inventory_item_crud.update(db, item, payload)
