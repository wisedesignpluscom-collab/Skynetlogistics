import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.delivery_order import DeliveryOrder, DeliveryOrderItem
from app.schemas.delivery_order import DeliveryOrderCreate, DeliveryOrderUpdate


async def get(db: AsyncSession, order_id: uuid.UUID, company_id: uuid.UUID) -> DeliveryOrder | None:
    result = await db.execute(
        select(DeliveryOrder)
        .where(DeliveryOrder.id == order_id, DeliveryOrder.company_id == company_id)
        .options(selectinload(DeliveryOrder.items))
    )
    return result.scalar_one_or_none()


async def list_paginated(
    db: AsyncSession,
    *,
    company_id: uuid.UUID,
    page: int,
    page_size: int,
    status: str | None = None,
    trip_id: uuid.UUID | None = None,
    client_id: uuid.UUID | None = None,
) -> tuple[list[DeliveryOrder], int]:
    query = (
        select(DeliveryOrder)
        .where(DeliveryOrder.company_id == company_id)
        .options(selectinload(DeliveryOrder.items))
    )
    count_query = select(func.count()).select_from(DeliveryOrder).where(DeliveryOrder.company_id == company_id)

    if status:
        query = query.where(DeliveryOrder.status == status)
        count_query = count_query.where(DeliveryOrder.status == status)
    if trip_id:
        query = query.where(DeliveryOrder.trip_id == trip_id)
        count_query = count_query.where(DeliveryOrder.trip_id == trip_id)
    if client_id:
        query = query.where(DeliveryOrder.client_id == client_id)
        count_query = count_query.where(DeliveryOrder.client_id == client_id)

    total = (await db.execute(count_query)).scalar_one()
    query = query.order_by(DeliveryOrder.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(query)).scalars().all()
    return list(items), total


async def list_for_trips(db: AsyncSession, trip_ids: list[uuid.UUID], company_id: uuid.UUID) -> list[DeliveryOrder]:
    if not trip_ids:
        return []
    result = await db.execute(
        select(DeliveryOrder)
        .where(DeliveryOrder.company_id == company_id, DeliveryOrder.trip_id.in_(trip_ids))
        .options(selectinload(DeliveryOrder.items))
        .order_by(DeliveryOrder.priority.desc(), DeliveryOrder.created_at.asc())
    )
    return list(result.scalars().all())


async def create(
    db: AsyncSession, company_id: uuid.UUID, data: DeliveryOrderCreate, created_by: uuid.UUID | None
) -> DeliveryOrder:
    order = DeliveryOrder(
        company_id=company_id,
        client_id=data.client_id,
        address=data.address,
        lat=data.lat,
        lng=data.lng,
        priority=data.priority,
        time_window_start=data.time_window_start,
        time_window_end=data.time_window_end,
        notes=data.notes,
        custom_data=data.custom_data,
        created_by=created_by,
    )
    order.items = [DeliveryOrderItem(goods_id=item.goods_id, quantity=item.quantity) for item in data.items]
    db.add(order)
    await db.commit()
    return await get(db, order.id, company_id)


async def update(db: AsyncSession, order: DeliveryOrder, data: DeliveryOrderUpdate) -> DeliveryOrder:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(order, field, value)
    await db.commit()
    return await get(db, order.id, order.company_id)
