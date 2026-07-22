from httpx import AsyncClient

from app.core.security import hash_password
from app.models.company import Company
from app.models.role import Role
from app.models.user import User
from app.models.warehouse import Warehouse
from tests.conftest import auth_headers


async def _create_goods(client: AsyncClient, headers: dict, warehouse_id: str, sku: str = "MERC-001") -> dict:
    resp = await client.post(
        "/api/v1/delivery-goods",
        headers=headers,
        json={
            "warehouse_id": warehouse_id,
            "sku": sku,
            "name": "Caja de repuestos cliente",
            "unit": "caja",
            "min_stock": 5,
            "weight_kg_per_unit": 12.5,
            "volume_m3_per_unit": 0.08,
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


async def test_admin_creates_delivery_goods_with_zero_stock(
    client: AsyncClient, admin_user: User, warehouse: Warehouse
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    goods = await _create_goods(client, headers, str(warehouse.id))
    assert goods["quantity"] == 0
    assert goods["sku"] == "MERC-001"
    assert goods["weight_kg_per_unit"] == 12.5


async def test_duplicate_sku_conflicts(client: AsyncClient, admin_user: User, warehouse: Warehouse) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    await _create_goods(client, headers, str(warehouse.id), "MERC-DUP")
    resp = await client.post(
        "/api/v1/delivery-goods",
        headers=headers,
        json={"warehouse_id": str(warehouse.id), "sku": "MERC-DUP", "name": "Otra"},
    )
    assert resp.status_code == 409


async def test_movement_updates_quantity_end_to_end(
    client: AsyncClient, admin_user: User, warehouse: Warehouse
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    goods = await _create_goods(client, headers, str(warehouse.id), "MERC-MOV")

    resp = await client.post(
        "/api/v1/delivery-goods/movements",
        headers=headers,
        json={"goods_id": goods["id"], "movement_type": "entrada", "quantity": 40, "reference_doc": "GUIA-1"},
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["movement_type"] == "entrada"

    detail = await client.get(f"/api/v1/delivery-goods/{goods['id']}", headers=headers)
    assert detail.json()["quantity"] == 40
    assert len(detail.json()["movements"]) == 1


async def test_salida_beyond_stock_rejected(client: AsyncClient, admin_user: User, warehouse: Warehouse) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    goods = await _create_goods(client, headers, str(warehouse.id), "MERC-NEG")
    resp = await client.post(
        "/api/v1/delivery-goods/movements",
        headers=headers,
        json={"goods_id": goods["id"], "movement_type": "salida", "quantity": 5},
    )
    assert resp.status_code == 422


async def test_low_stock_generates_alert(client: AsyncClient, admin_user: User, warehouse: Warehouse) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    goods = await _create_goods(client, headers, str(warehouse.id), "MERC-LOW")

    # entra 3 con mínimo 5 -> stock bajo
    await client.post(
        "/api/v1/delivery-goods/movements",
        headers=headers,
        json={"goods_id": goods["id"], "movement_type": "entrada", "quantity": 3},
    )
    alerts = await client.get("/api/v1/alerts", headers=headers)
    matching = [a for a in alerts.json()["items"] if a["entity_id"] == goods["id"]]
    assert len(matching) == 1
    assert matching[0]["type"] == "low_stock_delivery"


async def test_delivery_goods_isolated_per_company(
    client: AsyncClient, admin_user: User, warehouse: Warehouse, db, other_company: Company
) -> None:
    other_role = Role(company_id=other_company.id, name="Admin", permissions={"delivery": ["read"]})
    db.add(other_role)
    await db.flush()
    other_admin = User(
        company_id=other_company.id,
        role_id=other_role.id,
        name="Other Admin",
        email="admin@othercompany.dev",
        password_hash=hash_password("OtherPass1!"),
    )
    db.add(other_admin)
    await db.commit()

    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    await _create_goods(client, headers, str(warehouse.id), "MERC-ISO")

    other_headers = await auth_headers(client, "admin@othercompany.dev", "OtherPass1!")
    resp = await client.get("/api/v1/delivery-goods", headers=other_headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


async def test_create_rejects_warehouse_from_other_company(
    client: AsyncClient, admin_user: User, db, other_company: Company
) -> None:
    other_wh = Warehouse(company_id=other_company.id, name="Almacén ajeno", location="X")
    db.add(other_wh)
    await db.commit()
    await db.refresh(other_wh)

    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/delivery-goods",
        headers=headers,
        json={"warehouse_id": str(other_wh.id), "sku": "MERC-X", "name": "X"},
    )
    assert resp.status_code == 404
