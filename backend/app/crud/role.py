import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role
from app.models.user import User
from app.schemas.role import RoleCreate, RoleUpdate


async def get(db: AsyncSession, role_id: uuid.UUID, company_id: uuid.UUID) -> Role | None:
    result = await db.execute(select(Role).where(Role.id == role_id, Role.company_id == company_id))
    return result.scalar_one_or_none()


async def get_by_name(db: AsyncSession, company_id: uuid.UUID, name: str) -> Role | None:
    result = await db.execute(select(Role).where(Role.company_id == company_id, Role.name == name))
    return result.scalar_one_or_none()


async def list_paginated(
    db: AsyncSession, *, company_id: uuid.UUID, page: int, page_size: int
) -> tuple[list[Role], int]:
    query = select(Role).where(Role.company_id == company_id)
    count_query = select(func.count()).select_from(Role).where(Role.company_id == company_id)

    total = (await db.execute(count_query)).scalar_one()
    query = query.order_by(Role.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(query)).scalars().all()
    return list(items), total


async def create(db: AsyncSession, company_id: uuid.UUID, data: RoleCreate) -> Role:
    role = Role(company_id=company_id, name=data.name, permissions=data.permissions)
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


async def update(db: AsyncSession, role: Role, data: RoleUpdate) -> Role:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(role, field, value)
    await db.commit()
    await db.refresh(role)
    return role


async def has_assigned_users(db: AsyncSession, role_id: uuid.UUID) -> bool:
    result = await db.execute(select(func.count()).select_from(User).where(User.role_id == role_id))
    return result.scalar_one() > 0


async def delete(db: AsyncSession, role: Role) -> None:
    await db.delete(role)
    await db.commit()
