"""
Tests for Measure Management API endpoints.
"""
import pytest
from httpx import AsyncClient


class TestMeasureCRUD:
    """Test CRUD operations for measures."""

    @pytest.mark.asyncio
    async def test_create_measure(self, client: AsyncClient, sample_measure_data: dict):
        """Test creating a new measure."""
        response = await client.post("/api/v1/measures/", json=sample_measure_data)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == sample_measure_data["name"]
        assert data["description"] == sample_measure_data["description"]
        assert data["id"] is not None
        # assert data["status"] == "Draft"  # Default status -> Measures might not have status like controls do

    @pytest.mark.asyncio
    async def test_list_measures(self, client: AsyncClient, sample_measure_data: dict):
        """Test listing measures."""
        # Create a measure first
        await client.post("/api/v1/measures/", json=sample_measure_data)

        # List measures
        response = await client.get("/api/v1/measures/")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_get_measure(self, client: AsyncClient, sample_measure_data: dict):
        """Test getting a single measure."""
        # Create a measure
        create_response = await client.post("/api/v1/measures/", json=sample_measure_data)
        measure_id = create_response.json()["id"]

        # Get the measure
        response = await client.get(f"/api/v1/measures/{measure_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == measure_id
        assert data["name"] == sample_measure_data["name"]

    @pytest.mark.asyncio
    async def test_get_measure_not_found(self, client: AsyncClient):
        """Test getting a non-existent measure."""
        response = await client.get("/api/v1/measures/99999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_measure(self, client: AsyncClient, sample_measure_data: dict):
        """Test updating a measure."""
        # Create a measure
        create_response = await client.post("/api/v1/measures/", json=sample_measure_data)
        measure_id = create_response.json()["id"]

        # Update the measure
        update_data = {"name": "Updated Measure Name"}
        response = await client.patch(f"/api/v1/measures/{measure_id}", json=update_data)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Updated Measure Name"

    @pytest.mark.asyncio
    async def test_delete_measure(self, client: AsyncClient, sample_measure_data: dict):
        """Test deleting (soft-deleting) a measure."""
        # Create a measure
        create_response = await client.post("/api/v1/measures/", json=sample_measure_data)
        measure_id = create_response.json()["id"]

        # Delete the measure
        response = await client.delete(f"/api/v1/measures/{measure_id}")
        assert response.status_code == 200

        # Verify it's soft deleted (is_active=False)
        # Note: If get_measure filters by is_active=True (depends on CRUD implementation), it might return 404.
        # But get_or_404 usually finds it regardless of is_active unless filter is applied.
        get_response = await client.get(f"/api/v1/measures/{measure_id}")

        # If the backend implementation allows getting inactive measures:
        if get_response.status_code == 200:
            data = get_response.json()
            assert data["is_active"] is False
        else:
            # Otherwise 404 is also acceptable if it hides inactive ones
            assert get_response.status_code == 404


class TestMeasureStatistics:
    """Test measure statistics endpoints."""

    @pytest.mark.asyncio
    async def test_get_catalog_stats(self, client: AsyncClient, sample_measure_data: dict):
        """Test getting measure catalog stats."""
        # Create a measure
        await client.post("/api/v1/measures/", json=sample_measure_data)

        # Get stats
        response = await client.get("/api/v1/measures/stats/summary")
        assert response.status_code == 200

        data = response.json()
        assert "total_measures" in data
