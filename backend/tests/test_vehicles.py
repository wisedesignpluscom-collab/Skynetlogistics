from httpx import AsyncClient

from app.models.company import Company
from app.models.user import User
from app.models.vehicle import Vehicle
from tests.conftest import auth_headers


async def test_admin_creates_vehicle(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/vehicles",
        headers=headers,
        json={"plate": "XYZ-999", "brand": "Ford", "model": "Cargo", "year": 2021, "type": "camion"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["plate"] == "XYZ-999"
    assert body["status"] == "activo"
    assert body["current_odometer_km"] == 0


async def test_readonly_user_cannot_create_vehicle(client: AsyncClient, readonly_user: User) -> None:
    headers = await auth_headers(client, "readonly@acmetransport.dev", "ReadOnly123!")
    resp = await client.post(
        "/api/v1/vehicles",
        headers=headers,
        json={"plate": "XYZ-999", "brand": "Ford", "model": "Cargo", "year": 2021, "type": "camion"},
    )
    assert resp.status_code == 403


async def test_duplicate_plate_conflicts(client: AsyncClient, admin_user: User, vehicle: Vehicle) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/vehicles",
        headers=headers,
        json={"plate": vehicle.plate, "brand": "Ford", "model": "Cargo", "year": 2021, "type": "camion"},
    )
    assert resp.status_code == 409


async def test_invalid_type_rejected(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/vehicles",
        headers=headers,
        json={"plate": "AAA-111", "brand": "Ford", "model": "Cargo", "year": 2021, "type": "avion"},
    )
    assert resp.status_code == 422


async def test_tenant_isolation_vehicles_list(
    client: AsyncClient, admin_user: User, vehicle: Vehicle, other_company: Company, db
) -> None:
    other_vehicle = Vehicle(
        company_id=other_company.id, plate="OTH-001", brand="Scania", model="R450", year=2020, type="cabezal"
    )
    db.add(other_vehicle)
    await db.commit()

    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.get("/api/v1/vehicles", headers=headers)
    assert resp.status_code == 200
    plates = [v["plate"] for v in resp.json()["items"]]
    assert vehicle.plate in plates
    assert "OTH-001" not in plates


async def test_filter_by_status_and_type(client: AsyncClient, admin_user: User, vehicle: Vehicle) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.get("/api/v1/vehicles", headers=headers, params={"type": "camion"})
    assert resp.status_code == 200
    assert len(resp.json()["items"]) == 1

    resp2 = await client.get("/api/v1/vehicles", headers=headers, params={"type": "remolque"})
    assert resp2.json()["items"] == []


async def test_delete_vehicle_soft_deletes(client: AsyncClient, admin_user: User, vehicle: Vehicle) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.delete(f"/api/v1/vehicles/{vehicle.id}", headers=headers)
    assert resp.status_code == 204

    get_resp = await client.get(f"/api/v1/vehicles/{vehicle.id}", headers=headers)
    assert get_resp.json()["status"] == "inactivo"


async def test_vehicle_maintenance_history_empty(
    client: AsyncClient, admin_user: User, vehicle: Vehicle
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.get(f"/api/v1/vehicles/{vehicle.id}/maintenance", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == []
