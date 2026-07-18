"""Siembra la empresa plataforma, el rol Superadmin y el primer usuario superadmin.

Uso: python -m app.seed
"""

import asyncio

from sqlalchemy import select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.company import Company
from app.models.role import Role
from app.models.user import User
from app.utils.permissions import SUPERADMIN_PERMISSIONS

PLATFORM_COMPANY_NAME = "Platform"
PLATFORM_TAX_ID = "PLATFORM"
SUPERADMIN_ROLE_NAME = "Superadmin"


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Company).where(Company.tax_id == PLATFORM_TAX_ID))
        company = result.scalar_one_or_none()
        if company is None:
            company = Company(name=PLATFORM_COMPANY_NAME, tax_id=PLATFORM_TAX_ID, plan="platform")
            db.add(company)
            await db.flush()

        result = await db.execute(
            select(Role).where(Role.company_id == company.id, Role.name == SUPERADMIN_ROLE_NAME)
        )
        role = result.scalar_one_or_none()
        if role is None:
            role = Role(
                company_id=company.id,
                name=SUPERADMIN_ROLE_NAME,
                permissions=SUPERADMIN_PERMISSIONS,
                is_system=True,
            )
            db.add(role)
            await db.flush()

        result = await db.execute(select(User).where(User.email == settings.seed_superadmin_email))
        user = result.scalar_one_or_none()
        if user is None:
            user = User(
                company_id=company.id,
                role_id=role.id,
                name="Superadmin",
                email=settings.seed_superadmin_email,
                password_hash=hash_password(settings.seed_superadmin_password),
                is_superadmin=True,
            )
            db.add(user)
            print(f"Superadmin creado: {settings.seed_superadmin_email}")
        else:
            print(f"Superadmin ya existía: {settings.seed_superadmin_email}")

        await db.commit()


if __name__ == "__main__":
    asyncio.run(seed())
