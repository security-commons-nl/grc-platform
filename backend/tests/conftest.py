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
    """
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

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
        "name": "Test Measure",
        "description": "A test measure for unit testing",
        "implementation_guidance": "Implementation steps here",
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


@pytest.fixture
def sample_standard_data() -> dict:
    """Sample standard data for testing."""
    return {
        "name": "Test Standard",
        "version": "1.0",
        "type": "BIO",
        "description": "A test standard for unit testing",
    }


@pytest.fixture
def sample_requirement_data() -> dict:
    """Sample requirement data for testing."""
    return {
        "code": "REQ-001",
        "title": "Test Requirement",
        "description": "A test requirement for unit testing",
        "guidance": "Test guidance",
    }


@pytest.fixture
def sample_control_data() -> dict:
    """Sample control data for testing."""
    return {
        "tenant_id": 1,
        "title": "Test Control",
        "description": "A test control for unit testing",
        "control_type": "Preventive",
        "automation_level": "Manual",
    }
