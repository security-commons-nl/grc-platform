"""
Tests for Scope Management API endpoints.
Scopes vormen de hiërarchie: Organization → Cluster → Process → Asset → Supplier.
"""
import pytest
from httpx import AsyncClient


@pytest.fixture
def sample_scope_data() -> dict:
    return {
        "tenant_id": 1,
        "name": "IT-afdeling",
        "description": "Alle IT-processen en systemen",
        "type": "Organization",
    }


@pytest.fixture
def sample_child_scope_data() -> dict:
    return {
        "tenant_id": 1,
        "name": "Applicatiebeheer",
        "description": "Beheer van applicaties",
        "type": "Process",
    }


class TestScopeCRUD:
    """Basic CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_scope(self, client: AsyncClient, sample_scope_data: dict):
        response = await client.post("/api/v1/scopes/", json=sample_scope_data)
        assert response.status_code == 200

        data = response.json()
        assert data["id"] is not None
        assert data["name"] == sample_scope_data["name"]
        assert data["tenant_id"] == 1

    @pytest.mark.asyncio
    async def test_list_scopes(self, client: AsyncClient, sample_scope_data: dict):
        await client.post("/api/v1/scopes/", json=sample_scope_data)

        response = await client.get("/api/v1/scopes/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_get_scope(self, client: AsyncClient, sample_scope_data: dict):
        create_resp = await client.post("/api/v1/scopes/", json=sample_scope_data)
        scope_id = create_resp.json()["id"]

        response = await client.get(f"/api/v1/scopes/{scope_id}")
        assert response.status_code == 200
        assert response.json()["id"] == scope_id

    @pytest.mark.asyncio
    async def test_get_scope_not_found(self, client: AsyncClient):
        response = await client.get("/api/v1/scopes/99999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_scope(self, client: AsyncClient, sample_scope_data: dict):
        create_resp = await client.post("/api/v1/scopes/", json=sample_scope_data)
        scope_id = create_resp.json()["id"]

        response = await client.patch(
            f"/api/v1/scopes/{scope_id}",
            json={"name": "Bijgewerkte naam", "description": "Nieuwe omschrijving"},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Bijgewerkte naam"

    @pytest.mark.asyncio
    async def test_delete_scope(self, client: AsyncClient, sample_scope_data: dict):
        """Delete deactivates the scope (soft delete)."""
        create_resp = await client.post("/api/v1/scopes/", json=sample_scope_data)
        scope_id = create_resp.json()["id"]

        delete_resp = await client.delete(f"/api/v1/scopes/{scope_id}")
        assert delete_resp.status_code == 200

        # Scope is soft-deleted (is_active=False) — still retrievable
        get_resp = await client.get(f"/api/v1/scopes/{scope_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["is_active"] is False


class TestScopeHierarchy:
    """Parent-child relaties in de scope-hiërarchie."""

    @pytest.mark.asyncio
    async def test_create_child_scope(
        self, client: AsyncClient, sample_scope_data: dict, sample_child_scope_data: dict
    ):
        """Kind-scope kan gekoppeld worden aan ouder-scope."""
        parent_resp = await client.post("/api/v1/scopes/", json=sample_scope_data)
        parent_id = parent_resp.json()["id"]

        child_data = {**sample_child_scope_data, "parent_id": parent_id, "type": "Process"}
        child_resp = await client.post("/api/v1/scopes/", json=child_data)
        assert child_resp.status_code == 200

        child = child_resp.json()
        assert child["parent_id"] == parent_id

    @pytest.mark.asyncio
    async def test_get_scope_children(self, client: AsyncClient, sample_scope_data: dict):
        """Kind-scopes zijn opvraagbaar via parent endpoint."""
        parent_resp = await client.post("/api/v1/scopes/", json=sample_scope_data)
        parent_id = parent_resp.json()["id"]

        child_data = {
            "tenant_id": 1,
            "name": "Kind-scope",
            "type": "Process",
            "parent_id": parent_id,
        }
        await client.post("/api/v1/scopes/", json=child_data)

        response = await client.get(f"/api/v1/scopes/{parent_id}/children")
        assert response.status_code == 200
        children = response.json()
        assert isinstance(children, list)
        assert any(c["name"] == "Kind-scope" for c in children)

    @pytest.mark.asyncio
    async def test_list_scopes_filter_by_type(self, client: AsyncClient, sample_scope_data: dict):
        """Filteren op scope_type werkt."""
        await client.post("/api/v1/scopes/", json=sample_scope_data)
        await client.post("/api/v1/scopes/", json={
            "tenant_id": 1,
            "name": "Ander type",
            "type": "Asset",
        })

        response = await client.get("/api/v1/scopes/?scope_type=Organization")
        assert response.status_code == 200
        data = response.json()
        assert all(s["type"] == "Organization" for s in data)
