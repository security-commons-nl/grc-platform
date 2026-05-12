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
from app.core.rate_limit import limiter

TEST_DATABASE_URL = settings.DATABASE_URL.replace("/ims", "/ims_test")


@pytest_asyncio.fixture(autouse=True)
async def reset_rate_limiter():
    """Default: rate limiting OFF in tests so the 105+ existing tests
    can freely hammer endpoints. Tests that specifically verify rate-
    limit behaviour (test_rate_limit.py) re-enable the limiter via the
    `with_rate_limit` fixture."""
    limiter.reset()
    original_enabled = limiter.enabled
    limiter.enabled = False
    yield
    limiter.enabled = original_enabled
    limiter.reset()


@pytest_asyncio.fixture(scope="session")
async def engine():
    eng = create_async_engine(TEST_DATABASE_URL, echo=False, pool_size=5)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture(autouse=True)
async def clean_tables(engine):
    async with engine.begin() as conn:
        # Truncate user/tenant data but NOT reference data (ims_steps, ims_step_dependencies, ims_step_outputs, ims_standards)
        # Clean tenant/user data but preserve reference data:
        # - ims_standards (seeded by migration 003 + 011)
        # - ims_requirements van NIST RMF (seeded by migration 011)
        # TRUNCATE eerst — CASCADE haalt ims_controls.requirement_id-verwijzingen
        # weg, daarna kunnen requirements veilig met DELETE worden opgeschoond.
        await conn.execute(text(
            "TRUNCATE TABLE "
            "agent_messages, agent_conversations, "
            "ai_hitl_checkpoints, ai_audit_logs, ims_ai_systems, ims_gap_analysis_results, ims_step_input_documents, "
            "ims_knowledge_chunks, ims_grc_scores, ims_setup_scores, ims_maturity_profiles, "
            "ims_incidents, ims_evidence, ims_corrective_actions, ims_findings, "
            "ims_assessments, ims_risk_simulations, ims_risk_control_links, ims_controls, ims_risks, ims_scopes, "
            "ims_custom_field_definitions, "
            "ims_organizational_units, "
            "ims_standard_ingestions, ims_tenant_normenkader, "
            "ims_document_versions, ims_documents, "
            "ims_step_output_fulfillments, ims_decisions, ims_step_executions, "
            "user_region_roles, user_tenant_roles, users, tenants, regions "
            "CASCADE"
        ))
        await conn.execute(text("DELETE FROM ims_requirement_mappings"))
        await conn.execute(text(
            "DELETE FROM ims_requirements WHERE standard_id NOT IN "
            "(SELECT id FROM ims_standards WHERE name = 'NIST AI RMF')"
        ))
        # Clean up test-created steps AFTER truncating FKs (executions, fulfillments, etc.)
        await conn.execute(text(
            "DELETE FROM ims_step_outputs WHERE step_id IN "
            "(SELECT id FROM ims_steps WHERE name LIKE 'Agent Test%' OR name LIKE 'Test Step%')"
        ))
        await conn.execute(text(
            "DELETE FROM ims_step_dependencies WHERE step_id IN "
            "(SELECT id FROM ims_steps WHERE name LIKE 'Agent Test%' OR name LIKE 'Test Step%') "
            "OR depends_on_step_id IN "
            "(SELECT id FROM ims_steps WHERE name LIKE 'Agent Test%' OR name LIKE 'Test Step%')"
        ))
        await conn.execute(text(
            "DELETE FROM ims_steps WHERE name LIKE 'Agent Test%' OR name LIKE 'Test Step%'"
        ))
    yield


def make_token(user_id=None, tenant_id=None, role="admin", domain=None,
               token_type="user", agent_name=None, scope=None, ai_system_id=None):
    """Helper to create JWT tokens for tests."""
    payload = {
        "sub": str(user_id or uuid.uuid4()),
        "tenant_id": str(tenant_id or uuid.uuid4()),
        "role": role,
        "domain": domain,
        "token_type": token_type,
        "agent_name": agent_name,
    }
    if scope is not None:
        payload["scope"] = scope
    if ai_system_id is not None:
        payload["ai_system_id"] = str(ai_system_id)
    return create_token(payload)


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
        json={"name": "Voorbeeldgemeente", "type": "centrum"},
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
        json={"name": "Voorbeeldregio", "centrum_tenant_id": test_tenant["id"]},
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
            "email": "test@ims.dev",
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


@pytest_asyncio.fixture
async def user_token(test_user):
    """A token tied to a user that ACTUALLY exists in the users table.

    Use this when a test calls an endpoint that inserts a foreign key
    reference to users (e.g. AI HITL checkpoints, where reviewer_user_id
    must exist). Most tests can use tenant_token, but FK-creating
    endpoints need a real user."""
    return make_token(
        user_id=test_user["id"],
        tenant_id=test_user["tenant_id"],
        role="admin",
    )
