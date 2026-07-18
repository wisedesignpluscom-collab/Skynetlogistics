import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.gps_provider_vehicle_map import GPSProviderVehicleMap
from app.schemas.gps_provider_vehicle_map import GPSProviderVehicleMapCreate


async def get(db: AsyncSession, mapping_id: uuid.UUID, provider_id: uuid.UUID) -> GPSProviderVehicleMap | None:
    result = await db.execute(
        select(GPSProviderVehicleMap).where(
            GPSProviderVehicleMap.id == mapping_id, GPSProviderVehicleMap.provider_id == provider_id
        )
    )
    return result.scalar_one_or_none()


async def get_by_external_device_id(
    db: AsyncSession, provider_id: uuid.UUID, external_device_id: str
) -> GPSProviderVehicleMap | None:
    result = await db.execute(
        select(GPSProviderVehicleMap).where(
            GPSProviderVehicleMap.provider_id == provider_id,
            GPSProviderVehicleMap.external_device_id == external_device_id,
        )
    )
    return result.scalar_one_or_none()


async def list_for_provider(db: AsyncSession, provider_id: uuid.UUID) -> list[GPSProviderVehicleMap]:
    result = await db.execute(
        select(GPSProviderVehicleMap).where(GPSProviderVehicleMap.provider_id == provider_id)
    )
    return list(result.scalars().all())


async def create(
    db: AsyncSession, provider_id: uuid.UUID, data: GPSProviderVehicleMapCreate
) -> GPSProviderVehicleMap:
    mapping = GPSProviderVehicleMap(provider_id=provider_id, **data.model_dump())
    db.add(mapping)
    await db.commit()
    await db.refresh(mapping)
    return mapping


async def delete(db: AsyncSession, mapping: GPSProviderVehicleMap) -> None:
    await db.delete(mapping)
    await db.commit()
