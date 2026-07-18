import uuid
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company_holiday import CompanyHoliday
from app.schemas.company_holiday import CompanyHolidayCreate


async def get(db: AsyncSession, holiday_id: uuid.UUID, company_id: uuid.UUID) -> CompanyHoliday | None:
    result = await db.execute(
        select(CompanyHoliday).where(CompanyHoliday.id == holiday_id, CompanyHoliday.company_id == company_id)
    )
    return result.scalar_one_or_none()


async def count_between(db: AsyncSession, company_id: uuid.UUID, start: date, end: date) -> int:
    result = await db.execute(
        select(func.count())
        .select_from(CompanyHoliday)
        .where(
            CompanyHoliday.company_id == company_id,
            CompanyHoliday.date >= start,
            CompanyHoliday.date <= end,
        )
    )
    return result.scalar_one()


async def list_all_for_company(db: AsyncSession, company_id: uuid.UUID) -> list[CompanyHoliday]:
    result = await db.execute(
        select(CompanyHoliday).where(CompanyHoliday.company_id == company_id).order_by(CompanyHoliday.date)
    )
    return list(result.scalars().all())


async def create(db: AsyncSession, company_id: uuid.UUID, data: CompanyHolidayCreate) -> CompanyHoliday:
    holiday = CompanyHoliday(company_id=company_id, **data.model_dump())
    db.add(holiday)
    await db.commit()
    await db.refresh(holiday)
    return holiday


async def delete(db: AsyncSession, holiday: CompanyHoliday) -> None:
    await db.delete(holiday)
    await db.commit()
