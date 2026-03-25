import uuid
import pytest
from httpx import AsyncClient
from datetime import datetime
from tests.conftest import make_token


@pytest.mark.asyncio
async def test_create_decision(client: AsyncClient, test_tenant, tenant_token):
    response = await client.post(
        "/api/v1/decisions/",
        json={
            "number": "B-001",
            "decision_type": "normaal",
            "content": "Scope vastgesteld voor ISMS",
            "grondslag": "ISO 27001:2022 §4.3",
            "gremium": "sims",
            "decided_by_name": "Test User",
            "decided_by_role": "SIMS-voorzitter",
            "decided_at": datetime.utcnow().isoformat(),
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["number"] == "B-001"
    assert data["decision_type"] == "normaal"
    assert data["gremium"] == "sims"


@pytest.mark.asyncio
async def test_create_restrisico_acceptatie_sims(client: AsyncClient, test_tenant, tenant_token):
    response = await client.post(
        "/api/v1/decisions/",
        json={
            "number": "B-002",
            "decision_type": "restrisico_acceptatie",
            "content": "Restrisico aanvaard",
            "grondslag": "Risk assessment",
            "gremium": "sims",
            "decided_by_name": "SIMS Chair",
            "decided_by_role": "SIMS-voorzitter",
            "decided_at": datetime.utcnow().isoformat(),
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 201
    assert response.json()["decision_type"] == "restrisico_acceptatie"


@pytest.mark.asyncio
async def test_reject_restrisico_wrong_gremium(client: AsyncClient, test_tenant, tenant_token):
    response = await client.post(
        "/api/v1/decisions/",
        json={
            "number": "B-003",
            "decision_type": "restrisico_acceptatie",
            "content": "Restrisico aanvaard",
            "grondslag": "Risk assessment",
            "gremium": "tims",
            "decided_by_name": "TIMS member",
            "decided_by_role": "TIMS-lid",
            "decided_at": datetime.utcnow().isoformat(),
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 422
    assert "SIMS" in response.json()["detail"]


@pytest.mark.asyncio
async def test_reject_beleidsafwijking_wrong_gremium(client: AsyncClient, test_tenant, tenant_token):
    response = await client.post(
        "/api/v1/decisions/",
        json={
            "number": "B-004",
            "decision_type": "beleidsafwijking",
            "content": "Afwijking van beleid",
            "grondslag": "Beleid X",
            "gremium": "lijnmanagement",
            "decided_by_name": "Manager",
            "decided_by_role": "Lijnmanager",
            "decided_at": datetime.utcnow().isoformat(),
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_decision_immutability_no_patch(client: AsyncClient, test_tenant, tenant_token):
    """Verify there is no PATCH endpoint for decisions."""
    create_resp = await client.post(
        "/api/v1/decisions/",
        json={
            "number": "B-005",
            "decision_type": "normaal",
            "content": "Test immutability",
            "grondslag": "Test",
            "gremium": "sims",
            "decided_by_name": "User",
            "decided_by_role": "Admin",
            "decided_at": datetime.utcnow().isoformat(),
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    decision_id = create_resp.json()["id"]

    response = await client.patch(
        f"/api/v1/decisions/{decision_id}",
        json={"content": "Modified"},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    # Should return 405 Method Not Allowed or 404 (no route matches)
    assert response.status_code in (404, 405)


@pytest.mark.asyncio
async def test_decision_immutability_no_delete(client: AsyncClient, test_tenant, tenant_token):
    """Verify there is no DELETE endpoint for decisions."""
    create_resp = await client.post(
        "/api/v1/decisions/",
        json={
            "number": "B-006",
            "decision_type": "normaal",
            "content": "Test immutability delete",
            "grondslag": "Test",
            "gremium": "sims",
            "decided_by_name": "User",
            "decided_by_role": "Admin",
            "decided_at": datetime.utcnow().isoformat(),
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    decision_id = create_resp.json()["id"]

    response = await client.delete(
        f"/api/v1/decisions/{decision_id}",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code in (404, 405)


@pytest.mark.asyncio
async def test_supersedes_chain(client: AsyncClient, test_tenant, tenant_token):
    first_resp = await client.post(
        "/api/v1/decisions/",
        json={
            "number": "B-010",
            "decision_type": "normaal",
            "content": "Eerste besluit",
            "grondslag": "Test",
            "gremium": "sims",
            "decided_by_name": "User",
            "decided_by_role": "Admin",
            "decided_at": datetime.utcnow().isoformat(),
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    first_id = first_resp.json()["id"]

    second_resp = await client.post(
        "/api/v1/decisions/",
        json={
            "number": "B-011",
            "decision_type": "normaal",
            "content": "Vervangt B-010",
            "grondslag": "Test",
            "gremium": "sims",
            "decided_by_name": "User",
            "decided_by_role": "Admin",
            "decided_at": datetime.utcnow().isoformat(),
            "supersedes_id": first_id,
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert second_resp.status_code == 201
    assert second_resp.json()["supersedes_id"] == first_id


@pytest.mark.asyncio
async def test_list_decisions(client: AsyncClient, test_tenant, tenant_token):
    response = await client.get(
        "/api/v1/decisions/",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_decision_not_found(client: AsyncClient, admin_token):
    response = await client.get(
        f"/api/v1/decisions/{uuid.uuid4()}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404
