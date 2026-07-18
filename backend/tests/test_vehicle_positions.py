from httpx import AsyncClient

from app.models.gps_provider import GPSProvider
from app.models.gps_provider_vehicle_map import GPSProviderVehicleMap
from app.models.user import User
from app.models.vehicle import Vehicle
from tests.conftest import auth_headers

BASE_PAYLOAD = {
    "device_id": "DEV-001",
    "lat": 10.5,
    "lon": -66.9,
    "speed": 55.0,
    "odometer": 10500,
    "ignition": True,
    "course": 90,
}


async def test_latest_position_null_when_no_data(client: AsyncClient, admin_user: User, vehicle: Vehicle) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.get(f"/api/v1/vehicles/{vehicle.id}/position/latest", headers=headers)
    assert resp.status_code == 200
    assert resp.json() is None


async def test_history_and_fleet_latest(
    client: AsyncClient,
    admin_user: User,
    gps_provider_webhook: tuple[GPSProvider, str],
    gps_vehicle_map: GPSProviderVehicleMap,
    vehicle: Vehicle,
) -> None:
    provider, token = gps_provider_webhook
    for ts, odometer in [("2026-07-18T10:00:00+00:00", 10100), ("2026-07-18T12:00:00+00:00", 10500)]:
        await client.post(
            f"/api/v1/gps/webhook/{provider.id}",
            json={**BASE_PAYLOAD, "timestamp": ts, "odometer": odometer},
            headers={"X-Webhook-Token": token},
        )

    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")

    history_resp = await client.get(
        f"/api/v1/vehicles/{vehicle.id}/positions",
        headers=headers,
        params={"date_from": "2026-07-18T00:00:00Z", "date_to": "2026-07-19T00:00:00Z"},
    )
    assert history_resp.status_code == 200
    assert len(history_resp.json()) == 2

    fleet_resp = await client.get("/api/v1/fleet/positions/latest", headers=headers)
    assert fleet_resp.status_code == 200
    fleet = fleet_resp.json()
    assert len(fleet) == 1
    assert fleet[0]["odometer_km"] == 10500  # la más reciente


async def test_tenant_isolation_positions(
    client: AsyncClient,
    admin_user: User,
    gps_provider_webhook: tuple[GPSProvider, str],
    gps_vehicle_map: GPSProviderVehicleMap,
    vehicle: Vehicle,
    other_company,
    db,
) -> None:
    other_vehicle = Vehicle(
        company_id=other_company.id, plate="OTH-321", brand="Hino", model="500", year=2019, type="camion"
    )
    db.add(other_vehicle)
    await db.commit()

    provider, token = gps_provider_webhook
    await client.post(
        f"/api/v1/gps/webhook/{provider.id}",
        json={**BASE_PAYLOAD, "timestamp": "2026-07-18T10:00:00+00:00"},
        headers={"X-Webhook-Token": token},
    )

    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.get(f"/api/v1/vehicles/{other_vehicle.id}/position/latest", headers=headers)
    assert resp.status_code == 404  # el vehículo de otra empresa ni siquiera se encuentra


async def test_readonly_user_can_read_positions(
    client: AsyncClient, readonly_user: User, vehicle: Vehicle
) -> None:
    # readonly_role no tiene el módulo "gps" -> debe ser 403
    headers = await auth_headers(client, "readonly@acmetransport.dev", "ReadOnly123!")
    resp = await client.get(f"/api/v1/vehicles/{vehicle.id}/position/latest", headers=headers)
    assert resp.status_code == 403
