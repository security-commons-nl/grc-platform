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

TEST_DATABASE_URL = settings.DATABASE_URL.replace("/ims", "/ims_test")


@pytest_asyncio.fixture
async def client():
    """Create a fresh engine + session factory per test — avoids event loop conflicts."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Truncate all tables before test
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

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
    await engine.dispose()


@pytest_asyncio.fixture
async def test_tenant(client):
    response = await client.post(
        "/api/v1/tenants/",
        json={"name": "Gemeente Leiden", "type": "centrum"},
    )
    assert response.status_code == 201, f"Failed to create tenant: {response.text}"
    return response.json()


@pytest_asyncio.fixture
async def test_region(client, test_tenant):
    response = await client.post(
        "/api/v1/tenants/regions/",
        json={"name": "Leidse Regio", "centrum_tenant_id": test_tenant["id"]},
    )
    assert response.status_code == 201, f"Failed to create region: {response.text}"
    return response.json()


@pytest_asyncio.fixture
async def test_user(client, test_tenant):
    response = await client.post(
        "/api/v1/tenants/users/",
        json={
            "name": "Test User",
            "email": "test@leiden.nl",
            "external_id": f"test-ext-{uuid.uuid4().hex[:8]}",
            "tenant_id": test_tenant["id"],
        },
    )
    assert response.status_code == 201, f"Failed to create user: {response.text}"
    return response.json()
