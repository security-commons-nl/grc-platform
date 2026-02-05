"""
Tests for Standards/Frameworks API endpoints.
"""
import pytest
from httpx import AsyncClient

class TestFrameworks:
    """Test framework/standard management."""

    @pytest.mark.asyncio
    async def test_create_standard(self, client: AsyncClient, sample_standard_data: dict):
        """Test creating a new standard."""
        response = await client.post("/api/v1/standards/", json=sample_standard_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_standard_data["name"]
        assert data["version"] == sample_standard_data["version"]
        assert data["id"] is not None

    @pytest.mark.asyncio
    async def test_list_standards(self, client: AsyncClient, sample_standard_data: dict):
        """Test listing standards."""
        await client.post("/api/v1/standards/", json=sample_standard_data)
        response = await client.get("/api/v1/standards/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_get_standard(self, client: AsyncClient, sample_standard_data: dict):
        """Test getting a single standard."""
        create_response = await client.post("/api/v1/standards/", json=sample_standard_data)
        std_id = create_response.json()["id"]
        response = await client.get(f"/api/v1/standards/{std_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == std_id
        assert data["name"] == sample_standard_data["name"]

    @pytest.mark.asyncio
    async def test_get_standard_not_found(self, client: AsyncClient):
        """Test getting a non-existent standard."""
        response = await client.get("/api/v1/standards/9999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_requirement(self, client: AsyncClient, sample_standard_data: dict, sample_requirement_data: dict):
        """Test creating a requirement under a standard."""
        # Create standard first
        std_resp = await client.post("/api/v1/standards/", json=sample_standard_data)
        std_id = std_resp.json()["id"]

        # Create requirement
        response = await client.post(f"/api/v1/standards/{std_id}/requirements/", json=sample_requirement_data)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == sample_requirement_data["code"]
        assert data["standard_id"] == std_id
        assert data["id"] is not None

    @pytest.mark.asyncio
    async def test_list_requirements(self, client: AsyncClient, sample_standard_data: dict, sample_requirement_data: dict):
        """Test listing requirements for a standard."""
        std_resp = await client.post("/api/v1/standards/", json=sample_standard_data)
        std_id = std_resp.json()["id"]
        await client.post(f"/api/v1/standards/{std_id}/requirements/", json=sample_requirement_data)

        response = await client.get(f"/api/v1/standards/{std_id}/requirements/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["code"] == sample_requirement_data["code"]

    @pytest.mark.asyncio
    async def test_create_requirement_invalid_standard(self, client: AsyncClient, sample_requirement_data: dict):
        """Test creating a requirement for a non-existent standard."""
        response = await client.post("/api/v1/standards/9999/requirements/", json=sample_requirement_data)
        assert response.status_code == 404
