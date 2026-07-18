from sqlalchemy import select

from httpx import AsyncClient

from app.models.alert import Alert
from app.models.tire import Tire
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.warehouse import Warehouse
from tests.conftest import auth_headers


async def _create_tire(client: AsyncClient, headers: dict, unique_code: str, thickness: float = 15.0) -> dict:
    resp = await client.post(
        "/api/v1/tires",
        headers=headers,
        json={
            "unique_code": unique_code,
            "brand": "Michelin",
            "model": "X Multi",
            "current_thickness_mm": thickness,
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


async def test_admin_creates_tire(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    tire = await _create_tire(client, headers, "TIRE-001")
    assert tire["status"] == "almacen"
    assert tire["current_thickness_mm"] == 15.0


async def test_create_tire_duplicate_unique_code_conflicts(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    await _create_tire(client, headers, "TIRE-DUP")
    resp = await client.post(
        "/api/v1/tires",
        headers=headers,
        json={"unique_code": "TIRE-DUP", "brand": "Bridgestone", "model": "R150", "current_thickness_mm": 12},
    )
    assert resp.status_code == 409


async def test_list_tires_filters_by_status_and_brand(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    await _create_tire(client, headers, "TIRE-A")
    resp = await client.get("/api/v1/tires", headers=headers, params={"brand": "Michelin"})
    assert resp.status_code == 200
    assert resp.json()["total"] == 1
    resp_none = await client.get("/api/v1/tires", headers=headers, params={"status_filter": "instalado"})
    assert resp_none.json()["total"] == 0


async def test_patch_tire_updates_thickness(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    tire = await _create_tire(client, headers, "TIRE-PATCH")
    resp = await client.patch(
        f"/api/v1/tires/{tire['id']}", headers=headers, json={"current_thickness_mm": 8.5}
    )
    assert resp.status_code == 200
    assert resp.json()["current_thickness_mm"] == 8.5


async def test_readonly_user_cannot_create_tire(client: AsyncClient, readonly_user: User) -> None:
    headers = await auth_headers(client, "readonly@acmetransport.dev", "ReadOnly123!")
    resp = await client.post(
        "/api/v1/tires",
        headers=headers,
        json={"unique_code": "X", "brand": "X", "model": "X", "current_thickness_mm": 10},
    )
    assert resp.status_code == 403


async def test_installation_requires_position_fields(
    client: AsyncClient, admin_user: User, vehicle: Vehicle
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    tire = await _create_tire(client, headers, "TIRE-NOPOS")
    resp = await client.post(
        "/api/v1/tire-movements",
        headers=headers,
        json={"tire_id": tire["id"], "movement_type": "instalacion", "vehicle_id": str(vehicle.id)},
    )
    assert resp.status_code == 422


async def test_install_captures_km_at_movement_and_updates_tire_state(
    client: AsyncClient, admin_user: User, vehicle: Vehicle
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    tire = await _create_tire(client, headers, "TIRE-INSTALL")

    resp = await client.post(
        "/api/v1/tire-movements",
        headers=headers,
        json={
            "tire_id": tire["id"],
            "movement_type": "instalacion",
            "vehicle_id": str(vehicle.id),
            "axle_number": 1,
            "axle_side": "izquierdo",
            "axle_dual_position": "interior",
        },
    )
    assert resp.status_code == 201, resp.text
    movement = resp.json()
    assert movement["km_at_movement"] == vehicle.current_odometer_km

    tire_resp = await client.get(f"/api/v1/tires/{tire['id']}", headers=headers)
    body = tire_resp.json()
    assert body["status"] == "instalado"
    assert body["vehicle_id"] == str(vehicle.id)
    assert body["axle_number"] == 1


async def test_cannot_install_two_tires_on_same_position(
    client: AsyncClient, admin_user: User, vehicle: Vehicle
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    tire_a = await _create_tire(client, headers, "TIRE-POS-A")
    tire_b = await _create_tire(client, headers, "TIRE-POS-B")

    position = {
        "vehicle_id": str(vehicle.id),
        "axle_number": 1,
        "axle_side": "izquierdo",
        "axle_dual_position": "exterior",
    }
    ok = await client.post(
        "/api/v1/tire-movements",
        headers=headers,
        json={"tire_id": tire_a["id"], "movement_type": "instalacion", **position},
    )
    assert ok.status_code == 201

    conflict = await client.post(
        "/api/v1/tire-movements",
        headers=headers,
        json={"tire_id": tire_b["id"], "movement_type": "instalacion", **position},
    )
    assert conflict.status_code == 422


async def test_cannot_install_tire_that_is_already_installed(
    client: AsyncClient, admin_user: User, vehicle: Vehicle
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    tire = await _create_tire(client, headers, "TIRE-TWICE")
    position = {
        "vehicle_id": str(vehicle.id),
        "axle_number": 2,
        "axle_side": "derecho",
        "axle_dual_position": "unico",
    }
    first = await client.post(
        "/api/v1/tire-movements",
        headers=headers,
        json={"tire_id": tire["id"], "movement_type": "instalacion", **position},
    )
    assert first.status_code == 201

    second = await client.post(
        "/api/v1/tire-movements",
        headers=headers,
        json={"tire_id": tire["id"], "movement_type": "instalacion", **position},
    )
    assert second.status_code == 422


async def test_full_lifecycle_install_uninstall_repair_return(
    client: AsyncClient, admin_user: User, vehicle: Vehicle, warehouse: Warehouse
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    tire = await _create_tire(client, headers, "TIRE-LIFECYCLE")

    install = await client.post(
        "/api/v1/tire-movements",
        headers=headers,
        json={
            "tire_id": tire["id"],
            "movement_type": "instalacion",
            "vehicle_id": str(vehicle.id),
            "axle_number": 1,
            "axle_side": "izquierdo",
            "axle_dual_position": "interior",
        },
    )
    assert install.status_code == 201

    uninstall = await client.post(
        "/api/v1/tire-movements",
        headers=headers,
        json={
            "tire_id": tire["id"],
            "movement_type": "desinstalacion",
            "warehouse_id": str(warehouse.id),
        },
    )
    assert uninstall.status_code == 201
    assert uninstall.json()["axle_number"] == 1  # snapshot de la posición liberada

    repair = await client.post(
        "/api/v1/tire-movements",
        headers=headers,
        json={"tire_id": tire["id"], "movement_type": "envio_reencauche"},
    )
    assert repair.status_code == 201

    tire_after_repair = await client.get(f"/api/v1/tires/{tire['id']}", headers=headers)
    assert tire_after_repair.json()["status"] == "reparacion"

    return_movement = await client.post(
        "/api/v1/tire-movements",
        headers=headers,
        json={
            "tire_id": tire["id"],
            "movement_type": "retorno_taller",
            "warehouse_id": str(warehouse.id),
        },
    )
    assert return_movement.status_code == 201
    final = await client.get(f"/api/v1/tires/{tire['id']}", headers=headers)
    assert final.json()["status"] == "almacen"
    assert final.json()["warehouse_id"] == str(warehouse.id)


async def test_tire_km_calculation_via_detail_endpoint(
    client: AsyncClient, admin_user: User, db, vehicle: Vehicle, warehouse: Warehouse
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    tire = await _create_tire(client, headers, "TIRE-KM")

    await client.post(
        "/api/v1/tire-movements",
        headers=headers,
        json={
            "tire_id": tire["id"],
            "movement_type": "instalacion",
            "vehicle_id": str(vehicle.id),
            "axle_number": 1,
            "axle_side": "izquierdo",
            "axle_dual_position": "interior",
        },
    )

    vehicle.current_odometer_km = 13_500
    db.add(vehicle)
    await db.commit()

    detail = await client.get(f"/api/v1/tires/{tire['id']}", headers=headers)
    body = detail.json()
    assert body["km_current_period"] == 3_500
    assert body["km_lifetime_total"] == 3_500
    assert len(body["movements"]) == 1


async def test_batch_movement_desinstalacion(
    client: AsyncClient, admin_user: User, vehicle: Vehicle, warehouse: Warehouse
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    tire_a = await _create_tire(client, headers, "TIRE-BATCH-A")
    tire_b = await _create_tire(client, headers, "TIRE-BATCH-B")

    for tire, side in ((tire_a, "izquierdo"), (tire_b, "derecho")):
        resp = await client.post(
            "/api/v1/tire-movements",
            headers=headers,
            json={
                "tire_id": tire["id"],
                "movement_type": "instalacion",
                "vehicle_id": str(vehicle.id),
                "axle_number": 1,
                "axle_side": side,
                "axle_dual_position": "unico",
            },
        )
        assert resp.status_code == 201

    batch = await client.post(
        "/api/v1/tire-movements/batch",
        headers=headers,
        json={
            "movement_type": "desinstalacion",
            "warehouse_id": str(warehouse.id),
            "items": [{"tire_id": tire_a["id"]}, {"tire_id": tire_b["id"]}],
        },
    )
    assert batch.status_code == 201
    assert len(batch.json()) == 2

    for tire in (tire_a, tire_b):
        resp = await client.get(f"/api/v1/tires/{tire['id']}", headers=headers)
        assert resp.json()["status"] == "almacen"


async def test_disparity_alert_generated_when_threshold_exceeded(
    client: AsyncClient, admin_user: User, db, company, vehicle: Vehicle
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    tire_a = await _create_tire(client, headers, "TIRE-DISP-A", thickness=15.0)
    tire_b = await _create_tire(client, headers, "TIRE-DISP-B", thickness=10.0)  # diff 5mm > 3mm default

    for tire, dual in ((tire_a, "interior"), (tire_b, "exterior")):
        resp = await client.post(
            "/api/v1/tire-movements",
            headers=headers,
            json={
                "tire_id": tire["id"],
                "movement_type": "instalacion",
                "vehicle_id": str(vehicle.id),
                "axle_number": 3,
                "axle_side": "izquierdo",
                "axle_dual_position": dual,
            },
        )
        assert resp.status_code == 201

    alerts = (await db.execute(select(Alert).where(Alert.company_id == company.id))).scalars().all()
    disparity_alerts = [a for a in alerts if a.type == "tire_disparity"]
    assert len(disparity_alerts) == 1
    assert disparity_alerts[0].entity_id == uuid_of(tire_b["id"])


async def test_disparity_alert_not_generated_within_threshold(
    client: AsyncClient, admin_user: User, db, company, vehicle: Vehicle
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    tire_a = await _create_tire(client, headers, "TIRE-OK-A", thickness=15.0)
    tire_b = await _create_tire(client, headers, "TIRE-OK-B", thickness=14.0)  # diff 1mm < 3mm default

    for tire, dual in ((tire_a, "interior"), (tire_b, "exterior")):
        resp = await client.post(
            "/api/v1/tire-movements",
            headers=headers,
            json={
                "tire_id": tire["id"],
                "movement_type": "instalacion",
                "vehicle_id": str(vehicle.id),
                "axle_number": 4,
                "axle_side": "derecho",
                "axle_dual_position": dual,
            },
        )
        assert resp.status_code == 201

    alerts = (await db.execute(select(Alert).where(Alert.company_id == company.id))).scalars().all()
    assert not any(a.type == "tire_disparity" for a in alerts)


async def test_vehicle_tires_endpoint_lists_only_installed(
    client: AsyncClient, admin_user: User, vehicle: Vehicle
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    tire = await _create_tire(client, headers, "TIRE-VEH")
    await client.post(
        "/api/v1/tire-movements",
        headers=headers,
        json={
            "tire_id": tire["id"],
            "movement_type": "instalacion",
            "vehicle_id": str(vehicle.id),
            "axle_number": 1,
            "axle_side": "unico",
            "axle_dual_position": "unico",
        },
    )
    resp = await client.get(f"/api/v1/vehicles/{vehicle.id}/tires", headers=headers)
    assert resp.status_code == 200
    codes = [t["unique_code"] for t in resp.json()]
    assert codes == ["TIRE-VEH"]


async def test_performance_analytics_reports_avg_km_by_brand_model(
    client: AsyncClient, admin_user: User, db, vehicle: Vehicle
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    tire = await _create_tire(client, headers, "TIRE-PERF")

    await client.post(
        "/api/v1/tire-movements",
        headers=headers,
        json={
            "tire_id": tire["id"],
            "movement_type": "instalacion",
            "vehicle_id": str(vehicle.id),
            "axle_number": 1,
            "axle_side": "unico",
            "axle_dual_position": "unico",
        },
    )
    vehicle.current_odometer_km = 40_000
    db.add(vehicle)
    await db.commit()

    await client.post(
        "/api/v1/tire-movements",
        headers=headers,
        json={"tire_id": tire["id"], "movement_type": "envio_reencauche"},
    )

    resp = await client.get("/api/v1/tires/analytics/performance", headers=headers)
    assert resp.status_code == 200
    rows = resp.json()
    assert len(rows) == 1
    assert rows[0]["brand"] == "Michelin"
    assert rows[0]["end_reason"] == "envio_reencauche"
    assert rows[0]["avg_km"] == 30_000.0


def uuid_of(value: str):
    import uuid

    return uuid.UUID(value)
