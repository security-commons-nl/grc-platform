"""
Tests for Reports API endpoints.
Smoke-tests die controleren of alle report-endpoints 200 teruggeven
zonder interne server errors — regression voor de 500-fouten van 2026-03-11.
"""
import pytest
from httpx import AsyncClient


class TestReportEndpointsSmoke:
    """Elk report-endpoint moet 200 teruggeven als er data is."""

    @pytest.mark.asyncio
    async def test_executive_dashboard_empty(self, client: AsyncClient):
        """Executive dashboard met lege DB geeft 200 (geen 500)."""
        response = await client.get("/api/v1/reports/dashboard/executive")
        assert response.status_code == 200

        data = response.json()
        assert "risks" in data
        assert "policies" in data
        assert "incidents" in data
        assert "compliance" in data

    @pytest.mark.asyncio
    async def test_risk_summary_empty(self, client: AsyncClient):
        response = await client.get("/api/v1/reports/risks/summary")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_assessment_summary_empty(self, client: AsyncClient):
        response = await client.get("/api/v1/reports/assessments/summary")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_actions_summary_empty(self, client: AsyncClient):
        """Corrective actions summary — regression: correctiveaction.risk_id ontbrak."""
        response = await client.get("/api/v1/reports/actions/summary")
        assert response.status_code == 200

        data = response.json()
        assert "total" in data
        assert "open" in data
        assert "overdue" in data

    @pytest.mark.asyncio
    async def test_incident_summary_empty(self, client: AsyncClient):
        response = await client.get("/api/v1/reports/incidents/summary")
        assert response.status_code == 200


class TestReportEndpointsWithData:
    """Report-endpoints met echte data."""

    @pytest.mark.asyncio
    async def test_executive_dashboard_with_risks(self, client: AsyncClient):
        """Executive dashboard telt risico's correct."""
        # Maak twee risico's aan
        for title in ["Risico A", "Risico B"]:
            await client.post("/api/v1/risks/", json={
                "tenant_id": 1,
                "title": title,
                "inherent_likelihood": "HIGH",
                "inherent_impact": "HIGH",
            })

        response = await client.get("/api/v1/reports/dashboard/executive")
        assert response.status_code == 200

        data = response.json()
        assert data["risks"]["total"] >= 2

    @pytest.mark.asyncio
    async def test_actions_summary_with_data(self, client: AsyncClient):
        """Actions summary telt open vs gesloten acties correct."""
        # Maak twee acties, sluit er één
        r1 = await client.post("/api/v1/corrective-actions/", json={
            "tenant_id": 1, "title": "Open actie", "priority": "MEDIUM",
        })
        r2 = await client.post("/api/v1/corrective-actions/", json={
            "tenant_id": 1, "title": "Te sluiten actie", "priority": "LOW",
        })

        if r1.status_code == 200 and r2.status_code == 200:
            action_id = r2.json()["id"]
            await client.post(
                f"/api/v1/corrective-actions/{action_id}/complete",
                json={"result_notes": "Klaar"},
            )

            response = await client.get("/api/v1/reports/actions/summary")
            assert response.status_code == 200
            data = response.json()
            assert data["total"] >= 2

    @pytest.mark.asyncio
    async def test_risk_summary_counts_by_level(self, client: AsyncClient):
        """Risk summary levert kwadrant-verdeling op."""
        await client.post("/api/v1/risks/", json={
            "tenant_id": 1,
            "title": "Hoog risico",
            "inherent_likelihood": "CRITICAL",
            "inherent_impact": "CRITICAL",
        })

        response = await client.get("/api/v1/reports/risks/summary")
        assert response.status_code == 200
