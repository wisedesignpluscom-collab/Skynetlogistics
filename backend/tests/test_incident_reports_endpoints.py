from httpx import AsyncClient

from app.models.company import Company
from app.models.driver import Driver
from app.models.user import User
from tests.conftest import auth_headers


async def test_driver_creates_incident_report(client: AsyncClient, driver_user: User, driver: Driver) -> None:
    headers = await auth_headers(client, "conductor@acmetransport.dev", "Conductor123!")
    resp = await client.post(
        "/api/v1/incident-reports",
        headers=headers,
        json={"type": "averia_mecanica", "severity": "media", "description": "Se rompió una manguera"},
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["driver_id"] == str(driver.id)
    assert body["status"] == "reportado"


async def test_driver_cannot_impersonate_another_driver(
    client: AsyncClient, driver_user: User, driver: Driver
) -> None:
    """El driver_id siempre se deriva del token — el payload no lo acepta, así que no hay campo
    que "falsificar", pero verificamos que el creado quede atado al conductor logueado."""
    headers = await auth_headers(client, "conductor@acmetransport.dev", "Conductor123!")
    resp = await client.post(
        "/api/v1/incident-reports",
        headers=headers,
        json={"type": "multa", "severity": "baja", "description": "Multa por exceso de velocidad"},
    )
    assert resp.status_code == 201
    assert resp.json()["driver_id"] == str(driver.id)


async def test_admin_without_linked_driver_cannot_create_own_report(
    client: AsyncClient, admin_user: User
) -> None:
    headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resp = await client.post(
        "/api/v1/incident-reports",
        headers=headers,
        json={"type": "otro", "severity": "baja", "description": "test"},
    )
    assert resp.status_code == 403


async def test_dispatcher_sees_all_reports_driver_sees_only_own(
    client: AsyncClient, admin_user: User, driver_user: User, driver: Driver
) -> None:
    driver_headers = await auth_headers(client, "conductor@acmetransport.dev", "Conductor123!")
    await client.post(
        "/api/v1/incident-reports",
        headers=driver_headers,
        json={"type": "pernocte", "severity": "baja", "description": "Pernocte no planificado por clima"},
    )

    admin_headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    dispatcher_list = await client.get("/api/v1/incident-reports", headers=admin_headers)
    assert dispatcher_list.status_code == 200
    assert dispatcher_list.json()["total"] == 1

    driver_list = await client.get("/api/v1/incident-reports/mine", headers=driver_headers)
    assert driver_list.status_code == 200
    assert len(driver_list.json()) == 1


async def test_high_severity_report_generates_alert(client: AsyncClient, admin_user: User, driver_user: User) -> None:
    headers = await auth_headers(client, "conductor@acmetransport.dev", "Conductor123!")
    resp = await client.post(
        "/api/v1/incident-reports",
        headers=headers,
        json={"type": "accidente", "severity": "critica", "description": "Colisión en la autopista"},
    )
    assert resp.status_code == 201
    incident_id = resp.json()["id"]

    admin_headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    alerts = await client.get("/api/v1/alerts", headers=admin_headers)
    assert alerts.status_code == 200
    matching = [a for a in alerts.json()["items"] if a["entity_id"] == incident_id]
    assert len(matching) == 1
    assert matching[0]["type"] == "incident_report"
    assert matching[0]["severity"] == "alta"


async def test_low_severity_report_does_not_generate_alert(
    client: AsyncClient, admin_user: User, driver_user: User
) -> None:
    headers = await auth_headers(client, "conductor@acmetransport.dev", "Conductor123!")
    resp = await client.post(
        "/api/v1/incident-reports",
        headers=headers,
        json={"type": "retraso_via", "severity": "baja", "description": "Tráfico pesado"},
    )
    incident_id = resp.json()["id"]

    admin_headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    alerts = await client.get("/api/v1/alerts", headers=admin_headers)
    matching = [a for a in alerts.json()["items"] if a["entity_id"] == incident_id]
    assert matching == []


async def test_dispatcher_resolves_incident_report(client: AsyncClient, admin_user: User, driver_user: User) -> None:
    driver_headers = await auth_headers(client, "conductor@acmetransport.dev", "Conductor123!")
    created = await client.post(
        "/api/v1/incident-reports",
        headers=driver_headers,
        json={"type": "falta_viaticos", "severity": "media", "description": "No recibió anticipo"},
    )
    incident_id = created.json()["id"]

    admin_headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    resolved = await client.patch(
        f"/api/v1/incident-reports/{incident_id}",
        headers=admin_headers,
        json={"status": "resuelto", "resolution_notes": "Se transfirió el anticipo"},
    )
    assert resolved.status_code == 200
    body = resolved.json()
    assert body["status"] == "resuelto"
    assert body["resolved_at"] is not None
    assert body["resolution_notes"] == "Se transfirió el anticipo"


async def test_reports_are_isolated_per_company(
    client: AsyncClient, admin_user: User, driver_user: User, other_company: Company, db, company: Company
) -> None:
    from app.core.security import hash_password
    from app.models.role import Role

    other_role = Role(company_id=other_company.id, name="Admin", permissions={"incidents": ["read"]})
    db.add(other_role)
    await db.flush()
    other_admin = User(
        company_id=other_company.id,
        role_id=other_role.id,
        name="Other Admin",
        email="admin@othercompany.dev",
        password_hash=hash_password("OtherPass1!"),
    )
    db.add(other_admin)
    await db.commit()

    driver_headers = await auth_headers(client, "conductor@acmetransport.dev", "Conductor123!")
    await client.post(
        "/api/v1/incident-reports",
        headers=driver_headers,
        json={"type": "otro", "severity": "baja", "description": "test"},
    )

    other_headers = await auth_headers(client, "admin@othercompany.dev", "OtherPass1!")
    resp = await client.get("/api/v1/incident-reports", headers=other_headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 0
