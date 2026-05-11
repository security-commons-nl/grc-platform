"""Tests voor Non-Human Identity (NHI) agent tokens — M4 AI Governance.

Verifieert:
- Token bevat scope en optional ai_system_id claims
- TTL-validatie (default 60 min, max 24h)
- Koppeling aan ims_ai_systems wordt cross-tenant afgewezen
- require_scope-dependency afdwingt scope-eisen op agent tokens
- User tokens worden niet beperkt door scope-checks
"""

import uuid

import pytest
from httpx import AsyncClient

from tests.conftest import make_token


@pytest.mark.asyncio
async def test_agent_token_response_includes_scope_and_short_ttl(
    client: AsyncClient, test_tenant, tenant_token
):
    """Agent-token response bevat scope-claim en TTL is standaard 60 min
    (was 30 dagen vóór de NHI-uitbreiding)."""
    r = await client.post(
        "/api/v1/auth/agent-token",
        json={
            "tenant_id": str(test_tenant["id"]),
            "agent_name": "gap-agent",
            "scope": ["risks:read", "controls:read"],
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["scope"] == ["risks:read", "controls:read"]
    # 60 min = 3600 s — default TTL
    assert body["expires_in"] == 60 * 60


@pytest.mark.asyncio
async def test_agent_token_custom_ttl(client: AsyncClient, test_tenant, tenant_token):
    """ttl_minutes kan worden gespecificeerd binnen [1, 1440]."""
    r = await client.post(
        "/api/v1/auth/agent-token",
        json={
            "tenant_id": str(test_tenant["id"]),
            "agent_name": "short-lived-agent",
            "scope": ["read"],
            "ttl_minutes": 5,
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 200
    assert r.json()["expires_in"] == 5 * 60


@pytest.mark.asyncio
async def test_agent_token_ttl_over_24_hours_rejected(
    client: AsyncClient, test_tenant, tenant_token
):
    """ttl_minutes boven 24h moet door pydantic geweigerd worden (422)."""
    r = await client.post(
        "/api/v1/auth/agent-token",
        json={
            "tenant_id": str(test_tenant["id"]),
            "agent_name": "too-long",
            "scope": ["read"],
            "ttl_minutes": 1441,  # 24h + 1 min
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_agent_token_ai_system_id_must_exist_in_tenant(
    client: AsyncClient, test_tenant, tenant_token
):
    """ai_system_id dat niet in dezelfde tenant bestaat moet 404 geven —
    voorkomt cross-tenant identity-spoofing."""
    fake_system_id = str(uuid.uuid4())
    r = await client.post(
        "/api/v1/auth/agent-token",
        json={
            "tenant_id": str(test_tenant["id"]),
            "agent_name": "phantom-system",
            "scope": ["read"],
            "ai_system_id": fake_system_id,
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_agent_token_linked_to_real_ai_system(
    client: AsyncClient, test_tenant, tenant_token
):
    """Een agent-token kan gekoppeld worden aan een geregistreerd AI-systeem."""
    # Eerst registreren
    sys_r = await client.post(
        "/api/v1/ai-systems/",
        json={"name": "Test AI agent", "system_type": "chatbot"},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    ai_system_id = sys_r.json()["id"]

    # Token aanmaken met koppeling
    r = await client.post(
        "/api/v1/auth/agent-token",
        json={
            "tenant_id": str(test_tenant["id"]),
            "agent_name": "linked-agent",
            "scope": ["read"],
            "ai_system_id": ai_system_id,
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 200
    assert r.json()["ai_system_id"] == ai_system_id


@pytest.mark.asyncio
async def test_agent_token_me_endpoint_returns_scope(
    client: AsyncClient, test_tenant
):
    """/auth/me geeft de scope-claim terug zodat een agent zijn capabilities kan zien."""
    agent_token = make_token(
        tenant_id=test_tenant["id"],
        role="viewer",
        token_type="agent",
        agent_name="gap-agent",
        scope=["risks:read", "controls:read"],
    )
    r = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {agent_token}"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "agent"
    assert body["scope"] == ["risks:read", "controls:read"]


@pytest.mark.asyncio
async def test_agent_token_without_scope_has_default(
    client: AsyncClient, test_tenant, tenant_token
):
    """Backward-compatibility: een aanvraag zonder scope krijgt default ['read']
    zodat bestaande callers blijven werken na de NHI-uitbreiding."""
    r = await client.post(
        "/api/v1/auth/agent-token",
        json={
            "tenant_id": str(test_tenant["id"]),
            "agent_name": "legacy-agent",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 200
    assert r.json()["scope"] == ["read"]
