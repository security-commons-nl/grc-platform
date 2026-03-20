import uuid
import pytest
from httpx import AsyncClient


async def _create_scope(client, tenant_id):
    resp = await client.post(
        "/api/v1/scopes/",
        params={"tenant_id": tenant_id},
        json={"type": "cluster", "name": f"Risk Scope {uuid.uuid4().hex[:6]}", "domain": "ISMS"},
    )
    return resp.json()


@pytest.mark.asyncio
async def test_create_risk_auto_score(client: AsyncClient, test_tenant):
    scope = await _create_scope(client, test_tenant["id"])

    response = await client.post(
        "/api/v1/risks/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "scope_id": scope["id"],
            "domain": "ISMS",
            "title": "Ransomware aanval",
            "description": "Risico op ransomware",
            "likelihood": 3,
            "impact": 4,
            "status": "open",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Ransomware aanval"
    assert data["risk_score"] == 12  # 3 * 4
    assert data["risk_level"] == "oranje"  # 10-14


@pytest.mark.asyncio
async def test_risk_level_groen(client: AsyncClient, test_tenant):
    scope = await _create_scope(client, test_tenant["id"])

    response = await client.post(
        "/api/v1/risks/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "scope_id": scope["id"],
            "domain": "ISMS",
            "title": "Laag risico",
            "description": "Minimaal risico",
            "likelihood": 1,
            "impact": 2,
            "status": "open",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["risk_score"] == 2
    assert data["risk_level"] == "groen"


@pytest.mark.asyncio
async def test_risk_level_geel(client: AsyncClient, test_tenant):
    scope = await _create_scope(client, test_tenant["id"])

    response = await client.post(
        "/api/v1/risks/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "scope_id": scope["id"],
            "domain": "ISMS",
            "title": "Gemiddeld risico",
            "description": "Test",
            "likelihood": 3,
            "impact": 3,
            "status": "open",
        },
    )
    data = response.json()
    assert data["risk_score"] == 9
    assert data["risk_level"] == "geel"


@pytest.mark.asyncio
async def test_risk_level_rood(client: AsyncClient, test_tenant):
    scope = await _create_scope(client, test_tenant["id"])

    response = await client.post(
        "/api/v1/risks/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "scope_id": scope["id"],
            "domain": "ISMS",
            "title": "Kritiek risico",
            "description": "Zeer hoog risico",
            "likelihood": 5,
            "impact": 5,
            "status": "open",
        },
    )
    data = response.json()
    assert data["risk_score"] == 25
    assert data["risk_level"] == "rood"


@pytest.mark.asyncio
async def test_update_risk_recalculates_level(client: AsyncClient, test_tenant):
    scope = await _create_scope(client, test_tenant["id"])

    create_resp = await client.post(
        "/api/v1/risks/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "scope_id": scope["id"],
            "domain": "ISMS",
            "title": "Update Risk",
            "description": "Test update",
            "likelihood": 1,
            "impact": 1,
            "status": "open",
        },
    )
    risk_id = create_resp.json()["id"]
    assert create_resp.json()["risk_level"] == "groen"

    # Update to high likelihood
    response = await client.patch(
        f"/api/v1/risks/{risk_id}",
        json={"likelihood": 5, "impact": 5},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] == "rood"


@pytest.mark.asyncio
async def test_list_risks_filter(client: AsyncClient, test_tenant):
    response = await client.get(
        "/api/v1/risks/",
        params={"tenant_id": test_tenant["id"], "domain": "ISMS"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_risk_not_found(client: AsyncClient):
    response = await client.get(f"/api/v1/risks/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_risk_control_link(client: AsyncClient, test_tenant):
    scope = await _create_scope(client, test_tenant["id"])

    risk_resp = await client.post(
        "/api/v1/risks/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "scope_id": scope["id"],
            "domain": "ISMS",
            "title": "Link Test Risk",
            "description": "Test",
            "likelihood": 2,
            "impact": 3,
            "status": "open",
        },
    )
    risk_id = risk_resp.json()["id"]

    control_resp = await client.post(
        "/api/v1/controls/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "title": "Link Test Control",
            "description": "Test",
            "domain": "ISMS",
            "implementation_status": "niet_gestart",
        },
    )
    control_id = control_resp.json()["id"]

    # Create link
    link_resp = await client.post(
        "/api/v1/risks/links/",
        json={"risk_id": risk_id, "control_id": control_id},
    )
    assert link_resp.status_code == 201
    assert link_resp.json()["risk_id"] == risk_id
    assert link_resp.json()["control_id"] == control_id

    # Delete link
    del_resp = await client.delete(f"/api/v1/risks/links/{risk_id}/{control_id}")
    assert del_resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_risk_cascades_links(client: AsyncClient, test_tenant):
    scope = await _create_scope(client, test_tenant["id"])

    risk_resp = await client.post(
        "/api/v1/risks/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "scope_id": scope["id"],
            "domain": "ISMS",
            "title": "Cascade Delete Risk",
            "description": "Test",
            "likelihood": 2,
            "impact": 2,
            "status": "open",
        },
    )
    risk_id = risk_resp.json()["id"]

    control_resp = await client.post(
        "/api/v1/controls/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "title": "Cascade Delete Control",
            "description": "Test",
            "domain": "ISMS",
            "implementation_status": "niet_gestart",
        },
    )
    control_id = control_resp.json()["id"]

    await client.post(
        "/api/v1/risks/links/",
        json={"risk_id": risk_id, "control_id": control_id},
    )

    # Delete risk should also delete link
    del_resp = await client.delete(f"/api/v1/risks/{risk_id}")
    assert del_resp.status_code == 204

    # Verify link is gone
    links_resp = await client.get(
        "/api/v1/risks/links/",
        params={"risk_id": risk_id},
    )
    assert len(links_resp.json()) == 0
