"""Tests voor AI Conformiteitsbeoordeling als assessment-type (M4)."""

import uuid

import pytest


@pytest.fixture
async def ai_system(client, tenant_token):
    """Maak een geregistreerd AI-systeem aan om assessments aan te koppelen."""
    r = await client.post(
        "/api/v1/ai-systems/",
        json={
            "name": "Frauded-detectie",
            "system_type": "decision_support",
            "eu_ai_act_risk": "high",
            "deployment_status": "deployed",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 201, r.text
    return r.json()


@pytest.mark.asyncio
async def test_create_ai_conformity_assessment(client, tenant_token, ai_system):
    """Een ai_conformity assessment kan worden aangemaakt en gekoppeld
    aan een geregistreerd AI-systeem."""
    r = await client.post(
        "/api/v1/assessments/",
        json={
            "assessment_type": "ai_conformity",
            "planned_at": "2026-06-01",
            "status": "gepland",
            "ai_system_id": ai_system["id"],
            "domain": "ISMS",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["assessment_type"] == "ai_conformity"
    assert body["ai_system_id"] == ai_system["id"]


@pytest.mark.asyncio
async def test_ai_conformity_without_ai_system_rejected(client, tenant_token):
    """ai_conformity assessment zonder ai_system_id wordt geweigerd (400) —
    EU AI Act-conformity vereist een specifiek systeem als scope."""
    r = await client.post(
        "/api/v1/assessments/",
        json={
            "assessment_type": "ai_conformity",
            "planned_at": "2026-06-01",
            "status": "gepland",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 400
    assert "ai_system_id" in r.json()["detail"].lower()


@pytest.mark.asyncio
async def test_ai_system_id_must_exist_in_tenant(client, tenant_token):
    """Een onbekend ai_system_id geeft 404, ook al is het UUID-formaat geldig."""
    r = await client.post(
        "/api/v1/assessments/",
        json={
            "assessment_type": "ai_conformity",
            "planned_at": "2026-06-01",
            "status": "gepland",
            "ai_system_id": str(uuid.uuid4()),
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_other_assessment_types_can_omit_ai_system_id(client, tenant_token):
    """Audit/dpia/pentest assessments mogen ai_system_id leeg laten —
    de check geldt alleen voor ai_conformity."""
    for assessment_type in ("audit", "dpia", "self_assessment", "gap_analysis"):
        r = await client.post(
            "/api/v1/assessments/",
            json={
                "assessment_type": assessment_type,
                "planned_at": "2026-06-01",
                "status": "gepland",
            },
            headers={"Authorization": f"Bearer {tenant_token}"},
        )
        assert r.status_code == 201, (
            f"{assessment_type} mag zonder ai_system_id — kreeg {r.status_code}: {r.text}"
        )


@pytest.mark.asyncio
async def test_list_assessments_filter_by_ai_system(client, tenant_token, ai_system):
    """Filter op ai_system_id geeft alleen assessments voor dat systeem."""
    # Maak twee assessments: één gekoppeld, één los
    await client.post(
        "/api/v1/assessments/",
        json={
            "assessment_type": "ai_conformity",
            "planned_at": "2026-06-01",
            "ai_system_id": ai_system["id"],
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    await client.post(
        "/api/v1/assessments/",
        json={"assessment_type": "audit", "planned_at": "2026-06-15"},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )

    r = await client.get(
        f"/api/v1/assessments/?ai_system_id={ai_system['id']}",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 1
    assert body[0]["ai_system_id"] == ai_system["id"]
    assert body[0]["assessment_type"] == "ai_conformity"


@pytest.mark.asyncio
async def test_list_assessments_filter_by_assessment_type(
    client, tenant_token, ai_system
):
    """Filter op assessment_type=ai_conformity werkt los van ai_system_id-filter."""
    await client.post(
        "/api/v1/assessments/",
        json={
            "assessment_type": "ai_conformity",
            "planned_at": "2026-06-01",
            "ai_system_id": ai_system["id"],
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    await client.post(
        "/api/v1/assessments/",
        json={"assessment_type": "dpia", "planned_at": "2026-06-15"},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )

    r = await client.get(
        "/api/v1/assessments/?assessment_type=ai_conformity",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 200
    types = [a["assessment_type"] for a in r.json()]
    assert all(t == "ai_conformity" for t in types)
    assert len(types) == 1
