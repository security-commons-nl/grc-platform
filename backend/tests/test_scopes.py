import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_scope_organisatie(client: AsyncClient, test_tenant):
    response = await client.post(
        "/api/v1/scopes/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "type": "organisatie",
            "name": "Gemeente Leiden",
            "domain": "ISMS",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "organisatie"
    assert data["name"] == "Gemeente Leiden"


@pytest.mark.asyncio
async def test_create_scope_hierarchy(client: AsyncClient, test_tenant):
    # Create org scope
    org_resp = await client.post(
        "/api/v1/scopes/",
        params={"tenant_id": test_tenant["id"]},
        json={"type": "organisatie", "name": "Org Hierarchy Test", "domain": "ISMS"},
    )
    org_id = org_resp.json()["id"]

    # Create cluster under org
    cluster_resp = await client.post(
        "/api/v1/scopes/",
        params={"tenant_id": test_tenant["id"]},
        json={"type": "cluster", "name": "ICT Cluster", "parent_id": org_id, "domain": "ISMS"},
    )
    cluster_id = cluster_resp.json()["id"]
    assert cluster_resp.json()["parent_id"] == org_id

    # Create process under cluster
    process_resp = await client.post(
        "/api/v1/scopes/",
        params={"tenant_id": test_tenant["id"]},
        json={"type": "proces", "name": "Backup Proces", "parent_id": cluster_id, "domain": "ISMS"},
    )
    assert process_resp.json()["parent_id"] == cluster_id

    # Create asset under process
    asset_resp = await client.post(
        "/api/v1/scopes/",
        params={"tenant_id": test_tenant["id"]},
        json={"type": "asset", "name": "Server01", "parent_id": process_resp.json()["id"]},
    )
    assert asset_resp.status_code == 201
    assert asset_resp.json()["type"] == "asset"


@pytest.mark.asyncio
async def test_scope_verwerkt_pii(client: AsyncClient, test_tenant):
    response = await client.post(
        "/api/v1/scopes/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "type": "proces",
            "name": "HR Proces",
            "domain": "PIMS",
            "verwerkt_pii": True,
            "ext_verwerking_ref": "VWR-001",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["verwerkt_pii"] is True
    assert data["ext_verwerking_ref"] == "VWR-001"


@pytest.mark.asyncio
async def test_list_scopes_filter(client: AsyncClient, test_tenant):
    await client.post(
        "/api/v1/scopes/",
        params={"tenant_id": test_tenant["id"]},
        json={"type": "organisatie", "name": "Filter Test", "domain": "BCMS"},
    )

    response = await client.get(
        "/api/v1/scopes/",
        params={"tenant_id": test_tenant["id"], "domain": "BCMS"},
    )
    assert response.status_code == 200
    for scope in response.json():
        assert scope["domain"] == "BCMS"


@pytest.mark.asyncio
async def test_scope_not_found(client: AsyncClient):
    response = await client.get(f"/api/v1/scopes/{uuid.uuid4()}")
    assert response.status_code == 404
