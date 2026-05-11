"""Tests voor health endpoints (M0 monitoring & observability)."""

import pytest


@pytest.mark.asyncio
async def test_health_basic(client):
    """Het basic /health endpoint geeft 200 + minimal payload."""
    r = await client.get("/api/v1/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["database"] == "connected"


@pytest.mark.asyncio
async def test_health_details_returns_200(client):
    """Het uitgebreide /health/details endpoint geeft 200."""
    r = await client.get("/api/v1/health/details")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_health_details_payload_shape(client):
    """De payload bevat alle verwachte velden voor monitoring tools."""
    r = await client.get("/api/v1/health/details")
    body = r.json()

    # Top-level
    assert "status" in body
    assert body["status"] in ("ok", "degraded", "unhealthy")
    assert "environment" in body

    # Database sub-object
    assert "database" in body
    assert body["database"]["connected"] is True
    assert isinstance(body["database"]["latency_ms"], int)
    assert body["database"]["latency_ms"] >= 0

    # AI-provider sub-object — booleans en URLs, geen secrets
    assert "ai_provider" in body
    assert "configured" in body["ai_provider"]
    assert "base_url" in body["ai_provider"]
    assert "model" in body["ai_provider"]
    # Geen 'api_key' of 'secret' velden — secrets mogen niet lekken
    forbidden = {"api_key", "secret", "key", "token"}
    assert not any(k in forbidden for k in body["ai_provider"].keys())

    # Observability sub-object
    assert "observability" in body
    assert "langfuse_configured" in body["observability"]

    # Rate limit sub-object
    assert "rate_limit" in body
    assert "enabled" in body["rate_limit"]
    assert "default" in body["rate_limit"]
    assert "auth" in body["rate_limit"]


@pytest.mark.asyncio
async def test_health_details_does_not_leak_secrets(client):
    """De /health/details response mag geen API-keys, JWT-secrets, of
    database-wachtwoorden bevatten."""
    r = await client.get("/api/v1/health/details")
    body_text = r.text.lower()

    # Geen JWT secret
    assert "jwt_secret" not in body_text
    # Geen postgres password
    assert "postgres_password" not in body_text
    # Geen AI api key — als die toevallig de string 'sk-' bevat is dat verdacht
    assert "sk-" not in r.text
