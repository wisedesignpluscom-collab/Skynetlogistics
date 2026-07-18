import uuid
from datetime import date, datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.trip import Trip
from app.schemas.trip import TripCreate, TripUpdate


async def get(db: AsyncSession, trip_id: uuid.UUID, company_id: uuid.UUID) -> Trip | None:
    result = await db.execute(select(Trip).where(Trip.id == trip_id, Trip.company_id == company_id))
    return result.scalar_one_or_none()


async def get_with_details(db: AsyncSession, trip_id: uuid.UUID, company_id: uuid.UUID) -> Trip | None:
    result = await db.execute(
        select(Trip)
        .options(selectinload(Trip.expenses), selectinload(Trip.payroll))
        .where(Trip.id == trip_id, Trip.company_id == company_id)
    )
    return result.scalar_one_or_none()


async def list_paginated(
    db: AsyncSession,
    *,
    company_id: uuid.UUID,
    page: int,
    page_size: int,
    status: str | None = None,
    driver_id: uuid.UUID | None = None,
    vehicle_id: uuid.UUID | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> tuple[list[Trip], int]:
    query = select(Trip).where(Trip.company_id == company_id)
    count_query = select(func.count()).select_from(Trip).where(Trip.company_id == company_id)

    if status:
        query = query.where(Trip.status == status)
        count_query = count_query.where(Trip.status == status)
    if driver_id:
        query = query.where(Trip.driver_id == driver_id)
        count_query = count_query.where(Trip.driver_id == driver_id)
    if vehicle_id:
        query = query.where(Trip.vehicle_id == vehicle_id)
        count_query = count_query.where(Trip.vehicle_id == vehicle_id)
    if date_from:
        query = query.where(Trip.created_at >= date_from)
        count_query = count_query.where(Trip.created_at >= date_from)
    if date_to:
        query = query.where(Trip.created_at <= date_to)
        count_query = count_query.where(Trip.created_at <= date_to)

    total = (await db.execute(count_query)).scalar_one()
    query = query.order_by(Trip.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(query)).scalars().all()
    return list(items), total


async def create(
    db: AsyncSession,
    company_id: uuid.UUID,
    data: TripCreate,
    *,
    distance_km: float | None,
    freight_cost: float | None,
) -> Trip:
    trip = Trip(
        company_id=company_id,
        distance_km=distance_km,
        freight_cost=freight_cost,
        **data.model_dump(),
    )
    db.add(trip)
    await db.commit()
    await db.refresh(trip)
    return trip


async def update(db: AsyncSession, trip: Trip, data: TripUpdate) -> Trip:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(trip, field, value)
    await db.commit()
    await db.refresh(trip)
    return trip


async def start(db: AsyncSession, trip: Trip, start_odometer_km: int) -> Trip:
    trip.status = "en_curso"
    trip.start_odometer_km = start_odometer_km
    trip.started_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(trip)
    return trip


async def set_advance_payment(db: AsyncSession, trip: Trip, advance_payment: float) -> Trip:
    trip.advance_payment = advance_payment
    await db.commit()
    await db.refresh(trip)
    return trip


async def close(
    db: AsyncSession, trip: Trip, *, end_odometer_km: int, freight_cost: float | None
) -> Trip:
    trip.status = "completado"
    trip.end_odometer_km = end_odometer_km
    if freight_cost is not None:
        trip.freight_cost = freight_cost
    trip.ended_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(trip)
    return trip


async def cancel(db: AsyncSession, trip: Trip) -> Trip:
    trip.status = "cancelado"
    await db.commit()
    await db.refresh(trip)
    return trip
