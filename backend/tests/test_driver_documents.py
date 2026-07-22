from datetime import date, timedelta

from httpx import AsyncClient

from app.models.company import Company
from app.models.driver import Driver
from app.models.driver_document_type import DriverDocumentType
from app.models.user import User
from tests.conftest import auth_headers


async def test_admin_creates_document_type(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/driver-document-types",
        headers=headers,
        json={"name": "Certificado médico", "alert_days_before": 45},
    )
    assert resp.status_code == 201
    assert resp.json()["alert_days_before"] == 45


async def test_create_document_for_driver(
    client: AsyncClient, admin_user: User, driver: Driver, db, company: Company
) -> None:
    doc_type = DriverDocumentType(company_id=company.id, name="Cédula de identidad", alert_days_before=60)
    db.add(doc_type)
    await db.commit()
    await db.refresh(doc_type)

    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        f"/api/v1/drivers/{driver.id}/documents",
        headers=headers,
        json={"document_type_id": str(doc_type.id), "number": "12345678", "expiry_date": "2027-01-01"},
    )
    assert resp.status_code == 201
    assert resp.json()["document_type"]["name"] == "Cédula de identidad"

    list_resp = await client.get(f"/api/v1/drivers/{driver.id}/documents", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1


async def test_document_expiring_soon_generates_alert(
    client: AsyncClient, admin_user: User, driver: Driver, db, company: Company
) -> None:
    doc_type = DriverDocumentType(company_id=company.id, name="Certificado médico", alert_days_before=30)
    db.add(doc_type)
    await db.commit()
    await db.refresh(doc_type)

    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    near_expiry = (date.today() + timedelta(days=10)).isoformat()
    create_resp = await client.post(
        f"/api/v1/drivers/{driver.id}/documents",
        headers=headers,
        json={"document_type_id": str(doc_type.id), "expiry_date": near_expiry},
    )
    assert create_resp.status_code == 201

    alerts_resp = await client.get("/api/v1/alerts", headers=headers)
    assert alerts_resp.status_code == 200
    messages = [a["message"] for a in alerts_resp.json()["items"]]
    assert any("Certificado médico" in m for m in messages)


async def test_update_and_delete_document_type(
    client: AsyncClient, admin_user: User, db, company: Company
) -> None:
    doc_type = DriverDocumentType(company_id=company.id, name="Permiso de trabajo", alert_days_before=30)
    db.add(doc_type)
    await db.commit()
    await db.refresh(doc_type)

    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    patch_resp = await client.patch(
        f"/api/v1/driver-document-types/{doc_type.id}", headers=headers, json={"alert_days_before": 15}
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["alert_days_before"] == 15

    delete_resp = await client.delete(f"/api/v1/driver-document-types/{doc_type.id}", headers=headers)
    assert delete_resp.status_code == 204
