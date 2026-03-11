"""
Tests for Corrective Actions API endpoints.
Acties ter verbetering gekoppeld aan findings, incidents, risico's of issues.
"""
import pytest
from httpx import AsyncClient


@pytest.fixture
def sample_action_data() -> dict:
    return {
        "tenant_id": 1,
        "title": "Implementeer wachtwoordbeleid",
        "description": "Minimaal 12 tekens, MFA verplicht",
        "priority": "HIGH",
    }


class TestCorrectiveActionCRUD:
    """Basic CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_action(self, client: AsyncClient, sample_action_data: dict):
        response = await client.post("/api/v1/corrective-actions/", json=sample_action_data)
        assert response.status_code == 200

        data = response.json()
        assert data["id"] is not None
        assert data["title"] == sample_action_data["title"]
        assert data["completed"] is False

    @pytest.mark.asyncio
    async def test_list_actions(self, client: AsyncClient, sample_action_data: dict):
        await client.post("/api/v1/corrective-actions/", json=sample_action_data)

        response = await client.get("/api/v1/corrective-actions/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) >= 1

    @pytest.mark.asyncio
    async def test_get_action(self, client: AsyncClient, sample_action_data: dict):
        create_resp = await client.post("/api/v1/corrective-actions/", json=sample_action_data)
        action_id = create_resp.json()["id"]

        response = await client.get(f"/api/v1/corrective-actions/{action_id}")
        assert response.status_code == 200
        assert response.json()["id"] == action_id

    @pytest.mark.asyncio
    async def test_get_action_not_found(self, client: AsyncClient):
        response = await client.get("/api/v1/corrective-actions/99999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_action(self, client: AsyncClient, sample_action_data: dict):
        create_resp = await client.post("/api/v1/corrective-actions/", json=sample_action_data)
        action_id = create_resp.json()["id"]

        response = await client.patch(
            f"/api/v1/corrective-actions/{action_id}",
            json={"title": "Bijgewerkte actie"},
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Bijgewerkte actie"

    @pytest.mark.asyncio
    async def test_delete_action(self, client: AsyncClient, sample_action_data: dict):
        create_resp = await client.post("/api/v1/corrective-actions/", json=sample_action_data)
        action_id = create_resp.json()["id"]

        delete_resp = await client.delete(f"/api/v1/corrective-actions/{action_id}")
        assert delete_resp.status_code == 200

        get_resp = await client.get(f"/api/v1/corrective-actions/{action_id}")
        assert get_resp.status_code == 404


class TestCorrectiveActionWorkflow:
    """Voortgangsworkflow: open → voltooid → geverifieerd."""

    @pytest.mark.asyncio
    async def test_complete_action(self, client: AsyncClient, sample_action_data: dict):
        """Actie afsluiten zet completed=True."""
        create_resp = await client.post("/api/v1/corrective-actions/", json=sample_action_data)
        action_id = create_resp.json()["id"]

        response = await client.post(
            f"/api/v1/corrective-actions/{action_id}/complete",
            json={"result_notes": "Wachtwoordbeleid geïmplementeerd en getest"},
        )
        assert response.status_code == 200
        assert response.json()["completed"] is True

    @pytest.mark.asyncio
    async def test_verify_completed_action(self, client: AsyncClient, sample_action_data: dict):
        """Voltooide actie kan worden geverifieerd."""
        create_resp = await client.post("/api/v1/corrective-actions/", json=sample_action_data)
        action_id = create_resp.json()["id"]

        await client.post(
            f"/api/v1/corrective-actions/{action_id}/complete",
            json={"result_notes": "Klaar"},
        )

        response = await client.post(
            f"/api/v1/corrective-actions/{action_id}/verify",
            params={"verified_by_id": 1},
        )
        assert response.status_code == 200
        assert response.json()["verified"] is True

    @pytest.mark.asyncio
    async def test_filter_open_actions(self, client: AsyncClient, sample_action_data: dict):
        """Filteren op completed=false geeft alleen open acties."""
        create_resp = await client.post("/api/v1/corrective-actions/", json=sample_action_data)
        action_id = create_resp.json()["id"]

        # Sluit één actie
        await client.post(
            f"/api/v1/corrective-actions/{action_id}/complete",
            json={"result_notes": "Klaar"},
        )

        # Maak nog een open actie
        await client.post("/api/v1/corrective-actions/", json={
            **sample_action_data, "title": "Nog open actie"
        })

        response = await client.get("/api/v1/corrective-actions/?status=open")
        assert response.status_code == 200
        data = response.json()
        assert all(not a["completed"] for a in data)
