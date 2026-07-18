import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tire import Tire
from app.schemas.tire import TireCreate, TireUpdate


async def get(db: AsyncSession, tire_id: uuid.UUID, company_id: uuid.UUID) -> Tire | None:
    result = await db.execute(select(Tire).where(Tire.id == tire_id, Tire.company_id == company_id))
    return result.scalar_one_or_none()


async def get_by_unique_code(db: AsyncSession, company_id: uuid.UUID, unique_code: str) -> Tire | None:
    result = await db.execute(
        select(Tire).where(Tire.company_id == company_id, Tire.unique_code == unique_code)
    )
    return result.scalar_one_or_none()


async def list_paginated(
    db: AsyncSession,
    *,
    company_id: uuid.UUID,
    page: int,
    page_size: int,
    status: str | None = None,
    brand: str | None = None,
    model: str | None = None,
    search: str | None = None,
) -> tuple[list[Tire], int]:
    query = select(Tire).where(Tire.company_id == company_id)
    count_query = select(func.count()).select_from(Tire).where(Tire.company_id == company_id)

    if status:
        query = query.where(Tire.status == status)
        count_query = count_query.where(Tire.status == status)
    if brand:
        query = query.where(Tire.brand == brand)
        count_query = count_query.where(Tire.brand == brand)
    if model:
        query = query.where(Tire.model == model)
        count_query = count_query.where(Tire.model == model)
    if search:
        pattern = f"%{search}%"
        query = query.where(Tire.unique_code.ilike(pattern) | Tire.brand.ilike(pattern))
        count_query = count_query.where(Tire.unique_code.ilike(pattern) | Tire.brand.ilike(pattern))

    total = (await db.execute(count_query)).scalar_one()
    query = query.order_by(Tire.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(query)).scalars().all()
    return list(items), total


async def list_installed_for_vehicle(db: AsyncSession, vehicle_id: uuid.UUID, company_id: uuid.UUID) -> list[Tire]:
    result = await db.execute(
        select(Tire).where(
            Tire.company_id == company_id, Tire.vehicle_id == vehicle_id, Tire.status == "instalado"
        )
    )
    return list(result.scalars().all())


async def get_installed_at_position(
    db: AsyncSession,
    *,
    company_id: uuid.UUID,
    vehicle_id: uuid.UUID,
    axle_number: int,
    axle_side: str,
    axle_dual_position: str,
) -> Tire | None:
    result = await db.execute(
        select(Tire).where(
            Tire.company_id == company_id,
            Tire.vehicle_id == vehicle_id,
            Tire.axle_number == axle_number,
            Tire.axle_side == axle_side,
            Tire.axle_dual_position == axle_dual_position,
            Tire.status == "instalado",
        )
    )
    return result.scalar_one_or_none()


async def list_all_for_company(db: AsyncSession, company_id: uuid.UUID) -> list[Tire]:
    result = await db.execute(select(Tire).where(Tire.company_id == company_id))
    return list(result.scalars().all())


async def create(db: AsyncSession, company_id: uuid.UUID, data: TireCreate) -> Tire:
    tire = Tire(company_id=company_id, status="almacen", **data.model_dump())
    db.add(tire)
    await db.commit()
    await db.refresh(tire)
    return tire


async def update(db: AsyncSession, tire: Tire, data: TireUpdate) -> Tire:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(tire, field, value)
    await db.commit()
    await db.refresh(tire)
    return tire
