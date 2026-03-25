import uuid
import pytest
from httpx import AsyncClient
from datetime import date, datetime
from tests.conftest import make_token


@pytest.mark.asyncio
async def test_create_standard(client: AsyncClient, admin_token):
    response = await client.post(
        "/api/v1/standards/",
        json={
            "name": "ISO 27001",
            "version": "2022",
            "published_at": "2022-10-25",
            "status": "actief",
            "domain": "ISMS",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "ISO 27001"
    assert data["version"] == "2022"
    assert data["domain"] == "ISMS"


@pytest.mark.asyncio
async def test_list_standards(client: AsyncClient, admin_token):
    response = await client.get(
        "/api/v1/standards/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_requirement(client: AsyncClient, admin_token):
    std_resp = await client.post(
        "/api/v1/standards/",
        json={
            "name": "BIO",
            "version": "2.0",
            "status": "actief",
            "domain": "ISMS",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    std_id = std_resp.json()["id"]

    response = await client.post(
        "/api/v1/standards/requirements/",
        json={
            "standard_id": std_id,
            "code": "BIO-5.1",
            "title": "Informatiebeveiligingsbeleid",
            "description": "Een set beleidsregels voor informatiebeveiliging",
            "domain": "ISMS",
            "is_mandatory": True,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "BIO-5.1"
    assert data["is_mandatory"] is True


@pytest.mark.asyncio
async def test_create_requirement_mapping(client: AsyncClient, admin_token):
    std1_resp = await client.post(
        "/api/v1/standards/",
        json={"name": "ISO27001-Map", "version": "2022", "status": "actief", "domain": "ISMS"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    std2_resp = await client.post(
        "/api/v1/standards/",
        json={"name": "BIO-Map", "version": "2.0", "status": "actief", "domain": "ISMS"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    req1_resp = await client.post(
        "/api/v1/standards/requirements/",
        json={
            "standard_id": std1_resp.json()["id"],
            "code": "A.5.1",
            "title": "Policies",
            "description": "Information security policies",
            "domain": "ISMS",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    req2_resp = await client.post(
        "/api/v1/standards/requirements/",
        json={
            "standard_id": std2_resp.json()["id"],
            "code": "BIO-5.1-M",
            "title": "Beleid",
            "description": "Beveiligingsbeleid",
            "domain": "ISMS",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    response = await client.post(
        "/api/v1/standards/mappings/",
        json={
            "source_requirement_id": req1_resp.json()["id"],
            "target_requirement_id": req2_resp.json()["id"],
            "norm_version_source": "ISO 27001:2022",
            "confidence_score": 0.95,
            "created_by": "ai",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert float(data["confidence_score"]) == 0.95
    assert data["created_by"] == "ai"


@pytest.mark.asyncio
async def test_create_tenant_normenkader(client: AsyncClient, test_tenant, tenant_token):
    std_resp = await client.post(
        "/api/v1/standards/",
        json={"name": "ISO27001-NK", "version": "2022", "status": "actief", "domain": "ISMS"},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )

    response = await client.post(
        "/api/v1/standards/normenkader/",
        json={
            "standard_id": std_resp.json()["id"],
            "adopted_at": "2024-01-01",
            "is_active": True,
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["tenant_id"] == test_tenant["id"]
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_create_standard_ingestion(client: AsyncClient, test_tenant, test_user, tenant_token):
    response = await client.post(
        "/api/v1/standards/ingestions/",
        json={
            "uploaded_by_user_id": test_user["id"],
            "source_type": "pdf",
            "source_path": "/uploads/standard.pdf",
            "status": "parsing",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "parsing"
    assert data["source_type"] == "pdf"


@pytest.mark.asyncio
async def test_update_ingestion_status(client: AsyncClient, test_tenant, test_user, tenant_token):
    create_resp = await client.post(
        "/api/v1/standards/ingestions/",
        json={
            "uploaded_by_user_id": test_user["id"],
            "source_type": "url",
            "source_path": "https://example.com/standard",
            "status": "parsing",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    ingestion_id = create_resp.json()["id"]

    response = await client.patch(
        f"/api/v1/standards/ingestions/{ingestion_id}",
        json={
            "status": "pending_review",
            "parsed_requirements_json": [{"code": "5.1", "title": "Test"}],
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending_review"
    assert len(data["parsed_requirements_json"]) == 1
