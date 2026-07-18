import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


async def get(db: AsyncSession, user_id: uuid.UUID, company_id: uuid.UUID) -> User | None:
    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .where(User.id == user_id, User.company_id == company_id)
    )
    return result.scalar_one_or_none()


async def get_by_id_any_company(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    result = await db.execute(
        select(User)
        .options(selectinload(User.role), selectinload(User.company))
        .where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def get_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(
        select(User)
        .options(selectinload(User.role), selectinload(User.company))
        .where(User.email == email)
    )
    return result.scalar_one_or_none()


async def list_paginated(
    db: AsyncSession,
    *,
    company_id: uuid.UUID,
    page: int,
    page_size: int,
    search: str | None = None,
    role_id: uuid.UUID | None = None,
    is_active: bool | None = None,
) -> tuple[list[User], int]:
    query = select(User).options(selectinload(User.role)).where(User.company_id == company_id)
    count_query = select(func.count()).select_from(User).where(User.company_id == company_id)

    if search:
        pattern = f"%{search}%"
        query = query.where(User.name.ilike(pattern) | User.email.ilike(pattern))
        count_query = count_query.where(User.name.ilike(pattern) | User.email.ilike(pattern))
    if role_id:
        query = query.where(User.role_id == role_id)
        count_query = count_query.where(User.role_id == role_id)
    if is_active is not None:
        query = query.where(User.is_active == is_active)
        count_query = count_query.where(User.is_active == is_active)

    total = (await db.execute(count_query)).scalar_one()
    query = query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(query)).scalars().all()
    return list(items), total


async def create(db: AsyncSession, company_id: uuid.UUID, data: UserCreate) -> User:
    user = User(
        company_id=company_id,
        role_id=data.role_id,
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user, attribute_names=["role"])
    return user


async def update(db: AsyncSession, user: User, data: UserUpdate) -> User:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user, attribute_names=["role"])
    return user


async def set_password(db: AsyncSession, user: User, new_password: str) -> User:
    user.password_hash = hash_password(new_password)
    await db.commit()
    await db.refresh(user, attribute_names=["role"])
    return user


async def deactivate(db: AsyncSession, user: User) -> User:
    user.is_active = False
    await db.commit()
    await db.refresh(user, attribute_names=["role"])
    return user


async def touch_last_login(db: AsyncSession, user: User) -> None:
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()
