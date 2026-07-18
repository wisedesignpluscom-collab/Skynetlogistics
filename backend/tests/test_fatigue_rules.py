from httpx import AsyncClient

from app.models.user import User
from tests.conftest import auth_headers


async def test_get_fatigue_rules_creates_defaults_on_first_access(
    client: AsyncClient, admin_user: User
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.get("/api/v1/fatigue-rules", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["max_continuous_hours"] == 4.5
    assert body["max_24h_hours"] == 10.0
    assert body["max_7day_hours"] == 60.0
    assert body["night_driving_weight"] == 1.5
    assert body["night_start_hour"] == 22
    assert body["night_end_hour"] == 5


async def test_get_fatigue_rules_is_idempotent(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    first = await client.get("/api/v1/fatigue-rules", headers=headers)
    second = await client.get("/api/v1/fatigue-rules", headers=headers)
    assert first.json()["id"] == second.json()["id"]


async def test_patch_fatigue_rules_updates_fields(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.patch(
        "/api/v1/fatigue-rules",
        headers=headers,
        json={"max_continuous_hours": 5, "night_driving_weight": 2},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["max_continuous_hours"] == 5
    assert body["night_driving_weight"] == 2
    # campos no enviados no cambian
    assert body["max_24h_hours"] == 10.0


async def test_patch_fatigue_rules_rejects_out_of_bounds(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.patch(
        "/api/v1/fatigue-rules",
        headers=headers,
        json={"max_continuous_hours": 30},
    )
    assert resp.status_code == 422


async def test_readonly_user_cannot_patch_fatigue_rules(client: AsyncClient, readonly_user: User) -> None:
    headers = await auth_headers(client, "readonly@acmetransport.dev", "ReadOnly123!")
    resp = await client.patch(
        "/api/v1/fatigue-rules",
        headers=headers,
        json={"max_continuous_hours": 5},
    )
    assert resp.status_code == 403


async def test_readonly_user_cannot_read_fatigue_rules(client: AsyncClient, readonly_user: User) -> None:
    headers = await auth_headers(client, "readonly@acmetransport.dev", "ReadOnly123!")
    resp = await client.get("/api/v1/fatigue-rules", headers=headers)
    assert resp.status_code == 403
