import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vehicle_owner import VehicleOwner
from app.schemas.vehicle_owner import VehicleOwnerCreate, VehicleOwnerUpdate


async def get(db: AsyncSession, owner_id: uuid.UUID, company_id: uuid.UUID) -> VehicleOwner | None:
    result = await db.execute(
        select(VehicleOwner).where(VehicleOwner.id == owner_id, VehicleOwner.company_id == company_id)
    )
    return result.scalar_one_or_none()


async def list_paginated(
    db: AsyncSession, *, company_id: uuid.UUID, page: int, page_size: int, search: str | None = None
) -> tuple[list[VehicleOwner], int]:
    query = select(VehicleOwner).where(VehicleOwner.company_id == company_id)
    count_query = select(func.count()).select_from(VehicleOwner).where(VehicleOwner.company_id == company_id)
    if search:
        pattern = f"%{search}%"
        query = query.where(VehicleOwner.name.ilike(pattern))
        count_query = count_query.where(VehicleOwner.name.ilike(pattern))

    total = (await db.execute(count_query)).scalar_one()
    query = query.order_by(VehicleOwner.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(query)).scalars().all()
    return list(items), total


async def create(db: AsyncSession, company_id: uuid.UUID, data: VehicleOwnerCreate) -> VehicleOwner:
    owner = VehicleOwner(company_id=company_id, **data.model_dump())
    db.add(owner)
    await db.commit()
    await db.refresh(owner)
    return owner


async def update(db: AsyncSession, owner: VehicleOwner, data: VehicleOwnerUpdate) -> VehicleOwner:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(owner, field, value)
    await db.commit()
    await db.refresh(owner)
    return owner


async def deactivate(db: AsyncSession, owner: VehicleOwner) -> VehicleOwner:
    owner.is_active = False
    await db.commit()
    await db.refresh(owner)
    return owner
