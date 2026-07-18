import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.warehouse import Warehouse
from app.schemas.warehouse import WarehouseCreate, WarehouseUpdate


async def get(db: AsyncSession, warehouse_id: uuid.UUID, company_id: uuid.UUID) -> Warehouse | None:
    result = await db.execute(
        select(Warehouse).where(Warehouse.id == warehouse_id, Warehouse.company_id == company_id)
    )
    return result.scalar_one_or_none()


async def get_by_name(db: AsyncSession, company_id: uuid.UUID, name: str) -> Warehouse | None:
    result = await db.execute(
        select(Warehouse).where(Warehouse.company_id == company_id, Warehouse.name == name)
    )
    return result.scalar_one_or_none()


async def list_paginated(
    db: AsyncSession, *, company_id: uuid.UUID, page: int, page_size: int
) -> tuple[list[Warehouse], int]:
    query = select(Warehouse).where(Warehouse.company_id == company_id)
    count_query = select(func.count()).select_from(Warehouse).where(Warehouse.company_id == company_id)

    total = (await db.execute(count_query)).scalar_one()
    query = query.order_by(Warehouse.name).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(query)).scalars().all()
    return list(items), total


async def create(db: AsyncSession, company_id: uuid.UUID, data: WarehouseCreate) -> Warehouse:
    warehouse = Warehouse(company_id=company_id, **data.model_dump())
    db.add(warehouse)
    await db.commit()
    await db.refresh(warehouse)
    return warehouse


async def update(db: AsyncSession, warehouse: Warehouse, data: WarehouseUpdate) -> Warehouse:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(warehouse, field, value)
    await db.commit()
    await db.refresh(warehouse)
    return warehouse
