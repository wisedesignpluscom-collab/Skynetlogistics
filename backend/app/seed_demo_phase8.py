"""Datos de demo para verificar la Fase 8 (reportes de conductor + chat) en el navegador.

Crea (idempotente) una empresa "Demo Transporte" con:
- rol Admin (despachador) + usuario despacho@demo.dev / Demo1234!
- rol Conductor + usuario conductor@demo.dev / Demo1234! vinculado a un Driver

Uso: python -m app.seed_demo_phase8
"""

import asyncio
from datetime import date

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.company import Company
from app.models.driver import Driver
from app.models.role import Role
from app.models.user import User
from app.utils.permissions import DEFAULT_ADMIN_PERMISSIONS, DRIVER_SUGGESTED_PERMISSIONS

COMPANY_TAX_ID = "DEMO-PHASE8"


async def _get_or_create(db, model, defaults=None, **filters):
    result = await db.execute(select(model).filter_by(**filters))
    obj = result.scalar_one_or_none()
    if obj is not None:
        return obj, False
    obj = model(**filters, **(defaults or {}))
    db.add(obj)
    await db.flush()
    return obj, True


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        company, _ = await _get_or_create(
            db, Company, tax_id=COMPANY_TAX_ID, defaults={"name": "Demo Transporte", "plan": "pro"}
        )

        admin_role, _ = await _get_or_create(
            db, Role, company_id=company.id, name="Admin",
            defaults={"permissions": DEFAULT_ADMIN_PERMISSIONS},
        )
        driver_role, _ = await _get_or_create(
            db, Role, company_id=company.id, name="Conductor",
            defaults={"permissions": DRIVER_SUGGESTED_PERMISSIONS},
        )

        admin_user, _ = await _get_or_create(
            db, User, email="despacho@demo.dev",
            defaults={
                "company_id": company.id,
                "role_id": admin_role.id,
                "name": "Despacho Demo",
                "password_hash": hash_password("Demo1234!"),
            },
        )

        driver_user, _ = await _get_or_create(
            db, User, email="conductor@demo.dev",
            defaults={
                "company_id": company.id,
                "role_id": driver_role.id,
                "name": "Carlos Conductor",
                "password_hash": hash_password("Demo1234!"),
            },
        )

        driver, _ = await _get_or_create(
            db, Driver, company_id=company.id, license_number="LIC-DEMO-01",
            defaults={
                "name": "Carlos Conductor",
                "license_expiry": date(2030, 1, 1),
                "user_id": driver_user.id,
            },
        )
        if driver.user_id is None:
            driver.user_id = driver_user.id

        await db.commit()
        print("Demo Fase 8 lista:")
        print("  Despachador: despacho@demo.dev / Demo1234!")
        print("  Conductor:   conductor@demo.dev / Demo1234!")


if __name__ == "__main__":
    asyncio.run(seed())
