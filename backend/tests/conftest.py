"""
Pytest configuration and fixtures for IMS backend tests.

Uses an in-memory SQLite database for fast, isolated tests.
For integration tests with PostgreSQL, use a separate test database.
"""
import asyncio
from typing import AsyncGenerator, Generator
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.main import app
from app.core.db import get_session
from app.core.rbac import get_current_user, get_tenant_id, get_scope_access, require_editor, require_admin, require_coordinator_or_admin, require_configurer, require_oversight
from app.models.core_models import User


# Test database URL (SQLite in-memory for speed)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
)

# Test session factory
TestSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh database session for each test.

    Creates all tables before the test and drops them after.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create an async HTTP client for API testing.

    Overrides the database session dependency to use the test database.
    Auth dependencies are bypassed with a fake superuser (tenant_id=1).
    """
    async def override_get_session():
        yield db_session

    # Fake superuser for all tests — bypasses JWT and DB user lookup
    _fake_user = User(
        id=1,
        email="test@ims.local",
        hashed_password="x",
        is_active=True,
        is_superuser=True,
        full_name="Test User",
        tenant_id=1,
    )

    async def override_get_current_user():
        return _fake_user

    async def override_get_tenant_id():
        return 1

    async def override_get_scope_access():
        return None  # superuser: no restriction

    async def override_require_role():
        return _fake_user

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_tenant_id] = override_get_tenant_id
    app.dependency_overrides[get_scope_access] = override_get_scope_access
    app.dependency_overrides[require_editor] = override_require_role
    app.dependency_overrides[require_admin] = override_require_role
    app.dependency_overrides[require_coordinator_or_admin] = override_require_role
    app.dependency_overrides[require_configurer] = override_require_role
    app.dependency_overrides[require_oversight] = override_require_role

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def tenant_headers() -> dict:
    """Default headers including tenant ID for multi-tenant tests."""
    return {"X-Tenant-ID": "1"}


@pytest.fixture
def sample_risk_data() -> dict:
    """Sample risk data for testing."""
    return {
        "tenant_id": 1,
        "title": "Test Risk",
        "description": "A test risk for unit testing",
        "inherent_likelihood": "MEDIUM",
        "inherent_impact": "HIGH",
    }


@pytest.fixture
def sample_measure_data() -> dict:
    """Sample measure data for testing."""
    return {
        "tenant_id": 1,
        "title": "Test Measure",
        "description": "A test measure for unit testing",
        "implementation_details": "Implementation steps here",
    }


@pytest.fixture
def sample_policy_data() -> dict:
    """Sample policy data for testing."""
    return {
        "tenant_id": 1,
        "title": "Test Policy",
        "content": "This is a test policy document.",
    }


@pytest.fixture
def sample_tenant_data() -> dict:
    """Sample tenant data for testing."""
    return {
        "name": "Test Tenant",
        "slug": "test-tenant",
        "is_active": True,
    }
