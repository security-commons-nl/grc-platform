import uuid
import pytest
from httpx import AsyncClient
from tests.conftest import make_token


@pytest.mark.asyncio
async def test_create_tenant(client: AsyncClient, admin_token):
    response = await client.post(
        "/api/v1/tenants/",
        json={"name": "Gemeente Test", "type": "single"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Gemeente Test"
    assert data["type"] == "single"
    assert data["is_active"] is True
    assert "id" in data


@pytest.mark.asyncio
async def test_create_tenant_centrum(client: AsyncClient, admin_token):
    response = await client.post(
        "/api/v1/tenants/",
        json={"name": "Gemeente Centrum", "type": "centrum"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201
    assert response.json()["type"] == "centrum"


@pytest.mark.asyncio
async def test_list_tenants(client: AsyncClient, test_tenant, tenant_token):
    response = await client.get(
        "/api/v1/tenants/",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_tenant(client: AsyncClient, test_tenant, tenant_token):
    response = await client.get(
        f"/api/v1/tenants/{test_tenant['id']}",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Gemeente Leiden"


@pytest.mark.asyncio
async def test_tenant_not_found(client: AsyncClient, admin_token):
    response = await client.get(
        f"/api/v1/tenants/{uuid.uuid4()}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_tenant(client: AsyncClient, test_tenant, tenant_token):
    response = await client.patch(
        f"/api/v1/tenants/{test_tenant['id']}",
        json={"name": "Gemeente Leiden Updated"},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Gemeente Leiden Updated"


@pytest.mark.asyncio
async def test_create_region(client: AsyncClient, test_tenant, tenant_token):
    response = await client.post(
        "/api/v1/tenants/regions/",
        json={"name": "Regio Holland", "centrum_tenant_id": test_tenant["id"]},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Regio Holland"
    assert data["centrum_tenant_id"] == test_tenant["id"]


@pytest.mark.asyncio
async def test_list_regions(client: AsyncClient, test_region, tenant_token):
    response = await client.get(
        "/api/v1/tenants/regions/",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient, test_tenant, tenant_token):
    response = await client.post(
        "/api/v1/tenants/users/",
        json={
            "name": "Jan de Vries",
            "email": "jan@leiden.nl",
            "external_id": f"jan-{uuid.uuid4().hex[:8]}",
            "tenant_id": test_tenant["id"],
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Jan de Vries"
    assert data["tenant_id"] == test_tenant["id"]


@pytest.mark.asyncio
async def test_list_users(client: AsyncClient, test_tenant, test_user, tenant_token):
    response = await client.get(
        "/api/v1/tenants/users/",
        params={"tenant_id": test_tenant["id"]},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_assign_tenant_role(client: AsyncClient, test_tenant, test_user, tenant_token):
    response = await client.post(
        "/api/v1/tenants/user-tenant-roles/",
        json={
            "user_id": test_user["id"],
            "tenant_id": test_tenant["id"],
            "role": "admin",
            "domain": "ISMS",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["role"] == "admin"
    assert data["domain"] == "ISMS"


@pytest.mark.asyncio
async def test_assign_region_role(client: AsyncClient, test_region, test_user, tenant_token):
    response = await client.post(
        "/api/v1/tenants/user-region-roles/",
        json={
            "user_id": test_user["id"],
            "region_id": test_region["id"],
            "role": "regionaal_toezichthouder",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 201
    assert response.json()["role"] == "regionaal_toezichthouder"


@pytest.mark.asyncio
async def test_unauthenticated_tenant_list(client: AsyncClient):
    response = await client.get("/api/v1/tenants/")
    assert response.status_code == 401
