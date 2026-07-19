import uuid

from httpx import AsyncClient
from sqlalchemy import select

from app.models.alert import Alert
from app.models.company import Company
from app.models.driver import Driver
from app.models.gps_provider import GPSProvider
from app.models.gps_provider_vehicle_map import GPSProviderVehicleMap
from app.models.trip import Trip
from app.models.user import User
from app.models.vehicle import Vehicle
from tests.conftest import auth_headers

_COORDS = {
    "origin_lat": 10.5,
    "origin_lng": -66.9,
    "destination_lat": 10.6,
    "destination_lng": -71.6,
}


async def _create_trip(client: AsyncClient, headers: dict, vehicle: Vehicle, driver: Driver, **extra) -> dict:
    payload = {
        "vehicle_id": str(vehicle.id),
        "driver_id": str(driver.id),
        "origin": "Caracas",
        "destination": "Maracaibo",
        "cargo_type": "general",
    }
    payload.update(extra)
    resp = await client.post("/api/v1/trips", headers=headers, json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()


async def test_autotrigger_creates_route_plan_on_trip_create_with_coords(
    client: AsyncClient, admin_user: User, vehicle: Vehicle, driver: Driver
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    trip = await _create_trip(client, headers, vehicle, driver, **_COORDS)

    resp = await client.get(f"/api/v1/trips/{trip['id']}/route", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["engine_used"] == "fake"
    assert body["calculated_distance_km"] > 0
    assert len(body["geometry"]) >= 2
    # No pisó el distance_km operativo (sin rate_table = null en este caso)
    assert trip["distance_km"] is None


async def test_no_route_plan_when_coords_omitted(
    client: AsyncClient, admin_user: User, vehicle: Vehicle, driver: Driver
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    trip = await _create_trip(client, headers, vehicle, driver)
    resp = await client.get(f"/api/v1/trips/{trip['id']}/route", headers=headers)
    assert resp.status_code == 404


async def test_compute_route_on_demand(
    client: AsyncClient, admin_user: User, vehicle: Vehicle, driver: Driver
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    trip = await _create_trip(client, headers, vehicle, driver)  # sin coords
    resp = await client.post(f"/api/v1/trips/{trip['id']}/route", headers=headers, json=_COORDS)
    assert resp.status_code == 200
    assert resp.json()["calculated_distance_km"] > 0


async def test_compute_route_for_unknown_trip_404(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(f"/api/v1/trips/{uuid.uuid4()}/route", headers=headers, json=_COORDS)
    assert resp.status_code == 404


async def test_manual_recalculate_endpoint(
    client: AsyncClient, admin_user: User, vehicle: Vehicle, driver: Driver
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    trip = await _create_trip(client, headers, vehicle, driver, **_COORDS)
    resp = await client.post(f"/api/v1/trips/{trip['id']}/route/recalculate", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["recalculations"]) == 1
    assert body["recalculations"][0]["reason"] == "manual"


async def test_recalculate_without_plan_404(
    client: AsyncClient, admin_user: User, vehicle: Vehicle, driver: Driver
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    trip = await _create_trip(client, headers, vehicle, driver)
    resp = await client.post(f"/api/v1/trips/{trip['id']}/route/recalculate", headers=headers)
    assert resp.status_code == 404


async def test_route_settings_get_creates_defaults(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.get("/api/v1/route-settings", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["deviation_threshold_m"] == 150
    assert body["recalc_cooldown_min"] == 5


async def test_route_settings_patch(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.patch(
        "/api/v1/route-settings", headers=headers, json={"deviation_threshold_m": 300}
    )
    assert resp.status_code == 200
    assert resp.json()["deviation_threshold_m"] == 300
    assert resp.json()["recalc_cooldown_min"] == 5


async def test_route_settings_patch_out_of_bounds_rejected(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.patch(
        "/api/v1/route-settings", headers=headers, json={"deviation_threshold_m": 5}
    )
    assert resp.status_code == 422


async def test_readonly_user_cannot_compute_route(
    client: AsyncClient, readonly_user: User, vehicle: Vehicle, driver: Driver, db
) -> None:
    # readonly_role solo tiene users/roles read -> sin permiso trips
    headers = await auth_headers(client, "readonly@acmetransport.dev", "ReadOnly123!")
    resp = await client.post(f"/api/v1/trips/{uuid.uuid4()}/route", headers=headers, json=_COORDS)
    assert resp.status_code == 403


async def test_tenant_isolation_on_route_get(
    client: AsyncClient, admin_user: User, vehicle: Vehicle, driver: Driver, other_company: Company, db
) -> None:
    from app.core.security import hash_password
    from app.models.role import Role
    from app.utils.permissions import DEFAULT_ADMIN_PERMISSIONS

    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    trip = await _create_trip(client, headers, vehicle, driver, **_COORDS)

    other_role = Role(company_id=other_company.id, name="Admin", permissions=DEFAULT_ADMIN_PERMISSIONS)
    db.add(other_role)
    await db.flush()
    other_user = User(
        company_id=other_company.id,
        role_id=other_role.id,
        name="Other Admin",
        email="other-admin@othercompany.dev",
        password_hash=hash_password("Sup3rSecret!"),
    )
    db.add(other_user)
    await db.commit()

    other_headers = await auth_headers(client, "other-admin@othercompany.dev", "Sup3rSecret!")
    resp = await client.get(f"/api/v1/trips/{trip['id']}/route", headers=other_headers)
    assert resp.status_code == 404


async def test_gps_webhook_off_route_triggers_deviation_alert(
    client: AsyncClient,
    admin_user: User,
    vehicle: Vehicle,
    driver: Driver,
    db,
    gps_provider_webhook: tuple[GPSProvider, str],
    gps_vehicle_map: GPSProviderVehicleMap,
) -> None:
    provider, token = gps_provider_webhook
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")

    # Viaje con ruta planeada y puesto en_curso
    trip = await _create_trip(client, headers, vehicle, driver, **_COORDS)
    trip_row = (await db.execute(select(Trip).where(Trip.id == uuid.UUID(trip["id"])))).scalar_one()
    trip_row.status = "en_curso"
    db.add(trip_row)
    await db.commit()

    # Posición GPS bien lejos de la recta Caracas→Maracaibo (device DEV-001 del fixture)
    off_route = {
        "device_id": "DEV-001",
        "lat": 8.0,
        "lon": -69.0,
        "speed": 60.0,
        "ignition": True,
        "course": 180,
        "timestamp": "2026-07-18T12:30:00+00:00",
    }
    resp = await client.post(
        f"/api/v1/gps/webhook/{provider.id}", json=off_route, headers={"X-Webhook-Token": token}
    )
    assert resp.status_code == 201

    alert = (await db.execute(select(Alert).where(Alert.type == "route_deviation"))).scalar_one()
    assert alert.entity_id == trip_row.id
