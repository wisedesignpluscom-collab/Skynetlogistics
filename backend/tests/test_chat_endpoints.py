from httpx import AsyncClient

from app.models.driver import Driver
from app.models.user import User
from tests.conftest import auth_headers


async def test_driver_opens_general_thread_and_sends_message(
    client: AsyncClient, driver_user: User, driver: Driver
) -> None:
    driver_headers = await auth_headers(client, "conductor@acmetransport.dev", "Conductor123!")
    thread_resp = await client.get("/api/v1/chat/my-thread", headers=driver_headers)
    assert thread_resp.status_code == 200
    thread = thread_resp.json()
    assert thread["driver_id"] == str(driver.id)
    assert thread["incident_report_id"] is None

    same_thread = await client.get("/api/v1/chat/my-thread", headers=driver_headers)
    assert same_thread.json()["id"] == thread["id"]

    msg_resp = await client.post(
        f"/api/v1/chat/threads/{thread['id']}/messages",
        headers=driver_headers,
        json={"message": "Tengo una duda sobre el peaje"},
    )
    assert msg_resp.status_code == 201, msg_resp.text
    assert msg_resp.json()["sender_type"] == "conductor"
    assert msg_resp.json()["sender_id"] == str(driver.id)


async def test_dispatcher_replies_in_driver_thread(
    client: AsyncClient, admin_user: User, driver_user: User
) -> None:
    driver_headers = await auth_headers(client, "conductor@acmetransport.dev", "Conductor123!")
    thread = (await client.get("/api/v1/chat/my-thread", headers=driver_headers)).json()

    admin_headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    reply = await client.post(
        f"/api/v1/chat/threads/{thread['id']}/messages",
        headers=admin_headers,
        json={"message": "Claro, dime"},
    )
    assert reply.status_code == 201
    assert reply.json()["sender_type"] == "despachador"

    messages = await client.get(f"/api/v1/chat/threads/{thread['id']}/messages", headers=driver_headers)
    assert messages.status_code == 200
    assert len(messages.json()) == 1


async def test_driver_cannot_read_another_drivers_thread(
    client: AsyncClient, admin_user: User, driver_user: User, db, company, driver_role
) -> None:
    from app.core.security import hash_password
    from app.models.driver import Driver as DriverModel
    from app.models.user import User as UserModel

    other_driver = DriverModel(company_id=company.id, name="Otro Conductor", license_number="LIC-999")
    from datetime import date

    other_driver.license_expiry = date(2030, 1, 1)
    db.add(other_driver)
    await db.flush()

    other_user = UserModel(
        company_id=company.id,
        role_id=driver_role.id,
        name="Otro Conductor",
        email="otroconductor@acmetransport.dev",
        password_hash=hash_password("Otro12345!"),
    )
    db.add(other_user)
    await db.flush()
    other_driver.user_id = other_user.id
    await db.commit()

    driver_headers = await auth_headers(client, "conductor@acmetransport.dev", "Conductor123!")
    my_thread = (await client.get("/api/v1/chat/my-thread", headers=driver_headers)).json()

    other_headers = await auth_headers(client, "otroconductor@acmetransport.dev", "Otro12345!")
    resp = await client.get(f"/api/v1/chat/threads/{my_thread['id']}/messages", headers=other_headers)
    assert resp.status_code == 403


async def test_incident_report_gets_its_own_thread(client: AsyncClient, admin_user: User, driver_user: User) -> None:
    driver_headers = await auth_headers(client, "conductor@acmetransport.dev", "Conductor123!")
    incident = await client.post(
        "/api/v1/incident-reports",
        headers=driver_headers,
        json={"type": "multa", "severity": "baja", "description": "Multa de tránsito"},
    )
    incident_id = incident.json()["id"]

    admin_headers = await auth_headers(client, "admin@acmetransport.dev", "Sup3rSecret!")
    thread = await client.get(f"/api/v1/chat/incident-reports/{incident_id}/thread", headers=admin_headers)
    assert thread.status_code == 200
    assert thread.json()["incident_report_id"] == incident_id

    general_thread = (await client.get("/api/v1/chat/my-thread", headers=driver_headers)).json()
    assert general_thread["id"] != thread.json()["id"]
