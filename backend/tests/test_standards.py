import uuid
import pytest
from httpx import AsyncClient
from datetime import date, datetime


@pytest.mark.asyncio
async def test_create_standard(client: AsyncClient):
    response = await client.post(
        "/api/v1/standards/",
        json={
            "name": "ISO 27001",
            "version": "2022",
            "published_at": "2022-10-25",
            "status": "actief",
            "domain": "ISMS",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "ISO 27001"
    assert data["version"] == "2022"
    assert data["domain"] == "ISMS"


@pytest.mark.asyncio
async def test_list_standards(client: AsyncClient):
    response = await client.get("/api/v1/standards/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_requirement(client: AsyncClient):
    std_resp = await client.post(
        "/api/v1/standards/",
        json={
            "name": "BIO",
            "version": "2.0",
            "status": "actief",
            "domain": "ISMS",
        },
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
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "BIO-5.1"
    assert data["is_mandatory"] is True


@pytest.mark.asyncio
async def test_create_requirement_mapping(client: AsyncClient):
    std1_resp = await client.post(
        "/api/v1/standards/",
        json={"name": "ISO27001-Map", "version": "2022", "status": "actief", "domain": "ISMS"},
    )
    std2_resp = await client.post(
        "/api/v1/standards/",
        json={"name": "BIO-Map", "version": "2.0", "status": "actief", "domain": "ISMS"},
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
    )
    assert response.status_code == 201
    data = response.json()
    assert float(data["confidence_score"]) == 0.95
    assert data["created_by"] == "ai"


@pytest.mark.asyncio
async def test_create_tenant_normenkader(client: AsyncClient, test_tenant):
    std_resp = await client.post(
        "/api/v1/standards/",
        json={"name": "ISO27001-NK", "version": "2022", "status": "actief", "domain": "ISMS"},
    )

    response = await client.post(
        "/api/v1/standards/normenkader/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "standard_id": std_resp.json()["id"],
            "adopted_at": "2024-01-01",
            "is_active": True,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["tenant_id"] == test_tenant["id"]
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_create_standard_ingestion(client: AsyncClient, test_tenant, test_user):
    response = await client.post(
        "/api/v1/standards/ingestions/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "uploaded_by_user_id": test_user["id"],
            "source_type": "pdf",
            "source_path": "/uploads/standard.pdf",
            "status": "parsing",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "parsing"
    assert data["source_type"] == "pdf"


@pytest.mark.asyncio
async def test_update_ingestion_status(client: AsyncClient, test_tenant, test_user):
    create_resp = await client.post(
        "/api/v1/standards/ingestions/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "uploaded_by_user_id": test_user["id"],
            "source_type": "url",
            "source_path": "https://example.com/standard",
            "status": "parsing",
        },
    )
    ingestion_id = create_resp.json()["id"]

    response = await client.patch(
        f"/api/v1/standards/ingestions/{ingestion_id}",
        json={
            "status": "pending_review",
            "parsed_requirements_json": [{"code": "5.1", "title": "Test"}],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending_review"
    assert len(data["parsed_requirements_json"]) == 1
