from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select

from app.jobs.fatigue import run_fatigue_checks
from app.models.alert import Alert
from app.models.driver import Driver
from app.models.driver_fatigue_log import DriverFatigueLog
from app.models.trip import Trip
from app.models.vehicle import Vehicle


async def test_job_creates_log_and_alert_for_critical_risk_via_trip_fallback(
    db, company, driver: Driver, vehicle: Vehicle
) -> None:
    now = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
    vehicle.assigned_driver_id = driver.id
    db.add(vehicle)
    trip = Trip(
        company_id=company.id,
        vehicle_id=vehicle.id,
        driver_id=driver.id,
        origin="A",
        destination="B",
        cargo_type="general",
        status="en_curso",
        started_at=now - timedelta(hours=8),
    )
    db.add(trip)
    await db.commit()

    result = await run_fatigue_checks(db, now=now)
    assert result["drivers_processed"] == 1
    assert result["alerts_created"] == 1

    log = (await db.execute(select(DriverFatigueLog).where(DriverFatigueLog.driver_id == driver.id))).scalar_one()
    assert log.risk_level in ("alto", "critico")
    assert log.date == now.date()

    alert = (await db.execute(select(Alert).where(Alert.entity_id == driver.id))).scalar_one()
    assert alert.type == "driver_fatigue"
    assert alert.entity_type == "driver"
    assert alert.status == "no_leida"


async def test_job_does_not_duplicate_alert_on_repeated_run(
    db, company, driver: Driver, vehicle: Vehicle
) -> None:
    now = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
    vehicle.assigned_driver_id = driver.id
    db.add(vehicle)
    trip = Trip(
        company_id=company.id,
        vehicle_id=vehicle.id,
        driver_id=driver.id,
        origin="A",
        destination="B",
        cargo_type="general",
        status="en_curso",
        started_at=now - timedelta(hours=8),
    )
    db.add(trip)
    await db.commit()

    first = await run_fatigue_checks(db, now=now)
    second = await run_fatigue_checks(db, now=now)
    assert first["alerts_created"] == 1
    assert second["alerts_created"] == 0

    alerts = (await db.execute(select(Alert).where(Alert.entity_id == driver.id))).scalars().all()
    assert len(alerts) == 1

    # el log se actualiza (upsert) en vez de duplicarse por (driver_id, date)
    logs = (await db.execute(select(DriverFatigueLog).where(DriverFatigueLog.driver_id == driver.id))).scalars().all()
    assert len(logs) == 1


async def test_job_skips_drivers_with_no_activity_no_log_created(db, driver: Driver) -> None:
    now = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
    result = await run_fatigue_checks(db, now=now)
    assert result["drivers_processed"] == 0
    assert result["alerts_created"] == 0

    logs = (await db.execute(select(DriverFatigueLog))).scalars().all()
    assert logs == []


async def test_job_skips_inactive_drivers(db, company, vehicle: Vehicle) -> None:
    now = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
    inactive_driver = Driver(
        company_id=company.id,
        name="Conductor Inactivo",
        license_number="LIC-INACTIVE",
        license_expiry=date(2030, 1, 1),
        status="inactivo",
    )
    db.add(inactive_driver)
    await db.flush()
    vehicle.assigned_driver_id = inactive_driver.id
    db.add(vehicle)
    trip = Trip(
        company_id=company.id,
        vehicle_id=vehicle.id,
        driver_id=inactive_driver.id,
        origin="A",
        destination="B",
        cargo_type="general",
        status="en_curso",
        started_at=now - timedelta(hours=8),
    )
    db.add(trip)
    await db.commit()

    result = await run_fatigue_checks(db, now=now)
    assert result["drivers_processed"] == 0
    assert result["alerts_created"] == 0


async def test_job_does_not_alert_for_low_risk_driver(db, company, driver: Driver, vehicle: Vehicle) -> None:
    now = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
    vehicle.assigned_driver_id = driver.id
    db.add(vehicle)
    trip = Trip(
        company_id=company.id,
        vehicle_id=vehicle.id,
        driver_id=driver.id,
        origin="A",
        destination="B",
        cargo_type="general",
        status="completado",
        started_at=now - timedelta(hours=2),
        ended_at=now - timedelta(hours=1, minutes=30),
    )
    db.add(trip)
    await db.commit()

    result = await run_fatigue_checks(db, now=now)
    assert result["drivers_processed"] == 1
    assert result["alerts_created"] == 0

    log = (await db.execute(select(DriverFatigueLog).where(DriverFatigueLog.driver_id == driver.id))).scalar_one()
    assert log.risk_level == "bajo"
