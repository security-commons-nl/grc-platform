import uuid
import pytest
from httpx import AsyncClient
from datetime import datetime


@pytest.mark.asyncio
async def test_create_incident(client: AsyncClient, test_tenant):
    response = await client.post(
        "/api/v1/incidents/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "title": "Datalek via email",
            "incident_type": "privacy",
            "severity": "hoog",
            "status": "open",
            "reported_at": datetime.utcnow().isoformat(),
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Datalek via email"
    assert data["incident_type"] == "privacy"
    assert data["severity"] == "hoog"


@pytest.mark.asyncio
async def test_incident_with_corrective_action(client: AsyncClient, test_tenant):
    ca_resp = await client.post(
        "/api/v1/assessments/corrective-actions/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "title": "Incident CA",
            "description": "Fix the incident",
            "due_date": "2024-12-01",
            "status": "open",
        },
    )
    ca_id = ca_resp.json()["id"]

    response = await client.post(
        "/api/v1/incidents/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "title": "Incident with CA",
            "incident_type": "informatiebeveiliging",
            "severity": "gemiddeld",
            "status": "open",
            "reported_at": datetime.utcnow().isoformat(),
            "corrective_action_id": ca_id,
        },
    )
    assert response.status_code == 201
    assert response.json()["corrective_action_id"] == ca_id


@pytest.mark.asyncio
async def test_update_incident_status(client: AsyncClient, test_tenant):
    create_resp = await client.post(
        "/api/v1/incidents/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "title": "Status Update Incident",
            "incident_type": "continuiteit",
            "severity": "laag",
            "status": "open",
            "reported_at": datetime.utcnow().isoformat(),
        },
    )
    incident_id = create_resp.json()["id"]

    response = await client.patch(
        f"/api/v1/incidents/{incident_id}",
        json={"status": "in_behandeling"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "in_behandeling"

    response = await client.patch(
        f"/api/v1/incidents/{incident_id}",
        json={"status": "afgerond", "resolved_at": datetime.utcnow().isoformat()},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "afgerond"
    assert response.json()["resolved_at"] is not None


@pytest.mark.asyncio
async def test_list_incidents(client: AsyncClient, test_tenant):
    response = await client.get(
        "/api/v1/incidents/",
        params={"tenant_id": test_tenant["id"]},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_incident_not_found(client: AsyncClient):
    response = await client.get(f"/api/v1/incidents/{uuid.uuid4()}")
    assert response.status_code == 404
