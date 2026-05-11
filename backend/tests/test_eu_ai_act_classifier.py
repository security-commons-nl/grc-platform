"""Tests voor de EU AI Act risicoclassificatie-helper (M4)."""

import pytest

from app.services.eu_ai_act_classifier import suggest_risk


# ── Unit tests op de service zelf (geen HTTP) ─────────────────────────────


def test_unacceptable_triggers_on_social_scoring():
    s = suggest_risk(
        system_type="classification",
        description="Implementeert een social score voor inwoners op basis van gedrag.",
    )
    assert s.suggested_risk == "unacceptable"
    assert any("social score" in t for t in s.triggered_by)


def test_unacceptable_overrules_high():
    """Onaanvaardbaar overstemt hoog-risico zelfs als beide keywords aanwezig zijn."""
    s = suggest_risk(
        system_type="decision_support",
        description="Burgerscore voor toelating tot uitkering toekennen.",
    )
    assert s.suggested_risk == "unacceptable"


def test_high_risk_on_welfare_decision():
    s = suggest_risk(
        system_type="decision_support",
        description="Beoordeelt bijstand beslissing automatisch.",
    )
    assert s.suggested_risk == "high"


def test_high_risk_on_critical_infrastructure():
    s = suggest_risk(
        system_type="monitoring",
        description="Bewaakt drinkwater-kwaliteit en triggert automatische maatregelen.",
    )
    assert s.suggested_risk == "high"


def test_limited_risk_on_chatbot():
    s = suggest_risk(
        system_type="chatbot",
        description="Beantwoordt vragen over openingstijden van het stadhuis.",
    )
    assert s.suggested_risk == "limited"


def test_minimal_default_for_automation():
    s = suggest_risk(
        system_type="automation",
        description="Sorteert binnenkomende e-mails op afdeling.",
    )
    assert s.suggested_risk == "minimal"


def test_not_classified_for_other_type_without_keywords():
    s = suggest_risk(
        system_type="other",
        description="Doet iets onbepaald.",
    )
    assert s.suggested_risk == "not_classified"


def test_reasoning_is_non_empty():
    s = suggest_risk(system_type="chatbot")
    assert s.reasoning
    assert isinstance(s.reasoning, str)


def test_triggered_by_includes_rules_or_default():
    s = suggest_risk(system_type="chatbot")
    assert len(s.triggered_by) > 0


# ── Integration tests via API endpoint ─────────────────────────────────────


@pytest.mark.asyncio
async def test_classify_endpoint_high_risk(client, tenant_token):
    r = await client.post(
        "/api/v1/ai-systems/classify-suggestion",
        json={
            "system_type": "decision_support",
            "description": "Beoordeelt kredietwaardigheid van inwoners.",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["suggested_risk"] == "high"
    assert body["reasoning"]


@pytest.mark.asyncio
async def test_classify_endpoint_unauthenticated(client):
    """Het advies-endpoint vereist authenticatie — voorkomt anonymous abuse."""
    r = await client.post(
        "/api/v1/ai-systems/classify-suggestion",
        json={"system_type": "chatbot"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_classify_endpoint_minimum_payload(client, tenant_token):
    """Alleen system_type is verplicht; description en use_case zijn optional."""
    r = await client.post(
        "/api/v1/ai-systems/classify-suggestion",
        json={"system_type": "chatbot"},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 200
    assert r.json()["suggested_risk"] == "limited"
