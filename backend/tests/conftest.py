import sys
import os
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.main import app
from app.core.db import get_db
from app.core.config import settings
from app.core.auth import create_token

TEST_DATABASE_URL = settings.DATABASE_URL.replace("/ims", "/ims_test")


@pytest_asyncio.fixture(scope="session")
async def engine():
    eng = create_async_engine(TEST_DATABASE_URL, echo=False, pool_size=5)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture(autouse=True)
async def clean_tables(engine):
    async with engine.begin() as conn:
        await conn.execute(text(
            "TRUNCATE TABLE "
            "ai_audit_logs, ims_gap_analysis_results, ims_step_input_documents, "
            "ims_knowledge_chunks, ims_grc_scores, ims_setup_scores, ims_maturity_profiles, "
            "ims_incidents, ims_evidence, ims_corrective_actions, ims_findings, "
            "ims_assessments, ims_risk_control_links, ims_controls, ims_risks, ims_scopes, "
            "ims_standard_ingestions, ims_tenant_normenkader, ims_requirement_mappings, "
            "ims_requirements, ims_standards, ims_document_versions, ims_documents, "
            "ims_decisions, ims_step_executions, ims_step_dependencies, ims_steps, "
            "user_region_roles, user_tenant_roles, users, tenants, regions "
            "CASCADE"
        ))
    yield


def make_token(user_id=None, tenant_id=None, role="admin", domain=None, token_type="user", agent_name=None):
    """Helper to create JWT tokens for tests."""
    return create_token({
        "sub": str(user_id or uuid.uuid4()),
        "tenant_id": str(tenant_id or uuid.uuid4()),
        "role": role,
        "domain": domain,
        "token_type": token_type,
        "agent_name": agent_name,
    })


@pytest_asyncio.fixture
async def client(engine):
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            async with session.begin():
                yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_token():
    """A token with admin role and a fixed tenant_id for testing."""
    return make_token(role="admin")


@pytest_asyncio.fixture
async def test_tenant(client, admin_token):
    response = await client.post(
        "/api/v1/tenants/",
        json={"name": "Gemeente Leiden", "type": "centrum"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201, f"Failed to create tenant: {response.text}"
    return response.json()


@pytest_asyncio.fixture
async def tenant_token(test_tenant):
    """A token with admin role tied to the test tenant."""
    return make_token(tenant_id=test_tenant["id"], role="admin")


@pytest_asyncio.fixture
async def test_region(client, test_tenant, tenant_token):
    response = await client.post(
        "/api/v1/tenants/regions/",
        json={"name": "Leidse Regio", "centrum_tenant_id": test_tenant["id"]},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 201, f"Failed to create region: {response.text}"
    return response.json()


@pytest_asyncio.fixture
async def test_user(client, test_tenant, tenant_token):
    response = await client.post(
        "/api/v1/tenants/users/",
        json={
            "name": "Test User",
            "email": "test@leiden.nl",
            "external_id": f"test-ext-{uuid.uuid4().hex[:8]}",
            "tenant_id": test_tenant["id"],
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 201, f"Failed to create user: {response.text}"
    return response.json()


@pytest_asyncio.fixture
async def viewer_token(test_tenant):
    """A token with viewer role (read-only)."""
    return make_token(tenant_id=test_tenant["id"], role="viewer")
