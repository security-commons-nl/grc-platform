"""
Tests for Control Management API endpoints.
"""
import pytest
from httpx import AsyncClient

class TestControls:
    """Test control management."""

    @pytest.mark.asyncio
    async def test_create_control(self, client: AsyncClient, sample_control_data: dict):
        """Test creating a new control."""
        response = await client.post("/api/v1/controls/", json=sample_control_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == sample_control_data["title"]
        assert data["status"] == "Draft"
        assert data["id"] is not None

    @pytest.mark.asyncio
    async def test_list_controls(self, client: AsyncClient, sample_control_data: dict):
        """Test listing controls."""
        await client.post("/api/v1/controls/", json=sample_control_data)
        response = await client.get("/api/v1/controls/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_get_control(self, client: AsyncClient, sample_control_data: dict):
        """Test getting a single control."""
        create_resp = await client.post("/api/v1/controls/", json=sample_control_data)
        ctrl_id = create_resp.json()["id"]
        response = await client.get(f"/api/v1/controls/{ctrl_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == ctrl_id
        assert data["title"] == sample_control_data["title"]

    @pytest.mark.asyncio
    async def test_update_control(self, client: AsyncClient, sample_control_data: dict):
        """Test updating a control."""
        create_resp = await client.post("/api/v1/controls/", json=sample_control_data)
        ctrl_id = create_resp.json()["id"]

        update_data = {"title": "Updated Control"}
        response = await client.patch(f"/api/v1/controls/{ctrl_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Control"

    @pytest.mark.asyncio
    async def test_delete_control(self, client: AsyncClient, sample_control_data: dict):
        """Test deleting a control."""
        create_resp = await client.post("/api/v1/controls/", json=sample_control_data)
        ctrl_id = create_resp.json()["id"]

        response = await client.delete(f"/api/v1/controls/{ctrl_id}")
        assert response.status_code == 200

        get_resp = await client.get(f"/api/v1/controls/{ctrl_id}")
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_activate_control(self, client: AsyncClient, sample_control_data: dict):
        """Test activating a control."""
        create_resp = await client.post("/api/v1/controls/", json=sample_control_data)
        ctrl_id = create_resp.json()["id"]

        response = await client.post(f"/api/v1/controls/{ctrl_id}/activate")
        assert response.status_code == 200
        assert response.json()["status"] == "Active"

    @pytest.mark.asyncio
    async def test_deactivate_control(self, client: AsyncClient, sample_control_data: dict):
        """Test deactivating a control."""
        create_resp = await client.post("/api/v1/controls/", json=sample_control_data)
        ctrl_id = create_resp.json()["id"]
        await client.post(f"/api/v1/controls/{ctrl_id}/activate")

        response = await client.post(f"/api/v1/controls/{ctrl_id}/deactivate")
        assert response.status_code == 200
        assert response.json()["status"] == "Deprecated"

    @pytest.mark.asyncio
    async def test_update_effectiveness(self, client: AsyncClient, sample_control_data: dict):
        """Test updating control effectiveness."""
        create_resp = await client.post("/api/v1/controls/", json=sample_control_data)
        ctrl_id = create_resp.json()["id"]

        response = await client.patch(f"/api/v1/controls/{ctrl_id}/effectiveness", params={"effectiveness_percentage": 90})
        assert response.status_code == 200
        assert response.json()["effectiveness_percentage"] == 90

    @pytest.mark.asyncio
    async def test_link_risk(self, client: AsyncClient, sample_control_data: dict, sample_risk_data: dict):
        """Test linking a control to a risk."""
        # Create control and risk
        c_resp = await client.post("/api/v1/controls/", json=sample_control_data)
        ctrl_id = c_resp.json()["id"]
        r_resp = await client.post("/api/v1/risks/", json=sample_risk_data)
        risk_id = r_resp.json()["id"]

        # Link
        response = await client.post(f"/api/v1/controls/{ctrl_id}/risks/{risk_id}", params={"mitigation_percent": 80})
        assert response.status_code == 200

        # Verify link
        risks_resp = await client.get(f"/api/v1/controls/{ctrl_id}/risks")
        assert risks_resp.status_code == 200
        data = risks_resp.json()
        assert len(data) == 1
        assert data[0]["id"] == risk_id

    @pytest.mark.asyncio
    async def test_control_stats(self, client: AsyncClient, sample_control_data: dict):
        """Test control statistics."""
        await client.post("/api/v1/controls/", json=sample_control_data)
        response = await client.get("/api/v1/controls/stats/by-status")
        assert response.status_code == 200
        data = response.json()
        assert "Draft" in data
