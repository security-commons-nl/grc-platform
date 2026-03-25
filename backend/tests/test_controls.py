import uuid
import pytest
from httpx import AsyncClient
from tests.conftest import make_token


@pytest.mark.asyncio
async def test_create_control(client: AsyncClient, test_tenant, tenant_token):
    response = await client.post(
        "/api/v1/controls/",
        json={
            "title": "Toegangscontrole",
            "description": "Beheer van toegangsrechten",
            "domain": "ISMS",
            "implementation_status": "niet_gestart",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Toegangscontrole"
    assert data["implementation_status"] == "niet_gestart"


@pytest.mark.asyncio
async def test_create_control_with_requirement(client: AsyncClient, test_tenant, tenant_token):
    std_resp = await client.post(
        "/api/v1/standards/",
        json={"name": "ISO27001-Ctrl", "version": "2022", "status": "actief", "domain": "ISMS"},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    req_resp = await client.post(
        "/api/v1/standards/requirements/",
        json={
            "standard_id": std_resp.json()["id"],
            "code": "A.8.1",
            "title": "User endpoint devices",
            "description": "Protect info on endpoint devices",
            "domain": "ISMS",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )

    response = await client.post(
        "/api/v1/controls/",
        json={
            "requirement_id": req_resp.json()["id"],
            "title": "Endpoint Protection",
            "description": "Deploy endpoint security",
            "domain": "ISMS",
            "implementation_status": "in_uitvoering",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 201
    assert response.json()["requirement_id"] == req_resp.json()["id"]


@pytest.mark.asyncio
async def test_update_implementation_status(client: AsyncClient, test_tenant, tenant_token):
    create_resp = await client.post(
        "/api/v1/controls/",
        json={
            "title": "Status Update Control",
            "description": "Test",
            "domain": "ISMS",
            "implementation_status": "niet_gestart",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    control_id = create_resp.json()["id"]

    response = await client.patch(
        f"/api/v1/controls/{control_id}",
        json={"implementation_status": "ge\u00efmplementeerd", "implementation_date": "2024-06-01"},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["implementation_status"] == "ge\u00efmplementeerd"
    assert data["implementation_date"] == "2024-06-01"


@pytest.mark.asyncio
async def test_list_controls(client: AsyncClient, test_tenant, tenant_token):
    response = await client.get(
        "/api/v1/controls/",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_delete_control_cascades_links(client: AsyncClient, test_tenant, tenant_token):
    # Create a scope, risk and control, link them, then delete control
    scope_resp = await client.post(
        "/api/v1/scopes/",
        json={"type": "cluster", "name": "Ctrl Cascade Test", "domain": "ISMS"},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    risk_resp = await client.post(
        "/api/v1/risks/",
        json={
            "scope_id": scope_resp.json()["id"],
            "domain": "ISMS",
            "title": "Ctrl Cascade Risk",
            "description": "Test",
            "likelihood": 2,
            "impact": 2,
            "status": "open",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    ctrl_resp = await client.post(
        "/api/v1/controls/",
        json={
            "title": "Ctrl to Delete",
            "description": "Test",
            "domain": "ISMS",
            "implementation_status": "niet_gestart",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )

    await client.post(
        "/api/v1/risks/links/",
        json={"risk_id": risk_resp.json()["id"], "control_id": ctrl_resp.json()["id"]},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )

    del_resp = await client.delete(
        f"/api/v1/controls/{ctrl_resp.json()['id']}",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert del_resp.status_code == 204


@pytest.mark.asyncio
async def test_control_not_found(client: AsyncClient, admin_token):
    response = await client.get(
        f"/api/v1/controls/{uuid.uuid4()}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404
