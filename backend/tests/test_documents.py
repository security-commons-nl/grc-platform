import uuid
import pytest
from httpx import AsyncClient
from datetime import datetime
from tests.conftest import make_token


@pytest.mark.asyncio
async def test_create_document(client: AsyncClient, test_tenant, tenant_token):
    response = await client.post(
        "/api/v1/documents/",
        json={
            "document_type": "handboek",
            "title": "ISMS Handboek v1",
            "domain": "ISMS",
            "visibility": "priv\u00e9",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "ISMS Handboek v1"
    assert data["document_type"] == "handboek"


@pytest.mark.asyncio
async def test_list_documents(client: AsyncClient, test_tenant, tenant_token):
    response = await client.get(
        "/api/v1/documents/",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_add_document_version_immutable(client: AsyncClient, test_tenant, tenant_token):
    doc_resp = await client.post(
        "/api/v1/documents/",
        json={
            "document_type": "soa",
            "title": "Statement of Applicability",
            "visibility": "priv\u00e9",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    doc_id = doc_resp.json()["id"]

    response = await client.post(
        "/api/v1/documents/versions/",
        json={
            "document_id": doc_id,
            "version_number": "1.0",
            "status": "concept",
            "content_json": {"chapters": [{"title": "Inleiding"}]},
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["version_number"] == "1.0"
    assert data["document_id"] == doc_id


@pytest.mark.asyncio
async def test_list_document_versions(client: AsyncClient, test_tenant, tenant_token):
    doc_resp = await client.post(
        "/api/v1/documents/",
        json={
            "document_type": "handboek",
            "title": "Test Doc for Versions",
            "visibility": "priv\u00e9",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    doc_id = doc_resp.json()["id"]

    await client.post(
        "/api/v1/documents/versions/",
        json={
            "document_id": doc_id,
            "version_number": "0.1",
            "status": "concept",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )

    response = await client.get(
        "/api/v1/documents/versions/",
        params={"document_id": doc_id},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_create_step_input_document(client: AsyncClient, test_tenant, test_user, tenant_token):
    step_resp = await client.post(
        "/api/v1/steps/",
        json={
            "number": "ID.1",
            "phase": 1,
            "name": "Input Doc Step",
            "waarom_nu": "Test",
            "required_gremium": "sims",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    step = step_resp.json()

    exec_resp = await client.post(
        "/api/v1/steps/executions/",
        json={"step_id": step["id"], "status": "niet_gestart"},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    exec_id = exec_resp.json()["id"]

    response = await client.post(
        "/api/v1/documents/input-documents/",
        json={
            "step_execution_id": exec_id,
            "source_type": "pdf",
            "storage_path": "/uploads/doc.pdf",
            "status": "pending",
            "uploaded_at": datetime.utcnow().isoformat(),
            "uploaded_by_user_id": test_user["id"],
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["source_type"] == "pdf"
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_create_gap_analysis_result(client: AsyncClient, test_tenant, test_user, tenant_token):
    step_resp = await client.post(
        "/api/v1/steps/",
        json={
            "number": "GA.1",
            "phase": 1,
            "name": "Gap Analysis Step",
            "waarom_nu": "Test",
            "required_gremium": "sims",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    exec_resp = await client.post(
        "/api/v1/steps/executions/",
        json={"step_id": step_resp.json()["id"], "status": "niet_gestart"},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    input_doc_resp = await client.post(
        "/api/v1/documents/input-documents/",
        json={
            "step_execution_id": exec_resp.json()["id"],
            "source_type": "pdf",
            "storage_path": "/uploads/gap.pdf",
            "status": "pending",
            "uploaded_at": datetime.utcnow().isoformat(),
            "uploaded_by_user_id": test_user["id"],
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    input_doc_id = input_doc_resp.json()["id"]

    response = await client.post(
        "/api/v1/documents/gap-analysis/",
        json={
            "input_document_id": input_doc_id,
            "field_reference": "\u00a74.1 Context",
            "ai_suggestion": "Organisatiecontext ontbreekt",
            "uncertainty": True,
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["field_reference"] == "\u00a74.1 Context"
    assert data["uncertainty"] is True
    assert data["validated"] is False


@pytest.mark.asyncio
async def test_validate_gap_analysis_result(client: AsyncClient, test_tenant, test_user, tenant_token):
    step_resp = await client.post(
        "/api/v1/steps/",
        json={
            "number": "GV.1",
            "phase": 1,
            "name": "Gap Validate Step",
            "waarom_nu": "Test",
            "required_gremium": "sims",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    exec_resp = await client.post(
        "/api/v1/steps/executions/",
        json={"step_id": step_resp.json()["id"], "status": "niet_gestart"},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    input_doc_resp = await client.post(
        "/api/v1/documents/input-documents/",
        json={
            "step_execution_id": exec_resp.json()["id"],
            "source_type": "docx",
            "storage_path": "/uploads/validate.docx",
            "status": "pending",
            "uploaded_at": datetime.utcnow().isoformat(),
            "uploaded_by_user_id": test_user["id"],
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    gap_resp = await client.post(
        "/api/v1/documents/gap-analysis/",
        json={
            "input_document_id": input_doc_resp.json()["id"],
            "field_reference": "\u00a75.2 Policy",
            "ai_suggestion": "Beleid voldoet",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    gap_id = gap_resp.json()["id"]

    response = await client.patch(
        f"/api/v1/documents/gap-analysis/{gap_id}",
        json={"validated": True, "validated_by_user_id": test_user["id"]},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["validated"] is True
    assert data["validated_at"] is not None
    assert data["validated_by_user_id"] == test_user["id"]
