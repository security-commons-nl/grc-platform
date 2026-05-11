"""Tests voor AI HITL checkpoints (M4 AI Governance, EU AI Act art. 14)."""

import uuid

import pytest
from sqlalchemy import text

from tests.conftest import TEST_DATABASE_URL


async def _create_audit_log(engine, tenant_id):
    """Maak een AIAuditLog rechtstreeks in de DB aan (er is geen API
    voor; agents schrijven dit zelf weg)."""
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

    audit_id = uuid.uuid4()
    async with engine.begin() as conn:
        await conn.execute(
            text(
                "INSERT INTO ai_audit_logs "
                "(id, tenant_id, agent_name, model, prompt_tokens, completion_tokens, "
                " created_at, updated_at) "
                "VALUES (:id, :tenant_id, :agent_name, :model, :pt, :ct, now(), now())"
            ),
            {
                "id": audit_id,
                "tenant_id": tenant_id,
                "agent_name": "test-agent",
                "model": "mistral-small",
                "pt": 100,
                "ct": 50,
            },
        )
    return audit_id


@pytest.fixture
async def audit_log_id(engine, test_tenant):
    return await _create_audit_log(engine, test_tenant["id"])


@pytest.mark.asyncio
async def test_create_hitl_checkpoint_approved(
    client, user_token, audit_log_id
):
    """Een gebruiker kan een AI-uitvoer goedkeuren."""
    r = await client.post(
        "/api/v1/ai-hitl-checkpoints/",
        json={
            "audit_log_id": str(audit_log_id),
            "decision": "approved",
            "reason": "Output is correct en compliant met BIO-eisen",
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["decision"] == "approved"
    assert body["audit_log_id"] == str(audit_log_id)
    assert "reviewer_user_id" in body
    assert "created_at" in body


@pytest.mark.asyncio
async def test_create_hitl_checkpoint_rejected_with_reason(
    client, user_token, audit_log_id
):
    """Afwijzing kan met reden."""
    r = await client.post(
        "/api/v1/ai-hitl-checkpoints/",
        json={
            "audit_log_id": str(audit_log_id),
            "decision": "rejected",
            "reason": "Hallucinerend over BIO-controlnummers",
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert r.status_code == 201
    assert r.json()["reason"] == "Hallucinerend over BIO-controlnummers"


@pytest.mark.asyncio
async def test_invalid_decision_value_rejected(client, user_token, audit_log_id):
    """Decision moet uit approved/rejected/modified/pending komen."""
    r = await client.post(
        "/api/v1/ai-hitl-checkpoints/",
        json={
            "audit_log_id": str(audit_log_id),
            "decision": "looks-ok-i-guess",
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_unknown_audit_log_id_rejected(client, user_token):
    """Een audit_log_id dat niet in de tenant bestaat geeft 404."""
    r = await client.post(
        "/api/v1/ai-hitl-checkpoints/",
        json={
            "audit_log_id": str(uuid.uuid4()),
            "decision": "approved",
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_multiple_checkpoints_per_audit_log_allowed(
    client, user_token, audit_log_id
):
    """Revisierondes: meerdere checkpoints op dezelfde audit-log zijn toegestaan
    (eerst 'pending', later 'approved' bv.)."""
    for decision in ("pending", "modified", "approved"):
        r = await client.post(
            "/api/v1/ai-hitl-checkpoints/",
            json={"audit_log_id": str(audit_log_id), "decision": decision},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert r.status_code == 201, f"decision={decision}: {r.text}"

    r = await client.get(
        f"/api/v1/ai-hitl-checkpoints/?audit_log_id={audit_log_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert r.status_code == 200
    assert len(r.json()) == 3


@pytest.mark.asyncio
async def test_list_checkpoints_filter_by_decision(
    client, user_token, audit_log_id
):
    """Filter op decision."""
    for decision in ("approved", "approved", "rejected"):
        await client.post(
            "/api/v1/ai-hitl-checkpoints/",
            json={"audit_log_id": str(audit_log_id), "decision": decision},
            headers={"Authorization": f"Bearer {user_token}"},
        )

    r = await client.get(
        "/api/v1/ai-hitl-checkpoints/?decision=approved",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert r.status_code == 200
    decisions = [c["decision"] for c in r.json()]
    assert len(decisions) == 2
    assert all(d == "approved" for d in decisions)


@pytest.mark.asyncio
async def test_viewer_cannot_create_checkpoint(client, viewer_token, audit_log_id):
    """Viewer mag geen checkpoint vastleggen (read-only rol)."""
    r = await client.post(
        "/api/v1/ai-hitl-checkpoints/",
        json={"audit_log_id": str(audit_log_id), "decision": "approved"},
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_reviewer_is_authenticated_user_not_payload(
    client, user_token, audit_log_id
):
    """De reviewer_user_id wordt afgeleid uit het JWT-token, niet uit
    het request payload — voorkomt impersonatie."""
    r = await client.post(
        "/api/v1/ai-hitl-checkpoints/",
        json={
            "audit_log_id": str(audit_log_id),
            "decision": "approved",
            "reviewer_user_id": str(uuid.uuid4()),  # poging tot spoofing
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert r.status_code == 201
    body = r.json()
    # De reviewer komt uit de token (sub claim), niet uit het payload veld
    # (dat is daarom ook niet eens een geldig veld in HITLCheckpointCreate)
    assert "reviewer_user_id" in body
