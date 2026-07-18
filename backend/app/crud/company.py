import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate


async def get(db: AsyncSession, company_id: uuid.UUID) -> Company | None:
    return await db.get(Company, company_id)


async def get_by_tax_id(db: AsyncSession, tax_id: str) -> Company | None:
    result = await db.execute(select(Company).where(Company.tax_id == tax_id))
    return result.scalar_one_or_none()


async def list_paginated(
    db: AsyncSession, *, page: int, page_size: int, search: str | None = None
) -> tuple[list[Company], int]:
    query = select(Company)
    count_query = select(func.count()).select_from(Company)
    if search:
        pattern = f"%{search}%"
        query = query.where(Company.name.ilike(pattern))
        count_query = count_query.where(Company.name.ilike(pattern))

    total = (await db.execute(count_query)).scalar_one()
    query = query.order_by(Company.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(query)).scalars().all()
    return list(items), total


async def create(db: AsyncSession, data: CompanyCreate) -> Company:
    company = Company(name=data.name, tax_id=data.tax_id, plan=data.plan)
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company


async def update(db: AsyncSession, company: Company, data: CompanyUpdate) -> Company:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(company, field, value)
    await db.commit()
    await db.refresh(company)
    return company


async def deactivate(db: AsyncSession, company: Company) -> Company:
    company.is_active = False
    await db.commit()
    await db.refresh(company)
    return company
