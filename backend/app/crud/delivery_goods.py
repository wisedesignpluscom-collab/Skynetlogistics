import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.delivery_goods import DeliveryGoods, DeliveryGoodsMovement
from app.schemas.delivery_goods import DeliveryGoodsCreate, DeliveryGoodsUpdate


async def get(db: AsyncSession, goods_id: uuid.UUID, company_id: uuid.UUID) -> DeliveryGoods | None:
    result = await db.execute(
        select(DeliveryGoods).where(DeliveryGoods.id == goods_id, DeliveryGoods.company_id == company_id)
    )
    return result.scalar_one_or_none()


async def get_by_sku(db: AsyncSession, company_id: uuid.UUID, sku: str) -> DeliveryGoods | None:
    result = await db.execute(
        select(DeliveryGoods).where(DeliveryGoods.company_id == company_id, DeliveryGoods.sku == sku)
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
) -> tuple[list[DeliveryGoods], int]:
    query = select(DeliveryGoods).where(DeliveryGoods.company_id == company_id)
    count_query = select(func.count()).select_from(DeliveryGoods).where(DeliveryGoods.company_id == company_id)

    if warehouse_id:
        query = query.where(DeliveryGoods.warehouse_id == warehouse_id)
        count_query = count_query.where(DeliveryGoods.warehouse_id == warehouse_id)
    if search:
        pattern = f"%{search}%"
        query = query.where(DeliveryGoods.sku.ilike(pattern) | DeliveryGoods.name.ilike(pattern))
        count_query = count_query.where(DeliveryGoods.sku.ilike(pattern) | DeliveryGoods.name.ilike(pattern))
    if low_stock:
        query = query.where(DeliveryGoods.quantity <= DeliveryGoods.min_stock)
        count_query = count_query.where(DeliveryGoods.quantity <= DeliveryGoods.min_stock)

    total = (await db.execute(count_query)).scalar_one()
    query = query.order_by(DeliveryGoods.name).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(query)).scalars().all()
    return list(items), total


async def create(db: AsyncSession, company_id: uuid.UUID, data: DeliveryGoodsCreate) -> DeliveryGoods:
    goods = DeliveryGoods(company_id=company_id, quantity=0, **data.model_dump())
    db.add(goods)
    await db.commit()
    await db.refresh(goods)
    return goods


async def update(db: AsyncSession, goods: DeliveryGoods, data: DeliveryGoodsUpdate) -> DeliveryGoods:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(goods, field, value)
    await db.commit()
    await db.refresh(goods)
    return goods


async def create_movement(db: AsyncSession, *, company_id: uuid.UUID, **fields) -> DeliveryGoodsMovement:
    movement = DeliveryGoodsMovement(company_id=company_id, **fields)
    db.add(movement)
    await db.flush()
    return movement


async def list_movements(db: AsyncSession, goods_id: uuid.UUID, company_id: uuid.UUID) -> list[DeliveryGoodsMovement]:
    result = await db.execute(
        select(DeliveryGoodsMovement)
        .where(DeliveryGoodsMovement.company_id == company_id, DeliveryGoodsMovement.goods_id == goods_id)
        .order_by(DeliveryGoodsMovement.created_at.asc())
    )
    return list(result.scalars().all())
