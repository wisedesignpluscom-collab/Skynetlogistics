import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tire_movement import TireMovement


async def create(db: AsyncSession, *, company_id: uuid.UUID, **fields) -> TireMovement:
    movement = TireMovement(company_id=company_id, **fields)
    db.add(movement)
    await db.flush()
    return movement


async def list_for_tire(db: AsyncSession, tire_id: uuid.UUID, company_id: uuid.UUID) -> list[TireMovement]:
    result = await db.execute(
        select(TireMovement)
        .where(TireMovement.company_id == company_id, TireMovement.tire_id == tire_id)
        .order_by(TireMovement.created_at.asc())
    )
    return list(result.scalars().all())


async def list_all_for_company(db: AsyncSession, company_id: uuid.UUID) -> list[TireMovement]:
    result = await db.execute(
        select(TireMovement)
        .where(TireMovement.company_id == company_id)
        .order_by(TireMovement.tire_id, TireMovement.created_at.asc())
    )
    return list(result.scalars().all())


async def list_filtered(
    db: AsyncSession,
    *,
    company_id: uuid.UUID,
    tire_id: uuid.UUID | None = None,
    vehicle_id: uuid.UUID | None = None,
) -> list[TireMovement]:
    query = select(TireMovement).where(TireMovement.company_id == company_id)
    if tire_id is not None:
        query = query.where(TireMovement.tire_id == tire_id)
    if vehicle_id is not None:
        query = query.where(TireMovement.vehicle_id == vehicle_id)
    query = query.order_by(TireMovement.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())
