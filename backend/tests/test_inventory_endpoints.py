from httpx import AsyncClient

from app.core.security import hash_password
from app.models.company import Company
from app.models.role import Role
from app.models.user import User
from app.models.warehouse import Warehouse
from app.utils.permissions import DEFAULT_ADMIN_PERMISSIONS
from tests.conftest import auth_headers


async def _create_item(client: AsyncClient, headers: dict, warehouse_id: str, sku: str = "SKU-001") -> dict:
    resp = await client.post(
        "/api/v1/inventory-items",
        headers=headers,
        json={"warehouse_id": warehouse_id, "sku": sku, "name": "Filtro de aceite", "unit": "unidad", "min_stock": 3},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


async def test_admin_creates_inventory_item_with_zero_stock(
    client: AsyncClient, admin_user: User, warehouse: Warehouse
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    item = await _create_item(client, headers, str(warehouse.id))
    assert item["quantity"] == 0
    assert item["sku"] == "SKU-001"


async def test_create_item_duplicate_sku_conflicts(client: AsyncClient, admin_user: User, warehouse: Warehouse) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    await _create_item(client, headers, str(warehouse.id), "SKU-DUP")
    resp = await client.post(
        "/api/v1/inventory-items",
        headers=headers,
        json={"warehouse_id": str(warehouse.id), "sku": "SKU-DUP", "name": "Otro", "unit": "unidad"},
    )
    assert resp.status_code == 409


async def test_movement_updates_item_quantity_end_to_end(
    client: AsyncClient, admin_user: User, warehouse: Warehouse
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    item = await _create_item(client, headers, str(warehouse.id), "SKU-MOV")

    resp = await client.post(
        "/api/v1/inventory-movements",
        headers=headers,
        json={"item_id": item["id"], "movement_type": "entrada", "quantity": 20, "reference_doc": "FAC-100"},
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["movement_type"] == "entrada"

    detail = await client.get(f"/api/v1/inventory-items/{item['id']}", headers=headers)
    assert detail.json()["quantity"] == 20
    assert len(detail.json()["movements"]) == 1


async def test_salida_beyond_stock_rejected_with_422(
    client: AsyncClient, admin_user: User, warehouse: Warehouse
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    item = await _create_item(client, headers, str(warehouse.id), "SKU-NEG")

    resp = await client.post(
        "/api/v1/inventory-movements",
        headers=headers,
        json={"item_id": item["id"], "movement_type": "salida", "quantity": 1},
    )
    assert resp.status_code == 422


async def test_patch_item_cannot_set_quantity_directly(
    client: AsyncClient, admin_user: User, warehouse: Warehouse
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    item = await _create_item(client, headers, str(warehouse.id), "SKU-PATCH")

    resp = await client.patch(
        f"/api/v1/inventory-items/{item['id']}",
        headers=headers,
        json={"name": "Filtro de aceite premium", "quantity": 999},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Filtro de aceite premium"
    assert resp.json()["quantity"] == 0  # 'quantity' no es un campo aceptado por InventoryItemUpdate


async def test_low_stock_filter(client: AsyncClient, admin_user: User, warehouse: Warehouse) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    low_item = await _create_item(client, headers, str(warehouse.id), "SKU-LOWF")
    ok_item = await _create_item(client, headers, str(warehouse.id), "SKU-OKF")

    await client.post(
        "/api/v1/inventory-movements",
        headers=headers,
        json={"item_id": low_item["id"], "movement_type": "entrada", "quantity": 1},
    )
    # SKU-OKF también tiene min_stock=3 (helper por defecto) — subirlo bien por encima para
    # que no cuente como bajo stock y el filtro discrimine de verdad.
    await client.post(
        "/api/v1/inventory-movements",
        headers=headers,
        json={"item_id": ok_item["id"], "movement_type": "entrada", "quantity": 50},
    )

    resp = await client.get("/api/v1/inventory-items", headers=headers, params={"low_stock": True})
    assert resp.status_code == 200
    skus = [i["sku"] for i in resp.json()["items"]]
    assert "SKU-LOWF" in skus
    assert "SKU-OKF" not in skus


async def test_readonly_user_cannot_create_item(client: AsyncClient, readonly_user: User, warehouse: Warehouse) -> None:
    headers = await auth_headers(client, "readonly@acmetransport.dev", "ReadOnly123!")
    resp = await client.post(
        "/api/v1/inventory-items",
        headers=headers,
        json={"warehouse_id": str(warehouse.id), "sku": "SKU-RO", "name": "X", "unit": "unidad"},
    )
    assert resp.status_code == 403


async def test_create_item_rejects_warehouse_from_another_company(
    client: AsyncClient, admin_user: User, other_company: Company, db
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")

    other_warehouse = Warehouse(company_id=other_company.id, name="Otro Almacén")
    db.add(other_warehouse)
    await db.commit()
    await db.refresh(other_warehouse)

    resp = await client.post(
        "/api/v1/inventory-items",
        headers=headers,
        json={"warehouse_id": str(other_warehouse.id), "sku": "SKU-CROSS", "name": "X", "unit": "unidad"},
    )
    assert resp.status_code == 404


async def test_tenant_isolation_on_item_detail(
    client: AsyncClient, admin_user: User, warehouse: Warehouse, other_company: Company, db
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    item = await _create_item(client, headers, str(warehouse.id), "SKU-ISO")

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
    resp = await client.get(f"/api/v1/inventory-items/{item['id']}", headers=other_headers)
    assert resp.status_code == 404
