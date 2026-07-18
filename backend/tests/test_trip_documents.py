from httpx import AsyncClient

from app.models.driver import Driver
from app.models.user import User
from app.models.vehicle import Vehicle
from tests.conftest import auth_headers


async def test_loading_order_document_renders_html(
    client: AsyncClient, admin_user: User, vehicle: Vehicle, driver: Driver
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    trip_resp = await client.post(
        "/api/v1/trips",
        headers=headers,
        json={
            "vehicle_id": str(vehicle.id),
            "driver_id": str(driver.id),
            "origin": "Caracas",
            "destination": "Maracaibo",
            "cargo_type": "general",
        },
    )
    trip_id = trip_resp.json()["id"]

    resp = await client.get(f"/api/v1/trips/{trip_id}/documents/loading-order", headers=headers)
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "Orden de Carga" in resp.text
    assert vehicle.plate in resp.text


async def test_expense_receipt_document_renders_html(
    client: AsyncClient, admin_user: User, vehicle: Vehicle, driver: Driver, expense_concept
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    trip_resp = await client.post(
        "/api/v1/trips",
        headers=headers,
        json={
            "vehicle_id": str(vehicle.id),
            "driver_id": str(driver.id),
            "origin": "Caracas",
            "destination": "Maracaibo",
            "cargo_type": "general",
        },
    )
    trip_id = trip_resp.json()["id"]
    await client.post(
        f"/api/v1/trips/{trip_id}/start",
        headers=headers,
        json={"start_odometer_km": vehicle.current_odometer_km},
    )
    await client.post(
        f"/api/v1/trips/{trip_id}/expenses",
        headers=headers,
        json={"concept_id": str(expense_concept.id), "amount": 25.5, "notes": "Diesel"},
    )

    resp = await client.get(f"/api/v1/trips/{trip_id}/documents/expense-receipt", headers=headers)
    assert resp.status_code == 200
    assert "Recibo de Viáticos" in resp.text
    assert "Combustible" in resp.text
    assert "25.5" in resp.text
