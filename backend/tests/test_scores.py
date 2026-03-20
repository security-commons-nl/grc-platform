import uuid
import pytest
from httpx import AsyncClient
from datetime import datetime


@pytest.mark.asyncio
async def test_create_maturity_profile(client: AsyncClient, test_tenant):
    response = await client.post(
        "/api/v1/scores/maturity-profiles/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "domain": "ISMS",
            "existing_registers": "aanwezig",
            "existing_analyses": "gedeeltelijk",
            "coordination_capacity": "gemiddeld",
            "linemanagement_structure": "formeel",
            "recommended_option": "B",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["domain"] == "ISMS"
    assert data["existing_registers"] == "aanwezig"
    assert data["recommended_option"] == "B"


@pytest.mark.asyncio
async def test_list_maturity_profiles(client: AsyncClient, test_tenant):
    response = await client.get(
        "/api/v1/scores/maturity-profiles/",
        params={"tenant_id": test_tenant["id"]},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_setup_score(client: AsyncClient, test_tenant):
    response = await client.post(
        "/api/v1/scores/setup-scores/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "domain": "ISMS",
            "cyclus_year": 2024,
            "score_pct": 75.50,
            "steps_completed": 15,
            "steps_total": 20,
            "calculated_at": datetime.utcnow().isoformat(),
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["cyclus_year"] == 2024
    assert float(data["score_pct"]) == 75.50
    assert data["steps_completed"] == 15


@pytest.mark.asyncio
async def test_list_setup_scores(client: AsyncClient, test_tenant):
    response = await client.get(
        "/api/v1/scores/setup-scores/",
        params={"tenant_id": test_tenant["id"]},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_grc_score(client: AsyncClient, test_tenant):
    response = await client.post(
        "/api/v1/scores/grc-scores/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "domain": "ISMS",
            "cyclus_year": 2024,
            "score_pct": 82.30,
            "components_json": {
                "governance": 85.0,
                "risk": 78.0,
                "compliance": 84.0,
            },
            "calculated_at": datetime.utcnow().isoformat(),
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["domain"] == "ISMS"
    assert data["components_json"]["governance"] == 85.0


@pytest.mark.asyncio
async def test_list_grc_scores(client: AsyncClient, test_tenant):
    response = await client.get(
        "/api/v1/scores/grc-scores/",
        params={"tenant_id": test_tenant["id"]},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
