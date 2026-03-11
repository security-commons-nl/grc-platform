"""
Tests for Control Management API endpoints.
Controls are context-specific, testable implementations of Measures.

Covers:
- CRUD operations
- Status transitions (activate, deactivate)
- Effectiveness tracking
- Regression: RLS session.refresh() 500 error (bug d9cb3ad)
"""
import pytest
from httpx import AsyncClient


@pytest.fixture
def sample_control_data() -> dict:
    return {
        "tenant_id": 1,
        "title": "MFA op Azure AD",
        "description": "Multi-factor authenticatie via Conditional Access",
        "control_type": "Preventive",
        "automation_level": "Semi-automated",
        "status": "Draft",
    }


class TestControlCRUD:
    """Basic CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_control(self, client: AsyncClient, sample_control_data: dict):
        """Creating a control returns 200 with id set — regression for RLS 500."""
        response = await client.post("/api/v1/controls/", json=sample_control_data)
        assert response.status_code == 200

        data = response.json()
        assert data["id"] is not None
        assert data["title"] == sample_control_data["title"]
        assert data["control_type"] == "Preventive"
        assert data["status"] == "Draft"

    @pytest.mark.asyncio
    async def test_create_control_minimal(self, client: AsyncClient):
        """Only title + tenant_id required."""
        response = await client.post("/api/v1/controls/", json={
            "tenant_id": 1,
            "title": "Minimale controle",
        })
        assert response.status_code == 200
        assert response.json()["id"] is not None

    @pytest.mark.asyncio
    async def test_list_controls(self, client: AsyncClient, sample_control_data: dict):
        """List returns created control."""
        await client.post("/api/v1/controls/", json=sample_control_data)

        response = await client.get("/api/v1/controls/")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_get_control(self, client: AsyncClient, sample_control_data: dict):
        """Get by id returns correct record."""
        create_resp = await client.post("/api/v1/controls/", json=sample_control_data)
        control_id = create_resp.json()["id"]

        response = await client.get(f"/api/v1/controls/{control_id}")
        assert response.status_code == 200
        assert response.json()["id"] == control_id
        assert response.json()["title"] == sample_control_data["title"]

    @pytest.mark.asyncio
    async def test_get_control_not_found(self, client: AsyncClient):
        response = await client.get("/api/v1/controls/99999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_control(self, client: AsyncClient, sample_control_data: dict):
        """PATCH updates fields correctly — also exercises TenantCRUDBase.update RLS fix."""
        create_resp = await client.post("/api/v1/controls/", json=sample_control_data)
        control_id = create_resp.json()["id"]

        response = await client.patch(
            f"/api/v1/controls/{control_id}",
            json={"title": "Bijgewerkte titel", "description": "Nieuwe omschrijving"},
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Bijgewerkte titel"

    @pytest.mark.asyncio
    async def test_delete_control(self, client: AsyncClient, sample_control_data: dict):
        """Delete removes the control."""
        create_resp = await client.post("/api/v1/controls/", json=sample_control_data)
        control_id = create_resp.json()["id"]

        delete_resp = await client.delete(f"/api/v1/controls/{control_id}")
        assert delete_resp.status_code == 200

        get_resp = await client.get(f"/api/v1/controls/{control_id}")
        assert get_resp.status_code == 404


class TestControlStatusTransitions:
    """Status workflow: Draft → Active → Deprecated."""

    @pytest.mark.asyncio
    async def test_activate_draft_control(self, client: AsyncClient, sample_control_data: dict):
        """Draft control can be activated."""
        create_resp = await client.post("/api/v1/controls/", json=sample_control_data)
        control_id = create_resp.json()["id"]

        response = await client.post(f"/api/v1/controls/{control_id}/activate")
        assert response.status_code == 200
        assert response.json()["status"] == "Active"

    @pytest.mark.asyncio
    async def test_cannot_activate_active_control(self, client: AsyncClient, sample_control_data: dict):
        """Activating an already-active control returns 400."""
        create_resp = await client.post("/api/v1/controls/", json=sample_control_data)
        control_id = create_resp.json()["id"]

        await client.post(f"/api/v1/controls/{control_id}/activate")

        response = await client.post(f"/api/v1/controls/{control_id}/activate")
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_deactivate_active_control(self, client: AsyncClient, sample_control_data: dict):
        """Active control can be deactivated → Deprecated."""
        create_resp = await client.post("/api/v1/controls/", json=sample_control_data)
        control_id = create_resp.json()["id"]

        await client.post(f"/api/v1/controls/{control_id}/activate")

        response = await client.post(f"/api/v1/controls/{control_id}/deactivate")
        assert response.status_code == 200
        assert response.json()["status"] == "Deprecated"

    @pytest.mark.asyncio
    async def test_cannot_deactivate_draft_control(self, client: AsyncClient, sample_control_data: dict):
        """Deactivating a draft control returns 400."""
        create_resp = await client.post("/api/v1/controls/", json=sample_control_data)
        control_id = create_resp.json()["id"]

        response = await client.post(f"/api/v1/controls/{control_id}/deactivate")
        assert response.status_code == 400


class TestControlEffectiveness:
    """Effectiveness tracking."""

    @pytest.mark.asyncio
    async def test_set_effectiveness(self, client: AsyncClient, sample_control_data: dict):
        """Effectiveness percentage can be set (0-100)."""
        create_resp = await client.post("/api/v1/controls/", json=sample_control_data)
        control_id = create_resp.json()["id"]

        response = await client.patch(
            f"/api/v1/controls/{control_id}/effectiveness",
            params={"effectiveness_percentage": 75},
        )
        assert response.status_code == 200
        assert response.json()["effectiveness_percentage"] == 75

    @pytest.mark.asyncio
    async def test_effectiveness_out_of_range(self, client: AsyncClient, sample_control_data: dict):
        """Effectiveness > 100 is rejected."""
        create_resp = await client.post("/api/v1/controls/", json=sample_control_data)
        control_id = create_resp.json()["id"]

        response = await client.patch(
            f"/api/v1/controls/{control_id}/effectiveness",
            params={"effectiveness_percentage": 150},
        )
        assert response.status_code == 422
