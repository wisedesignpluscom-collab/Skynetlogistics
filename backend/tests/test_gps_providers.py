from httpx import AsyncClient

from app.models.gps_provider import GPSProvider
from app.models.user import User
from app.models.vehicle import Vehicle
from tests.conftest import auth_headers


async def test_admin_creates_webhook_provider_and_receives_token(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/gps-providers",
        headers=headers,
        json={
            "provider_name": "Traker GPS",
            "adapter_type": "traker_gps",
            "api_credentials": {"api_key": "secret-123"},
            "ingestion_mode": "webhook",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["webhook_token"]
    assert "api_credentials" not in body  # nunca se devuelven las credenciales


async def test_readonly_user_cannot_create_provider(client: AsyncClient, readonly_user: User) -> None:
    headers = await auth_headers(client, "readonly@acmetransport.dev", "ReadOnly123!")
    resp = await client.post(
        "/api/v1/gps-providers",
        headers=headers,
        json={
            "provider_name": "Traker GPS",
            "adapter_type": "traker_gps",
            "api_credentials": {},
            "ingestion_mode": "webhook",
        },
    )
    assert resp.status_code == 403


async def test_regenerate_token_invalidates_previous(
    client: AsyncClient, admin_user: User, gps_provider_webhook: tuple[GPSProvider, str]
) -> None:
    provider, old_token = gps_provider_webhook
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(f"/api/v1/gps-providers/{provider.id}/regenerate-token", headers=headers)
    assert resp.status_code == 200
    new_token = resp.json()["webhook_token"]
    assert new_token != old_token


async def test_map_vehicle_to_device(
    client: AsyncClient, admin_user: User, gps_provider_webhook: tuple[GPSProvider, str], vehicle: Vehicle
) -> None:
    provider, _ = gps_provider_webhook
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        f"/api/v1/gps-providers/{provider.id}/vehicle-map",
        headers=headers,
        json={"vehicle_id": str(vehicle.id), "external_device_id": "DEV-999"},
    )
    assert resp.status_code == 201

    duplicate_resp = await client.post(
        f"/api/v1/gps-providers/{provider.id}/vehicle-map",
        headers=headers,
        json={"vehicle_id": str(vehicle.id), "external_device_id": "DEV-999"},
    )
    assert duplicate_resp.status_code == 409


async def test_map_vehicle_from_another_company_rejected(
    client: AsyncClient,
    admin_user: User,
    gps_provider_webhook: tuple[GPSProvider, str],
    other_company,
    db,
) -> None:
    other_vehicle = Vehicle(
        company_id=other_company.id, plate="OTH-555", brand="Hino", model="500", year=2018, type="camion"
    )
    db.add(other_vehicle)
    await db.commit()
    await db.refresh(other_vehicle)

    provider, _ = gps_provider_webhook
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        f"/api/v1/gps-providers/{provider.id}/vehicle-map",
        headers=headers,
        json={"vehicle_id": str(other_vehicle.id), "external_device_id": "DEV-XYZ"},
    )
    assert resp.status_code == 400
