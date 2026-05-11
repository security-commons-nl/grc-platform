"""Tests voor rate limiting (M0 productie-readiness).

Strategie:
- Bestaande tests draaien met rate limit UIT (conftest.py disable autouse).
- Deze tests zetten de limiter expliciet aan via `with_rate_limit` fixture
  en gebruiken de productie-defaults (10/minute voor auth-endpoints, 100/
  minute globaal).
- Tussen tests wordt de in-memory storage gereset.
"""

import uuid

import pytest
import pytest_asyncio

from app.core.rate_limit import limiter


@pytest_asyncio.fixture
async def with_rate_limit():
    """Enable rate limiting for a single test. Resets storage afterwards."""
    limiter.reset()
    limiter.enabled = True
    yield limiter
    limiter.enabled = False
    limiter.reset()


@pytest.mark.asyncio
async def test_auth_endpoint_rate_limited_after_threshold(client, with_rate_limit):
    """De 11e POST op /auth/dev-token binnen 1 minuut moet 429 geven
    (default RATE_LIMIT_AUTH = '10/minute')."""
    payload = {
        "user_id": str(uuid.uuid4()),
        "tenant_id": str(uuid.uuid4()),
        "role": "admin",
    }

    last_status = None
    last_response = None
    for i in range(15):
        r = await client.post("/api/v1/auth/dev-token", json=payload)
        last_status = r.status_code
        last_response = r
        if last_status == 429:
            break

    assert last_status == 429, (
        f"Verwachte 429 binnen 15 requests; laatste status was {last_status}. "
        f"Body: {last_response.text if last_response else 'n/a'}"
    )


@pytest.mark.asyncio
async def test_rate_limit_response_has_retry_after_header(client, with_rate_limit):
    """Bij een 429 moet de Retry-After header gezet zijn zodat clients
    weten wanneer ze opnieuw mogen proberen."""
    payload = {
        "user_id": str(uuid.uuid4()),
        "tenant_id": str(uuid.uuid4()),
        "role": "admin",
    }

    # Verbruik de limit
    for _ in range(15):
        r = await client.post("/api/v1/auth/dev-token", json=payload)
        if r.status_code == 429:
            break

    assert r.status_code == 429
    assert "retry-after" in {h.lower() for h in r.headers.keys()}, (
        f"Retry-After header ontbreekt. Headers: {dict(r.headers)}"
    )


@pytest.mark.asyncio
async def test_health_endpoint_not_rate_limited(client, with_rate_limit):
    """Health endpoint moet onbeperkt aanroepbaar zijn — load balancers
    en monitoring kunnen anders een organisatie als 'unhealthy' markeren
    wanneer ze de rate limit raken."""
    # Doe meer requests dan de globale default (100/minute) zou toestaan.
    # Note: de health endpoint heeft geen @limiter.limit decorator, en
    # GET-routes vallen onder de globale SlowAPIMiddleware default. We
    # vertrouwen erop dat de globale default geen GET /health blokkeert
    # binnen een redelijk testaantal. Bij toekomstige verlaging van
    # RATE_LIMIT_DEFAULT moet health expliciet exempt worden.
    for _ in range(20):
        r = await client.get("/api/v1/health")
        assert r.status_code == 200, (
            f"Health endpoint mag niet rate-limited zijn. Status: {r.status_code}"
        )


@pytest.mark.asyncio
async def test_rate_limit_disabled_in_default_test_mode(client):
    """Sanity check: zonder `with_rate_limit` fixture moet de limiter
    uit staan zodat bestaande tests niet onverwacht raken."""
    payload = {
        "user_id": str(uuid.uuid4()),
        "tenant_id": str(uuid.uuid4()),
        "role": "admin",
    }
    # 20 requests, allemaal moeten slagen (200 of 403 als ENVIRONMENT
    # != development, maar nooit 429).
    for _ in range(20):
        r = await client.post("/api/v1/auth/dev-token", json=payload)
        assert r.status_code != 429, (
            "Rate limit zou uit moeten staan in default test-mode; "
            f"kreeg 429 op iteratie. Body: {r.text}"
        )


@pytest.mark.asyncio
async def test_rate_limit_can_be_disabled_via_setting(client, with_rate_limit):
    """Wanneer RATE_LIMIT_ENABLED runtime op False staat moet er geen
    429 meer komen, ook niet na veel requests."""
    limiter.enabled = False
    payload = {
        "user_id": str(uuid.uuid4()),
        "tenant_id": str(uuid.uuid4()),
        "role": "admin",
    }
    for _ in range(25):
        r = await client.post("/api/v1/auth/dev-token", json=payload)
        assert r.status_code != 429
