"""Verifieert dat NIST AI RMF correct als normenkader is geseed (migration 011)."""

import pytest


@pytest.mark.asyncio
async def test_nist_ai_rmf_standard_exists(client, tenant_token):
    """Het NIST AI RMF normenkader is via /standards bereikbaar."""
    r = await client.get(
        "/api/v1/standards/",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert r.status_code == 200
    names = [s["name"] for s in r.json()]
    assert "NIST AI RMF" in names, f"NIST AI RMF ontbreekt. Aanwezige standards: {names}"


@pytest.mark.asyncio
async def test_nist_ai_rmf_has_aims_domain(client, tenant_token):
    """Het NIST AI RMF normenkader heeft domain=AIMS — onderscheidend van ISMS/PIMS/BCMS."""
    r = await client.get(
        "/api/v1/standards/",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    nist = next(s for s in r.json() if s["name"] == "NIST AI RMF")
    assert nist["domain"] == "AIMS"
    assert nist["version"] == "1.0"
    assert nist["status"] == "actief"


@pytest.mark.asyncio
async def test_nist_ai_rmf_has_four_core_functions(client, tenant_token):
    """NIST AI RMF heeft exact vier kernfuncties als requirements:
    GOVERN, MAP, MEASURE, MANAGE."""
    standards_r = await client.get(
        "/api/v1/standards/",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    nist = next(s for s in standards_r.json() if s["name"] == "NIST AI RMF")

    reqs_r = await client.get(
        f"/api/v1/standards/requirements/?standard_id={nist['id']}",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert reqs_r.status_code == 200
    codes = sorted([r["code"] for r in reqs_r.json()])
    assert codes == ["GOVERN", "MANAGE", "MAP", "MEASURE"], f"Onverwachte codes: {codes}"
