from httpx import AsyncClient

from app.models.user import User
from app.models.warehouse import Warehouse
from tests.conftest import auth_headers


async def test_admin_creates_warehouse(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/warehouses", headers=headers, json={"name": "Almacén Norte", "location": "Maracaibo"}
    )
    assert resp.status_code == 201
    assert resp.json()["name"] == "Almacén Norte"


async def test_update_warehouse(client: AsyncClient, admin_user: User, warehouse: Warehouse) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.patch(
        f"/api/v1/warehouses/{warehouse.id}", headers=headers, json={"location": "Valencia"}
    )
    assert resp.status_code == 200
    assert resp.json()["location"] == "Valencia"


async def test_list_warehouses(client: AsyncClient, admin_user: User, warehouse: Warehouse) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.get("/api/v1/warehouses", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 1


async def test_create_warehouse_duplicate_name_conflicts(
    client: AsyncClient, admin_user: User, warehouse: Warehouse
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post("/api/v1/warehouses", headers=headers, json={"name": warehouse.name})
    assert resp.status_code == 409


async def test_readonly_user_cannot_create_warehouse(client: AsyncClient, readonly_user: User) -> None:
    headers = await auth_headers(client, "readonly@acmetransport.dev", "ReadOnly123!")
    resp = await client.post("/api/v1/warehouses", headers=headers, json={"name": "Otro"})
    assert resp.status_code == 403
