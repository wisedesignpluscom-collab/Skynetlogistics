from httpx import AsyncClient

from app.models.company import Company
from app.models.role import Role
from app.models.user import User
from tests.conftest import auth_headers


async def test_admin_creates_role(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/roles",
        headers=headers,
        json={"name": "Dispatcher", "permissions": {"users": ["read"]}},
    )
    assert resp.status_code == 201
    assert resp.json()["name"] == "Dispatcher"


async def test_readonly_role_cannot_create_role(client: AsyncClient, readonly_user: User) -> None:
    headers = await auth_headers(client, "readonly@acmetransport.dev", "ReadOnly123!")
    resp = await client.post(
        "/api/v1/roles", headers=headers, json={"name": "Dispatcher", "permissions": {}}
    )
    assert resp.status_code == 403


async def test_duplicate_role_name_in_company_conflicts(
    client: AsyncClient, admin_user: User, admin_role: Role
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/roles", headers=headers, json={"name": admin_role.name, "permissions": {}}
    )
    assert resp.status_code == 409


async def test_system_role_cannot_be_edited_or_deleted(
    client: AsyncClient, admin_user: User, db, company: Company
) -> None:
    from app.crud import role as role_crud
    from app.schemas.role import RoleCreate

    system_role = await role_crud.create(
        db, company.id, RoleCreate(name="Sistema", permissions={"users": ["read"]})
    )
    system_role.is_system = True
    await db.commit()

    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    edit_resp = await client.patch(
        f"/api/v1/roles/{system_role.id}", headers=headers, json={"name": "Otro"}
    )
    assert edit_resp.status_code == 403

    delete_resp = await client.delete(f"/api/v1/roles/{system_role.id}", headers=headers)
    assert delete_resp.status_code == 403


async def test_delete_role_with_assigned_users_conflicts(
    client: AsyncClient, admin_user: User, admin_role: Role
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.delete(f"/api/v1/roles/{admin_role.id}", headers=headers)
    assert resp.status_code == 409
