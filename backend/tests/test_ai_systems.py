"""Tests voor het AI-systemenregister (M4 AI Governance)."""

import uuid

import pytest


@pytest.fixture
def ai_system_payload():
    return {
        "name": "Klantvraag-chatbot",
        "description": "Beantwoordt veelgestelde vragen op website",
        "vendor": "Eigen ontwikkeling",
        "system_type": "chatbot",
        "eu_ai_act_risk": "limited",
        "nist_ai_rmf_status": "map",
        "deployment_status": "deployed",
    }


@pytest.mark.asyncio
async def test_create_ai_system(client, tenant_token, ai_system_payload):
    """Een tactisch lid kan een AI-systeem registreren."""
    r = await client.post(
        "/api/v1/ai-systems/",
        json=ai_system_payload,
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["name"] == ai_system_payload["name"]
    assert body["eu_ai_act_risk"] == "limited"
    assert body["deployment_status"] == "deployed"
    assert "id" in body
    assert "tenant_id" in body


@pytest.mark.asyncio
async def test_create_ai_system_uses_sensible_defaults(client, tenant_token):
    """Bij minimale input vult het schema sensible defaults in:
    eu_ai_act_risk=not_classified, nist_ai_rmf_status=not_started,
    deployment_status=planned, system_type=other."""
    r = await client.post(
        "/api/v1/ai-systems/",
        json={"name": "Nieuw systeem"},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["eu_ai_act_risk"] == "not_classified"
    assert body["nist_ai_rmf_status"] == "not_started"
    assert body["deployment_status"] == "planned"
    assert body["system_type"] == "other"


@pytest.mark.asyncio
async def test_invalid_eu_ai_act_risk_value_rejected(client, tenant_token):
    """Pydantic moet vrije-tekst waarden voor eu_ai_act_risk weigeren."""
    r = await client.post(
        "/api/v1/ai-systems/",
        json={"name": "X", "eu_ai_act_risk": "super_high"},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_list_ai_systems(client, tenant_token, ai_system_payload):
    """List endpoint geeft eerder aangemaakte systemen terug."""
    await client.post(
        "/api/v1/ai-systems/",
        json=ai_system_payload,
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    await client.post(
        "/api/v1/ai-systems/",
        json={**ai_system_payload, "name": "Tweede systeem"},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    r = await client.get(
        "/api/v1/ai-systems/",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 200
    assert len(r.json()) == 2


@pytest.mark.asyncio
async def test_list_ai_systems_filter_by_eu_ai_act_risk(
    client, tenant_token, ai_system_payload
):
    """Filter op eu_ai_act_risk werkt."""
    await client.post(
        "/api/v1/ai-systems/",
        json={**ai_system_payload, "eu_ai_act_risk": "high"},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    await client.post(
        "/api/v1/ai-systems/",
        json={**ai_system_payload, "name": "B", "eu_ai_act_risk": "minimal"},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    r = await client.get(
        "/api/v1/ai-systems/?eu_ai_act_risk=high",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 1
    assert body[0]["eu_ai_act_risk"] == "high"


@pytest.mark.asyncio
async def test_get_ai_system_404_when_missing(client, tenant_token):
    r = await client.get(
        f"/api/v1/ai-systems/{uuid.uuid4()}",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_update_ai_system_eu_ai_act_classification(
    client, tenant_token, ai_system_payload
):
    """Een tactisch lid kan de EU AI Act-classificatie wijzigen."""
    create = await client.post(
        "/api/v1/ai-systems/",
        json=ai_system_payload,
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    ai_system_id = create.json()["id"]

    r = await client.patch(
        f"/api/v1/ai-systems/{ai_system_id}",
        json={"eu_ai_act_risk": "high", "nist_ai_rmf_status": "manage"},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["eu_ai_act_risk"] == "high"
    assert body["nist_ai_rmf_status"] == "manage"
    assert body["name"] == ai_system_payload["name"]  # andere velden onveranderd


@pytest.mark.asyncio
async def test_delete_ai_system_requires_admin(
    client, test_tenant, tenant_token, ai_system_payload
):
    """Alleen admin mag een AI-systeem uit het register verwijderen.
    Tactisch_lid token wordt verwacht 403 te geven."""
    create = await client.post(
        "/api/v1/ai-systems/",
        json=ai_system_payload,
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    ai_system_id = create.json()["id"]

    from tests.conftest import make_token
    tactisch_token = make_token(tenant_id=test_tenant["id"], role="tactisch_lid")

    r = await client.delete(
        f"/api/v1/ai-systems/{ai_system_id}",
        headers={"Authorization": f"Bearer {tactisch_token}"},
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_delete_ai_system_as_admin(client, tenant_token, ai_system_payload):
    """Admin kan verwijderen."""
    create = await client.post(
        "/api/v1/ai-systems/",
        json=ai_system_payload,
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    ai_system_id = create.json()["id"]

    r = await client.delete(
        f"/api/v1/ai-systems/{ai_system_id}",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 204

    # Verifieer dat hij weg is
    r = await client.get(
        f"/api/v1/ai-systems/{ai_system_id}",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_viewer_cannot_create_ai_system(client, viewer_token):
    """Viewer-rol mag geen AI-systeem aanmaken (read-only)."""
    r = await client.post(
        "/api/v1/ai-systems/",
        json={"name": "Verboden poging"},
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert r.status_code == 403
