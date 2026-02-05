"""
Tests for Risk Management API endpoints.
"""
import pytest
from httpx import AsyncClient


class TestRiskCRUD:
    """Test CRUD operations for risks."""

    @pytest.mark.asyncio
    async def test_create_risk(self, client: AsyncClient, sample_risk_data: dict):
        """Test creating a new risk."""
        response = await client.post("/api/v1/risks/", json=sample_risk_data)
        assert response.status_code == 200

        data = response.json()
        assert data["title"] == sample_risk_data["title"]
        assert data["description"] == sample_risk_data["description"]
        assert data["id"] is not None
        assert data["inherent_risk_score"] is not None

    @pytest.mark.asyncio
    async def test_list_risks(self, client: AsyncClient, sample_risk_data: dict):
        """Test listing risks."""
        # Create a risk first
        await client.post("/api/v1/risks/", json=sample_risk_data)

        # List risks
        response = await client.get("/api/v1/risks/")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_get_risk(self, client: AsyncClient, sample_risk_data: dict):
        """Test getting a single risk."""
        # Create a risk
        create_response = await client.post("/api/v1/risks/", json=sample_risk_data)
        risk_id = create_response.json()["id"]

        # Get the risk
        response = await client.get(f"/api/v1/risks/{risk_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == risk_id
        assert data["title"] == sample_risk_data["title"]

    @pytest.mark.asyncio
    async def test_get_risk_not_found(self, client: AsyncClient):
        """Test getting a non-existent risk."""
        response = await client.get("/api/v1/risks/99999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_risk(self, client: AsyncClient, sample_risk_data: dict):
        """Test updating a risk."""
        # Create a risk
        create_response = await client.post("/api/v1/risks/", json=sample_risk_data)
        risk_id = create_response.json()["id"]

        # Update the risk
        update_data = {"title": "Updated Risk Title"}
        response = await client.patch(f"/api/v1/risks/{risk_id}", json=update_data)
        assert response.status_code == 200

        data = response.json()
        assert data["title"] == "Updated Risk Title"

    @pytest.mark.asyncio
    async def test_delete_risk(self, client: AsyncClient, sample_risk_data: dict):
        """Test deleting a risk."""
        # Create a risk
        create_response = await client.post("/api/v1/risks/", json=sample_risk_data)
        risk_id = create_response.json()["id"]

        # Delete the risk
        response = await client.delete(f"/api/v1/risks/{risk_id}")
        assert response.status_code == 200

        # Verify it's deleted
        get_response = await client.get(f"/api/v1/risks/{risk_id}")
        assert get_response.status_code == 404


class TestRiskHeatmap:
    """Test risk heatmap functionality."""

    @pytest.mark.asyncio
    async def test_get_heatmap(self, client: AsyncClient, sample_risk_data: dict):
        """Test getting risk heatmap data."""
        # Create a risk
        await client.post("/api/v1/risks/", json=sample_risk_data)

        # Get heatmap
        response = await client.get("/api/v1/risks/heatmap")
        assert response.status_code == 200

        data = response.json()
        assert "quadrants" in data or isinstance(data, dict)


class TestRiskAcceptance:
    """Test risk acceptance workflow."""

    @pytest.mark.asyncio
    async def test_accept_risk(self, client: AsyncClient, sample_risk_data: dict):
        """Test accepting a risk."""
        # Create a risk
        create_response = await client.post("/api/v1/risks/", json=sample_risk_data)
        risk_id = create_response.json()["id"]

        # Accept the risk
        response = await client.post(
            f"/api/v1/risks/{risk_id}/accept",
            params={"accepted_by_id": 1, "justification": "Test justification"}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["risk_accepted"] is True
