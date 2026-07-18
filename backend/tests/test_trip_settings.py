from httpx import AsyncClient

from app.models.company_holiday import CompanyHoliday
from app.models.driver_pay_rate import DriverPayRate
from app.models.expense_concept import ExpenseConcept
from app.models.rate_table import RateTable
from app.models.user import User
from tests.conftest import auth_headers


async def test_admin_creates_rate_table(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/rate-tables",
        headers=headers,
        json={
            "origin": "Caracas",
            "destination": "Valencia",
            "vehicle_type": "camion",
            "cargo_type": "general",
            "distance_km": 180,
            "freight_amount": 300,
        },
    )
    assert resp.status_code == 201
    assert resp.json()["freight_amount"] == 300.0


async def test_duplicate_rate_table_route_conflicts(
    client: AsyncClient, admin_user: User, rate_table: RateTable
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/rate-tables",
        headers=headers,
        json={
            "origin": rate_table.origin,
            "destination": rate_table.destination,
            "vehicle_type": rate_table.vehicle_type,
            "cargo_type": rate_table.cargo_type,
            "distance_km": 1,
            "freight_amount": 1,
        },
    )
    assert resp.status_code == 409


async def test_readonly_user_cannot_create_rate_table(client: AsyncClient, readonly_user: User) -> None:
    headers = await auth_headers(client, "readonly@acmetransport.dev", "ReadOnly123!")
    resp = await client.post(
        "/api/v1/rate-tables",
        headers=headers,
        json={
            "origin": "A",
            "destination": "B",
            "vehicle_type": "camion",
            "cargo_type": "general",
            "distance_km": 1,
            "freight_amount": 1,
        },
    )
    assert resp.status_code == 403


async def test_admin_creates_driver_pay_rate(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/driver-pay-rates",
        headers=headers,
        json={
            "vehicle_type": "cabezal",
            "daily_base_rate": 60,
            "meal_allowance_per_day": 20,
            "holiday_bonus_rate": 35,
            "return_bonus_rate": 45,
        },
    )
    assert resp.status_code == 201


async def test_duplicate_driver_pay_rate_vehicle_type_conflicts(
    client: AsyncClient, admin_user: User, driver_pay_rate: DriverPayRate
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/driver-pay-rates",
        headers=headers,
        json={"vehicle_type": "camion", "daily_base_rate": 1},
    )
    assert resp.status_code == 409


async def test_admin_creates_and_deletes_holiday(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/holidays", headers=headers, json={"date": "2026-12-25", "name": "Navidad"}
    )
    assert resp.status_code == 201
    holiday_id = resp.json()["id"]

    delete_resp = await client.delete(f"/api/v1/holidays/{holiday_id}", headers=headers)
    assert delete_resp.status_code == 204


async def test_admin_creates_expense_concept(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/expense-concepts", headers=headers, json={"name": "Peaje", "default_limit": 20}
    )
    assert resp.status_code == 201


async def test_duplicate_expense_concept_name_conflicts(
    client: AsyncClient, admin_user: User, expense_concept: ExpenseConcept
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/expense-concepts", headers=headers, json={"name": expense_concept.name}
    )
    assert resp.status_code == 409
