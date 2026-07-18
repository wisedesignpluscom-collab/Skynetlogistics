from collections.abc import AsyncGenerator
from datetime import date

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models.company import Company
from app.models.driver import Driver
from app.models.provider import Provider
from app.models.role import Role
from app.models.user import User
from app.models.vehicle import Vehicle
from app.utils.permissions import DEFAULT_ADMIN_PERMISSIONS, SUPERADMIN_PERMISSIONS

TEST_DATABASE_URL = "postgresql+asyncpg://fleet:fleet_dev_pw@localhost:5432/fleet_test_db"

engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


@pytest_asyncio.fixture(autouse=True)
async def _clean_db() -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())
    yield


@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async def _get_db_override() -> AsyncGenerator[AsyncSession, None]:
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = _get_db_override
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def company(db: AsyncSession) -> Company:
    c = Company(name="Acme Transport", tax_id="ACME-001", plan="pro")
    db.add(c)
    await db.commit()
    await db.refresh(c)
    return c


@pytest_asyncio.fixture
async def other_company(db: AsyncSession) -> Company:
    c = Company(name="Other Fleet Co", tax_id="OTHER-001", plan="basic")
    db.add(c)
    await db.commit()
    await db.refresh(c)
    return c


@pytest_asyncio.fixture
async def admin_role(db: AsyncSession, company: Company) -> Role:
    r = Role(company_id=company.id, name="Admin", permissions=DEFAULT_ADMIN_PERMISSIONS)
    db.add(r)
    await db.commit()
    await db.refresh(r)
    return r


@pytest_asyncio.fixture
async def readonly_role(db: AsyncSession, company: Company) -> Role:
    r = Role(
        company_id=company.id,
        name="ReadOnly",
        permissions={"users": ["read"], "roles": ["read"]},
    )
    db.add(r)
    await db.commit()
    await db.refresh(r)
    return r


@pytest_asyncio.fixture
async def admin_user(db: AsyncSession, company: Company, admin_role: Role) -> User:
    u = User(
        company_id=company.id,
        role_id=admin_role.id,
        name="Admin User",
        email="admin@acmetransport.dev",
        password_hash=hash_password("Sup3rSecret!"),
    )
    db.add(u)
    await db.commit()
    await db.refresh(u)
    return u


@pytest_asyncio.fixture
async def readonly_user(db: AsyncSession, company: Company, readonly_role: Role) -> User:
    u = User(
        company_id=company.id,
        role_id=readonly_role.id,
        name="Readonly User",
        email="readonly@acmetransport.dev",
        password_hash=hash_password("ReadOnly123!"),
    )
    db.add(u)
    await db.commit()
    await db.refresh(u)
    return u


@pytest_asyncio.fixture
async def superadmin_user(db: AsyncSession) -> User:
    platform = Company(name="Platform", tax_id="PLATFORM-TEST", plan="platform")
    db.add(platform)
    await db.flush()
    role = Role(
        company_id=platform.id, name="Superadmin", permissions=SUPERADMIN_PERMISSIONS, is_system=True
    )
    db.add(role)
    await db.flush()
    u = User(
        company_id=platform.id,
        role_id=role.id,
        name="Root",
        email="root@platformfleet.dev",
        password_hash=hash_password("RootPass1!"),
        is_superadmin=True,
    )
    db.add(u)
    await db.commit()
    await db.refresh(u)
    return u


@pytest_asyncio.fixture
async def driver(db: AsyncSession, company: Company) -> Driver:
    d = Driver(
        company_id=company.id,
        name="Juan Pérez",
        license_number="LIC-001",
        license_expiry=date(2030, 1, 1),
    )
    db.add(d)
    await db.commit()
    await db.refresh(d)
    return d


@pytest_asyncio.fixture
async def vehicle(db: AsyncSession, company: Company) -> Vehicle:
    v = Vehicle(
        company_id=company.id,
        plate="ABC-123",
        brand="Volvo",
        model="FH16",
        year=2022,
        type="camion",
        current_odometer_km=10_000,
    )
    db.add(v)
    await db.commit()
    await db.refresh(v)
    return v


@pytest_asyncio.fixture
async def provider(db: AsyncSession, company: Company) -> Provider:
    p = Provider(company_id=company.id, name="Taller Central", type="taller")
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p


async def login(client: AsyncClient, email: str, password: str) -> dict:
    resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()


async def auth_headers(client: AsyncClient, email: str, password: str) -> dict[str, str]:
    tokens = await login(client, email, password)
    return {"Authorization": f"Bearer {tokens['access_token']}"}
