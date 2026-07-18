import uuid
from datetime import date, datetime, timedelta, timezone

from httpx import AsyncClient
from sqlalchemy import select

from app.models.company import Company
from app.models.company_holiday import CompanyHoliday
from app.models.driver import Driver
from app.models.driver_pay_rate import DriverPayRate
from app.models.maintenance_task import MaintenanceTask
from app.models.rate_table import RateTable
from app.models.trip import Trip
from app.models.user import User
from app.models.vehicle import Vehicle
from tests.conftest import auth_headers


async def _create_trip(
    client: AsyncClient, headers: dict, vehicle: Vehicle, driver: Driver, **overrides
) -> dict:
    payload = {
        "vehicle_id": str(vehicle.id),
        "driver_id": str(driver.id),
        "origin": "Caracas",
        "destination": "Maracaibo",
        "cargo_type": "general",
        "is_round_trip": True,
    }
    payload.update(overrides)
    resp = await client.post("/api/v1/trips", headers=headers, json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()


async def test_create_trip_suggests_distance_and_freight_from_rate_table(
    client: AsyncClient, admin_user: User, vehicle: Vehicle, driver: Driver, rate_table: RateTable
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    trip = await _create_trip(client, headers, vehicle, driver)
    assert trip["distance_km"] == 550.0
    assert trip["freight_cost"] == 800.0
    assert trip["status"] == "planificado"


async def test_create_trip_without_rate_match_has_null_estimates(
    client: AsyncClient, admin_user: User, vehicle: Vehicle, driver: Driver
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    trip = await _create_trip(client, headers, vehicle, driver, destination="Unknown City")
    assert trip["distance_km"] is None
    assert trip["freight_cost"] is None


async def test_create_trip_rejects_trailer_of_wrong_type(
    client: AsyncClient, admin_user: User, vehicle: Vehicle, driver: Driver
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/trips",
        headers=headers,
        json={
            "vehicle_id": str(vehicle.id),
            "driver_id": str(driver.id),
            "trailer_id": str(vehicle.id),  # es un camión, no un remolque
            "origin": "Caracas",
            "destination": "Maracaibo",
            "cargo_type": "general",
        },
    )
    assert resp.status_code == 400


async def test_start_trip_rejects_odometer_below_current(
    client: AsyncClient, admin_user: User, vehicle: Vehicle, driver: Driver
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    trip = await _create_trip(client, headers, vehicle, driver)
    resp = await client.post(
        f"/api/v1/trips/{trip['id']}/start",
        headers=headers,
        json={"start_odometer_km": vehicle.current_odometer_km - 1},
    )
    assert resp.status_code == 400


async def test_expenses_only_allowed_while_en_curso(
    client: AsyncClient, admin_user: User, vehicle: Vehicle, driver: Driver, expense_concept
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    trip = await _create_trip(client, headers, vehicle, driver)

    blocked_resp = await client.post(
        f"/api/v1/trips/{trip['id']}/expenses",
        headers=headers,
        json={"concept_id": str(expense_concept.id), "amount": 10},
    )
    assert blocked_resp.status_code == 409

    await client.post(
        f"/api/v1/trips/{trip['id']}/start",
        headers=headers,
        json={"start_odometer_km": vehicle.current_odometer_km},
    )
    ok_resp = await client.post(
        f"/api/v1/trips/{trip['id']}/expenses",
        headers=headers,
        json={"concept_id": str(expense_concept.id), "amount": 10, "notes": "Diesel"},
    )
    assert ok_resp.status_code == 201

    list_resp = await client.get(f"/api/v1/trips/{trip['id']}/expenses", headers=headers)
    assert len(list_resp.json()) == 1


async def test_close_without_started_trip_conflicts(
    client: AsyncClient, admin_user: User, vehicle: Vehicle, driver: Driver
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    trip = await _create_trip(client, headers, vehicle, driver)
    resp = await client.post(
        f"/api/v1/trips/{trip['id']}/close",
        headers=headers,
        json={"end_odometer_km": vehicle.current_odometer_km + 100},
    )
    assert resp.status_code == 409


async def test_close_without_pay_rate_configured_rejects(
    client: AsyncClient, admin_user: User, vehicle: Vehicle, driver: Driver
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    trip = await _create_trip(client, headers, vehicle, driver)
    await client.post(
        f"/api/v1/trips/{trip['id']}/start",
        headers=headers,
        json={"start_odometer_km": vehicle.current_odometer_km},
    )
    resp = await client.post(
        f"/api/v1/trips/{trip['id']}/close",
        headers=headers,
        json={"end_odometer_km": vehicle.current_odometer_km + 100},
    )
    assert resp.status_code == 400


async def test_close_trip_computes_payroll_per_approved_formula(
    client: AsyncClient,
    admin_user: User,
    vehicle: Vehicle,
    driver: Driver,
    driver_pay_rate: DriverPayRate,
    db,
    company: Company,
) -> None:
    """Reproduce el ejemplo numérico aprobado: base $150 + bonos $115 - anticipo $50 = $215."""
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    trip = await _create_trip(client, headers, vehicle, driver)

    await client.post(
        f"/api/v1/trips/{trip['id']}/start",
        headers=headers,
        json={"start_odometer_km": vehicle.current_odometer_km},
    )

    # Fuerza started_at a hace 2 días (trip_days=3) y agrega un feriado en esa fecha.
    forced_start = datetime.now(timezone.utc) - timedelta(days=2)
    trip_obj = (await db.execute(select(Trip).where(Trip.id == uuid.UUID(trip["id"])))).scalar_one()
    trip_obj.started_at = forced_start
    db.add(CompanyHoliday(company_id=company.id, date=forced_start.date(), name="Feriado de prueba"))
    await db.commit()

    advance_resp = await client.patch(
        f"/api/v1/trips/{trip['id']}/advance", headers=headers, json={"advance_payment": 50}
    )
    assert advance_resp.status_code == 200

    preview_resp = await client.get(f"/api/v1/trips/{trip['id']}/close-preview", headers=headers)
    assert preview_resp.status_code == 200
    preview = preview_resp.json()
    assert preview["trip_days"] == 3
    assert preview["base_salary"] == 150.0
    assert preview["meal_allowance"] == 45.0
    assert preview["holiday_bonus"] == 30.0
    assert preview["holiday_count"] == 1
    assert preview["return_bonus"] == 40.0
    assert preview["bonuses"] == 115.0
    assert preview["total_to_pay"] == 215.0

    close_resp = await client.post(
        f"/api/v1/trips/{trip['id']}/close",
        headers=headers,
        json={"end_odometer_km": vehicle.current_odometer_km + 550},
    )
    assert close_resp.status_code == 200
    body = close_resp.json()
    assert body["status"] == "completado"
    payroll = body["payroll"]
    assert payroll["base_salary"] == 150.0
    assert payroll["meal_allowance"] == 45.0
    assert payroll["holiday_bonus"] == 30.0
    assert payroll["return_bonus"] == 40.0
    assert payroll["bonuses"] == 115.0
    assert payroll["advance_payment"] == 50.0
    assert payroll["total_to_pay"] == 215.0


async def test_close_trip_updates_vehicle_odometer_and_rechecks_maintenance(
    client: AsyncClient,
    admin_user: User,
    vehicle: Vehicle,
    driver: Driver,
    driver_pay_rate: DriverPayRate,
    db,
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")

    # Tarea de mantenimiento que quedará a 200 km (severidad "media") tras el cierre.
    new_odometer = vehicle.current_odometer_km + 1000
    task = MaintenanceTask(
        company_id=vehicle.company_id,
        vehicle_id=vehicle.id,
        type="preventivo",
        scheduled_by="km",
        due_km=new_odometer + 200,
        status="pendiente",
    )
    db.add(task)
    await db.commit()

    trip = await _create_trip(client, headers, vehicle, driver)
    await client.post(
        f"/api/v1/trips/{trip['id']}/start",
        headers=headers,
        json={"start_odometer_km": vehicle.current_odometer_km},
    )
    close_resp = await client.post(
        f"/api/v1/trips/{trip['id']}/close", headers=headers, json={"end_odometer_km": new_odometer}
    )
    assert close_resp.status_code == 200

    vehicle_resp = await client.get(f"/api/v1/vehicles/{vehicle.id}", headers=headers)
    assert vehicle_resp.json()["current_odometer_km"] == new_odometer

    alerts_resp = await client.get("/api/v1/alerts", headers=headers)
    alerts = alerts_resp.json()["items"]
    assert any(a["type"] == "maintenance_due" and a["entity_id"] == str(task.id) for a in alerts)


async def test_cancel_trip(client: AsyncClient, admin_user: User, vehicle: Vehicle, driver: Driver) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    trip = await _create_trip(client, headers, vehicle, driver)
    resp = await client.post(f"/api/v1/trips/{trip['id']}/cancel", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelado"


async def test_tenant_isolation_trips_list(
    client: AsyncClient,
    admin_user: User,
    vehicle: Vehicle,
    driver: Driver,
    other_company: Company,
    db,
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    await _create_trip(client, headers, vehicle, driver)

    other_vehicle = Vehicle(
        company_id=other_company.id, plate="OTH-999", brand="Scania", model="R450", year=2020, type="camion"
    )
    other_driver = Driver(
        company_id=other_company.id, name="Other Driver", license_number="OTH-LIC", license_expiry=date(2030, 1, 1)
    )
    db.add_all([other_vehicle, other_driver])
    await db.commit()
    await db.refresh(other_vehicle)
    await db.refresh(other_driver)
    other_trip = Trip(
        company_id=other_company.id,
        vehicle_id=other_vehicle.id,
        driver_id=other_driver.id,
        origin="X",
        destination="Y",
        cargo_type="general",
    )
    db.add(other_trip)
    await db.commit()

    resp = await client.get("/api/v1/trips", headers=headers)
    trip_ids = [t["id"] for t in resp.json()["items"]]
    assert str(other_trip.id) not in trip_ids


async def test_readonly_user_cannot_create_trip(
    client: AsyncClient, readonly_user: User, vehicle: Vehicle, driver: Driver
) -> None:
    headers = await auth_headers(client, "readonly@acmetransport.dev", "ReadOnly123!")
    resp = await client.post(
        "/api/v1/trips",
        headers=headers,
        json={
            "vehicle_id": str(vehicle.id),
            "driver_id": str(driver.id),
            "origin": "A",
            "destination": "B",
            "cargo_type": "general",
        },
    )
    assert resp.status_code == 403
