import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rate_table import RateTable
from app.schemas.rate_table import RateTableCreate, RateTableUpdate


async def get(db: AsyncSession, rate_table_id: uuid.UUID, company_id: uuid.UUID) -> RateTable | None:
    result = await db.execute(
        select(RateTable).where(RateTable.id == rate_table_id, RateTable.company_id == company_id)
    )
    return result.scalar_one_or_none()


async def find_match(
    db: AsyncSession,
    *,
    company_id: uuid.UUID,
    origin: str,
    destination: str,
    vehicle_type: str,
    cargo_type: str,
) -> RateTable | None:
    result = await db.execute(
        select(RateTable).where(
            RateTable.company_id == company_id,
            RateTable.origin == origin,
            RateTable.destination == destination,
            RateTable.vehicle_type == vehicle_type,
            RateTable.cargo_type == cargo_type,
            RateTable.is_active.is_(True),
        )
    )
    return result.scalar_one_or_none()


async def list_paginated(
    db: AsyncSession, *, company_id: uuid.UUID, page: int, page_size: int
) -> tuple[list[RateTable], int]:
    query = select(RateTable).where(RateTable.company_id == company_id)
    count_query = select(func.count()).select_from(RateTable).where(RateTable.company_id == company_id)

    total = (await db.execute(count_query)).scalar_one()
    query = query.order_by(RateTable.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(query)).scalars().all()
    return list(items), total


async def create(db: AsyncSession, company_id: uuid.UUID, data: RateTableCreate) -> RateTable:
    rate_table = RateTable(company_id=company_id, **data.model_dump())
    db.add(rate_table)
    await db.commit()
    await db.refresh(rate_table)
    return rate_table


async def update(db: AsyncSession, rate_table: RateTable, data: RateTableUpdate) -> RateTable:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(rate_table, field, value)
    await db.commit()
    await db.refresh(rate_table)
    return rate_table


async def delete(db: AsyncSession, rate_table: RateTable) -> None:
    await db.delete(rate_table)
    await db.commit()
