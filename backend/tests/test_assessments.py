import uuid
import pytest
from httpx import AsyncClient
from datetime import date


@pytest.mark.asyncio
async def test_create_assessment(client: AsyncClient, test_tenant):
    response = await client.post(
        "/api/v1/assessments/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "assessment_type": "audit",
            "domain": "ISMS",
            "planned_at": "2024-06-01",
            "status": "gepland",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["assessment_type"] == "audit"
    assert data["status"] == "gepland"


@pytest.mark.asyncio
async def test_create_assessment_types(client: AsyncClient, test_tenant):
    for atype in ["dpia", "pentest", "self_assessment", "bc_oefening", "gap_analysis"]:
        response = await client.post(
            "/api/v1/assessments/",
            params={"tenant_id": test_tenant["id"]},
            json={
                "assessment_type": atype,
                "planned_at": "2024-07-01",
                "status": "gepland",
            },
        )
        assert response.status_code == 201
        assert response.json()["assessment_type"] == atype


@pytest.mark.asyncio
async def test_list_assessments(client: AsyncClient, test_tenant):
    response = await client.get(
        "/api/v1/assessments/",
        params={"tenant_id": test_tenant["id"]},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_finding(client: AsyncClient, test_tenant):
    assessment_resp = await client.post(
        "/api/v1/assessments/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "assessment_type": "audit",
            "planned_at": "2024-06-01",
            "status": "actief",
        },
    )
    assessment_id = assessment_resp.json()["id"]

    response = await client.post(
        "/api/v1/assessments/findings/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "assessment_id": assessment_id,
            "title": "Ontbrekend wachtwoordbeleid",
            "description": "Geen wachtwoordbeleid aanwezig",
            "severity": "hoog",
            "status": "open",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Ontbrekend wachtwoordbeleid"
    assert data["severity"] == "hoog"


@pytest.mark.asyncio
async def test_create_corrective_action_from_finding(client: AsyncClient, test_tenant):
    assessment_resp = await client.post(
        "/api/v1/assessments/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "assessment_type": "audit",
            "planned_at": "2024-06-01",
            "status": "actief",
        },
    )
    finding_resp = await client.post(
        "/api/v1/assessments/findings/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "assessment_id": assessment_resp.json()["id"],
            "title": "CA Finding",
            "description": "Test",
            "severity": "gemiddeld",
            "status": "open",
        },
    )

    response = await client.post(
        "/api/v1/assessments/corrective-actions/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "finding_id": finding_resp.json()["id"],
            "title": "Wachtwoordbeleid implementeren",
            "description": "Stel wachtwoordbeleid op en implementeer",
            "due_date": "2024-09-01",
            "status": "open",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["finding_id"] == finding_resp.json()["id"]
    assert data["status"] == "open"


@pytest.mark.asyncio
async def test_create_corrective_action_from_risk(client: AsyncClient, test_tenant):
    scope_resp = await client.post(
        "/api/v1/scopes/",
        params={"tenant_id": test_tenant["id"]},
        json={"type": "cluster", "name": "CA Risk Scope", "domain": "ISMS"},
    )
    risk_resp = await client.post(
        "/api/v1/risks/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "scope_id": scope_resp.json()["id"],
            "domain": "ISMS",
            "title": "CA Risk",
            "description": "Test",
            "likelihood": 3,
            "impact": 3,
            "status": "open",
        },
    )

    response = await client.post(
        "/api/v1/assessments/corrective-actions/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "risk_id": risk_resp.json()["id"],
            "title": "Risico mitigeren",
            "description": "Implementeer beveiligingsmaatregel",
            "due_date": "2024-12-01",
            "status": "open",
        },
    )
    assert response.status_code == 201
    assert response.json()["risk_id"] == risk_resp.json()["id"]


@pytest.mark.asyncio
async def test_assessment_not_found(client: AsyncClient):
    response = await client.get(f"/api/v1/assessments/{uuid.uuid4()}")
    assert response.status_code == 404
