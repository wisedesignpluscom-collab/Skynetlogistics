import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.driver import Driver
from app.schemas.driver import DriverCreate, DriverUpdate


async def get(db: AsyncSession, driver_id: uuid.UUID, company_id: uuid.UUID) -> Driver | None:
    result = await db.execute(select(Driver).where(Driver.id == driver_id, Driver.company_id == company_id))
    return result.scalar_one_or_none()


async def get_by_license(db: AsyncSession, company_id: uuid.UUID, license_number: str) -> Driver | None:
    result = await db.execute(
        select(Driver).where(Driver.company_id == company_id, Driver.license_number == license_number)
    )
    return result.scalar_one_or_none()


async def list_paginated(
    db: AsyncSession,
    *,
    company_id: uuid.UUID,
    page: int,
    page_size: int,
    search: str | None = None,
    status: str | None = None,
) -> tuple[list[Driver], int]:
    query = select(Driver).where(Driver.company_id == company_id)
    count_query = select(func.count()).select_from(Driver).where(Driver.company_id == company_id)

    if search:
        pattern = f"%{search}%"
        query = query.where(Driver.name.ilike(pattern) | Driver.license_number.ilike(pattern))
        count_query = count_query.where(Driver.name.ilike(pattern) | Driver.license_number.ilike(pattern))
    if status:
        query = query.where(Driver.status == status)
        count_query = count_query.where(Driver.status == status)

    total = (await db.execute(count_query)).scalar_one()
    query = query.order_by(Driver.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(query)).scalars().all()
    return list(items), total


async def list_all_for_company(db: AsyncSession, company_id: uuid.UUID) -> list[Driver]:
    result = await db.execute(select(Driver).where(Driver.company_id == company_id))
    return list(result.scalars().all())


async def create(db: AsyncSession, company_id: uuid.UUID, data: DriverCreate) -> Driver:
    driver = Driver(company_id=company_id, **data.model_dump())
    db.add(driver)
    await db.commit()
    await db.refresh(driver)
    return driver


async def update(db: AsyncSession, driver: Driver, data: DriverUpdate) -> Driver:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(driver, field, value)
    await db.commit()
    await db.refresh(driver)
    return driver


async def deactivate(db: AsyncSession, driver: Driver) -> Driver:
    driver.status = "inactivo"
    await db.commit()
    await db.refresh(driver)
    return driver
