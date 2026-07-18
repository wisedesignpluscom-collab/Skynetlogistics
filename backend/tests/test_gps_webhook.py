from httpx import AsyncClient

from app.models.gps_provider import GPSProvider
from app.models.gps_provider_vehicle_map import GPSProviderVehicleMap
from app.models.maintenance_task import MaintenanceTask
from app.models.user import User
from app.models.vehicle import Vehicle
from tests.conftest import auth_headers

VALID_PAYLOAD = {
    "device_id": "DEV-001",
    "lat": 10.5,
    "lon": -66.9,
    "speed": 55.0,
    "odometer": 10500,
    "ignition": True,
    "course": 90,
    "timestamp": "2026-07-18T12:00:00+00:00",
}


async def test_webhook_rejects_missing_token(
    client: AsyncClient, gps_provider_webhook: tuple[GPSProvider, str], gps_vehicle_map: GPSProviderVehicleMap
) -> None:
    provider, _ = gps_provider_webhook
    resp = await client.post(f"/api/v1/gps/webhook/{provider.id}", json=VALID_PAYLOAD)
    assert resp.status_code == 401


async def test_webhook_rejects_wrong_token(
    client: AsyncClient, gps_provider_webhook: tuple[GPSProvider, str], gps_vehicle_map: GPSProviderVehicleMap
) -> None:
    provider, _ = gps_provider_webhook
    resp = await client.post(
        f"/api/v1/gps/webhook/{provider.id}",
        json=VALID_PAYLOAD,
        headers={"X-Webhook-Token": "wrong-token"},
    )
    assert resp.status_code == 401


async def test_webhook_rejects_unmapped_device(
    client: AsyncClient, gps_provider_webhook: tuple[GPSProvider, str]
) -> None:
    provider, token = gps_provider_webhook
    resp = await client.post(
        f"/api/v1/gps/webhook/{provider.id}",
        json=VALID_PAYLOAD,
        headers={"X-Webhook-Token": token},
    )
    assert resp.status_code == 404


async def test_webhook_accepts_valid_payload_and_advances_odometer(
    client: AsyncClient,
    admin_user: User,
    gps_provider_webhook: tuple[GPSProvider, str],
    gps_vehicle_map: GPSProviderVehicleMap,
    vehicle: Vehicle,
    db,
) -> None:
    task = MaintenanceTask(
        company_id=vehicle.company_id,
        vehicle_id=vehicle.id,
        type="preventivo",
        scheduled_by="km",
        due_km=10700,
        status="pendiente",
    )
    db.add(task)
    await db.commit()

    provider, token = gps_provider_webhook
    resp = await client.post(
        f"/api/v1/gps/webhook/{provider.id}",
        json=VALID_PAYLOAD,
        headers={"X-Webhook-Token": token},
    )
    assert resp.status_code == 201

    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")

    vehicle_resp = await client.get(f"/api/v1/vehicles/{vehicle.id}", headers=headers)
    assert vehicle_resp.json()["current_odometer_km"] == 10500  # vehicle fixture arranca en 10_000

    alerts_resp = await client.get("/api/v1/alerts", headers=headers)
    alerts = alerts_resp.json()["items"]
    assert any(a["type"] == "maintenance_due" and a["entity_id"] == str(task.id) for a in alerts)


async def test_webhook_ignores_lower_odometer_reading(
    client: AsyncClient,
    admin_user: User,
    gps_provider_webhook: tuple[GPSProvider, str],
    gps_vehicle_map: GPSProviderVehicleMap,
    vehicle: Vehicle,
) -> None:
    provider, token = gps_provider_webhook
    payload = {**VALID_PAYLOAD, "odometer": vehicle.current_odometer_km - 100}
    resp = await client.post(
        f"/api/v1/gps/webhook/{provider.id}", json=payload, headers={"X-Webhook-Token": token}
    )
    assert resp.status_code == 201  # la posición se guarda igual, solo no retrocede el odómetro

    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    vehicle_resp = await client.get(f"/api/v1/vehicles/{vehicle.id}", headers=headers)
    assert vehicle_resp.json()["current_odometer_km"] == vehicle.current_odometer_km


async def test_webhook_raw_payload_is_stored_for_audit(
    client: AsyncClient,
    admin_user: User,
    gps_provider_webhook: tuple[GPSProvider, str],
    gps_vehicle_map: GPSProviderVehicleMap,
    vehicle: Vehicle,
) -> None:
    provider, token = gps_provider_webhook
    await client.post(
        f"/api/v1/gps/webhook/{provider.id}", json=VALID_PAYLOAD, headers={"X-Webhook-Token": token}
    )

    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    latest_resp = await client.get(f"/api/v1/vehicles/{vehicle.id}/position/latest", headers=headers)
    assert latest_resp.status_code == 200
    body = latest_resp.json()
    assert body["lat"] == 10.5
    assert body["odometer_km"] == 10500
