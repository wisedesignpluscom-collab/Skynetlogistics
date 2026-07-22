from httpx import AsyncClient

from app.models.user import User
from tests.conftest import auth_headers


async def _mk_validation_rule(client, headers, **overrides) -> dict:
    """Regla: si el año del vehículo es menor a 2000, bloquear al guardar."""
    body = {
        "entity_type": "vehicle",
        "kind": "validacion",
        "name": "Bloquear vehículos muy viejos",
        "condition": {"match": "all", "conditions": [{"field": "year", "op": "menor", "value": 2000}]},
        "actions": [{"type": "bloquear", "message": "No se admiten vehículos anteriores al año 2000"}],
    }
    body.update(overrides)
    resp = await client.post("/api/v1/form-rules", headers=headers, json=body)
    assert resp.status_code == 201, resp.text
    return resp.json()


async def test_entity_schema_combines_system_and_custom(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    # crear un campo custom para que aparezca en el schema
    await client.post(
        "/api/v1/custom-fields", headers=headers,
        json={"entity_type": "vehicle", "key": "poliza", "label": "Póliza", "field_type": "texto"},
    )
    resp = await client.get("/api/v1/form-rules/entity-schema?entity_type=vehicle", headers=headers)
    assert resp.status_code == 200
    keys = {f["key"] for f in resp.json()["fields"]}
    assert "type" in keys  # campo de sistema
    assert "custom.poliza" in keys  # campo custom
    sources = {f["key"]: f["source"] for f in resp.json()["fields"]}
    assert sources["type"] == "sistema"
    assert sources["custom.poliza"] == "custom"


async def test_validation_rule_blocks_matching_create(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    await _mk_validation_rule(client, headers)

    blocked = await client.post(
        "/api/v1/vehicles", headers=headers,
        json={"plate": "OLD-1", "brand": "X", "model": "Y", "year": 1990, "type": "camion"},
    )
    assert blocked.status_code == 422
    assert "anteriores al año 2000" in blocked.json()["detail"]

    ok = await client.post(
        "/api/v1/vehicles", headers=headers,
        json={"plate": "NEW-1", "brand": "X", "model": "Y", "year": 2021, "type": "camion"},
    )
    assert ok.status_code == 201


async def test_validation_rule_on_custom_field(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    await client.post(
        "/api/v1/custom-fields", headers=headers,
        json={"entity_type": "vehicle", "key": "riesgo", "label": "Riesgo", "field_type": "select",
              "options": [{"value": "alto", "label": "Alto"}, {"value": "bajo", "label": "Bajo"}]},
    )
    await _mk_validation_rule(
        client, headers, name="Bloquear riesgo alto",
        condition={"match": "all", "conditions": [{"field": "custom.riesgo", "op": "igual", "value": "alto"}]},
        actions=[{"type": "bloquear", "message": "Riesgo alto no permitido"}],
    )
    blocked = await client.post(
        "/api/v1/vehicles", headers=headers,
        json={"plate": "R-1", "brand": "X", "model": "Y", "year": 2021, "type": "camion",
              "custom_data": {"riesgo": "alto"}},
    )
    assert blocked.status_code == 422
    assert "Riesgo alto" in blocked.json()["detail"]


async def test_inactive_rule_does_not_block(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    rule = await _mk_validation_rule(client, headers)
    await client.patch(f"/api/v1/form-rules/{rule['id']}", headers=headers, json={"active": False})

    ok = await client.post(
        "/api/v1/vehicles", headers=headers,
        json={"plate": "OLD-2", "brand": "X", "model": "Y", "year": 1990, "type": "camion"},
    )
    assert ok.status_code == 201


async def test_create_form_rule_validates_actions(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    # regla de validación con acción de formulario -> 422 del schema
    resp = await client.post(
        "/api/v1/form-rules", headers=headers,
        json={"entity_type": "vehicle", "kind": "validacion", "name": "mala",
              "condition": {"conditions": []}, "actions": [{"type": "ocultar", "target": "brand"}]},
    )
    assert resp.status_code == 422


async def test_readonly_cannot_create_rule(client: AsyncClient, readonly_user: User) -> None:
    headers = await auth_headers(client, "readonly@acmetransport.dev", "ReadOnly123!")
    resp = await client.post(
        "/api/v1/form-rules", headers=headers,
        json={"entity_type": "vehicle", "kind": "formulario", "name": "x",
              "condition": {"conditions": []}, "actions": [{"type": "ocultar", "target": "brand"}]},
    )
    assert resp.status_code == 403
