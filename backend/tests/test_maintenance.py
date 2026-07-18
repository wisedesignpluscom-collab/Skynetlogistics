from httpx import AsyncClient

from app.models.company import Company
from app.models.user import User
from app.models.vehicle import Vehicle
from tests.conftest import auth_headers


async def test_create_task_scheduled_by_time(client: AsyncClient, admin_user: User, vehicle: Vehicle) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/maintenance-tasks",
        headers=headers,
        json={
            "vehicle_id": str(vehicle.id),
            "type": "preventivo",
            "scheduled_by": "tiempo",
            "due_date": "2030-01-01",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "pendiente"


async def test_create_task_missing_due_field_rejected(
    client: AsyncClient, admin_user: User, vehicle: Vehicle
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/maintenance-tasks",
        headers=headers,
        json={"vehicle_id": str(vehicle.id), "type": "preventivo", "scheduled_by": "tiempo"},
    )
    assert resp.status_code == 422


async def test_create_task_for_vehicle_from_another_company_rejected(
    client: AsyncClient, admin_user: User, other_company: Company, db
) -> None:
    other_vehicle = Vehicle(
        company_id=other_company.id, plate="OTH-777", brand="MAN", model="TGX", year=2019, type="cabezal"
    )
    db.add(other_vehicle)
    await db.commit()
    await db.refresh(other_vehicle)

    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/maintenance-tasks",
        headers=headers,
        json={
            "vehicle_id": str(other_vehicle.id),
            "type": "preventivo",
            "scheduled_by": "km",
            "due_km": 50000,
        },
    )
    assert resp.status_code == 400


async def test_complete_task_creates_record_and_marks_completed(
    client: AsyncClient, admin_user: User, vehicle: Vehicle, provider
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    create_resp = await client.post(
        "/api/v1/maintenance-tasks",
        headers=headers,
        json={
            "vehicle_id": str(vehicle.id),
            "type": "correctivo",
            "scheduled_by": "km",
            "due_km": 20000,
        },
    )
    task_id = create_resp.json()["id"]

    complete_resp = await client.post(
        f"/api/v1/maintenance-tasks/{task_id}/complete",
        headers=headers,
        json={"cost_labor": 100.5, "cost_parts": 50.25, "provider_id": str(provider.id), "notes": "Cambio de aceite"},
    )
    assert complete_resp.status_code == 200
    assert complete_resp.json()["status"] == "completada"

    history_resp = await client.get(f"/api/v1/vehicles/{vehicle.id}/maintenance", headers=headers)
    assert history_resp.status_code == 200
    history = history_resp.json()
    assert len(history) == 1
    assert len(history[0]["records"]) == 1
    assert history[0]["records"][0]["cost_labor"] == 100.5


async def test_complete_already_completed_task_conflicts(
    client: AsyncClient, admin_user: User, vehicle: Vehicle
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    create_resp = await client.post(
        "/api/v1/maintenance-tasks",
        headers=headers,
        json={"vehicle_id": str(vehicle.id), "type": "correctivo", "scheduled_by": "km", "due_km": 20000},
    )
    task_id = create_resp.json()["id"]

    first = await client.post(
        f"/api/v1/maintenance-tasks/{task_id}/complete",
        headers=headers,
        json={"cost_labor": 10, "cost_parts": 5},
    )
    assert first.status_code == 200

    second = await client.post(
        f"/api/v1/maintenance-tasks/{task_id}/complete",
        headers=headers,
        json={"cost_labor": 10, "cost_parts": 5},
    )
    assert second.status_code == 409
