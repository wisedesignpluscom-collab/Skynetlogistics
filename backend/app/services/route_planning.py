"""Servicio de planificación de rutas (Fase 7A).

Centraliza el cálculo de la ruta punto a punto (vía el `RoutingEngine` activo) y su persistencia
en `route_plans`, para que lo compartan: el auto-trigger al crear un viaje, el endpoint de cálculo
bajo demanda, el recálculo manual y el recálculo automático por desvío. Es el único lugar que
llama al motor de ruteo y escribe geometría — mismo criterio "un solo punto de entrada" que
`tire_movements.py::apply_movement` / `inventory_movements.py::apply_movement`.

`compute_route_plan` NUNCA toca `trips.distance_km`: la distancia estimada por el motor vive solo
en `route_plans.calculated_distance_km`; `trips.distance_km` es el dato operativo que alimenta el
flete (Fase 2) y lo controla el usuario.
"""

import uuid
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import route_plan as route_plan_crud
from app.crud import route_settings as route_settings_crud
from app.crud.alert import create_if_not_exists
from app.models.route_plan import RoutePlan
from app.models.route_recalculation import RouteRecalculation
from app.models.trip import Trip
from app.routing_engines import get_engine
from app.services.route_geometry import distance_to_polyline_m


async def compute_route_plan(
    db: AsyncSession,
    *,
    company_id: uuid.UUID,
    trip_id: uuid.UUID,
    origin_lat: float,
    origin_lng: float,
    destination_lat: float,
    destination_lng: float,
) -> RoutePlan:
    """Calcula la ruta con el motor activo y hace upsert del plan del viaje."""
    engine = get_engine()
    result = await engine.route(
        origin_lat=origin_lat,
        origin_lng=origin_lng,
        destination_lat=destination_lat,
        destination_lng=destination_lng,
    )
    return await route_plan_crud.upsert_for_trip(
        db,
        company_id=company_id,
        trip_id=trip_id,
        origin_lat=origin_lat,
        origin_lng=origin_lng,
        destination_lat=destination_lat,
        destination_lng=destination_lng,
        geometry=result.geometry,
        calculated_distance_km=result.distance_km,
        calculated_duration_min=result.duration_min,
        engine_used=engine.engine_name,
    )


async def compute_multi_stop_route_plan(
    db: AsyncSession,
    *,
    company_id: uuid.UUID,
    trip_id: uuid.UUID,
    origin_lat: float,
    origin_lng: float,
    stops: list[dict],
) -> RoutePlan:
    """Como `compute_route_plan`, pero para un trip con paradas intermedias (Fase 7B/VRP).

    No se extiende `RoutingEngine.route()` con soporte nativo de waypoints: en su lugar se llama
    al motor activo una vez por tramo (origen→parada1→parada2→...→última parada) y se concatenan
    los resultados — mismo motor, mismo "único punto de entrada" que `compute_route_plan`, sin
    tocar la interfaz de 7A. `stops` ya viene ordenado por el solver VRP;
    cada elemento es `{"lat": .., "lng": .., "label": ..}` y el último define el destino del trip.
    """
    if not stops:
        raise ValueError("compute_multi_stop_route_plan requiere al menos una parada")

    engine = get_engine()
    leg_points = [(origin_lat, origin_lng)] + [(s["lat"], s["lng"]) for s in stops]

    geometry: list[list[float]] = []
    total_distance_km = 0.0
    total_duration_min = 0
    for (lat_a, lng_a), (lat_b, lng_b) in zip(leg_points, leg_points[1:]):
        leg = await engine.route(
            origin_lat=lat_a, origin_lng=lng_a, destination_lat=lat_b, destination_lng=lng_b
        )
        # Evita duplicar el punto de unión entre tramos consecutivos.
        geometry.extend(leg.geometry[1:] if geometry else leg.geometry)
        total_distance_km += leg.distance_km
        total_duration_min += leg.duration_min

    destination_lat, destination_lng = leg_points[-1]
    return await route_plan_crud.upsert_for_trip(
        db,
        company_id=company_id,
        trip_id=trip_id,
        origin_lat=origin_lat,
        origin_lng=origin_lng,
        destination_lat=destination_lat,
        destination_lng=destination_lng,
        geometry=geometry,
        calculated_distance_km=round(total_distance_km, 2),
        calculated_duration_min=total_duration_min,
        engine_used=engine.engine_name,
        waypoints=stops,
    )


async def recalculate_route(
    db: AsyncSession,
    plan: RoutePlan,
    *,
    reason: str,
    deviation_m: float | None = None,
    trigger_lat: float | None = None,
    trigger_lng: float | None = None,
) -> RouteRecalculation:
    """Recalcula la geometría del plan (mismos origen/destino), la actualiza y registra el evento.

    Reutilizado por el recálculo manual (`reason='manual'`) y el automático por desvío
    (`reason='desvio'`).
    """
    engine = get_engine()
    result = await engine.route(
        origin_lat=float(plan.origin_lat),
        origin_lng=float(plan.origin_lng),
        destination_lat=float(plan.destination_lat),
        destination_lng=float(plan.destination_lng),
    )
    await route_plan_crud.update_geometry(
        db,
        plan,
        geometry=result.geometry,
        calculated_distance_km=result.distance_km,
        calculated_duration_min=result.duration_min,
    )
    return await route_plan_crud.create_recalculation(
        db,
        company_id=plan.company_id,
        route_plan_id=plan.id,
        reason=reason,
        deviation_m=deviation_m,
        trigger_lat=trigger_lat,
        trigger_lng=trigger_lng,
        new_distance_km=result.distance_km,
        new_duration_min=result.duration_min,
        new_route_data=result.geometry,
    )


async def check_deviation_and_recalculate(
    db: AsyncSession,
    *,
    vehicle_id: uuid.UUID,
    company_id: uuid.UUID,
    lat: float,
    lng: float,
    now: datetime,
) -> RouteRecalculation | None:
    """Tras una posición GPS nueva: si el vehículo tiene un viaje en curso con plan de ruta y se
    desvió más del umbral configurado (respetando el cooldown), recalcula, registra el evento y
    genera una alerta `route_deviation` (reutilizando el anti-duplicado de Fase 1).

    Devuelve el `RouteRecalculation` creado, o None si no hubo desvío accionable. No levanta
    excepciones hacia la ingesta: es una función best-effort que no debe tumbar el webhook.
    """
    # Viaje en curso del vehículo (si hay varios, el más reciente por started_at).
    trip_result = await db.execute(
        select(Trip)
        .where(
            Trip.vehicle_id == vehicle_id,
            Trip.company_id == company_id,
            Trip.status == "en_curso",
        )
        .order_by(Trip.started_at.desc())
        .limit(1)
    )
    trip = trip_result.scalar_one_or_none()
    if trip is None:
        return None

    plan = await route_plan_crud.get_by_trip(db, trip.id, company_id)
    if plan is None or not plan.geometry:
        return None

    settings = await route_settings_crud.get_or_create(db, company_id)
    deviation = distance_to_polyline_m(lat, lng, plan.geometry)
    if deviation <= settings.deviation_threshold_m:
        return None

    # Cooldown: no re-disparar si hubo un recálculo hace menos de recalc_cooldown_min.
    last = await route_plan_crud.latest_recalculation(db, plan.id)
    if last is not None and settings.recalc_cooldown_min > 0:
        if now - last.created_at < timedelta(minutes=settings.recalc_cooldown_min):
            return None

    recalc = await recalculate_route(
        db, plan, reason="desvio", deviation_m=round(deviation, 2), trigger_lat=lat, trigger_lng=lng
    )

    await create_if_not_exists(
        db,
        company_id=company_id,
        type="route_deviation",
        entity_type="trip",
        entity_id=trip.id,
        message=(
            f"Desvío de ruta detectado en el viaje {trip.origin} → {trip.destination} "
            f"({round(deviation)} m de la ruta planeada); ruta recalculada"
        ),
        severity="media",
    )
    return recalc


__all__ = [
    "compute_route_plan",
    "compute_multi_stop_route_plan",
    "recalculate_route",
    "check_deviation_and_recalculate",
]
