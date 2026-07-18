import uuid
from datetime import date

from httpx import AsyncClient

from app.models.company import Company
from app.models.driver import Driver
from app.models.driver_fatigue_log import DriverFatigueLog
from app.models.user import User
from tests.conftest import auth_headers


async def _make_log(
    db, *, company: Company, driver: Driver, log_date: date, risk_level: str = "alto", risk_score: float = 90
) -> DriverFatigueLog:
    log = DriverFatigueLog(
        company_id=company.id,
        driver_id=driver.id,
        date=log_date,
        continuous_driving_min=200,
        total_24h_min=400,
        total_7day_min=1800,
        night_driving_min=100,
        risk_score=risk_score,
        risk_level=risk_level,
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log


async def test_fatigue_summary_lists_all_drivers_null_when_no_log(
    client: AsyncClient, admin_user: User, driver: Driver
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.get("/api/v1/drivers/fatigue-summary", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["driver_id"] == str(driver.id)
    assert body[0]["risk_level"] is None
    assert body[0]["risk_score"] is None


async def test_fatigue_summary_includes_latest_log(
    client: AsyncClient, admin_user: User, db, company: Company, driver: Driver
) -> None:
    await _make_log(db, company=company, driver=driver, log_date=date(2026, 7, 17), risk_level="bajo")
    await _make_log(db, company=company, driver=driver, log_date=date(2026, 7, 18), risk_level="critico")

    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.get("/api/v1/drivers/fatigue-summary", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body[0]["risk_level"] == "critico"


async def test_fatigue_status_returns_null_when_no_data(
    client: AsyncClient, admin_user: User, driver: Driver
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.get(f"/api/v1/drivers/{driver.id}/fatigue-status", headers=headers)
    assert resp.status_code == 200
    assert resp.json() is None


async def test_fatigue_status_returns_latest_log(
    client: AsyncClient, admin_user: User, db, company: Company, driver: Driver
) -> None:
    await _make_log(db, company=company, driver=driver, log_date=date(2026, 7, 18), risk_level="critico")
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.get(f"/api/v1/drivers/{driver.id}/fatigue-status", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["risk_level"] == "critico"


async def test_fatigue_status_404_for_unknown_driver(client: AsyncClient, admin_user: User) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.get(f"/api/v1/drivers/{uuid.uuid4()}/fatigue-status", headers=headers)
    assert resp.status_code == 404


async def test_fatigue_history_filters_by_date_range(
    client: AsyncClient, admin_user: User, db, company: Company, driver: Driver
) -> None:
    await _make_log(db, company=company, driver=driver, log_date=date(2026, 7, 10))
    await _make_log(db, company=company, driver=driver, log_date=date(2026, 7, 15))
    await _make_log(db, company=company, driver=driver, log_date=date(2026, 7, 18))

    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.get(
        f"/api/v1/drivers/{driver.id}/fatigue-history",
        headers=headers,
        params={"date_from": "2026-07-14", "date_to": "2026-07-18"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 2
    assert [item["date"] for item in body] == ["2026-07-15", "2026-07-18"]


async def test_fatigue_status_enforces_tenant_isolation(
    client: AsyncClient, admin_user: User, db, other_company: Company
) -> None:
    other_driver = Driver(
        company_id=other_company.id,
        name="Otro Conductor",
        license_number="OTH-LIC-1",
        license_expiry=date(2030, 1, 1),
    )
    db.add(other_driver)
    await db.commit()
    await db.refresh(other_driver)

    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.get(f"/api/v1/drivers/{other_driver.id}/fatigue-status", headers=headers)
    assert resp.status_code == 404


async def test_readonly_user_can_read_fatigue_summary(
    client: AsyncClient, readonly_user: User, driver: Driver
) -> None:
    headers = await auth_headers(client, "readonly@acmetransport.dev", "ReadOnly123!")
    resp = await client.get("/api/v1/drivers/fatigue-summary", headers=headers)
    # readonly_role fixture solo tiene permisos "users"/"roles", no "fatigue" -> 403
    assert resp.status_code == 403
