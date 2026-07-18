from httpx import AsyncClient

from app.models.company import Company
from app.models.user import User
from tests.conftest import auth_headers


async def test_superadmin_can_list_companies(
    client: AsyncClient, superadmin_user: User, company: Company
) -> None:
    headers = await auth_headers(client, "root@platformfleet.dev", "RootPass1!")
    resp = await client.get("/api/v1/companies", headers=headers)
    assert resp.status_code == 200
    names = [c["name"] for c in resp.json()["items"]]
    assert "Acme Transport" in names


async def test_non_superadmin_cannot_access_companies(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.get("/api/v1/companies", headers=headers)
    assert resp.status_code == 403


async def test_superadmin_creates_company(client: AsyncClient, superadmin_user: User) -> None:
    headers = await auth_headers(client, "root@platformfleet.dev", "RootPass1!")
    resp = await client.post(
        "/api/v1/companies",
        headers=headers,
        json={"name": "New Fleet Co", "tax_id": "NEW-001", "plan": "trial"},
    )
    assert resp.status_code == 201
    assert resp.json()["is_active"] is True


async def test_create_company_duplicate_tax_id_conflicts(
    client: AsyncClient, superadmin_user: User, company: Company
) -> None:
    headers = await auth_headers(client, "root@platformfleet.dev", "RootPass1!")
    resp = await client.post(
        "/api/v1/companies",
        headers=headers,
        json={"name": "Duplicate", "tax_id": company.tax_id, "plan": "trial"},
    )
    assert resp.status_code == 409


async def test_delete_company_soft_deletes(
    client: AsyncClient, superadmin_user: User, company: Company
) -> None:
    headers = await auth_headers(client, "root@platformfleet.dev", "RootPass1!")
    resp = await client.delete(f"/api/v1/companies/{company.id}", headers=headers)
    assert resp.status_code == 204

    get_resp = await client.get(f"/api/v1/companies/{company.id}", headers=headers)
    assert get_resp.json()["is_active"] is False
