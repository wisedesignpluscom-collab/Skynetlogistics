import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.route_plan import RoutePlan
from app.models.route_recalculation import RouteRecalculation


async def get_by_trip(db: AsyncSession, trip_id: uuid.UUID, company_id: uuid.UUID) -> RoutePlan | None:
    result = await db.execute(
        select(RoutePlan).where(RoutePlan.trip_id == trip_id, RoutePlan.company_id == company_id)
    )
    return result.scalar_one_or_none()


async def get(db: AsyncSession, plan_id: uuid.UUID, company_id: uuid.UUID) -> RoutePlan | None:
    result = await db.execute(
        select(RoutePlan).where(RoutePlan.id == plan_id, RoutePlan.company_id == company_id)
    )
    return result.scalar_one_or_none()


async def upsert_for_trip(
    db: AsyncSession,
    *,
    company_id: uuid.UUID,
    trip_id: uuid.UUID,
    origin_lat: float,
    origin_lng: float,
    destination_lat: float,
    destination_lng: float,
    geometry: list,
    calculated_distance_km: float,
    calculated_duration_min: int,
    engine_used: str,
) -> RoutePlan:
    """Crea el plan del viaje o actualiza el existente (UNIQUE(trip_id) — un plan vigente por viaje)."""
    plan = await get_by_trip(db, trip_id, company_id)
    if plan is None:
        plan = RoutePlan(company_id=company_id, trip_id=trip_id, waypoints=[])
        db.add(plan)
    plan.origin_lat = origin_lat
    plan.origin_lng = origin_lng
    plan.destination_lat = destination_lat
    plan.destination_lng = destination_lng
    plan.geometry = geometry
    plan.calculated_distance_km = calculated_distance_km
    plan.calculated_duration_min = calculated_duration_min
    plan.engine_used = engine_used
    await db.commit()
    await db.refresh(plan)
    return plan


async def update_geometry(
    db: AsyncSession,
    plan: RoutePlan,
    *,
    geometry: list,
    calculated_distance_km: float,
    calculated_duration_min: int,
) -> RoutePlan:
    plan.geometry = geometry
    plan.calculated_distance_km = calculated_distance_km
    plan.calculated_duration_min = calculated_duration_min
    await db.commit()
    await db.refresh(plan)
    return plan


async def list_recalculations(
    db: AsyncSession, route_plan_id: uuid.UUID
) -> list[RouteRecalculation]:
    result = await db.execute(
        select(RouteRecalculation)
        .where(RouteRecalculation.route_plan_id == route_plan_id)
        .order_by(RouteRecalculation.created_at.desc())
    )
    return list(result.scalars().all())


async def create_recalculation(
    db: AsyncSession, *, company_id: uuid.UUID, route_plan_id: uuid.UUID, **fields
) -> RouteRecalculation:
    recalc = RouteRecalculation(company_id=company_id, route_plan_id=route_plan_id, **fields)
    db.add(recalc)
    await db.commit()
    await db.refresh(recalc)
    return recalc


async def latest_recalculation(
    db: AsyncSession, route_plan_id: uuid.UUID
) -> RouteRecalculation | None:
    result = await db.execute(
        select(RouteRecalculation)
        .where(RouteRecalculation.route_plan_id == route_plan_id)
        .order_by(RouteRecalculation.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()
