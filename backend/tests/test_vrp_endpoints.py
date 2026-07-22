import uuid
from datetime import date, datetime, timezone

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.driver import Driver
from app.models.gps_provider import GPSProvider
from app.models.vehicle import Vehicle
from app.models.vehicle_position import VehiclePosition
from tests.conftest import auth_headers

_STOP_A = {"lat": 10.001, "lng": -66.999, "label": "Cliente A"}
_STOP_B = {"lat": 10.002, "lng": -66.998, "label": "Cliente B"}


async def _make_available(
    db: AsyncSession, *, vehicle: Vehicle, driver: Driver, provider: GPSProvider, lat: float, lng: float
) -> None:
    """Deja `vehicle` listo como candidato VRP: activo, con conductor asignado y una posición GPS."""
    vehicle.assigned_driver_id = driver.id
    db.add(vehicle)
    db.add(
        VehiclePosition(
            vehicle_id=vehicle.id,
            company_id=vehicle.company_id,
            provider_id=provider.id,
            timestamp=datetime.now(timezone.utc),
            lat=lat,
            lng=lng,
            raw_payload={},
        )
    )
    await db.commit()


async def _second_vehicle_and_driver(db: AsyncSession, company: Company) -> tuple[Vehicle, Driver]:
    d = Driver(company_id=company.id, name="Ana Gómez", license_number="LIC-002", license_expiry=date(2030, 1, 1))
    v = Vehicle(
        company_id=company.id, plate="XYZ-987", brand="Ford", model="Cargo", year=2021, type="camion"
    )
    db.add(d)
    db.add(v)
    await db.commit()
    await db.refresh(d)
    await db.refresh(v)
    return v, d


async def test_optimize_creates_proposed_run(
    client: AsyncClient,
    admin_user,
    vehicle: Vehicle,
    driver: Driver,
    gps_provider_webhook: tuple[GPSProvider, str],
    db: AsyncSession,
) -> None:
    provider, _ = gps_provider_webhook
    await _make_available(db, vehicle=vehicle, driver=driver, provider=provider, lat=10.0, lng=-67.0)
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")

    resp = await client.post(
        "/api/v1/vrp/optimize",
        headers=headers,
        json={"stops": [_STOP_A, _STOP_B], "cargo_type": "general"},
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["status"] == "propuesto"
    assert len(body["proposed_assignment"]) == 1
    assigned = body["proposed_assignment"][0]
    assert assigned["vehicle_id"] == str(vehicle.id)
    assert assigned["driver_id"] == str(driver.id)
    assert {s["label"] for s in assigned["stops"]} == {"Cliente A", "Cliente B"}
    assert assigned["distance_km"] > 0


async def test_optimize_without_available_vehicles_400(
    client: AsyncClient, admin_user, vehicle: Vehicle, driver: Driver
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/vrp/optimize",
        headers=headers,
        json={"stops": [_STOP_A], "cargo_type": "general"},
    )
    assert resp.status_code == 400


async def test_confirm_creates_trips_with_route_plan(
    client: AsyncClient,
    admin_user,
    vehicle: Vehicle,
    driver: Driver,
    gps_provider_webhook: tuple[GPSProvider, str],
    db: AsyncSession,
) -> None:
    provider, _ = gps_provider_webhook
    await _make_available(db, vehicle=vehicle, driver=driver, provider=provider, lat=10.0, lng=-67.0)
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")

    optimize_resp = await client.post(
        "/api/v1/vrp/optimize",
        headers=headers,
        json={"stops": [_STOP_A, _STOP_B], "cargo_type": "general"},
    )
    run_id = optimize_resp.json()["id"]

    confirm_resp = await client.post(f"/api/v1/vrp/runs/{run_id}/confirm", headers=headers)
    assert confirm_resp.status_code == 200, confirm_resp.text
    body = confirm_resp.json()
    assert body["status"] == "confirmado"
    assert len(body["result_trip_ids"]) == 1

    trip_id = body["result_trip_ids"][0]
    trip_resp = await client.get(f"/api/v1/trips/{trip_id}", headers=headers)
    assert trip_resp.status_code == 200
    trip = trip_resp.json()
    assert trip["vehicle_id"] == str(vehicle.id)
    assert trip["driver_id"] == str(driver.id)
    assert trip["is_round_trip"] is False
    # No pisó distance_km operativo (Fase 7A/7B nunca lo tocan).
    assert trip["distance_km"] is None

    route_resp = await client.get(f"/api/v1/trips/{trip_id}/route", headers=headers)
    assert route_resp.status_code == 200
    route = route_resp.json()
    assert len(route["waypoints"]) == 2
    assert route["calculated_distance_km"] > 0
    assert len(route["geometry"]) >= 2

    # Re-confirmar una corrida ya confirmada debe rechazarse.
    second_confirm = await client.post(f"/api/v1/vrp/runs/{run_id}/confirm", headers=headers)
    assert second_confirm.status_code == 409


async def test_discard_run(
    client: AsyncClient,
    admin_user,
    vehicle: Vehicle,
    driver: Driver,
    gps_provider_webhook: tuple[GPSProvider, str],
    db: AsyncSession,
) -> None:
    provider, _ = gps_provider_webhook
    await _make_available(db, vehicle=vehicle, driver=driver, provider=provider, lat=10.0, lng=-67.0)
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")

    optimize_resp = await client.post(
        "/api/v1/vrp/optimize", headers=headers, json={"stops": [_STOP_A], "cargo_type": "general"}
    )
    run_id = optimize_resp.json()["id"]

    discard_resp = await client.post(f"/api/v1/vrp/runs/{run_id}/discard", headers=headers)
    assert discard_resp.status_code == 200
    assert discard_resp.json()["status"] == "descartado"

    confirm_resp = await client.post(f"/api/v1/vrp/runs/{run_id}/confirm", headers=headers)
    assert confirm_resp.status_code == 409


async def test_two_vehicles_split_stops_by_proximity(
    client: AsyncClient,
    admin_user,
    vehicle: Vehicle,
    driver: Driver,
    gps_provider_webhook: tuple[GPSProvider, str],
    db: AsyncSession,
    company: Company,
) -> None:
    provider, _ = gps_provider_webhook
    await _make_available(db, vehicle=vehicle, driver=driver, provider=provider, lat=10.0, lng=-66.0)
    vehicle2, driver2 = await _second_vehicle_and_driver(db, company)
    await _make_available(db, vehicle=vehicle2, driver=driver2, provider=provider, lat=10.0, lng=-65.0)
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")

    stops = [
        {"lat": 10.001, "lng": -65.999, "label": "cerca de v1"},
        {"lat": 10.001, "lng": -65.001, "label": "cerca de v2"},
    ]
    resp = await client.post(
        "/api/v1/vrp/optimize", headers=headers, json={"stops": stops, "cargo_type": "general"}
    )
    assert resp.status_code == 201
    body = resp.json()
    assert len(body["proposed_assignment"]) == 2
    by_vehicle = {a["vehicle_id"]: a["stops"] for a in body["proposed_assignment"]}
    assert by_vehicle[str(vehicle.id)][0]["label"] == "cerca de v1"
    assert by_vehicle[str(vehicle2.id)][0]["label"] == "cerca de v2"


async def test_available_vehicles_endpoint(
    client: AsyncClient,
    admin_user,
    vehicle: Vehicle,
    driver: Driver,
    gps_provider_webhook: tuple[GPSProvider, str],
    db: AsyncSession,
) -> None:
    provider, _ = gps_provider_webhook
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")

    resp = await client.get("/api/v1/vrp/available-vehicles", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == []

    await _make_available(db, vehicle=vehicle, driver=driver, provider=provider, lat=10.0, lng=-67.0)
    resp = await client.get("/api/v1/vrp/available-vehicles", headers=headers)
    assert resp.status_code == 200
    assert [v["id"] for v in resp.json()] == [str(vehicle.id)]


async def test_readonly_user_cannot_optimize(client: AsyncClient, readonly_user) -> None:
    headers = await auth_headers(client, "readonly@acmetransport.dev", "ReadOnly123!")
    resp = await client.post(
        "/api/v1/vrp/optimize", headers=headers, json={"stops": [_STOP_A], "cargo_type": "general"}
    )
    assert resp.status_code == 403


async def test_get_run_not_found(client: AsyncClient, admin_user) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.get(f"/api/v1/vrp/runs/{uuid.uuid4()}", headers=headers)
    assert resp.status_code == 404


async def test_stops_over_limit_rejected(client: AsyncClient, admin_user) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    stops = [{"lat": 10.0, "lng": -66.0, "label": f"parada {i}"} for i in range(61)]
    resp = await client.post(
        "/api/v1/vrp/optimize", headers=headers, json={"stops": stops, "cargo_type": "general"}
    )
    assert resp.status_code == 422
