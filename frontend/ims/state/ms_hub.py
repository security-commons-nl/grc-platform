"""
MS Hub State - PDCA overview data loading
Reuses the same report endpoints as ReportState, plus scopes/controls counts.
"""
import asyncio
import httpx
import reflex as rx

from ims.api.client import API_BASE_URL


_HUB_TIMEOUT = httpx.Timeout(connect=2.0, read=5.0, write=5.0, pool=5.0)
_HUB_HEADERS = {"X-User-ID": "1", "X-Tenant-ID": "1"}


class MsHubState(rx.State):
    """State for the MS Hub PDCA overview page."""

    is_loading: bool = False
    error: str = ""

    # Context & Scope
    total_scopes: int = 0
    total_policies: int = 0
    published_policies: int = 0

    # PLAN
    total_risks: int = 0
    high_critical_risks: int = 0
    compliance_pct: float = 0
    compliance_applicable: int = 0
    compliance_implemented: int = 0

    # DO
    active_controls: int = 0
    active_measures: int = 0
    avg_effectiveness: float = 0

    # CHECK
    total_assessments: int = 0
    active_assessments: int = 0
    open_findings: int = 0

    # ACT
    open_incidents: int = 0
    total_actions: int = 0
    open_actions: int = 0
    overdue_actions: int = 0
    completion_rate: float = 0

    # --- Computed vars for phase status ---

    @rx.var
    def context_ok(self) -> bool:
        return self.total_scopes > 0 and self.published_policies > 0

    @rx.var
    def plan_ok(self) -> bool:
        return self.total_risks > 0 and self.compliance_pct >= 50

    @rx.var
    def do_ok(self) -> bool:
        return self.active_controls > 0

    @rx.var
    def check_ok(self) -> bool:
        return self.total_assessments > 0

    @rx.var
    def act_ok(self) -> bool:
        return self.overdue_actions < 3

    # --- Data loading ---

    async def load_all(self):
        """Load all hub data in parallel with short connect timeout."""
        self.is_loading = True
        self.error = ""

        try:
            async with httpx.AsyncClient(
                base_url=API_BASE_URL, timeout=_HUB_TIMEOUT,
                headers=_HUB_HEADERS,
            ) as client:
                responses = await asyncio.gather(
                    client.get("/reports/dashboard/executive"),
                    client.get("/reports/compliance/overview"),
                    client.get("/reports/assessments/summary"),
                    client.get("/reports/actions/summary"),
                    client.get("/scopes/", params={"limit": 500}),
                    client.get("/controls/", params={"limit": 500}),
                    return_exceptions=True,
                )

            results = []
            for r in responses:
                if isinstance(r, Exception):
                    results.append(None)
                elif r.status_code == 200:
                    results.append(r.json())
                else:
                    results.append(None)

            if not any(results):
                self.error = "Backend niet bereikbaar — geen data beschikbaar"
            else:
                self._flatten_executive(results[0] or {})
                self._flatten_compliance(results[1] or {})
                self._flatten_assessments(results[2] or {})
                self._flatten_actions(results[3] or {})
                self._flatten_scopes(results[4])
                self._flatten_controls(results[5])
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

    def _flatten_compliance(self, data: dict):
        self.compliance_applicable = data.get("applicable", 0)
        impl = data.get("implementation_status", {})
        self.compliance_implemented = impl.get("implemented", 0)

    def _flatten_assessments(self, data: dict):
        a = data.get("assessments", {})
        self.total_assessments = a.get("total", 0)
        self.active_assessments = a.get("active", 0)
        f = data.get("findings", {})
        self.open_findings = f.get("open", 0)

    def _flatten_actions(self, data: dict):
        self.total_actions = data.get("total", 0)
        self.open_actions = data.get("open", 0)
        self.overdue_actions = data.get("overdue", 0)
        self.completion_rate = data.get("completion_rate", 0)

    def _flatten_scopes(self, data):
        if isinstance(data, list):
            self.total_scopes = len(data)
        else:
            self.total_scopes = 0

    def _flatten_controls(self, data):
        if isinstance(data, list):
            self.active_controls = len(data)
        else:
            self.active_controls = 0
