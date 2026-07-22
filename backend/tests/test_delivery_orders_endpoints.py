import uuid

from httpx import AsyncClient

from app.models.client import Client
from app.models.company import Company
from app.models.driver import Driver
from app.models.trip import Trip
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.warehouse import Warehouse
from tests.conftest import auth_headers


async def _create_goods_with_stock(
    client: AsyncClient, headers: dict, warehouse_id: str, sku: str, stock: int
) -> str:
    resp = await client.post(
        "/api/v1/delivery-goods",
        headers=headers,
        json={"warehouse_id": warehouse_id, "sku": sku, "name": f"Mercancía {sku}", "unit": "caja",
              "weight_kg_per_unit": 10, "volume_m3_per_unit": 0.1},
    )
    goods_id = resp.json()["id"]
    await client.post(
        "/api/v1/delivery-goods/movements",
        headers=headers,
        json={"goods_id": goods_id, "movement_type": "entrada", "quantity": stock},
    )
    return goods_id


async def _make_client(db, company: Company) -> Client:
    c = Client(company_id=company.id, name="Cliente Reparto")
    db.add(c)
    await db.commit()
    await db.refresh(c)
    return c


async def _make_trip(db, company: Company, vehicle: Vehicle, driver: Driver) -> Trip:
    t = Trip(
        company_id=company.id,
        vehicle_id=vehicle.id,
        driver_id=driver.id,
        origin="Depósito",
        destination="Ruta reparto",
        cargo_type="general",
        status="en_curso",
    )
    db.add(t)
    await db.commit()
    await db.refresh(t)
    return t


async def test_create_order_with_items(
    client: AsyncClient, admin_user: User, warehouse: Warehouse, db, company: Company
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    goods_id = await _create_goods_with_stock(client, headers, str(warehouse.id), "M-1", 50)
    cli = await _make_client(db, company)

    resp = await client.post(
        "/api/v1/delivery-orders",
        headers=headers,
        json={
            "client_id": str(cli.id),
            "address": "Av. Principal 123",
            "lat": 10.5,
            "lng": -66.9,
            "items": [{"goods_id": goods_id, "quantity": 4}],
        },
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["status"] == "pendiente"
    assert len(body["items"]) == 1
    assert body["items"][0]["quantity"] == 4


async def test_assign_discounts_stock(
    client: AsyncClient, admin_user: User, warehouse: Warehouse, db, company: Company, vehicle: Vehicle, driver: Driver
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    goods_id = await _create_goods_with_stock(client, headers, str(warehouse.id), "M-2", 20)
    cli = await _make_client(db, company)
    trip = await _make_trip(db, company, vehicle, driver)

    order = await client.post(
        "/api/v1/delivery-orders",
        headers=headers,
        json={"client_id": str(cli.id), "address": "X", "lat": 10, "lng": -66,
              "items": [{"goods_id": goods_id, "quantity": 7}]},
    )
    order_id = order.json()["id"]

    assigned = await client.post(
        f"/api/v1/delivery-orders/{order_id}/assign",
        headers=headers,
        json={"trip_id": str(trip.id)},
    )
    assert assigned.status_code == 200, assigned.text
    assert assigned.json()["status"] == "asignado"
    assert assigned.json()["trip_id"] == str(trip.id)

    goods = await client.get(f"/api/v1/delivery-goods/{goods_id}", headers=headers)
    assert goods.json()["quantity"] == 13  # 20 - 7


async def test_assign_insufficient_stock_rejected(
    client: AsyncClient, admin_user: User, warehouse: Warehouse, db, company: Company, vehicle: Vehicle, driver: Driver
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    goods_id = await _create_goods_with_stock(client, headers, str(warehouse.id), "M-3", 3)
    cli = await _make_client(db, company)
    trip = await _make_trip(db, company, vehicle, driver)

    order = await client.post(
        "/api/v1/delivery-orders",
        headers=headers,
        json={"client_id": str(cli.id), "address": "X", "lat": 10, "lng": -66,
              "items": [{"goods_id": goods_id, "quantity": 5}]},
    )
    order_id = order.json()["id"]

    assigned = await client.post(
        f"/api/v1/delivery-orders/{order_id}/assign",
        headers=headers,
        json={"trip_id": str(trip.id)},
    )
    assert assigned.status_code == 422
    # stock intacto
    goods = await client.get(f"/api/v1/delivery-goods/{goods_id}", headers=headers)
    assert goods.json()["quantity"] == 3


async def test_driver_sees_own_orders_and_delivers(
    client: AsyncClient, admin_user: User, driver_user: User, warehouse: Warehouse, db, company: Company,
    vehicle: Vehicle, driver: Driver
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    goods_id = await _create_goods_with_stock(client, headers, str(warehouse.id), "M-4", 10)
    cli = await _make_client(db, company)
    trip = await _make_trip(db, company, vehicle, driver)

    order = await client.post(
        "/api/v1/delivery-orders",
        headers=headers,
        json={"client_id": str(cli.id), "address": "X", "lat": 10, "lng": -66,
              "items": [{"goods_id": goods_id, "quantity": 2}]},
    )
    order_id = order.json()["id"]
    await client.post(f"/api/v1/delivery-orders/{order_id}/assign", headers=headers, json={"trip_id": str(trip.id)})

    driver_headers = await auth_headers(client, "conductor@acmetransport.dev", "Conductor123!")
    mine = await client.get("/api/v1/delivery-orders/mine", headers=driver_headers)
    assert mine.status_code == 200
    assert len(mine.json()) == 1
    assert mine.json()[0]["id"] == order_id

    delivered = await client.post(
        f"/api/v1/delivery-orders/{order_id}/deliver",
        headers=driver_headers,
        json={"notes": "Entregado en portería"},
    )
    assert delivered.status_code == 200, delivered.text
    assert delivered.json()["status"] == "entregado"
    assert delivered.json()["delivered_at"] is not None


async def test_fail_returns_stock(
    client: AsyncClient, admin_user: User, driver_user: User, warehouse: Warehouse, db, company: Company,
    vehicle: Vehicle, driver: Driver
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    goods_id = await _create_goods_with_stock(client, headers, str(warehouse.id), "M-5", 10)
    cli = await _make_client(db, company)
    trip = await _make_trip(db, company, vehicle, driver)

    order = await client.post(
        "/api/v1/delivery-orders",
        headers=headers,
        json={"client_id": str(cli.id), "address": "X", "lat": 10, "lng": -66,
              "items": [{"goods_id": goods_id, "quantity": 6}]},
    )
    order_id = order.json()["id"]
    await client.post(f"/api/v1/delivery-orders/{order_id}/assign", headers=headers, json={"trip_id": str(trip.id)})

    # tras asignar: 10 - 6 = 4
    goods = await client.get(f"/api/v1/delivery-goods/{goods_id}", headers=headers)
    assert goods.json()["quantity"] == 4

    driver_headers = await auth_headers(client, "conductor@acmetransport.dev", "Conductor123!")
    failed = await client.post(
        f"/api/v1/delivery-orders/{order_id}/fail",
        headers=driver_headers,
        json={"failure_reason": "Cliente ausente", "return_stock": True},
    )
    assert failed.status_code == 200, failed.text
    assert failed.json()["status"] == "fallido"

    # stock restaurado: 4 + 6 = 10
    goods = await client.get(f"/api/v1/delivery-goods/{goods_id}", headers=headers)
    assert goods.json()["quantity"] == 10


async def test_driver_cannot_deliver_others_order(
    client: AsyncClient, admin_user: User, driver_user: User, warehouse: Warehouse, db, company: Company,
    vehicle: Vehicle
) -> None:
    """Un pedido asignado a un trip de OTRO conductor no es tocable por este conductor."""
    from datetime import date

    other_driver = Driver(company_id=company.id, name="Otro", license_number="LIC-OTRO", license_expiry=date(2030, 1, 1))
    db.add(other_driver)
    await db.commit()
    await db.refresh(other_driver)

    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    goods_id = await _create_goods_with_stock(client, headers, str(warehouse.id), "M-6", 10)
    cli = await _make_client(db, company)
    other_trip = await _make_trip(db, company, vehicle, other_driver)

    order = await client.post(
        "/api/v1/delivery-orders",
        headers=headers,
        json={"client_id": str(cli.id), "address": "X", "lat": 10, "lng": -66,
              "items": [{"goods_id": goods_id, "quantity": 1}]},
    )
    order_id = order.json()["id"]
    await client.post(f"/api/v1/delivery-orders/{order_id}/assign", headers=headers, json={"trip_id": str(other_trip.id)})

    driver_headers = await auth_headers(client, "conductor@acmetransport.dev", "Conductor123!")
    resp = await client.post(
        f"/api/v1/delivery-orders/{order_id}/deliver", headers=driver_headers, json={}
    )
    assert resp.status_code == 403


async def test_orders_isolated_per_company(
    client: AsyncClient, admin_user: User, warehouse: Warehouse, db, company: Company, other_company: Company
) -> None:
    from app.core.security import hash_password
    from app.models.role import Role

    other_role = Role(company_id=other_company.id, name="Admin", permissions={"delivery": ["read"]})
    db.add(other_role)
    await db.flush()
    other_admin = User(
        company_id=other_company.id, role_id=other_role.id, name="OA",
        email="oa@othercompany.dev", password_hash=hash_password("OtherPass1!"),
    )
    db.add(other_admin)
    await db.commit()

    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    goods_id = await _create_goods_with_stock(client, headers, str(warehouse.id), "M-7", 5)
    cli = await _make_client(db, company)
    await client.post(
        "/api/v1/delivery-orders",
        headers=headers,
        json={"client_id": str(cli.id), "address": "X", "lat": 10, "lng": -66,
              "items": [{"goods_id": goods_id, "quantity": 1}]},
    )

    other_headers = await auth_headers(client, "oa@othercompany.dev", "OtherPass1!")
    resp = await client.get("/api/v1/delivery-orders", headers=other_headers)
    assert resp.json()["total"] == 0
