import pytest
from httpx import AsyncClient

from app.core.security import hash_password
from app.models.company import Company
from app.models.custom_field import CustomFieldDefinition
from app.models.role import Role
from app.models.user import User
from app.services.custom_fields import CustomDataValidationError, validate_custom_data
from tests.conftest import auth_headers


# --- Validador puro ---

def _def(**kw) -> CustomFieldDefinition:
    base = dict(entity_type="vehicle", key="k", label="Campo", field_type="texto", options=[], required=False)
    base.update(kw)
    return CustomFieldDefinition(**base)


def test_validate_required_missing_raises() -> None:
    defs = [_def(key="poliza", label="Póliza", required=True)]
    with pytest.raises(CustomDataValidationError):
        validate_custom_data(defs, {})


def test_validate_number_coerced() -> None:
    defs = [_def(key="peso", field_type="numero")]
    assert validate_custom_data(defs, {"peso": "12.5"}) == {"peso": 12.5}


def test_validate_number_invalid_raises() -> None:
    defs = [_def(key="peso", field_type="numero")]
    with pytest.raises(CustomDataValidationError):
        validate_custom_data(defs, {"peso": "abc"})


def test_validate_select_out_of_options_raises() -> None:
    defs = [_def(key="cat", field_type="select", options=[{"value": "a", "label": "A"}])]
    with pytest.raises(CustomDataValidationError):
        validate_custom_data(defs, {"cat": "z"})
    assert validate_custom_data(defs, {"cat": "a"}) == {"cat": "a"}


def test_validate_discards_unknown_keys() -> None:
    defs = [_def(key="conocido")]
    assert validate_custom_data(defs, {"conocido": "x", "otro": "y"}) == {"conocido": "x"}


def test_validate_date_and_checkbox() -> None:
    defs = [_def(key="f", field_type="fecha"), _def(key="b", field_type="checkbox")]
    assert validate_custom_data(defs, {"f": "2026-01-15", "b": True}) == {"f": "2026-01-15", "b": True}
    with pytest.raises(CustomDataValidationError):
        validate_custom_data(defs, {"f": "no-fecha", "b": True})


# --- Endpoints ---

async def _mk_field(client, headers, **body) -> dict:
    payload = {"entity_type": "vehicle", "key": "poliza", "label": "N° Póliza", "field_type": "texto"}
    payload.update(body)
    resp = await client.post("/api/v1/custom-fields", headers=headers, json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()


async def test_admin_creates_and_lists_custom_field(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    await _mk_field(client, headers)
    resp = await client.get("/api/v1/custom-fields?entity_type=vehicle", headers=headers)
    assert resp.status_code == 200
    assert [f["key"] for f in resp.json()] == ["poliza"]


async def test_duplicate_key_conflicts(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    await _mk_field(client, headers)
    resp = await client.post(
        "/api/v1/custom-fields", headers=headers,
        json={"entity_type": "vehicle", "key": "poliza", "label": "Otra", "field_type": "texto"},
    )
    assert resp.status_code == 409


async def test_select_requires_options(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/custom-fields", headers=headers,
        json={"entity_type": "vehicle", "key": "cat", "label": "Cat", "field_type": "select", "options": []},
    )
    assert resp.status_code == 422


async def test_vehicle_create_with_custom_data_validated(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    await _mk_field(client, headers, key="poliza", label="Póliza", required=True)

    # falta el campo requerido -> 422
    bad = await client.post(
        "/api/v1/vehicles", headers=headers,
        json={"plate": "CF-1", "brand": "Ford", "model": "X", "year": 2020, "type": "camion"},
    )
    assert bad.status_code == 422

    ok = await client.post(
        "/api/v1/vehicles", headers=headers,
        json={"plate": "CF-2", "brand": "Ford", "model": "X", "year": 2020, "type": "camion",
              "custom_data": {"poliza": "POL-123"}},
    )
    assert ok.status_code == 201, ok.text
    assert ok.json()["custom_data"] == {"poliza": "POL-123"}


async def test_readonly_user_cannot_create_field(client: AsyncClient, readonly_user: User) -> None:
    headers = await auth_headers(client, "readonly@acmetransport.dev", "ReadOnly123!")
    resp = await client.post(
        "/api/v1/custom-fields", headers=headers,
        json={"entity_type": "vehicle", "key": "x", "label": "X", "field_type": "texto"},
    )
    assert resp.status_code == 403


async def test_fields_isolated_per_company(
    client: AsyncClient, admin_user: User, db, other_company: Company
) -> None:
    other_role = Role(company_id=other_company.id, name="Admin", permissions={"config": ["read"]})
    db.add(other_role)
    await db.flush()
    other_admin = User(
        company_id=other_company.id, role_id=other_role.id, name="OA",
        email="oa2@othercompany.dev", password_hash=hash_password("OtherPass1!"),
    )
    db.add(other_admin)
    await db.commit()

    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    await _mk_field(client, headers)

    other_headers = await auth_headers(client, "oa2@othercompany.dev", "OtherPass1!")
    resp = await client.get("/api/v1/custom-fields?entity_type=vehicle", headers=other_headers)
    assert resp.status_code == 200
    assert resp.json() == []
