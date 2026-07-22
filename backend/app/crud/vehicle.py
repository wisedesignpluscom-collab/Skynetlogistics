import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleUpdate


async def get(db: AsyncSession, vehicle_id: uuid.UUID, company_id: uuid.UUID) -> Vehicle | None:
    result = await db.execute(
        select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.company_id == company_id)
    )
    return result.scalar_one_or_none()


async def get_odometers_by_ids(
    db: AsyncSession, vehicle_ids: list[uuid.UUID], company_id: uuid.UUID
) -> dict[uuid.UUID, int]:
    if not vehicle_ids:
        return {}
    result = await db.execute(
        select(Vehicle.id, Vehicle.current_odometer_km).where(
            Vehicle.id.in_(vehicle_ids), Vehicle.company_id == company_id
        )
    )
    return {row.id: row.current_odometer_km for row in result}


async def get_by_plate(db: AsyncSession, company_id: uuid.UUID, plate: str) -> Vehicle | None:
    result = await db.execute(
        select(Vehicle).where(Vehicle.company_id == company_id, Vehicle.plate == plate)
    )
    return result.scalar_one_or_none()


async def list_paginated(
    db: AsyncSession,
    *,
    company_id: uuid.UUID,
    page: int,
    page_size: int,
    search: str | None = None,
    status: str | None = None,
    type: str | None = None,
) -> tuple[list[Vehicle], int]:
    query = select(Vehicle).where(Vehicle.company_id == company_id)
    count_query = select(func.count()).select_from(Vehicle).where(Vehicle.company_id == company_id)

    if search:
        pattern = f"%{search}%"
        query = query.where(Vehicle.plate.ilike(pattern) | Vehicle.brand.ilike(pattern))
        count_query = count_query.where(Vehicle.plate.ilike(pattern) | Vehicle.brand.ilike(pattern))
    if status:
        query = query.where(Vehicle.status == status)
        count_query = count_query.where(Vehicle.status == status)
    if type:
        query = query.where(Vehicle.type == type)
        count_query = count_query.where(Vehicle.type == type)

    total = (await db.execute(count_query)).scalar_one()
    query = query.order_by(Vehicle.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(query)).scalars().all()
    return list(items), total


async def create(db: AsyncSession, company_id: uuid.UUID, data: VehicleCreate) -> Vehicle:
    vehicle = Vehicle(company_id=company_id, **data.model_dump())
    db.add(vehicle)
    await db.commit()
    await db.refresh(vehicle)
    return vehicle


async def update(db: AsyncSession, vehicle: Vehicle, data: VehicleUpdate) -> Vehicle:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(vehicle, field, value)
    await db.commit()
    await db.refresh(vehicle)
    return vehicle


async def deactivate(db: AsyncSession, vehicle: Vehicle) -> Vehicle:
    vehicle.status = "inactivo"
    await db.commit()
    await db.refresh(vehicle)
    return vehicle
