import uuid
import pytest
from httpx import AsyncClient
from tests.conftest import make_token


@pytest.mark.asyncio
async def test_dev_token(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/dev-token",
        json={
            "user_id": str(uuid.uuid4()),
            "tenant_id": str(uuid.uuid4()),
            "role": "admin",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_me_authenticated(client: AsyncClient):
    token = make_token(role="tims_lid")
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "tims_lid"


@pytest.mark.asyncio
async def test_me_unauthenticated(client: AsyncClient):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_role_hierarchy(client: AsyncClient, test_tenant, tenant_token):
    """Admin can do everything that lower roles can do."""
    # Admin can list risks (viewer-level)
    response = await client.get(
        "/api/v1/risks/",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_viewer_cannot_create(client: AsyncClient, test_tenant, viewer_token):
    """Viewer should not be able to create resources."""
    response = await client.post(
        "/api/v1/scopes/",
        json={"name": "Test Scope", "type": "cluster", "domain": "ISMS"},
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_agent_token_requires_admin(client: AsyncClient, test_tenant):
    """Only admins can create agent tokens."""
    viewer_token = make_token(tenant_id=test_tenant["id"], role="viewer")
    response = await client.post(
        "/api/v1/auth/agent-token",
        json={"tenant_id": str(test_tenant["id"]), "agent_name": "gap-agent"},
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_invalid_token(client: AsyncClient):
    response = await client.get(
        "/api/v1/risks/",
        headers={"Authorization": "Bearer invalid-token-here"},
    )
    assert response.status_code == 401
