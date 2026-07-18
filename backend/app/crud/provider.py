import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.provider import Provider
from app.schemas.provider import ProviderCreate, ProviderUpdate


async def get(db: AsyncSession, provider_id: uuid.UUID, company_id: uuid.UUID) -> Provider | None:
    result = await db.execute(
        select(Provider).where(Provider.id == provider_id, Provider.company_id == company_id)
    )
    return result.scalar_one_or_none()


async def list_paginated(
    db: AsyncSession, *, company_id: uuid.UUID, page: int, page_size: int
) -> tuple[list[Provider], int]:
    query = select(Provider).where(Provider.company_id == company_id)
    count_query = select(func.count()).select_from(Provider).where(Provider.company_id == company_id)

    total = (await db.execute(count_query)).scalar_one()
    query = query.order_by(Provider.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(query)).scalars().all()
    return list(items), total


async def create(db: AsyncSession, company_id: uuid.UUID, data: ProviderCreate) -> Provider:
    provider = Provider(company_id=company_id, **data.model_dump())
    db.add(provider)
    await db.commit()
    await db.refresh(provider)
    return provider


async def update(db: AsyncSession, provider: Provider, data: ProviderUpdate) -> Provider:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(provider, field, value)
    await db.commit()
    await db.refresh(provider)
    return provider


async def delete(db: AsyncSession, provider: Provider) -> None:
    await db.delete(provider)
    await db.commit()
