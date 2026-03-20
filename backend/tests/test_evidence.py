import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_evidence(client: AsyncClient, test_tenant):
    control_resp = await client.post(
        "/api/v1/controls/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "title": "Evidence Control",
            "description": "Test",
            "domain": "ISMS",
            "implementation_status": "ge\u00efmplementeerd",
        },
    )
    control_id = control_resp.json()["id"]

    response = await client.post(
        "/api/v1/evidence/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "control_id": control_id,
            "title": "Firewall configuratie screenshot",
            "evidence_type": "screenshot",
            "storage_path": "/evidence/firewall.png",
            "collected_at": "2024-06-01",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Firewall configuratie screenshot"
    assert data["evidence_type"] == "screenshot"


@pytest.mark.asyncio
async def test_create_evidence_with_valid_until(client: AsyncClient, test_tenant):
    control_resp = await client.post(
        "/api/v1/controls/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "title": "Validity Control",
            "description": "Test",
            "domain": "ISMS",
            "implementation_status": "niet_gestart",
        },
    )

    response = await client.post(
        "/api/v1/evidence/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "control_id": control_resp.json()["id"],
            "title": "Pentest rapport",
            "evidence_type": "document",
            "storage_path": "/evidence/pentest.pdf",
            "collected_at": "2024-01-15",
            "valid_until": "2025-01-15",
        },
    )
    assert response.status_code == 201
    assert response.json()["valid_until"] == "2025-01-15"


@pytest.mark.asyncio
async def test_list_evidence_by_control(client: AsyncClient, test_tenant):
    control_resp = await client.post(
        "/api/v1/controls/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "title": "List Evidence Control",
            "description": "Test",
            "domain": "ISMS",
            "implementation_status": "niet_gestart",
        },
    )
    control_id = control_resp.json()["id"]

    await client.post(
        "/api/v1/evidence/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "control_id": control_id,
            "title": "Evidence 1",
            "evidence_type": "document",
            "storage_path": "/evidence/e1.pdf",
            "collected_at": "2024-01-01",
        },
    )
    await client.post(
        "/api/v1/evidence/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "control_id": control_id,
            "title": "Evidence 2",
            "evidence_type": "log",
            "storage_path": "/evidence/e2.log",
            "collected_at": "2024-02-01",
        },
    )

    response = await client.get(
        "/api/v1/evidence/",
        params={"tenant_id": test_tenant["id"], "control_id": control_id},
    )
    assert response.status_code == 200
    assert len(response.json()) >= 2


@pytest.mark.asyncio
async def test_evidence_not_found(client: AsyncClient):
    response = await client.get(f"/api/v1/evidence/{uuid.uuid4()}")
    assert response.status_code == 404
