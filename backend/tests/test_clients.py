from httpx import AsyncClient

from app.models.client import Client
from app.models.company import Company
from app.models.driver import Driver
from app.models.user import User
from app.models.vehicle import Vehicle
from tests.conftest import auth_headers


async def test_admin_creates_client(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/clients",
        headers=headers,
        json={"name": "Coca Cola Company", "tax_id": "J-09876543-2", "default_cargo_type": "Gaseosas"},
    )
    assert resp.status_code == 201
    assert resp.json()["name"] == "Coca Cola Company"
    assert resp.json()["is_active"] is True


async def test_update_and_deactivate_client(client: AsyncClient, admin_user: User, db, company: Company) -> None:
    c = Client(company_id=company.id, name="Cliente Original")
    db.add(c)
    await db.commit()
    await db.refresh(c)

    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    patch_resp = await client.patch(
        f"/api/v1/clients/{c.id}", headers=headers, json={"name": "Cliente Renombrado"}
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["name"] == "Cliente Renombrado"

    delete_resp = await client.delete(f"/api/v1/clients/{c.id}", headers=headers)
    assert delete_resp.status_code == 204

    get_resp = await client.get(f"/api/v1/clients/{c.id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["is_active"] is False


async def test_tenant_isolation_clients_list(
    client: AsyncClient, admin_user: User, db, company: Company, other_company: Company
) -> None:
    own = Client(company_id=company.id, name="Cliente Propio")
    other = Client(company_id=other_company.id, name="Cliente Ajeno")
    db.add_all([own, other])
    await db.commit()

    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.get("/api/v1/clients", headers=headers)
    assert resp.status_code == 200
    names = [item["name"] for item in resp.json()["items"]]
    assert "Cliente Propio" in names
    assert "Cliente Ajeno" not in names


async def test_trip_can_reference_client(
    client: AsyncClient, admin_user: User, db, company: Company, vehicle: Vehicle, driver: Driver
) -> None:
    c = Client(company_id=company.id, name="Cliente de Prueba")
    db.add(c)
    await db.commit()
    await db.refresh(c)

    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/trips",
        headers=headers,
        json={
            "vehicle_id": str(vehicle.id),
            "driver_id": str(driver.id),
            "client_id": str(c.id),
            "origin": "Maracaibo",
            "destination": "Caracas",
            "cargo_type": "Alimentos",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["client_id"] == str(c.id)
