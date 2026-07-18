from datetime import date, timedelta

from httpx import AsyncClient

from app.jobs.alerts import run_alert_checks
from app.models.driver import Driver
from app.models.maintenance_task import MaintenanceTask
from app.models.user import User
from app.models.vehicle import Vehicle
from tests.conftest import auth_headers


async def test_job_creates_alert_for_maintenance_due_by_date(
    db, company, vehicle: Vehicle
) -> None:
    today = date(2026, 1, 1)
    task = MaintenanceTask(
        company_id=company.id,
        vehicle_id=vehicle.id,
        type="preventivo",
        scheduled_by="tiempo",
        due_date=today + timedelta(days=1),
        status="pendiente",
    )
    db.add(task)
    await db.commit()

    result = await run_alert_checks(db, today=today)
    assert result["maintenance_due"] == 1

    from sqlalchemy import select

    from app.models.alert import Alert

    alerts = (await db.execute(select(Alert))).scalars().all()
    assert len(alerts) == 1
    assert alerts[0].severity == "alta"
    assert alerts[0].type == "maintenance_due"


async def test_job_creates_medium_severity_for_km_threshold(db, company, vehicle: Vehicle) -> None:
    # vehicle.current_odometer_km = 10_000 (fixture); due_km - odometer = 300 -> media
    task = MaintenanceTask(
        company_id=company.id,
        vehicle_id=vehicle.id,
        type="preventivo",
        scheduled_by="km",
        due_km=vehicle.current_odometer_km + 300,
        status="pendiente",
    )
    db.add(task)
    await db.commit()

    result = await run_alert_checks(db, today=date(2026, 1, 1))
    assert result["maintenance_due"] == 1

    from sqlalchemy import select

    from app.models.alert import Alert

    alert = (await db.execute(select(Alert))).scalar_one()
    assert alert.severity == "media"


async def test_job_ignores_task_far_from_due(db, company, vehicle: Vehicle) -> None:
    task = MaintenanceTask(
        company_id=company.id,
        vehicle_id=vehicle.id,
        type="preventivo",
        scheduled_by="tiempo",
        due_date=date(2026, 6, 1),
        status="pendiente",
    )
    db.add(task)
    await db.commit()

    result = await run_alert_checks(db, today=date(2026, 1, 1))
    assert result["maintenance_due"] == 0


async def test_job_does_not_duplicate_unread_alerts(db, company, vehicle: Vehicle) -> None:
    today = date(2026, 1, 1)
    task = MaintenanceTask(
        company_id=company.id,
        vehicle_id=vehicle.id,
        type="preventivo",
        scheduled_by="tiempo",
        due_date=today,
        status="pendiente",
    )
    db.add(task)
    await db.commit()

    first = await run_alert_checks(db, today=today)
    second = await run_alert_checks(db, today=today)
    assert first["maintenance_due"] == 1
    assert second["maintenance_due"] == 0

    from sqlalchemy import select

    from app.models.alert import Alert

    alerts = (await db.execute(select(Alert))).scalars().all()
    assert len(alerts) == 1


async def test_job_creates_alert_for_expiring_license(db, company, driver: Driver) -> None:
    today = date(2026, 1, 1)
    driver.license_expiry = today + timedelta(days=5)
    await db.commit()

    result = await run_alert_checks(db, today=today)
    assert result["license_expiring"] == 1

    from sqlalchemy import select

    from app.models.alert import Alert

    alert = (await db.execute(select(Alert))).scalar_one()
    assert alert.type == "license_expiring"
    assert alert.severity == "alta"


async def test_alerts_endpoints_list_read_and_unread_count(
    client: AsyncClient, admin_user: User, db, company, vehicle: Vehicle
) -> None:
    today = date(2026, 1, 1)
    task = MaintenanceTask(
        company_id=company.id,
        vehicle_id=vehicle.id,
        type="preventivo",
        scheduled_by="tiempo",
        due_date=today,
        status="pendiente",
    )
    db.add(task)
    await db.commit()
    await run_alert_checks(db, today=today)

    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")

    count_resp = await client.get("/api/v1/alerts/unread-count", headers=headers)
    assert count_resp.json()["count"] == 1

    list_resp = await client.get("/api/v1/alerts", headers=headers)
    assert list_resp.status_code == 200
    alert_id = list_resp.json()["items"][0]["id"]

    read_resp = await client.patch(f"/api/v1/alerts/{alert_id}/read", headers=headers)
    assert read_resp.status_code == 200
    assert read_resp.json()["status"] == "leida"

    count_after = await client.get("/api/v1/alerts/unread-count", headers=headers)
    assert count_after.json()["count"] == 0
