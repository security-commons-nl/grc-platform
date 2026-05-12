"""Integration tests voor /risks/{id}/simulate (M5)."""

import pytest


@pytest.fixture
async def scope_id(client, tenant_token):
    r = await client.post(
        "/api/v1/scopes/",
        json={"name": "Test Scope", "type": "cluster", "domain": "ISMS"},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


async def _create_risk(client, token, scope_id, **overrides):
    payload = {
        "scope_id": scope_id,
        "domain": "ISMS",
        "title": "Test risico",
        "description": "voor simulatie",
        "likelihood": 3,
        "impact": 4,
    }
    payload.update(overrides)
    r = await client.post(
        "/api/v1/risks/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201, r.text
    return r.json()


@pytest.mark.asyncio
async def test_simulate_triangular_returns_full_payload(
    client, tenant_token, scope_id
):
    """Een risico met triangular distributie kan worden gesimuleerd."""
    risk = await _create_risk(
        client,
        tenant_token,
        scope_id,
        financial_impact_eur=25000,
        financial_impact_min_eur=10000,
        financial_impact_max_eur=100000,
        impact_distribution="triangular",
    )
    r = await client.post(
        f"/api/v1/risks/{risk['id']}/simulate?iterations=5000&seed=42",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["distribution"] == "triangular"
    assert body["iterations"] == 5000
    assert body["parameters"] == {"min": 10000.0, "mode": 25000.0, "max": 100000.0}
    assert "statistics" in body and "mean" in body["statistics"]
    assert "percentiles" in body and "p95" in body["percentiles"]
    assert body["expected_loss"] == body["statistics"]["mean"]
    assert body["var_95"] == body["percentiles"]["p95"]
    assert body["var_99"] == body["percentiles"]["p99"]
    # Sanity: percentielen moeten monotoon stijgen
    p = body["percentiles"]
    assert p["p5"] < p["p50"] < p["p95"] < p["p99"]


@pytest.mark.asyncio
async def test_simulate_uniform(client, tenant_token, scope_id):
    risk = await _create_risk(
        client,
        tenant_token,
        scope_id,
        financial_impact_min_eur=1000,
        financial_impact_max_eur=2000,
        impact_distribution="uniform",
    )
    r = await client.post(
        f"/api/v1/risks/{risk['id']}/simulate?iterations=10000&seed=1",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 200
    body = r.json()
    # Uniform(1000, 2000) mean ≈ 1500
    assert 1490 < body["statistics"]["mean"] < 1510


@pytest.mark.asyncio
async def test_simulate_without_distribution_rejected(
    client, tenant_token, scope_id
):
    """Een risico zonder impact_distribution kan niet gesimuleerd worden."""
    risk = await _create_risk(
        client, tenant_token, scope_id, financial_impact_eur=50000
    )
    r = await client.post(
        f"/api/v1/risks/{risk['id']}/simulate",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 400
    assert "distributie" in r.json()["detail"].lower()


@pytest.mark.asyncio
async def test_simulate_with_single_distribution_rejected(
    client, tenant_token, scope_id
):
    """'single' is geen distributie waar simulatie zinvol is — point estimate.
    Endpoint moet dat weigeren."""
    risk = await _create_risk(
        client,
        tenant_token,
        scope_id,
        financial_impact_eur=50000,
        impact_distribution="single",
    )
    r = await client.post(
        f"/api/v1/risks/{risk['id']}/simulate",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_simulate_unknown_risk_returns_404(client, tenant_token):
    import uuid

    r = await client.post(
        f"/api/v1/risks/{uuid.uuid4()}/simulate",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_simulate_iterations_below_min_rejected(
    client, tenant_token, scope_id
):
    risk = await _create_risk(
        client,
        tenant_token,
        scope_id,
        financial_impact_min_eur=0,
        financial_impact_max_eur=100,
        impact_distribution="uniform",
    )
    r = await client.post(
        f"/api/v1/risks/{risk['id']}/simulate?iterations=10",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 422  # Pydantic/FastAPI Query ge=1000


@pytest.mark.asyncio
async def test_simulate_reproducible_with_seed(client, tenant_token, scope_id):
    """Twee runs met dezelfde seed geven dezelfde statistieken."""
    risk = await _create_risk(
        client,
        tenant_token,
        scope_id,
        financial_impact_min_eur=0,
        financial_impact_max_eur=1000,
        impact_distribution="uniform",
    )
    r1 = await client.post(
        f"/api/v1/risks/{risk['id']}/simulate?iterations=5000&seed=99",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    r2 = await client.post(
        f"/api/v1/risks/{risk['id']}/simulate?iterations=5000&seed=99",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r1.status_code == r2.status_code == 200
    assert r1.json()["statistics"]["mean"] == r2.json()["statistics"]["mean"]
    assert r1.json()["percentiles"]["p95"] == r2.json()["percentiles"]["p95"]


@pytest.mark.asyncio
async def test_simulate_default_omits_samples(client, tenant_token, scope_id):
    """Default response laat samples weg (kleine payload)."""
    risk = await _create_risk(
        client,
        tenant_token,
        scope_id,
        financial_impact_min_eur=0,
        financial_impact_max_eur=100,
        impact_distribution="uniform",
    )
    r = await client.post(
        f"/api/v1/risks/{risk['id']}/simulate?iterations=1000&seed=1",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body.get("samples") is None


@pytest.mark.asyncio
async def test_simulate_include_samples_returns_array(
    client, tenant_token, scope_id
):
    """Met include_samples=true retourneert response de ruwe trekkingen."""
    risk = await _create_risk(
        client,
        tenant_token,
        scope_id,
        financial_impact_min_eur=100,
        financial_impact_max_eur=500,
        impact_distribution="uniform",
    )
    r = await client.post(
        f"/api/v1/risks/{risk['id']}/simulate?iterations=2500&seed=7&include_samples=true",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 200
    body = r.json()
    samples = body.get("samples")
    assert isinstance(samples, list)
    assert len(samples) == 2500
    # Sample-bereik moet liggen binnen distributie-grenzen
    assert all(100 <= s <= 500 for s in samples)
    # Steekproef-mean moet ongeveer (100+500)/2 = 300 zijn
    assert 290 < sum(samples) / len(samples) < 310


@pytest.mark.asyncio
async def test_simulate_persists_history_row(client, tenant_token, scope_id):
    """Elke succesvolle simulate-call slaat een ims_risk_simulations-row op."""
    risk = await _create_risk(
        client,
        tenant_token,
        scope_id,
        financial_impact_min_eur=0,
        financial_impact_max_eur=1000,
        impact_distribution="uniform",
    )
    r = await client.post(
        f"/api/v1/risks/{risk['id']}/simulate?iterations=2000&seed=5",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert "simulation_id" in body and body["simulation_id"]

    # Lijst-endpoint moet exact één entry tonen
    history = await client.get(
        f"/api/v1/risks/{risk['id']}/simulations",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert history.status_code == 200
    items = history.json()
    assert len(items) == 1
    item = items[0]
    assert item["id"] == body["simulation_id"]
    assert item["distribution"] == "uniform"
    assert item["iterations"] == 2000
    assert item["seed"] == 5
    assert item["parameters"] == {"min": 0.0, "max": 1000.0}
    # Samples worden niet teruggegeven in historie-rijen
    assert "samples" not in item


@pytest.mark.asyncio
async def test_simulate_accepts_label_and_note(client, tenant_token, scope_id):
    """Label en note query-params landen in historie-row."""
    risk = await _create_risk(
        client,
        tenant_token,
        scope_id,
        financial_impact_min_eur=10,
        financial_impact_max_eur=20,
        impact_distribution="uniform",
    )
    r = await client.post(
        f"/api/v1/risks/{risk['id']}/simulate"
        f"?iterations=1000&seed=1&label=Baseline&note=Initi%C3%ABle%20schatting",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 200
    history = await client.get(
        f"/api/v1/risks/{risk['id']}/simulations",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    items = history.json()
    assert items[0]["label"] == "Baseline"
    assert items[0]["note"] == "Initiële schatting"


@pytest.mark.asyncio
async def test_simulations_list_paginates_newest_first(
    client, tenant_token, scope_id
):
    """Drie runs → nieuwste eerst; limit en skip werken."""
    risk = await _create_risk(
        client,
        tenant_token,
        scope_id,
        financial_impact_min_eur=0,
        financial_impact_max_eur=100,
        impact_distribution="uniform",
    )
    for i in range(3):
        r = await client.post(
            f"/api/v1/risks/{risk['id']}/simulate?iterations=1000&seed={i}&label=Run-{i}",
            headers={"Authorization": f"Bearer {tenant_token}"},
        )
        assert r.status_code == 200

    full = await client.get(
        f"/api/v1/risks/{risk['id']}/simulations",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    items = full.json()
    assert len(items) == 3
    # Nieuwste eerst — Run-2 is laatste insert
    assert items[0]["label"] == "Run-2"
    assert items[2]["label"] == "Run-0"

    paged = await client.get(
        f"/api/v1/risks/{risk['id']}/simulations?skip=1&limit=1",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    paged_items = paged.json()
    assert len(paged_items) == 1
    assert paged_items[0]["label"] == "Run-1"


@pytest.mark.asyncio
async def test_simulations_list_unknown_risk_returns_404(client, tenant_token):
    import uuid as _uuid

    r = await client.get(
        f"/api/v1/risks/{_uuid.uuid4()}/simulations",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_simulations_list_isolates_between_tenants(
    client, tenant_token, scope_id, admin_token
):
    """Een tweede tenant kan de simulatie-historie van een eerste tenant niet zien.

    De tweede tenant krijgt 404 bij het opvragen van het risico — RLS plus
    expliciete tenant_id-filter dekken het beide samen.
    """
    from tests.conftest import make_token

    risk = await _create_risk(
        client,
        tenant_token,
        scope_id,
        financial_impact_min_eur=0,
        financial_impact_max_eur=50,
        impact_distribution="uniform",
    )
    r1 = await client.post(
        f"/api/v1/risks/{risk['id']}/simulate?iterations=1000&seed=1",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r1.status_code == 200

    # Tweede tenant aanmaken en eigen token uitgeven.
    other_tenant_resp = await client.post(
        "/api/v1/tenants/",
        json={"name": "Andere gemeente", "type": "regio"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert other_tenant_resp.status_code == 201, other_tenant_resp.text
    other_tenant = other_tenant_resp.json()
    other_token = make_token(tenant_id=other_tenant["id"], role="admin")

    r2 = await client.get(
        f"/api/v1/risks/{risk['id']}/simulations",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert r2.status_code == 404


@pytest.mark.asyncio
async def test_create_risk_with_simulation_fields(client, tenant_token, scope_id):
    """RiskCreate accepteert de nieuwe M5-velden en de RiskResponse retourneert ze."""
    r = await client.post(
        "/api/v1/risks/",
        json={
            "scope_id": scope_id,
            "domain": "ISMS",
            "title": "Risico met range",
            "description": "Test",
            "likelihood": 2,
            "impact": 5,
            "financial_impact_eur": 50000,
            "financial_impact_min_eur": 10000,
            "financial_impact_max_eur": 200000,
            "impact_distribution": "triangular",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["impact_distribution"] == "triangular"
    assert float(body["financial_impact_min_eur"]) == 10000.0
    assert float(body["financial_impact_max_eur"]) == 200000.0
