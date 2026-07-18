import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.gps_adapters.base import NormalizedPosition
from app.models.vehicle_position import VehiclePosition


async def create(
    db: AsyncSession,
    *,
    company_id: uuid.UUID,
    vehicle_id: uuid.UUID,
    provider_id: uuid.UUID,
    position: NormalizedPosition,
    raw_payload: dict[str, Any],
) -> VehiclePosition:
    record = VehiclePosition(
        vehicle_id=vehicle_id,
        company_id=company_id,
        provider_id=provider_id,
        timestamp=position.timestamp,
        lat=position.lat,
        lng=position.lng,
        speed_kmh=position.speed_kmh,
        odometer_km=position.odometer_km,
        ignition_status=position.ignition_status,
        heading=position.heading,
        raw_payload=raw_payload,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def get_latest_for_vehicle(
    db: AsyncSession, vehicle_id: uuid.UUID, company_id: uuid.UUID
) -> VehiclePosition | None:
    result = await db.execute(
        select(VehiclePosition)
        .where(VehiclePosition.vehicle_id == vehicle_id, VehiclePosition.company_id == company_id)
        .order_by(VehiclePosition.timestamp.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_latest_for_fleet(db: AsyncSession, company_id: uuid.UUID) -> list[VehiclePosition]:
    result = await db.execute(
        select(VehiclePosition)
        .distinct(VehiclePosition.vehicle_id)
        .where(VehiclePosition.company_id == company_id)
        .order_by(VehiclePosition.vehicle_id, VehiclePosition.timestamp.desc())
    )
    return list(result.scalars().all())


async def list_history(
    db: AsyncSession,
    *,
    vehicle_id: uuid.UUID,
    company_id: uuid.UUID,
    date_from: datetime,
    date_to: datetime,
) -> list[VehiclePosition]:
    result = await db.execute(
        select(VehiclePosition)
        .where(
            VehiclePosition.vehicle_id == vehicle_id,
            VehiclePosition.company_id == company_id,
            VehiclePosition.timestamp >= date_from,
            VehiclePosition.timestamp <= date_to,
        )
        .order_by(VehiclePosition.timestamp.asc())
    )
    return list(result.scalars().all())
