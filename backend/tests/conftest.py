import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.main import app
from app.core.db import get_db
from app.core.config import settings
from app.models.core_models import Base

# Use test database
TEST_DATABASE_URL = settings.DATABASE_URL.replace("/ims", "/ims_test")

engine_test = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine_test.dispose()


@pytest_asyncio.fixture
async def db_session():
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_tenant(client):
    response = await client.post(
        "/api/v1/tenants/",
        json={"name": "Gemeente Leiden", "type": "centrum"},
    )
    return response.json()


@pytest_asyncio.fixture
async def test_region(client, test_tenant):
    response = await client.post(
        "/api/v1/tenants/regions/",
        json={"name": "Leidse Regio", "centrum_tenant_id": test_tenant["id"]},
    )
    return response.json()


@pytest_asyncio.fixture
async def test_user(client, test_tenant):
    import uuid
    response = await client.post(
        "/api/v1/tenants/users/",
        json={
            "name": "Test User",
            "email": "test@leiden.nl",
            "external_id": f"test-ext-{uuid.uuid4().hex[:8]}",
            "tenant_id": test_tenant["id"],
        },
    )
    return response.json()
