"""Tests voor RFC 0001 — extensible attributes (custom fields)."""

import uuid

import pytest


# ── Helpers ────────────────────────────────────────────────────────────────


async def _create_scope(client, token):
    r = await client.post(
        "/api/v1/scopes/",
        json={"name": "Test Scope", "type": "cluster", "domain": "ISMS"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


async def _create_field(client, token, **overrides):
    payload = {
        "entity_type": "risk",
        "field_name": "kadernota_programma",
        "display_label": "Kadernota-programma",
        "json_schema": {"type": "string", "maxLength": 200},
        "is_required": False,
    }
    payload.update(overrides)
    r = await client.post(
        "/api/v1/custom-fields/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    return r


# ── Definition CRUD ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_custom_field_definition(client, tenant_token):
    r = await _create_field(client, tenant_token)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["field_name"] == "kadernota_programma"
    assert body["entity_type"] == "risk"
    assert body["is_required"] is False


@pytest.mark.asyncio
async def test_create_reserved_field_name_returns_409(client, tenant_token):
    # 'tenant_id' is een kernveld op ims_risks → reserved.
    r = await _create_field(client, tenant_token, field_name="tenant_id")
    assert r.status_code == 409
    assert "kernveld" in r.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_duplicate_definition_returns_409(client, tenant_token):
    r1 = await _create_field(client, tenant_token)
    assert r1.status_code == 201
    r2 = await _create_field(client, tenant_token)
    assert r2.status_code == 409


@pytest.mark.asyncio
async def test_field_name_pattern_rejects_uppercase(client, tenant_token):
    r = await _create_field(client, tenant_token, field_name="Bad_Name")
    # Pydantic-pattern faalt vóór endpoint geraakt wordt → 422
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_list_filters_by_entity_type(client, tenant_token):
    await _create_field(client, tenant_token, field_name="a", entity_type="risk")
    await _create_field(client, tenant_token, field_name="b", entity_type="control")
    r = await client.get(
        "/api/v1/custom-fields/?entity_type=risk",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 200
    names = [d["field_name"] for d in r.json()]
    assert "a" in names and "b" not in names


# ── Validatie van risk-payloads tegen custom-veld-definities ───────────────


@pytest.mark.asyncio
async def test_risk_with_valid_custom_attributes(client, tenant_token):
    """Geldige custom_attributes worden geaccepteerd en geretourneerd."""
    await _create_field(client, tenant_token)
    scope_id = await _create_scope(client, tenant_token)

    r = await client.post(
        "/api/v1/risks/",
        json={
            "scope_id": scope_id,
            "domain": "ISMS",
            "title": "Risico met custom field",
            "description": "Test",
            "likelihood": 2,
            "impact": 3,
            "custom_attributes": {"kadernota_programma": "Programma 7 — Veiligheid"},
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["custom_attributes"]["kadernota_programma"] == "Programma 7 — Veiligheid"


@pytest.mark.asyncio
async def test_risk_with_missing_required_attr_returns_422(client, tenant_token):
    await _create_field(client, tenant_token, is_required=True)
    scope_id = await _create_scope(client, tenant_token)

    r = await client.post(
        "/api/v1/risks/",
        json={
            "scope_id": scope_id,
            "domain": "ISMS",
            "title": "Zonder verplicht veld",
            "description": "Test",
            "likelihood": 2,
            "impact": 3,
            # Geen custom_attributes — required veld ontbreekt
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 422
    detail = r.json()["detail"]
    assert any("kadernota_programma" in str(item) for item in detail)


@pytest.mark.asyncio
async def test_risk_with_unknown_custom_attr_returns_422(client, tenant_token):
    """additionalProperties=false sluit onbekende velden uit."""
    await _create_field(client, tenant_token)
    scope_id = await _create_scope(client, tenant_token)

    r = await client.post(
        "/api/v1/risks/",
        json={
            "scope_id": scope_id,
            "domain": "ISMS",
            "title": "Onbekend veld",
            "description": "Test",
            "likelihood": 2,
            "impact": 3,
            "custom_attributes": {"verzonnen_veld": "foo"},
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_risk_custom_attrs_when_no_definitions(client, tenant_token):
    """Zonder definities zijn alleen lege custom_attributes toegestaan."""
    scope_id = await _create_scope(client, tenant_token)

    r_ok = await client.post(
        "/api/v1/risks/",
        json={
            "scope_id": scope_id,
            "domain": "ISMS",
            "title": "Zonder def, zonder attrs",
            "description": "Test",
            "likelihood": 1,
            "impact": 1,
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r_ok.status_code == 201

    r_fail = await client.post(
        "/api/v1/risks/",
        json={
            "scope_id": scope_id,
            "domain": "ISMS",
            "title": "Zonder def, met attrs",
            "description": "Test",
            "likelihood": 1,
            "impact": 1,
            "custom_attributes": {"ergens_iets": "x"},
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r_fail.status_code == 422


@pytest.mark.asyncio
async def test_definition_update_changes_required_flag(client, tenant_token):
    r1 = await _create_field(client, tenant_token, is_required=False)
    definition_id = r1.json()["id"]
    r2 = await client.patch(
        f"/api/v1/custom-fields/{definition_id}",
        json={"is_required": True},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r2.status_code == 200
    assert r2.json()["is_required"] is True


@pytest.mark.asyncio
async def test_delete_definition_removes_validation(client, tenant_token):
    r1 = await _create_field(client, tenant_token, is_required=True)
    definition_id = r1.json()["id"]

    # Met required veld zou een leeg risico falen
    scope_id = await _create_scope(client, tenant_token)
    payload = {
        "scope_id": scope_id,
        "domain": "ISMS",
        "title": "Test",
        "description": "Test",
        "likelihood": 1,
        "impact": 1,
    }
    rf = await client.post(
        "/api/v1/risks/",
        json=payload,
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert rf.status_code == 422

    # Verwijder definitie → nu mag het wel
    rd = await client.delete(
        f"/api/v1/custom-fields/{definition_id}",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert rd.status_code == 204

    rok = await client.post(
        "/api/v1/risks/",
        json=payload,
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert rok.status_code == 201
