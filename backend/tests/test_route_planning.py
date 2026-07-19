from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.crud import route_plan as route_plan_crud
from app.crud import route_settings as route_settings_crud
from app.models.alert import Alert
from app.models.route_recalculation import RouteRecalculation
from app.models.trip import Trip
from app.services.route_planning import (
    check_deviation_and_recalculate,
    compute_route_plan,
    recalculate_route,
)

# Caracas -> Maracaibo (aprox). El FakeRoutingEngine interpola una recta entre ambos.
_ORIGIN = (10.5, -66.9)
_DEST = (10.6, -71.6)


async def _make_trip(db, company, vehicle, driver, *, status="en_curso") -> Trip:
    trip = Trip(
        company_id=company.id,
        vehicle_id=vehicle.id,
        driver_id=driver.id,
        origin="Caracas",
        destination="Maracaibo",
        cargo_type="general",
        status=status,
        distance_km=550,
        started_at=datetime(2026, 7, 18, 8, 0, tzinfo=timezone.utc),
    )
    db.add(trip)
    await db.commit()
    await db.refresh(trip)
    return trip


async def test_compute_route_plan_creates_plan_without_touching_trip_distance(
    db, company, vehicle, driver
) -> None:
    trip = await _make_trip(db, company, vehicle, driver, status="planificado")
    plan = await compute_route_plan(
        db,
        company_id=company.id,
        trip_id=trip.id,
        origin_lat=_ORIGIN[0],
        origin_lng=_ORIGIN[1],
        destination_lat=_DEST[0],
        destination_lng=_DEST[1],
    )
    assert plan.engine_used == "fake"
    assert plan.calculated_distance_km > 0
    assert len(plan.geometry) >= 2
    # trip.distance_km sigue siendo el operativo (550), no lo pisa el motor
    await db.refresh(trip)
    assert float(trip.distance_km) == 550


async def test_compute_route_plan_is_idempotent_per_trip(db, company, vehicle, driver) -> None:
    trip = await _make_trip(db, company, vehicle, driver, status="planificado")
    p1 = await compute_route_plan(
        db, company_id=company.id, trip_id=trip.id,
        origin_lat=_ORIGIN[0], origin_lng=_ORIGIN[1], destination_lat=_DEST[0], destination_lng=_DEST[1],
    )
    p2 = await compute_route_plan(
        db, company_id=company.id, trip_id=trip.id,
        origin_lat=_ORIGIN[0], origin_lng=_ORIGIN[1], destination_lat=_DEST[0], destination_lng=_DEST[1],
    )
    assert p1.id == p2.id  # UNIQUE(trip_id): un solo plan vigente por viaje


async def test_deviation_triggers_recalc_and_alert(db, company, vehicle, driver) -> None:
    trip = await _make_trip(db, company, vehicle, driver)
    vehicle.assigned_driver_id = driver.id
    db.add(vehicle)
    await compute_route_plan(
        db, company_id=company.id, trip_id=trip.id,
        origin_lat=_ORIGIN[0], origin_lng=_ORIGIN[1], destination_lat=_DEST[0], destination_lng=_DEST[1],
    )

    # Punto muy lejos de la recta Caracas-Maracaibo (bien al sur) -> desvío enorme
    now = datetime(2026, 7, 18, 10, 0, tzinfo=timezone.utc)
    recalc = await check_deviation_and_recalculate(
        db, vehicle_id=vehicle.id, company_id=company.id, lat=8.0, lng=-69.0, now=now
    )
    assert recalc is not None
    assert recalc.reason == "desvio"
    assert recalc.deviation_m > 150

    alert = (await db.execute(select(Alert).where(Alert.type == "route_deviation"))).scalar_one()
    assert alert.entity_id == trip.id
    assert alert.severity == "media"


async def test_no_deviation_when_on_route(db, company, vehicle, driver) -> None:
    trip = await _make_trip(db, company, vehicle, driver)
    await compute_route_plan(
        db, company_id=company.id, trip_id=trip.id,
        origin_lat=_ORIGIN[0], origin_lng=_ORIGIN[1], destination_lat=_DEST[0], destination_lng=_DEST[1],
    )
    now = datetime(2026, 7, 18, 10, 0, tzinfo=timezone.utc)
    # Punto sobre la recta (punto medio aprox)
    recalc = await check_deviation_and_recalculate(
        db, vehicle_id=vehicle.id, company_id=company.id, lat=10.55, lng=-69.25, now=now
    )
    assert recalc is None


async def test_no_recalc_when_vehicle_has_no_active_trip(db, company, vehicle, driver) -> None:
    trip = await _make_trip(db, company, vehicle, driver, status="planificado")
    await compute_route_plan(
        db, company_id=company.id, trip_id=trip.id,
        origin_lat=_ORIGIN[0], origin_lng=_ORIGIN[1], destination_lat=_DEST[0], destination_lng=_DEST[1],
    )
    now = datetime(2026, 7, 18, 10, 0, tzinfo=timezone.utc)
    # No hay viaje en_curso -> None aunque esté lejísimos de la ruta
    recalc = await check_deviation_and_recalculate(
        db, vehicle_id=vehicle.id, company_id=company.id, lat=8.0, lng=-69.0, now=now
    )
    assert recalc is None


async def test_cooldown_prevents_second_recalc(db, company, vehicle, driver) -> None:
    trip = await _make_trip(db, company, vehicle, driver)
    plan = await compute_route_plan(
        db, company_id=company.id, trip_id=trip.id,
        origin_lat=_ORIGIN[0], origin_lng=_ORIGIN[1], destination_lat=_DEST[0], destination_lng=_DEST[1],
    )
    # El cooldown compara `now` contra el created_at (reloj de la DB) del último recálculo, por eso
    # se usan tiempos relativos al reloj real (default cooldown = 5 min).
    base = datetime.now(timezone.utc)
    first = await check_deviation_and_recalculate(
        db, vehicle_id=vehicle.id, company_id=company.id, lat=8.0, lng=-69.0, now=base
    )
    assert first is not None

    # ~2 min después, sigue desviado -> bloqueado por cooldown
    second = await check_deviation_and_recalculate(
        db, vehicle_id=vehicle.id, company_id=company.id, lat=8.0, lng=-69.0, now=base + timedelta(minutes=2),
    )
    assert second is None

    # ~6 min después -> se permite de nuevo
    third = await check_deviation_and_recalculate(
        db, vehicle_id=vehicle.id, company_id=company.id, lat=8.0, lng=-69.0, now=base + timedelta(minutes=6),
    )
    assert third is not None

    recalcs = (
        await db.execute(select(RouteRecalculation).where(RouteRecalculation.route_plan_id == plan.id))
    ).scalars().all()
    assert len(recalcs) == 2


async def test_manual_recalculation_logs_event(db, company, vehicle, driver) -> None:
    trip = await _make_trip(db, company, vehicle, driver)
    plan = await compute_route_plan(
        db, company_id=company.id, trip_id=trip.id,
        origin_lat=_ORIGIN[0], origin_lng=_ORIGIN[1], destination_lat=_DEST[0], destination_lng=_DEST[1],
    )
    recalc = await recalculate_route(db, plan, reason="manual")
    assert recalc.reason == "manual"
    assert recalc.deviation_m is None
    assert recalc.new_distance_km > 0
