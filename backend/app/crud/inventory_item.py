import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory_item import InventoryItem
from app.schemas.inventory_item import InventoryItemCreate, InventoryItemUpdate


async def get(db: AsyncSession, item_id: uuid.UUID, company_id: uuid.UUID) -> InventoryItem | None:
    result = await db.execute(
        select(InventoryItem).where(InventoryItem.id == item_id, InventoryItem.company_id == company_id)
    )
    return result.scalar_one_or_none()


async def get_by_sku(db: AsyncSession, company_id: uuid.UUID, sku: str) -> InventoryItem | None:
    result = await db.execute(
        select(InventoryItem).where(InventoryItem.company_id == company_id, InventoryItem.sku == sku)
    )
    return result.scalar_one_or_none()


async def list_paginated(
    db: AsyncSession,
    *,
    company_id: uuid.UUID,
    page: int,
    page_size: int,
    warehouse_id: uuid.UUID | None = None,
    search: str | None = None,
    low_stock: bool = False,
) -> tuple[list[InventoryItem], int]:
    query = select(InventoryItem).where(InventoryItem.company_id == company_id)
    count_query = select(func.count()).select_from(InventoryItem).where(InventoryItem.company_id == company_id)

    if warehouse_id:
        query = query.where(InventoryItem.warehouse_id == warehouse_id)
        count_query = count_query.where(InventoryItem.warehouse_id == warehouse_id)
    if search:
        pattern = f"%{search}%"
        query = query.where(InventoryItem.sku.ilike(pattern) | InventoryItem.name.ilike(pattern))
        count_query = count_query.where(InventoryItem.sku.ilike(pattern) | InventoryItem.name.ilike(pattern))
    if low_stock:
        query = query.where(InventoryItem.quantity <= InventoryItem.min_stock)
        count_query = count_query.where(InventoryItem.quantity <= InventoryItem.min_stock)

    total = (await db.execute(count_query)).scalar_one()
    query = query.order_by(InventoryItem.name).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(query)).scalars().all()
    return list(items), total


async def list_all_for_company(db: AsyncSession, company_id: uuid.UUID) -> list[InventoryItem]:
    result = await db.execute(select(InventoryItem).where(InventoryItem.company_id == company_id))
    return list(result.scalars().all())


async def create(db: AsyncSession, company_id: uuid.UUID, data: InventoryItemCreate) -> InventoryItem:
    item = InventoryItem(company_id=company_id, quantity=0, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def update(db: AsyncSession, item: InventoryItem, data: InventoryItemUpdate) -> InventoryItem:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item
