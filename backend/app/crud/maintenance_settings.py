import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.maintenance_settings import MaintenanceSettings
from app.schemas.maintenance_settings import MaintenanceSettingsUpdate


async def get_by_company(db: AsyncSession, company_id: uuid.UUID) -> MaintenanceSettings | None:
    result = await db.execute(
        select(MaintenanceSettings).where(MaintenanceSettings.company_id == company_id)
    )
    return result.scalar_one_or_none()


async def get_or_create(db: AsyncSession, company_id: uuid.UUID) -> MaintenanceSettings:
    settings = await get_by_company(db, company_id)
    if settings is not None:
        return settings
    settings = MaintenanceSettings(company_id=company_id)
    db.add(settings)
    await db.commit()
    await db.refresh(settings)
    return settings


async def update(
    db: AsyncSession, settings: MaintenanceSettings, data: MaintenanceSettingsUpdate
) -> MaintenanceSettings:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(settings, field, value)
    await db.commit()
    await db.refresh(settings)
    return settings
