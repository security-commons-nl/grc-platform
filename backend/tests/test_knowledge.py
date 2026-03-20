import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_knowledge_chunk(client: AsyncClient, test_tenant):
    response = await client.post(
        "/api/v1/knowledge/",
        json={
            "layer": "organisatie",
            "tenant_id": test_tenant["id"],
            "source_type": "beleid",
            "chunk_index": 0,
            "content": "Het informatiebeveiliigingsbeleid van Gemeente Leiden is gebaseerd op ISO 27001:2022.",
            "model_used": "mistral-small-latest",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["layer"] == "organisatie"
    assert data["content"].startswith("Het informatiebeveilig")
    assert data["tenant_id"] == test_tenant["id"]


@pytest.mark.asyncio
async def test_create_normatief_chunk_no_tenant(client: AsyncClient):
    response = await client.post(
        "/api/v1/knowledge/",
        json={
            "layer": "normatief",
            "source_type": "standaard",
            "chunk_index": 0,
            "content": "ISO 27001 clause 4.1 requires understanding context.",
            "model_used": "mistral-small-latest",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["layer"] == "normatief"
    assert data["tenant_id"] is None


@pytest.mark.asyncio
async def test_list_knowledge_filter_layer(client: AsyncClient, test_tenant):
    # Create one of each layer
    await client.post(
        "/api/v1/knowledge/",
        json={
            "layer": "normatief",
            "source_type": "standaard",
            "chunk_index": 10,
            "content": "Normatief test chunk",
            "model_used": "test-model",
        },
    )
    await client.post(
        "/api/v1/knowledge/",
        json={
            "layer": "organisatie",
            "tenant_id": test_tenant["id"],
            "source_type": "beleid",
            "chunk_index": 10,
            "content": "Organisatie test chunk",
            "model_used": "test-model",
        },
    )

    # Filter normatief
    response = await client.get(
        "/api/v1/knowledge/",
        params={"layer": "normatief"},
    )
    assert response.status_code == 200
    for chunk in response.json():
        assert chunk["layer"] == "normatief"

    # Filter organisatie
    response = await client.get(
        "/api/v1/knowledge/",
        params={"layer": "organisatie", "tenant_id": test_tenant["id"]},
    )
    assert response.status_code == 200
    for chunk in response.json():
        assert chunk["layer"] == "organisatie"


@pytest.mark.asyncio
async def test_knowledge_chunk_not_found(client: AsyncClient):
    response = await client.get(f"/api/v1/knowledge/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_knowledge_chunk(client: AsyncClient, test_tenant):
    create_resp = await client.post(
        "/api/v1/knowledge/",
        json={
            "layer": "organisatie",
            "tenant_id": test_tenant["id"],
            "source_type": "besluit",
            "chunk_index": 0,
            "content": "Original content",
            "model_used": "test-model",
        },
    )
    chunk_id = create_resp.json()["id"]

    response = await client.patch(
        f"/api/v1/knowledge/{chunk_id}",
        json={"content": "Updated content"},
    )
    assert response.status_code == 200
    assert response.json()["content"] == "Updated content"


@pytest.mark.asyncio
async def test_delete_knowledge_chunk(client: AsyncClient, test_tenant):
    create_resp = await client.post(
        "/api/v1/knowledge/",
        json={
            "layer": "organisatie",
            "tenant_id": test_tenant["id"],
            "source_type": "beleid",
            "chunk_index": 99,
            "content": "To be deleted",
            "model_used": "test-model",
        },
    )
    chunk_id = create_resp.json()["id"]

    response = await client.delete(f"/api/v1/knowledge/{chunk_id}")
    assert response.status_code == 204

    # Verify deletion
    get_resp = await client.get(f"/api/v1/knowledge/{chunk_id}")
    assert get_resp.status_code == 404
