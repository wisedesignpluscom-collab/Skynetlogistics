import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.driver_pay_rate import DriverPayRate
from app.schemas.driver_pay_rate import DriverPayRateCreate, DriverPayRateUpdate


async def get(db: AsyncSession, rate_id: uuid.UUID, company_id: uuid.UUID) -> DriverPayRate | None:
    result = await db.execute(
        select(DriverPayRate).where(DriverPayRate.id == rate_id, DriverPayRate.company_id == company_id)
    )
    return result.scalar_one_or_none()


async def get_by_vehicle_type(
    db: AsyncSession, company_id: uuid.UUID, vehicle_type: str
) -> DriverPayRate | None:
    result = await db.execute(
        select(DriverPayRate).where(
            DriverPayRate.company_id == company_id, DriverPayRate.vehicle_type == vehicle_type
        )
    )
    return result.scalar_one_or_none()


async def list_all_for_company(db: AsyncSession, company_id: uuid.UUID) -> list[DriverPayRate]:
    result = await db.execute(select(DriverPayRate).where(DriverPayRate.company_id == company_id))
    return list(result.scalars().all())


async def create(db: AsyncSession, company_id: uuid.UUID, data: DriverPayRateCreate) -> DriverPayRate:
    rate = DriverPayRate(company_id=company_id, **data.model_dump())
    db.add(rate)
    await db.commit()
    await db.refresh(rate)
    return rate


async def update(db: AsyncSession, rate: DriverPayRate, data: DriverPayRateUpdate) -> DriverPayRate:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(rate, field, value)
    await db.commit()
    await db.refresh(rate)
    return rate


async def delete(db: AsyncSession, rate: DriverPayRate) -> None:
    await db.delete(rate)
    await db.commit()
