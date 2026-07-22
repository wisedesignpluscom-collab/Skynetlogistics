from datetime import date, timedelta

from httpx import AsyncClient

from app.models.company import Company
from app.models.vehicle import Vehicle
from app.models.vehicle_document_type import VehicleDocumentType
from app.models.vehicle_owner import VehicleOwner
from app.models.user import User
from tests.conftest import auth_headers


async def test_admin_creates_vehicle_owner(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/vehicle-owners",
        headers=headers,
        json={"name": "Transportes del Zulia C.A.", "tax_id": "J-12345678-9"},
    )
    assert resp.status_code == 201
    assert resp.json()["is_active"] is True


async def test_vehicle_create_accepts_owner_and_new_fields(
    client: AsyncClient, admin_user: User, db, company: Company
) -> None:
    owner = VehicleOwner(company_id=company.id, name="Propietario Externo")
    db.add(owner)
    await db.commit()
    await db.refresh(owner)

    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/vehicles",
        headers=headers,
        json={
            "plate": "OWN-001",
            "brand": "Freightliner",
            "model": "Cascadia",
            "year": 2023,
            "type": "camion",
            "owner_id": str(owner.id),
            "color": "Blanco",
            "engine_serial": "ENG-999",
            "has_odometer": True,
            "odometer_digits": 6,
            "cargo_capacity_kg": 15000,
            "contract": "Contrato-2026-01",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["owner_id"] == str(owner.id)
    assert body["color"] == "Blanco"
    assert body["cargo_capacity_kg"] == 15000.0


async def test_vehicle_rejects_owner_from_other_company(
    client: AsyncClient, admin_user: User, db, other_company: Company
) -> None:
    other_owner = VehicleOwner(company_id=other_company.id, name="Ajeno")
    db.add(other_owner)
    await db.commit()
    await db.refresh(other_owner)

    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/vehicles",
        headers=headers,
        json={
            "plate": "OWN-002",
            "brand": "Volvo",
            "model": "VNL",
            "year": 2022,
            "type": "camion",
            "owner_id": str(other_owner.id),
        },
    )
    assert resp.status_code == 404


async def test_create_document_for_vehicle_and_alert(
    client: AsyncClient, admin_user: User, vehicle: Vehicle, db, company: Company
) -> None:
    doc_type = VehicleDocumentType(company_id=company.id, name="Póliza de seguro", alert_days_before=30)
    db.add(doc_type)
    await db.commit()
    await db.refresh(doc_type)

    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    near_expiry = (date.today() + timedelta(days=10)).isoformat()
    resp = await client.post(
        f"/api/v1/vehicles/{vehicle.id}/documents",
        headers=headers,
        json={"document_type_id": str(doc_type.id), "number": "POL-001", "expiry_date": near_expiry},
    )
    assert resp.status_code == 201
    assert resp.json()["document_type"]["name"] == "Póliza de seguro"

    list_resp = await client.get(f"/api/v1/vehicles/{vehicle.id}/documents", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    alerts_resp = await client.get("/api/v1/alerts", headers=headers)
    assert alerts_resp.status_code == 200
    messages = [a["message"] for a in alerts_resp.json()["items"]]
    assert any("Póliza de seguro" in m for m in messages)
