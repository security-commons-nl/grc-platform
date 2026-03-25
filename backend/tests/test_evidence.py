import uuid
import pytest
from httpx import AsyncClient
from tests.conftest import make_token


@pytest.mark.asyncio
async def test_create_evidence(client: AsyncClient, test_tenant, tenant_token):
    control_resp = await client.post(
        "/api/v1/controls/",
        json={
            "title": "Evidence Control",
            "description": "Test",
            "domain": "ISMS",
            "implementation_status": "ge\u00efmplementeerd",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    control_id = control_resp.json()["id"]

    response = await client.post(
        "/api/v1/evidence/",
        json={
            "control_id": control_id,
            "title": "Firewall configuratie screenshot",
            "evidence_type": "screenshot",
            "storage_path": "/evidence/firewall.png",
            "collected_at": "2024-06-01",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Firewall configuratie screenshot"
    assert data["evidence_type"] == "screenshot"


@pytest.mark.asyncio
async def test_create_evidence_with_valid_until(client: AsyncClient, test_tenant, tenant_token):
    control_resp = await client.post(
        "/api/v1/controls/",
        json={
            "title": "Validity Control",
            "description": "Test",
            "domain": "ISMS",
            "implementation_status": "niet_gestart",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )

    response = await client.post(
        "/api/v1/evidence/",
        json={
            "control_id": control_resp.json()["id"],
            "title": "Pentest rapport",
            "evidence_type": "document",
            "storage_path": "/evidence/pentest.pdf",
            "collected_at": "2024-01-15",
            "valid_until": "2025-01-15",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 201
    assert response.json()["valid_until"] == "2025-01-15"


@pytest.mark.asyncio
async def test_list_evidence_by_control(client: AsyncClient, test_tenant, tenant_token):
    control_resp = await client.post(
        "/api/v1/controls/",
        json={
            "title": "List Evidence Control",
            "description": "Test",
            "domain": "ISMS",
            "implementation_status": "niet_gestart",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    control_id = control_resp.json()["id"]

    await client.post(
        "/api/v1/evidence/",
        json={
            "control_id": control_id,
            "title": "Evidence 1",
            "evidence_type": "document",
            "storage_path": "/evidence/e1.pdf",
            "collected_at": "2024-01-01",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    await client.post(
        "/api/v1/evidence/",
        json={
            "control_id": control_id,
            "title": "Evidence 2",
            "evidence_type": "log",
            "storage_path": "/evidence/e2.log",
            "collected_at": "2024-02-01",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )

    response = await client.get(
        "/api/v1/evidence/",
        params={"control_id": control_id},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 200
    assert len(response.json()) >= 2


@pytest.mark.asyncio
async def test_evidence_not_found(client: AsyncClient, admin_token):
    response = await client.get(
        f"/api/v1/evidence/{uuid.uuid4()}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404
