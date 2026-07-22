from httpx import AsyncClient

from app.models.user import User
from tests.conftest import auth_headers


async def _mk_workflow(client, headers, **overrides) -> dict:
    body = {
        "entity_type": "vehicle",
        "event": "creado",
        "name": "Alertar vehículo remolque",
        "condition": {"match": "all", "conditions": [{"field": "type", "op": "igual", "value": "remolque"}]},
        "actions": [{"type": "crear_alerta", "message": "Se creó un remolque nuevo", "severity": "media"}],
    }
    body.update(overrides)
    resp = await client.post("/api/v1/workflows", headers=headers, json=body)
    assert resp.status_code == 201, resp.text
    return resp.json()


async def test_create_and_list_workflow(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    await _mk_workflow(client, headers)
    resp = await client.get("/api/v1/workflows?entity_type=vehicle", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["event"] == "creado"


async def test_workflow_requires_at_least_one_action(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/workflows", headers=headers,
        json={"entity_type": "vehicle", "event": "creado", "name": "Sin acciones", "condition": {}, "actions": []},
    )
    assert resp.status_code == 422


async def test_actualizar_campo_requires_custom_target(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/workflows", headers=headers,
        json={
            "entity_type": "vehicle", "event": "creado", "name": "Malo", "condition": {},
            "actions": [{"type": "actualizar_campo", "target": "brand", "value": "x"}],
        },
    )
    assert resp.status_code == 422


async def test_workflow_creates_alert_on_matching_create(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    await _mk_workflow(client, headers)

    created = await client.post(
        "/api/v1/vehicles", headers=headers,
        json={"plate": "WF-1", "brand": "X", "model": "Y", "year": 2020, "type": "remolque"},
    )
    assert created.status_code == 201, created.text
    vehicle_id = created.json()["id"]

    alerts = await client.get("/api/v1/alerts", headers=headers)
    matching = [a for a in alerts.json()["items"] if a["entity_id"] == vehicle_id]
    assert len(matching) == 1
    assert matching[0]["message"] == "Se creó un remolque nuevo"


async def test_workflow_condition_not_met_no_alert(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    await _mk_workflow(client, headers)

    created = await client.post(
        "/api/v1/vehicles", headers=headers,
        json={"plate": "WF-2", "brand": "X", "model": "Y", "year": 2020, "type": "camion"},
    )
    assert created.status_code == 201
    vehicle_id = created.json()["id"]

    alerts = await client.get("/api/v1/alerts", headers=headers)
    matching = [a for a in alerts.json()["items"] if a["entity_id"] == vehicle_id]
    assert len(matching) == 0


async def test_workflow_actualizar_campo_sets_custom_data(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    await client.post(
        "/api/v1/custom-fields", headers=headers,
        json={"entity_type": "vehicle", "key": "revisado", "label": "Revisado", "field_type": "checkbox"},
    )
    await _mk_workflow(
        client, headers,
        name="Marcar revisión pendiente",
        actions=[{"type": "actualizar_campo", "target": "custom.revisado", "value": False}],
    )

    created = await client.post(
        "/api/v1/vehicles", headers=headers,
        json={"plate": "WF-3", "brand": "X", "model": "Y", "year": 2020, "type": "remolque"},
    )
    assert created.status_code == 201, created.text
    vehicle_id = created.json()["id"]

    detail = await client.get(f"/api/v1/vehicles/{vehicle_id}", headers=headers)
    assert detail.json()["custom_data"]["revisado"] is False


async def test_cambio_estado_workflow_fires_on_status_change(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    await _mk_workflow(
        client, headers,
        event="cambio_estado",
        name="Alerta vehículo a taller",
        condition={"match": "all", "conditions": [{"field": "status", "op": "igual", "value": "taller"}]},
        actions=[{"type": "crear_alerta", "message": "Vehículo entró a taller", "severity": "alta"}],
    )

    created = await client.post(
        "/api/v1/vehicles", headers=headers,
        json={"plate": "WF-4", "brand": "X", "model": "Y", "year": 2020, "type": "camion"},
    )
    vehicle_id = created.json()["id"]

    # sin cambiar status: no dispara
    await client.patch(f"/api/v1/vehicles/{vehicle_id}", headers=headers, json={"brand": "Otra"})
    alerts = await client.get("/api/v1/alerts", headers=headers)
    assert len([a for a in alerts.json()["items"] if a["entity_id"] == vehicle_id]) == 0

    # cambia a 'taller': dispara
    await client.patch(f"/api/v1/vehicles/{vehicle_id}", headers=headers, json={"status": "taller"})
    alerts = await client.get("/api/v1/alerts", headers=headers)
    matching = [a for a in alerts.json()["items"] if a["entity_id"] == vehicle_id]
    assert len(matching) == 1
    assert matching[0]["message"] == "Vehículo entró a taller"


async def test_readonly_user_cannot_create_workflow(client: AsyncClient, readonly_user: User) -> None:
    headers = await auth_headers(client, "readonly@acmetransport.dev", "ReadOnly123!")
    resp = await client.post(
        "/api/v1/workflows", headers=headers,
        json={
            "entity_type": "vehicle", "event": "creado", "name": "X", "condition": {},
            "actions": [{"type": "crear_alerta", "message": "x"}],
        },
    )
    assert resp.status_code == 403


async def test_inactive_workflow_does_not_fire(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    await _mk_workflow(client, headers, active=False)

    created = await client.post(
        "/api/v1/vehicles", headers=headers,
        json={"plate": "WF-5", "brand": "X", "model": "Y", "year": 2020, "type": "remolque"},
    )
    vehicle_id = created.json()["id"]
    alerts = await client.get("/api/v1/alerts", headers=headers)
    assert len([a for a in alerts.json()["items"] if a["entity_id"] == vehicle_id]) == 0
