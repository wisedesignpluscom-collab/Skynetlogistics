from httpx import AsyncClient

from app.models.company import Company
from app.models.role import Role
from app.models.user import User
from tests.conftest import auth_headers


async def test_admin_creates_user(client: AsyncClient, admin_user: User, admin_role: Role) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "name": "Nuevo Usuario",
            "email": "nuevo@acmetransport.dev",
            "password": "ClaveSegura1!",
            "role_id": str(admin_role.id),
        },
    )
    assert resp.status_code == 201
    assert resp.json()["email"] == "nuevo@acmetransport.dev"


async def test_readonly_user_cannot_create_user(
    client: AsyncClient, readonly_user: User, admin_role: Role
) -> None:
    headers = await auth_headers(client, "readonly@acmetransport.dev", "ReadOnly123!")
    resp = await client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "name": "Intruso",
            "email": "intruso@acmetransport.dev",
            "password": "ClaveSegura1!",
            "role_id": str(admin_role.id),
        },
    )
    assert resp.status_code == 403


async def test_readonly_user_can_list_users(client: AsyncClient, readonly_user: User) -> None:
    headers = await auth_headers(client, "readonly@acmetransport.dev", "ReadOnly123!")
    resp = await client.get("/api/v1/users", headers=headers)
    assert resp.status_code == 200


async def test_cannot_assign_role_from_another_company(
    client: AsyncClient,
    admin_user: User,
    other_company: Company,
    db,
) -> None:
    from app.crud import role as role_crud
    from app.schemas.role import RoleCreate

    foreign_role = await role_crud.create(db, other_company.id, RoleCreate(name="Foreign", permissions={}))

    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "name": "Hacker",
            "email": "hacker@acmetransport.dev",
            "password": "ClaveSegura1!",
            "role_id": str(foreign_role.id),
        },
    )
    assert resp.status_code == 400


async def test_tenant_isolation_users_list(
    client: AsyncClient,
    admin_user: User,
    other_company: Company,
    db,
) -> None:
    from app.crud import role as role_crud
    from app.crud import user as user_crud
    from app.schemas.role import RoleCreate
    from app.schemas.user import UserCreate

    other_role = await role_crud.create(db, other_company.id, RoleCreate(name="OtherAdmin", permissions={}))
    await user_crud.create(
        db,
        other_company.id,
        UserCreate(
            name="Otro Usuario", email="otro@otherfleet.dev", password="ClaveSegura1!", role_id=other_role.id
        ),
    )

    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.get("/api/v1/users", headers=headers)
    assert resp.status_code == 200
    emails = [u["email"] for u in resp.json()["items"]]
    assert "otro@otherfleet.dev" not in emails
    assert "admin@acmetransport.dev" in emails


async def test_user_cannot_deactivate_self(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.delete(f"/api/v1/users/{admin_user.id}", headers=headers)
    assert resp.status_code == 400


async def test_self_password_change_requires_current_password(
    client: AsyncClient, admin_user: User
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")

    wrong_resp = await client.patch(
        f"/api/v1/users/{admin_user.id}/password",
        headers=headers,
        json={"current_password": "incorrecta", "new_password": "NuevaClave1!"},
    )
    assert wrong_resp.status_code == 400

    ok_resp = await client.patch(
        f"/api/v1/users/{admin_user.id}/password",
        headers=headers,
        json={"current_password": "Sup3rSecret!", "new_password": "NuevaClave1!"},
    )
    assert ok_resp.status_code == 200

    relogin = await client.post(
        "/api/v1/auth/login", json={"email": "admin@acmetransport.dev", "password": "NuevaClave1!"}
    )
    assert relogin.status_code == 200
