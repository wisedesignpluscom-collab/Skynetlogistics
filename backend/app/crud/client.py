import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate


async def get(db: AsyncSession, client_id: uuid.UUID, company_id: uuid.UUID) -> Client | None:
    result = await db.execute(
        select(Client).where(Client.id == client_id, Client.company_id == company_id)
    )
    return result.scalar_one_or_none()


async def list_paginated(
    db: AsyncSession, *, company_id: uuid.UUID, page: int, page_size: int, search: str | None = None
) -> tuple[list[Client], int]:
    query = select(Client).where(Client.company_id == company_id)
    count_query = select(func.count()).select_from(Client).where(Client.company_id == company_id)
    if search:
        pattern = f"%{search}%"
        query = query.where(Client.name.ilike(pattern))
        count_query = count_query.where(Client.name.ilike(pattern))

    total = (await db.execute(count_query)).scalar_one()
    query = query.order_by(Client.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(query)).scalars().all()
    return list(items), total


async def create(db: AsyncSession, company_id: uuid.UUID, data: ClientCreate) -> Client:
    client = Client(company_id=company_id, **data.model_dump())
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return client


async def update(db: AsyncSession, client: Client, data: ClientUpdate) -> Client:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(client, field, value)
    await db.commit()
    await db.refresh(client)
    return client


async def deactivate(db: AsyncSession, client: Client) -> Client:
    client.is_active = False
    await db.commit()
    await db.refresh(client)
    return client
