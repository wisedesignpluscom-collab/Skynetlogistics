from httpx import AsyncClient

from app.models.provider import Provider
from app.models.user import User
from tests.conftest import auth_headers


async def test_admin_creates_provider(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/providers",
        headers=headers,
        json={"name": "Repuestos SA", "type": "repuestos", "contact_info": {"phone": "555-1234"}},
    )
    assert resp.status_code == 201
    assert resp.json()["contact_info"]["phone"] == "555-1234"


async def test_update_and_delete_provider(client: AsyncClient, admin_user: User, provider: Provider) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    patch_resp = await client.patch(
        f"/api/v1/providers/{provider.id}", headers=headers, json={"name": "Taller Renovado"}
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["name"] == "Taller Renovado"

    delete_resp = await client.delete(f"/api/v1/providers/{provider.id}", headers=headers)
    assert delete_resp.status_code == 204

    get_resp = await client.get(f"/api/v1/providers/{provider.id}", headers=headers)
    assert get_resp.status_code == 404
