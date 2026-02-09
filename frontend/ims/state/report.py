"""
Report State - handles report data loading for the Rapportage hub
"""
import asyncio
import httpx
import reflex as rx
from typing import Dict, Any

from ims.api.client import API_BASE_URL


# Short-timeout client for report calls — prevents UI freeze when backend is down
_REPORT_TIMEOUT = httpx.Timeout(connect=2.0, read=5.0, write=5.0, pool=5.0)
_REPORT_HEADERS = {"X-User-ID": "1", "X-Tenant-ID": "1"}


class ReportState(rx.State):
    """State for the reports/rapportage page."""

    is_loading: bool = False
    error: str = ""

    # Executive
    total_risks: int = 0
    high_critical_risks: int = 0
    total_policies: int = 0
    published_policies: int = 0
    active_measures: int = 0
    avg_effectiveness: float = 0
    open_incidents: int = 0
    compliance_pct: float = 0

    # Risk quadrants
    risk_mitigate: int = 0
    risk_assurance: int = 0
    risk_monitor: int = 0
    risk_accept: int = 0

    # Compliance
    compliance_applicable: int = 0
    compliance_implemented: int = 0
    compliance_not_started: int = 0
    compliance_in_progress: int = 0
    compliance_gaps: int = 0

    # Assessments
    total_assessments: int = 0
    active_assessments: int = 0
    open_findings: int = 0

    # Actions
    total_actions: int = 0
    open_actions: int = 0
    overdue_actions: int = 0
    completion_rate: float = 0

    async def load_all(self):
        """Load all report data in parallel with a short connect timeout."""
        self.is_loading = True
        self.error = ""

        try:
            async with httpx.AsyncClient(
                base_url=API_BASE_URL, timeout=_REPORT_TIMEOUT,
                headers=_REPORT_HEADERS,
            ) as client:
                responses = await asyncio.gather(
                    client.get("/reports/dashboard/executive"),
                    client.get("/reports/risks/summary"),
                    client.get("/reports/compliance/overview"),
                    client.get("/reports/assessments/summary"),
                    client.get("/reports/incidents/summary"),
                    client.get("/reports/actions/summary"),
                    return_exceptions=True,
                )

            results = []
            for r in responses:
                if isinstance(r, Exception):
                    results.append({})
                elif r.status_code == 200:
                    results.append(r.json())
                else:
                    results.append({})

            if not any(results):
                self.error = "Backend niet bereikbaar — geen rapportagedata beschikbaar"
            else:
                self._flatten_executive(results[0])
                self._flatten_risk(results[1])
                self._flatten_compliance(results[2])
                self._flatten_assessments(results[3])
                self._flatten_incidents(results[4])
                self._flatten_actions(results[5])
        except Exception:
            self.error = "Backend niet bereikbaar"

        self.is_loading = False

    def _flatten_executive(self, data: dict):
        risks = data.get("risks", {})
        self.total_risks = risks.get("total", 0)
        self.high_critical_risks = risks.get("high_critical", 0)
        policies = data.get("policies", {})
        self.total_policies = policies.get("total", 0)
        self.published_policies = policies.get("published", 0)
        measures = data.get("measures", {})
        self.active_measures = measures.get("active", 0)
        self.avg_effectiveness = measures.get("avg_effectiveness", 0)
        incidents = data.get("incidents", {})
        self.open_incidents = incidents.get("open", 0)
        compliance = data.get("compliance", {})
        self.compliance_pct = compliance.get("overall_percentage", 0)

    def _flatten_risk(self, data: dict):
        q = data.get("by_quadrant", {})
        self.risk_mitigate = q.get("mitigate", 0)
        self.risk_assurance = q.get("assurance", 0)
        self.risk_monitor = q.get("monitor", 0)
        self.risk_accept = q.get("accept", 0)

    def _flatten_compliance(self, data: dict):
        self.compliance_applicable = data.get("applicable", 0)
        impl = data.get("implementation_status", {})
        self.compliance_implemented = impl.get("implemented", 0)
        self.compliance_not_started = impl.get("not_started", 0)
        self.compliance_in_progress = impl.get("in_progress", 0)
        self.compliance_gaps = data.get("gaps_count", 0)

    def _flatten_assessments(self, data: dict):
        a = data.get("assessments", {})
        self.total_assessments = a.get("total", 0)
        self.active_assessments = a.get("active", 0)
        f = data.get("findings", {})
        self.open_findings = f.get("open", 0)

    def _flatten_incidents(self, data: dict):
        self.open_incidents = data.get("open", 0)

    def _flatten_actions(self, data: dict):
        self.total_actions = data.get("total", 0)
        self.open_actions = data.get("open", 0)
        self.overdue_actions = data.get("overdue", 0)
        self.completion_rate = data.get("completion_rate", 0)
