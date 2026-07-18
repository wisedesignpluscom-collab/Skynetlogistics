from datetime import datetime, timedelta, timezone

import pytest

from app.models.fatigue_rule import FatigueRule
from app.models.trip import Trip
from app.models.vehicle_position import VehiclePosition
from app.services.fatigue_calculations import calculate_risk, compute_driver_fatigue


def _default_rule() -> FatigueRule:
    return FatigueRule(
        max_continuous_hours=4.5,
        max_24h_hours=10.0,
        max_7day_hours=60.0,
        night_driving_weight=1.5,
        night_start_hour=22,
        night_end_hour=5,
    )


def test_calculate_risk_matches_approved_example() -> None:
    score, level = calculate_risk(
        continuous_driving_min=240,
        total_24h_min=480,
        total_7day_min=2100,
        night_driving_min=180,
        rule=_default_rule(),
    )
    assert score == 105.56
    assert level == "critico"


def test_calculate_risk_thresholds() -> None:
    rule = _default_rule()

    low_score, low_level = calculate_risk(
        continuous_driving_min=60, total_24h_min=120, total_7day_min=600, night_driving_min=0, rule=rule
    )
    assert low_level == "bajo"
    assert low_score < 60

    high_score, high_level = calculate_risk(
        continuous_driving_min=250, total_24h_min=450, total_7day_min=2000, night_driving_min=0, rule=rule
    )
    assert high_level == "alto"
    assert 85 <= high_score < 100


async def test_compute_driver_fatigue_reconstructs_current_window_from_gps(
    db, company, driver, vehicle, gps_provider_webhook
) -> None:
    provider, _ = gps_provider_webhook
    now = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)

    start = now - timedelta(hours=3)
    ts = start
    while ts <= now:
        db.add(
            VehiclePosition(
                vehicle_id=vehicle.id,
                company_id=company.id,
                provider_id=provider.id,
                timestamp=ts,
                lat=10.0,
                lng=-66.0,
                ignition_status=True,
                raw_payload={},
            )
        )
        ts += timedelta(minutes=5)
    await db.commit()

    breakdown = await compute_driver_fatigue(
        db, driver=driver, vehicle_id=vehicle.id, rule=_default_rule(), now=now
    )
    assert breakdown is not None
    assert breakdown["continuous_driving_min"] == pytest.approx(180, abs=5)
    assert breakdown["total_24h_min"] == pytest.approx(180, abs=5)


async def test_long_gps_gap_splits_the_window(db, company, driver, vehicle, gps_provider_webhook) -> None:
    provider, _ = gps_provider_webhook
    now = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)

    t1 = now - timedelta(hours=5)
    t1_end = t1 + timedelta(minutes=30)
    # hueco de 20 min (> tolerancia de 15) antes de retomar -> debe cortar la ventana
    t2 = t1_end + timedelta(minutes=20)

    # primera ventana continua (lecturas cada 10 min, dentro de la tolerancia de 15)
    ts1 = t1
    while ts1 <= t1_end:
        db.add(
            VehiclePosition(
                vehicle_id=vehicle.id,
                company_id=company.id,
                provider_id=provider.id,
                timestamp=ts1,
                lat=10.0,
                lng=-66.0,
                ignition_status=True,
                raw_payload={},
            )
        )
        ts1 += timedelta(minutes=10)
    # segunda ventana continua (lecturas cada 5 min) desde t2 hasta "now"
    ts = t2
    while ts <= now:
        db.add(
            VehiclePosition(
                vehicle_id=vehicle.id,
                company_id=company.id,
                provider_id=provider.id,
                timestamp=ts,
                lat=10.0,
                lng=-66.0,
                ignition_status=True,
                raw_payload={},
            )
        )
        ts += timedelta(minutes=5)
    await db.commit()

    breakdown = await compute_driver_fatigue(
        db, driver=driver, vehicle_id=vehicle.id, rule=_default_rule(), now=now
    )
    assert breakdown is not None
    expected_continuous = (now - t2).total_seconds() / 60
    assert breakdown["continuous_driving_min"] == pytest.approx(expected_continuous, abs=1)
    # el total de 24h debe incluir ambas ventanas, no solo la última
    assert breakdown["total_24h_min"] > expected_continuous + 10


async def test_ignition_off_resets_continuous_window(db, company, driver, vehicle, gps_provider_webhook) -> None:
    provider, _ = gps_provider_webhook
    now = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)

    # Manejó 2h hace un rato, se detuvo (ignition off) hace 1h -> ya no está "manejando ahora".
    stopped_at = now - timedelta(hours=1)
    db.add(
        VehiclePosition(
            vehicle_id=vehicle.id,
            company_id=company.id,
            provider_id=provider.id,
            timestamp=stopped_at - timedelta(hours=2),
            lat=10.0,
            lng=-66.0,
            ignition_status=True,
            raw_payload={},
        )
    )
    db.add(
        VehiclePosition(
            vehicle_id=vehicle.id,
            company_id=company.id,
            provider_id=provider.id,
            timestamp=stopped_at,
            lat=10.0,
            lng=-66.0,
            ignition_status=False,
            raw_payload={},
        )
    )
    await db.commit()

    breakdown = await compute_driver_fatigue(
        db, driver=driver, vehicle_id=vehicle.id, rule=_default_rule(), now=now
    )
    assert breakdown is not None
    assert breakdown["continuous_driving_min"] == 0
    assert breakdown["total_24h_min"] == pytest.approx(120, abs=1)


async def test_fallback_to_trips_when_no_gps_data(db, company, driver, vehicle) -> None:
    now = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
    trip = Trip(
        company_id=company.id,
        vehicle_id=vehicle.id,
        driver_id=driver.id,
        origin="A",
        destination="B",
        cargo_type="general",
        status="completado",
        started_at=now - timedelta(hours=6),
        ended_at=now - timedelta(hours=1),
    )
    db.add(trip)
    await db.commit()

    breakdown = await compute_driver_fatigue(
        db, driver=driver, vehicle_id=vehicle.id, rule=_default_rule(), now=now
    )
    assert breakdown is not None
    assert breakdown["total_24h_min"] == pytest.approx(300, abs=1)
    assert breakdown["continuous_driving_min"] == 0  # terminó hace 1h, ya no maneja "ahora"


async def test_no_activity_returns_none(db, driver) -> None:
    now = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
    breakdown = await compute_driver_fatigue(db, driver=driver, vehicle_id=None, rule=_default_rule(), now=now)
    assert breakdown is None
