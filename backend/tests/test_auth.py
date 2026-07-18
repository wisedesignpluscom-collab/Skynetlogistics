from httpx import AsyncClient

from app.models.user import User
from tests.conftest import auth_headers, login


async def test_login_success_returns_tokens_and_user(client: AsyncClient, admin_user: User) -> None:
    data = await login(client, "admin@acmetransport.dev", "Sup3rSecret!")
    assert data["access_token"]
    assert data["refresh_token"]
    assert data["user"]["email"] == "admin@acmetransport.dev"
    assert data["user"]["role"]["name"] == "Admin"


async def test_login_wrong_password_fails(client: AsyncClient, admin_user: User) -> None:
    resp = await client.post(
        "/api/v1/auth/login", json={"email": "admin@acmetransport.dev", "password": "wrong"}
    )
    assert resp.status_code == 401


async def test_login_unknown_email_fails(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/auth/login", json={"email": "nobody@acmetransport.dev", "password": "whatever"}
    )
    assert resp.status_code == 401


async def test_me_returns_permissions(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.get("/api/v1/auth/me", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["permissions"]["users"] == ["read", "write", "delete"]


async def test_me_without_token_is_401(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


async def test_refresh_rotates_token_and_invalidates_old_one(
    client: AsyncClient, admin_user: User
) -> None:
    tokens = await login(client, "admin@acmetransport.dev", "Sup3rSecret!")

    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert resp.status_code == 200
    new_tokens = resp.json()
    assert new_tokens["refresh_token"] != tokens["refresh_token"]

    reuse_resp = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert reuse_resp.status_code == 401


async def test_logout_revokes_refresh_token(client: AsyncClient, admin_user: User) -> None:
    tokens = await login(client, "admin@acmetransport.dev", "Sup3rSecret!")

    logout_resp = await client.post(
        "/api/v1/auth/logout", json={"refresh_token": tokens["refresh_token"]}
    )
    assert logout_resp.status_code == 204

    refresh_resp = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert refresh_resp.status_code == 401
