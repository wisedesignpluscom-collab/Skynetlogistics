from httpx import AsyncClient

from app.models.user import User
from tests.conftest import auth_headers


async def test_get_tire_settings_creates_defaults(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.get("/api/v1/tire-settings", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["disparity_threshold_mm"] == 3.0


async def test_update_tire_settings(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.patch(
        "/api/v1/tire-settings", headers=headers, json={"disparity_threshold_mm": 5.0}
    )
    assert resp.status_code == 200
    assert resp.json()["disparity_threshold_mm"] == 5.0
