from httpx import AsyncClient

from app.models.driver import Driver
from app.models.user import User
from tests.conftest import auth_headers


async def test_admin_creates_driver(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/drivers",
        headers=headers,
        json={"name": "María López", "license_number": "LIC-999", "license_expiry": "2030-05-01"},
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "activo"


async def test_duplicate_license_conflicts(client: AsyncClient, admin_user: User, driver: Driver) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/drivers",
        headers=headers,
        json={
            "name": "Otro Conductor",
            "license_number": driver.license_number,
            "license_expiry": "2030-05-01",
        },
    )
    assert resp.status_code == 409


async def test_deactivate_driver(client: AsyncClient, admin_user: User, driver: Driver) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.delete(f"/api/v1/drivers/{driver.id}", headers=headers)
    assert resp.status_code == 204

    get_resp = await client.get(f"/api/v1/drivers/{driver.id}", headers=headers)
    assert get_resp.json()["status"] == "inactivo"


async def test_readonly_user_can_list_drivers(client: AsyncClient, readonly_user: User) -> None:
    # readonly_role no incluye el módulo drivers -> debe ser 403, no 200.
    headers = await auth_headers(client, "readonly@acmetransport.dev", "ReadOnly123!")
    resp = await client.get("/api/v1/drivers", headers=headers)
    assert resp.status_code == 403
