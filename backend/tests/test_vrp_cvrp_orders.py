"""Fase 9C: optimizar VRP desde pedidos de reparto con capacidad (CVRP) y despacho al confirmar."""

from datetime import date, datetime, timezone

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.client import Client
from app.models.company import Company
from app.models.driver import Driver
from app.models.gps_provider import GPSProvider
from app.models.vehicle import Vehicle
from app.models.vehicle_position import VehiclePosition
from app.models.warehouse import Warehouse
from tests.conftest import auth_headers


async def _make_available(db, *, vehicle, driver, provider, lat, lng) -> None:
    vehicle.assigned_driver_id = driver.id
    db.add(vehicle)
    db.add(
        VehiclePosition(
            vehicle_id=vehicle.id, company_id=vehicle.company_id, provider_id=provider.id,
            timestamp=datetime.now(timezone.utc), lat=lat, lng=lng, raw_payload={},
        )
    )
    await db.commit()


async def _goods(client, headers, warehouse_id, sku, weight, volume, stock) -> str:
    resp = await client.post(
        "/api/v1/delivery-goods", headers=headers,
        json={"warehouse_id": warehouse_id, "sku": sku, "name": sku, "unit": "caja",
              "weight_kg_per_unit": weight, "volume_m3_per_unit": volume},
    )
    gid = resp.json()["id"]
    await client.post(
        "/api/v1/delivery-goods/movements", headers=headers,
        json={"goods_id": gid, "movement_type": "entrada", "quantity": stock},
    )
    return gid


async def _order(client, headers, client_id, goods_id, qty, lat, lng, label) -> str:
    resp = await client.post(
        "/api/v1/delivery-orders", headers=headers,
        json={"client_id": client_id, "address": label, "lat": lat, "lng": lng,
              "items": [{"goods_id": goods_id, "quantity": qty}]},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


async def _client(db, company: Company) -> Client:
    c = Client(company_id=company.id, name="Cliente CVRP")
    db.add(c)
    await db.commit()
    await db.refresh(c)
    return c


async def _second_vehicle_and_driver(db, company: Company, *, cap_kg=None):
    d = Driver(company_id=company.id, name="Ana", license_number="LIC-CVRP-2", license_expiry=date(2030, 1, 1))
    v = Vehicle(company_id=company.id, plate="CVRP-2", brand="Ford", model="Cargo", year=2021,
                type="camion", cargo_capacity_kg=cap_kg)
    db.add(d)
    db.add(v)
    await db.commit()
    await db.refresh(d)
    await db.refresh(v)
    return v, d


async def test_optimize_from_orders_dispatches_and_discounts_stock(
    client: AsyncClient, admin_user, vehicle: Vehicle, driver: Driver,
    gps_provider_webhook, db: AsyncSession, company: Company, warehouse: Warehouse,
) -> None:
    provider, _ = gps_provider_webhook
    await _make_available(db, vehicle=vehicle, driver=driver, provider=provider, lat=10.0, lng=-67.0)
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")

    goods_id = await _goods(client, headers, str(warehouse.id), "G-CVRP", weight=5, volume=0.1, stock=20)
    cli = await _client(db, company)
    order_id = await _order(client, headers, str(cli.id), goods_id, 3, 10.001, -66.999, "Cliente A")

    # optimizar desde pedidos
    resp = await client.post(
        "/api/v1/vrp/optimize", headers=headers,
        json={"order_ids": [order_id], "cargo_type": "reparto"},
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assigned = body["proposed_assignment"][0]
    assert assigned["load_kg"] == 15.0  # 3 * 5
    assert assigned["stops"][0]["order_id"] == order_id
    run_id = body["id"]

    # stock aún intacto (solo propuesta)
    goods = await client.get(f"/api/v1/delivery-goods/{goods_id}", headers=headers)
    assert goods.json()["quantity"] == 20

    # confirmar: crea trip + despacha pedido (descuenta stock 20 - 3 = 17)
    confirm = await client.post(f"/api/v1/vrp/runs/{run_id}/confirm", headers=headers)
    assert confirm.status_code == 200, confirm.text
    trip_id = confirm.json()["result_trip_ids"][0]

    order = await client.get(f"/api/v1/delivery-orders/{order_id}", headers=headers)
    assert order.json()["status"] == "asignado"
    assert order.json()["trip_id"] == trip_id

    goods = await client.get(f"/api/v1/delivery-goods/{goods_id}", headers=headers)
    assert goods.json()["quantity"] == 17


async def test_capacity_splits_orders_between_vehicles(
    client: AsyncClient, admin_user, vehicle: Vehicle, driver: Driver,
    gps_provider_webhook, db: AsyncSession, company: Company, warehouse: Warehouse,
) -> None:
    provider, _ = gps_provider_webhook
    # vehículo 1 cap 10 kg
    vehicle.cargo_capacity_kg = 10
    await _make_available(db, vehicle=vehicle, driver=driver, provider=provider, lat=10.0, lng=-66.0)
    # vehículo 2 cap 10 kg, arranca cerca de la 2da parada
    v2, d2 = await _second_vehicle_and_driver(db, company, cap_kg=10)
    await _make_available(db, vehicle=v2, driver=d2, provider=provider, lat=10.0, lng=-65.0)

    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    goods_id = await _goods(client, headers, str(warehouse.id), "G-CAP", weight=6, volume=0.1, stock=50)
    cli = await _client(db, company)
    # dos pedidos de 6 kg (1 unidad c/u): no caben los dos en un solo vehículo de 10 kg
    o1 = await _order(client, headers, str(cli.id), goods_id, 1, 10.001, -65.999, "cerca v1")
    o2 = await _order(client, headers, str(cli.id), goods_id, 1, 10.001, -65.001, "cerca v2")

    resp = await client.post(
        "/api/v1/vrp/optimize", headers=headers,
        json={"order_ids": [o1, o2], "cargo_type": "reparto"},
    )
    assert resp.status_code == 201, resp.text
    assignment = resp.json()["proposed_assignment"]
    # cada vehículo recibe un pedido (no se sobrecarga ninguno)
    assert len(assignment) == 2
    assert sorted(len(a["stops"]) for a in assignment) == [1, 1]
    for a in assignment:
        assert a["load_kg"] <= a["capacity_kg"]


async def test_capacity_infeasible_returns_400(
    client: AsyncClient, admin_user, vehicle: Vehicle, driver: Driver,
    gps_provider_webhook, db: AsyncSession, company: Company, warehouse: Warehouse,
) -> None:
    provider, _ = gps_provider_webhook
    vehicle.cargo_capacity_kg = 10
    await _make_available(db, vehicle=vehicle, driver=driver, provider=provider, lat=10.0, lng=-66.0)
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")

    goods_id = await _goods(client, headers, str(warehouse.id), "G-BIG", weight=15, volume=0.1, stock=10)
    cli = await _client(db, company)
    order_id = await _order(client, headers, str(cli.id), goods_id, 1, 10.001, -65.999, "pesado")

    resp = await client.post(
        "/api/v1/vrp/optimize", headers=headers,
        json={"order_ids": [order_id], "cargo_type": "reparto"},
    )
    assert resp.status_code == 400  # 15 kg > 10 kg de capacidad


async def test_optimize_requires_exactly_one_mode(client: AsyncClient, admin_user) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    # ni stops ni order_ids
    resp = await client.post("/api/v1/vrp/optimize", headers=headers, json={"cargo_type": "x"})
    assert resp.status_code == 422
