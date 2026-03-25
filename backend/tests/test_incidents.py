import uuid
import pytest
from httpx import AsyncClient
from datetime import datetime
from tests.conftest import make_token


@pytest.mark.asyncio
async def test_create_incident(client: AsyncClient, test_tenant, tenant_token):
    response = await client.post(
        "/api/v1/incidents/",
        json={
            "title": "Datalek via email",
            "incident_type": "privacy",
            "severity": "hoog",
            "status": "open",
            "reported_at": datetime.utcnow().isoformat(),
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Datalek via email"
    assert data["incident_type"] == "privacy"
    assert data["severity"] == "hoog"


@pytest.mark.asyncio
async def test_incident_with_corrective_action(client: AsyncClient, test_tenant, tenant_token):
    ca_resp = await client.post(
        "/api/v1/assessments/corrective-actions/",
        json={
            "title": "Incident CA",
            "description": "Fix the incident",
            "due_date": "2024-12-01",
            "status": "open",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    ca_id = ca_resp.json()["id"]

    response = await client.post(
        "/api/v1/incidents/",
        json={
            "title": "Incident with CA",
            "incident_type": "informatiebeveiliging",
            "severity": "gemiddeld",
            "status": "open",
            "reported_at": datetime.utcnow().isoformat(),
            "corrective_action_id": ca_id,
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 201
    assert response.json()["corrective_action_id"] == ca_id


@pytest.mark.asyncio
async def test_update_incident_status(client: AsyncClient, test_tenant, tenant_token):
    create_resp = await client.post(
        "/api/v1/incidents/",
        json={
            "title": "Status Update Incident",
            "incident_type": "continuiteit",
            "severity": "laag",
            "status": "open",
            "reported_at": datetime.utcnow().isoformat(),
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    incident_id = create_resp.json()["id"]

    response = await client.patch(
        f"/api/v1/incidents/{incident_id}",
        json={"status": "in_behandeling"},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "in_behandeling"

    response = await client.patch(
        f"/api/v1/incidents/{incident_id}",
        json={"status": "afgerond", "resolved_at": datetime.utcnow().isoformat()},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "afgerond"
    assert response.json()["resolved_at"] is not None


@pytest.mark.asyncio
async def test_list_incidents(client: AsyncClient, test_tenant, tenant_token):
    response = await client.get(
        "/api/v1/incidents/",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_incident_not_found(client: AsyncClient, admin_token):
    response = await client.get(
        f"/api/v1/incidents/{uuid.uuid4()}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404
