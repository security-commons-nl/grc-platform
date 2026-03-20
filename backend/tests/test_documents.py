import uuid
import pytest
from httpx import AsyncClient
from datetime import datetime


@pytest.mark.asyncio
async def test_create_document(client: AsyncClient, test_tenant):
    response = await client.post(
        "/api/v1/documents/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "document_type": "handboek",
            "title": "ISMS Handboek v1",
            "domain": "ISMS",
            "visibility": "privé",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "ISMS Handboek v1"
    assert data["document_type"] == "handboek"


@pytest.mark.asyncio
async def test_list_documents(client: AsyncClient, test_tenant):
    response = await client.get(
        "/api/v1/documents/",
        params={"tenant_id": test_tenant["id"]},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_add_document_version_immutable(client: AsyncClient, test_tenant):
    doc_resp = await client.post(
        "/api/v1/documents/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "document_type": "soa",
            "title": "Statement of Applicability",
            "visibility": "privé",
        },
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
    )
    assert response.status_code == 201
    data = response.json()
    assert data["version_number"] == "1.0"
    assert data["document_id"] == doc_id


@pytest.mark.asyncio
async def test_list_document_versions(client: AsyncClient, test_tenant):
    doc_resp = await client.post(
        "/api/v1/documents/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "document_type": "handboek",
            "title": "Test Doc for Versions",
            "visibility": "privé",
        },
    )
    doc_id = doc_resp.json()["id"]

    await client.post(
        "/api/v1/documents/versions/",
        json={
            "document_id": doc_id,
            "version_number": "0.1",
            "status": "concept",
        },
    )

    response = await client.get(
        "/api/v1/documents/versions/",
        params={"document_id": doc_id},
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_create_step_input_document(client: AsyncClient, test_tenant, test_user):
    step_resp = await client.post(
        "/api/v1/steps/",
        json={
            "number": "ID.1",
            "phase": 1,
            "name": "Input Doc Step",
            "waarom_nu": "Test",
            "required_gremium": "sims",
        },
    )
    step = step_resp.json()

    exec_resp = await client.post(
        "/api/v1/steps/executions/",
        params={"tenant_id": test_tenant["id"]},
        json={"step_id": step["id"], "status": "niet_gestart"},
    )
    exec_id = exec_resp.json()["id"]

    response = await client.post(
        "/api/v1/documents/input-documents/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "step_execution_id": exec_id,
            "source_type": "pdf",
            "storage_path": "/uploads/doc.pdf",
            "status": "pending",
            "uploaded_at": datetime.utcnow().isoformat(),
            "uploaded_by_user_id": test_user["id"],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["source_type"] == "pdf"
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_create_gap_analysis_result(client: AsyncClient, test_tenant, test_user):
    step_resp = await client.post(
        "/api/v1/steps/",
        json={
            "number": "GA.1",
            "phase": 1,
            "name": "Gap Analysis Step",
            "waarom_nu": "Test",
            "required_gremium": "sims",
        },
    )
    exec_resp = await client.post(
        "/api/v1/steps/executions/",
        params={"tenant_id": test_tenant["id"]},
        json={"step_id": step_resp.json()["id"], "status": "niet_gestart"},
    )
    input_doc_resp = await client.post(
        "/api/v1/documents/input-documents/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "step_execution_id": exec_resp.json()["id"],
            "source_type": "pdf",
            "storage_path": "/uploads/gap.pdf",
            "status": "pending",
            "uploaded_at": datetime.utcnow().isoformat(),
            "uploaded_by_user_id": test_user["id"],
        },
    )
    input_doc_id = input_doc_resp.json()["id"]

    response = await client.post(
        "/api/v1/documents/gap-analysis/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "input_document_id": input_doc_id,
            "field_reference": "§4.1 Context",
            "ai_suggestion": "Organisatiecontext ontbreekt",
            "uncertainty": True,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["field_reference"] == "§4.1 Context"
    assert data["uncertainty"] is True
    assert data["validated"] is False


@pytest.mark.asyncio
async def test_validate_gap_analysis_result(client: AsyncClient, test_tenant, test_user):
    step_resp = await client.post(
        "/api/v1/steps/",
        json={
            "number": "GV.1",
            "phase": 1,
            "name": "Gap Validate Step",
            "waarom_nu": "Test",
            "required_gremium": "sims",
        },
    )
    exec_resp = await client.post(
        "/api/v1/steps/executions/",
        params={"tenant_id": test_tenant["id"]},
        json={"step_id": step_resp.json()["id"], "status": "niet_gestart"},
    )
    input_doc_resp = await client.post(
        "/api/v1/documents/input-documents/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "step_execution_id": exec_resp.json()["id"],
            "source_type": "docx",
            "storage_path": "/uploads/validate.docx",
            "status": "pending",
            "uploaded_at": datetime.utcnow().isoformat(),
            "uploaded_by_user_id": test_user["id"],
        },
    )
    gap_resp = await client.post(
        "/api/v1/documents/gap-analysis/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "input_document_id": input_doc_resp.json()["id"],
            "field_reference": "§5.2 Policy",
            "ai_suggestion": "Beleid voldoet",
        },
    )
    gap_id = gap_resp.json()["id"]

    response = await client.patch(
        f"/api/v1/documents/gap-analysis/{gap_id}",
        json={"validated": True, "validated_by_user_id": test_user["id"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["validated"] is True
    assert data["validated_at"] is not None
    assert data["validated_by_user_id"] == test_user["id"]
