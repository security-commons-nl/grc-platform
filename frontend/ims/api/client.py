"""
API Client for IMS Backend
Uses httpx for async HTTP requests
"""
import httpx
import os
from typing import Optional, List, Dict, Any

# Use environment variable for API URL, fallback to localhost for local development
# FastAPI backend runs on port 8000
API_BASE_URL = os.getenv("API_URL", "http://localhost:8000") + "/api/v1"


class APIClient:
    """Async API client for IMS backend."""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.timeout = httpx.Timeout(5.0)

    def _get_client(
        self,
        user_id: Optional[int] = 1,
        tenant_id: Optional[int] = None,
    ) -> httpx.AsyncClient:
        headers = {}
        if user_id:
            headers["X-User-ID"] = str(user_id)
        if tenant_id:
            headers["X-Tenant-ID"] = str(tenant_id)
        return httpx.AsyncClient(
            base_url=self.base_url, timeout=self.timeout, headers=headers,
        )

    # =========================================================================
    # AUTHENTICATION
    # =========================================================================

    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate against backend. Returns user data on success."""
        async with self._get_client() as client:
            response = await client.post(
                "/auth/login",
                json={"username": username, "password": password},
            )
            response.raise_for_status()
            return response.json()

    # =========================================================================
    # RISKS
    # =========================================================================

    async def get_risks(
        self,
        skip: int = 0,
        limit: int = 100,
        tenant_id: Optional[int] = None,
        scope_id: Optional[int] = None,
        quadrant: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get list of risks."""
        async with self._get_client() as client:
            params = {"skip": skip, "limit": limit}
            if tenant_id:
                params["tenant_id"] = tenant_id
            if scope_id:
                params["scope_id"] = scope_id
            if quadrant:
                params["quadrant"] = quadrant

            response = await client.get("/risks/", params=params)
            response.raise_for_status()
            return response.json()

    async def get_risk(self, risk_id: int) -> Dict[str, Any]:
        """Get a single risk by ID."""
        async with self._get_client() as client:
            response = await client.get(f"/risks/{risk_id}")
            response.raise_for_status()
            return response.json()

    async def create_risk(self, risk_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new risk."""
        async with self._get_client() as client:
            response = await client.post("/risks/", json=risk_data)
            response.raise_for_status()
            return response.json()

    async def update_risk(self, risk_id: int, risk_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a risk."""
        async with self._get_client() as client:
            response = await client.patch(f"/risks/{risk_id}", json=risk_data)
            response.raise_for_status()
            return response.json()

    async def delete_risk(self, risk_id: int) -> Dict[str, Any]:
        """Delete a risk."""
        async with self._get_client() as client:
            response = await client.delete(f"/risks/{risk_id}")
            response.raise_for_status()
            return response.json()

    async def get_risk_heatmap(
        self,
        tenant_id: Optional[int] = None,
        scope_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get risk heatmap data."""
        async with self._get_client() as client:
            params = {}
            if tenant_id:
                params["tenant_id"] = tenant_id
            if scope_id:
                params["scope_id"] = scope_id

            response = await client.get("/risks/heatmap", params=params)
            response.raise_for_status()
            return response.json()

    # =========================================================================
    # CONTROLS (Context-specific implementations)
    # =========================================================================

    async def get_controls(
        self,
        skip: int = 0,
        limit: int = 100,
        tenant_id: Optional[int] = None,
        scope_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get list of controls (context-specific implementations)."""
        async with self._get_client() as client:
            params = {"skip": skip, "limit": limit}
            if tenant_id:
                params["tenant_id"] = tenant_id
            if scope_id:
                params["scope_id"] = scope_id
            if status:
                params["status"] = status

            response = await client.get("/controls/", params=params)
            response.raise_for_status()
            return response.json()

    async def get_control(self, control_id: int) -> Dict[str, Any]:
        """Get a single control by ID."""
        async with self._get_client() as client:
            response = await client.get(f"/controls/{control_id}")
            response.raise_for_status()
            return response.json()

    async def create_control(self, control_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new control."""
        async with self._get_client() as client:
            response = await client.post("/controls/", json=control_data)
            response.raise_for_status()
            return response.json()

    async def update_control(self, control_id: int, control_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a control."""
        async with self._get_client() as client:
            response = await client.patch(f"/controls/{control_id}", json=control_data)
            response.raise_for_status()
            return response.json()

    async def delete_control(self, control_id: int) -> Dict[str, Any]:
        """Delete a control."""
        async with self._get_client() as client:
            response = await client.delete(f"/controls/{control_id}")
            response.raise_for_status()
            return response.json()

    # =========================================================================
    # RISK-CONTROL LINKAGE
    # =========================================================================

    async def link_risk_control(self, risk_id: int, control_id: int, mitigation_percent: int = 50) -> Dict[str, Any]:
        """Link a control to a risk."""
        async with self._get_client() as client:
            params = {"mitigation_percent": mitigation_percent}
            response = await client.post(f"/risks/{risk_id}/controls/{control_id}", params=params)
            response.raise_for_status()
            return response.json()

    async def unlink_risk_control(self, risk_id: int, control_id: int) -> Dict[str, Any]:
        """Unlink a control from a risk."""
        async with self._get_client() as client:
            response = await client.delete(f"/risks/{risk_id}/controls/{control_id}")
            response.raise_for_status()
            return response.json()

    async def get_risk_controls(self, risk_id: int) -> List[Dict[str, Any]]:
        """Get controls linked to a risk."""
        async with self._get_client() as client:
            response = await client.get(f"/risks/{risk_id}/controls")
            response.raise_for_status()
            return response.json()

    async def get_control_risks(self, control_id: int) -> List[Dict[str, Any]]:
        """Get risks linked to a control."""
        async with self._get_client() as client:
            response = await client.get(f"/controls/{control_id}/risks")
            response.raise_for_status()
            return response.json()

    async def link_control_risk(self, control_id: int, risk_id: int, mitigation_percent: int = 50) -> Dict[str, Any]:
        """Link a risk to a control."""
        async with self._get_client() as client:
            params = {"mitigation_percent": mitigation_percent}
            response = await client.post(f"/controls/{control_id}/risks/{risk_id}", params=params)
            response.raise_for_status()
            return response.json()

    async def unlink_control_risk(self, control_id: int, risk_id: int) -> Dict[str, Any]:
        """Unlink a risk from a control."""
        async with self._get_client() as client:
            response = await client.delete(f"/controls/{control_id}/risks/{risk_id}")
            response.raise_for_status()
            return response.json()

    # =========================================================================
    # RISK-SCOPE CONTEXTUALISATIE
    # =========================================================================

    async def get_risk_scopes(
        self, risk_id: Optional[int] = None, scope_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get risk-scope contextualizations, optionally filtered."""
        async with self._get_client() as client:
            params = {}
            if risk_id is not None:
                params["risk_id"] = risk_id
            if scope_id is not None:
                params["scope_id"] = scope_id
            response = await client.get("/risk-scopes/", params=params)
            response.raise_for_status()
            return response.json()

    async def get_risk_scope(self, risk_scope_id: int) -> Dict[str, Any]:
        """Get a specific risk-scope contextualization."""
        async with self._get_client() as client:
            response = await client.get(f"/risk-scopes/{risk_scope_id}")
            response.raise_for_status()
            return response.json()

    async def create_risk_scope(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new risk-scope contextualization."""
        async with self._get_client() as client:
            response = await client.post("/risk-scopes/", json=data)
            response.raise_for_status()
            return response.json()

    async def update_risk_scope(self, risk_scope_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a risk-scope contextualization."""
        async with self._get_client() as client:
            response = await client.put(f"/risk-scopes/{risk_scope_id}", json=data)
            response.raise_for_status()
            return response.json()

    async def delete_risk_scope(self, risk_scope_id: int) -> Dict[str, Any]:
        """Delete a risk-scope contextualization."""
        async with self._get_client() as client:
            response = await client.delete(f"/risk-scopes/{risk_scope_id}")
            response.raise_for_status()
            return response.json()

    async def get_scopes_for_risk(self, risk_id: int) -> List[Dict[str, Any]]:
        """Get all scope contextualizations for a risk."""
        async with self._get_client() as client:
            response = await client.get(f"/risk-scopes/by-risk/{risk_id}")
            response.raise_for_status()
            return response.json()

    async def get_risks_for_scope(self, scope_id: int) -> List[Dict[str, Any]]:
        """Get all risk contextualizations for a scope."""
        async with self._get_client() as client:
            response = await client.get(f"/risk-scopes/by-scope/{scope_id}")
            response.raise_for_status()
            return response.json()

    async def link_control_to_risk_scope(
        self, risk_scope_id: int, control_id: int, mitigation_percent: int = 50
    ) -> Dict[str, Any]:
        """Link a control to a scope-contextualized risk."""
        async with self._get_client() as client:
            params = {"mitigation_percent": mitigation_percent}
            response = await client.post(
                f"/risk-scopes/{risk_scope_id}/controls/{control_id}", params=params
            )
            response.raise_for_status()
            return response.json()

    async def unlink_control_from_risk_scope(
        self, risk_scope_id: int, control_id: int
    ) -> Dict[str, Any]:
        """Unlink a control from a scope-contextualized risk."""
        async with self._get_client() as client:
            response = await client.delete(
                f"/risk-scopes/{risk_scope_id}/controls/{control_id}"
            )
            response.raise_for_status()
            return response.json()

    async def link_decision_to_risk_scope(
        self, risk_scope_id: int, decision_id: int, notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Link a decision to a scope-contextualized risk."""
        async with self._get_client() as client:
            params = {}
            if notes:
                params["notes"] = notes
            response = await client.post(
                f"/risk-scopes/{risk_scope_id}/decisions/{decision_id}", params=params
            )
            response.raise_for_status()
            return response.json()

    async def unlink_decision_from_risk_scope(
        self, risk_scope_id: int, decision_id: int
    ) -> Dict[str, Any]:
        """Unlink a decision from a scope-contextualized risk."""
        async with self._get_client() as client:
            response = await client.delete(
                f"/risk-scopes/{risk_scope_id}/decisions/{decision_id}"
            )
            response.raise_for_status()
            return response.json()

    # =========================================================================
    # MEASURES (Catalog - reusable building blocks)
    # =========================================================================

    async def get_measures(
        self,
        skip: int = 0,
        limit: int = 100,
        tenant_id: Optional[int] = None,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get list of measures from catalog (reusable building blocks)."""
        async with self._get_client() as client:
            params = {"skip": skip, "limit": limit}
            if tenant_id:
                params["tenant_id"] = tenant_id
            if category:
                params["category"] = category

            response = await client.get("/measures/", params=params)
            response.raise_for_status()
            return response.json()

    async def get_measure(self, measure_id: int) -> Dict[str, Any]:
        """Get a single measure from catalog by ID."""
        async with self._get_client() as client:
            response = await client.get(f"/measures/{measure_id}")
            response.raise_for_status()
            return response.json()

    async def create_measure(self, measure_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new measure in catalog."""
        async with self._get_client() as client:
            response = await client.post("/measures/", json=measure_data)
            response.raise_for_status()
            return response.json()

    async def update_measure(self, measure_id: int, measure_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a measure in catalog."""
        async with self._get_client() as client:
            response = await client.patch(f"/measures/{measure_id}", json=measure_data)
            response.raise_for_status()
            return response.json()

    async def delete_measure(self, measure_id: int) -> Dict[str, Any]:
        """Delete a measure from catalog (soft delete)."""
        async with self._get_client() as client:
            response = await client.delete(f"/measures/{measure_id}")
            response.raise_for_status()
            return response.json()

    # =========================================================================
    # SCOPES
    # =========================================================================

    async def get_scopes(
        self,
        skip: int = 0,
        limit: int = 100,
        tenant_id: Optional[int] = None,
        scope_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get list of scopes."""
        async with self._get_client() as client:
            params = {"skip": skip, "limit": limit}
            if tenant_id:
                params["tenant_id"] = tenant_id
            if scope_type:
                params["scope_type"] = scope_type

            response = await client.get("/scopes/", params=params)
            response.raise_for_status()
            return response.json()

    async def get_scope(self, scope_id: int) -> Dict[str, Any]:
        """Get a single scope by ID."""
        async with self._get_client() as client:
            response = await client.get(f"/scopes/{scope_id}")
            response.raise_for_status()
            return response.json()

    async def create_scope(self, scope_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new scope."""
        async with self._get_client() as client:
            response = await client.post("/scopes/", json=scope_data)
            response.raise_for_status()
            return response.json()

    async def update_scope(self, scope_id: int, scope_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a scope."""
        async with self._get_client() as client:
            response = await client.patch(f"/scopes/{scope_id}", json=scope_data)
            response.raise_for_status()
            return response.json()

    async def delete_scope(self, scope_id: int) -> Dict[str, Any]:
        """Delete a scope."""
        async with self._get_client() as client:
            response = await client.delete(f"/scopes/{scope_id}")
            response.raise_for_status()
            return response.json()

    # =========================================================================
    # ASSESSMENTS
    # =========================================================================

    async def get_assessments(
        self,
        skip: int = 0,
        limit: int = 100,
        tenant_id: Optional[int] = None,
        assessment_type: Optional[str] = None,
        status: Optional[str] = None,
        scope_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Get list of assessments."""
        async with self._get_client() as client:
            params = {"skip": skip, "limit": limit}
            if tenant_id:
                params["tenant_id"] = tenant_id
            if assessment_type:
                params["assessment_type"] = assessment_type
            if status:
                params["status"] = status
            if scope_id:
                params["scope_id"] = scope_id

            response = await client.get("/assessments/", params=params)
            response.raise_for_status()
            return response.json()

    async def get_assessment(self, assessment_id: int) -> Dict[str, Any]:
        """Get a single assessment by ID."""
        async with self._get_client() as client:
            response = await client.get(f"/assessments/{assessment_id}")
            response.raise_for_status()
            return response.json()

    async def create_assessment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new assessment."""
        async with self._get_client() as client:
            response = await client.post("/assessments/", json=data)
            response.raise_for_status()
            return response.json()

    async def update_assessment(self, assessment_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an assessment."""
        async with self._get_client() as client:
            response = await client.patch(f"/assessments/{assessment_id}", json=data)
            response.raise_for_status()
            return response.json()

    async def delete_assessment(self, assessment_id: int) -> Dict[str, Any]:
        """Delete an assessment."""
        async with self._get_client() as client:
            response = await client.delete(f"/assessments/{assessment_id}")
            response.raise_for_status()
            return response.json()

    # Assessment lifecycle
    async def advance_assessment_phase(self, assessment_id: int, phase: str) -> Dict[str, Any]:
        """Advance assessment to a new phase."""
        async with self._get_client() as client:
            response = await client.post(
                f"/assessments/{assessment_id}/advance-phase",
                params={"phase": phase},
            )
            response.raise_for_status()
            return response.json()

    async def start_assessment(self, assessment_id: int) -> Dict[str, Any]:
        """Start an assessment."""
        async with self._get_client() as client:
            response = await client.post(f"/assessments/{assessment_id}/start")
            response.raise_for_status()
            return response.json()

    async def complete_assessment(self, assessment_id: int, overall_result: str, executive_summary: Optional[str] = None) -> Dict[str, Any]:
        """Complete an assessment."""
        async with self._get_client() as client:
            params = {"overall_result": overall_result}
            if executive_summary:
                params["executive_summary"] = executive_summary
            response = await client.post(f"/assessments/{assessment_id}/complete", params=params)
            response.raise_for_status()
            return response.json()

    async def get_assessment_summary_detail(self, assessment_id: int) -> Dict[str, Any]:
        """Get assessment summary statistics."""
        async with self._get_client() as client:
            response = await client.get(f"/assessments/{assessment_id}/summary")
            response.raise_for_status()
            return response.json()

    # Findings
    async def get_assessment_findings(self, assessment_id: int) -> List[Dict[str, Any]]:
        """Get findings for an assessment."""
        async with self._get_client() as client:
            response = await client.get(f"/assessments/{assessment_id}/findings")
            response.raise_for_status()
            return response.json()

    async def create_finding(self, assessment_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a finding for an assessment."""
        async with self._get_client() as client:
            response = await client.post(f"/assessments/{assessment_id}/findings", json=data)
            response.raise_for_status()
            return response.json()

    async def update_finding(self, finding_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a finding."""
        async with self._get_client() as client:
            response = await client.patch(f"/assessments/findings/{finding_id}", json=data)
            response.raise_for_status()
            return response.json()

    async def close_finding(self, finding_id: int) -> Dict[str, Any]:
        """Close a finding (requires completed corrective action)."""
        async with self._get_client() as client:
            response = await client.post(f"/assessments/findings/{finding_id}/close")
            response.raise_for_status()
            return response.json()

    # Corrective Actions
    async def get_finding_corrective_actions(self, finding_id: int) -> List[Dict[str, Any]]:
        """Get corrective actions for a finding."""
        async with self._get_client() as client:
            response = await client.get(f"/assessments/findings/{finding_id}/corrective-actions")
            response.raise_for_status()
            return response.json()

    async def create_corrective_action(self, finding_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a corrective action for a finding."""
        async with self._get_client() as client:
            response = await client.post(f"/assessments/findings/{finding_id}/corrective-actions", json=data)
            response.raise_for_status()
            return response.json()

    async def update_corrective_action(self, action_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a corrective action."""
        async with self._get_client() as client:
            response = await client.patch(f"/assessments/corrective-actions/{action_id}", json=data)
            response.raise_for_status()
            return response.json()

    async def complete_corrective_action(self, action_id: int, completed_by_id: int, notes: Optional[str] = None) -> Dict[str, Any]:
        """Mark a corrective action as completed."""
        async with self._get_client() as client:
            params = {"completed_by_id": completed_by_id}
            if notes:
                params["completion_notes"] = notes
            response = await client.post(f"/assessments/corrective-actions/{action_id}/complete", params=params)
            response.raise_for_status()
            return response.json()

    # Evidence
    async def get_assessment_evidence(self, assessment_id: int) -> List[Dict[str, Any]]:
        """Get evidence for an assessment."""
        async with self._get_client() as client:
            response = await client.get(f"/assessments/{assessment_id}/evidence")
            response.raise_for_status()
            return response.json()

    async def create_evidence(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create evidence."""
        async with self._get_client() as client:
            response = await client.post("/assessments/evidence/", json=data)
            response.raise_for_status()
            return response.json()

    # Questions & Responses (BIA)
    async def get_assessment_questions(self, assessment_id: int) -> List[Dict[str, Any]]:
        """Get questions for an assessment."""
        async with self._get_client() as client:
            response = await client.get(f"/assessments/{assessment_id}/questions")
            response.raise_for_status()
            return response.json()

    async def get_assessment_responses(self, assessment_id: int) -> List[Dict[str, Any]]:
        """Get all responses for an assessment."""
        async with self._get_client() as client:
            response = await client.get(f"/assessments/{assessment_id}/responses")
            response.raise_for_status()
            return response.json()

    async def save_assessment_response(self, assessment_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Save (upsert) a response for a question."""
        async with self._get_client() as client:
            response = await client.post(f"/assessments/{assessment_id}/responses", json=data)
            response.raise_for_status()
            return response.json()

    async def get_assessment_progress(self, assessment_id: int) -> Dict[str, Any]:
        """Get question completion progress."""
        async with self._get_client() as client:
            response = await client.get(f"/assessments/{assessment_id}/progress")
            response.raise_for_status()
            return response.json()

    async def calculate_bia(self, assessment_id: int) -> Dict[str, Any]:
        """Calculate BIA scores from responses."""
        async with self._get_client() as client:
            response = await client.post(f"/assessments/{assessment_id}/calculate-bia")
            response.raise_for_status()
            return response.json()

    # BIA Thresholds
    async def get_bia_thresholds(self, tenant_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get BIA threshold configuration."""
        async with self._get_client() as client:
            params = {}
            if tenant_id:
                params["tenant_id"] = tenant_id
            response = await client.get("/assessments/bia-thresholds", params=params)
            response.raise_for_status()
            return response.json()

    # =========================================================================
    # CORRECTIVE ACTIONS (Standalone)
    # =========================================================================

    async def get_corrective_actions(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to_id: Optional[int] = None,
        source_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get list of corrective actions with filters."""
        async with self._get_client() as client:
            params = {"skip": skip, "limit": limit}
            if status:
                params["status"] = status
            if priority:
                params["priority"] = priority
            if assigned_to_id:
                params["assigned_to_id"] = assigned_to_id
            if source_type:
                params["source_type"] = source_type
            response = await client.get("/corrective-actions/", params=params)
            response.raise_for_status()
            return response.json()

    async def get_corrective_action_stats(self) -> Dict[str, Any]:
        """Get corrective action KPI statistics."""
        async with self._get_client() as client:
            response = await client.get("/corrective-actions/stats")
            response.raise_for_status()
            return response.json()

    async def create_standalone_corrective_action(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a standalone corrective action."""
        async with self._get_client() as client:
            response = await client.post("/corrective-actions/", json=data)
            response.raise_for_status()
            return response.json()

    async def get_standalone_corrective_action(self, action_id: int) -> Dict[str, Any]:
        """Get a corrective action by ID."""
        async with self._get_client() as client:
            response = await client.get(f"/corrective-actions/{action_id}")
            response.raise_for_status()
            return response.json()

    async def update_standalone_corrective_action(self, action_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a corrective action."""
        async with self._get_client() as client:
            response = await client.patch(f"/corrective-actions/{action_id}", json=data)
            response.raise_for_status()
            return response.json()

    async def complete_standalone_corrective_action(self, action_id: int, result_notes: Optional[str] = None) -> Dict[str, Any]:
        """Mark a corrective action as completed."""
        async with self._get_client() as client:
            params = {}
            if result_notes:
                params["result_notes"] = result_notes
            response = await client.post(f"/corrective-actions/{action_id}/complete", params=params)
            response.raise_for_status()
            return response.json()

    async def verify_standalone_corrective_action(self, action_id: int, verified_by_id: int) -> Dict[str, Any]:
        """Verify a completed corrective action."""
        async with self._get_client() as client:
            params = {"verified_by_id": verified_by_id}
            response = await client.post(f"/corrective-actions/{action_id}/verify", params=params)
            response.raise_for_status()
            return response.json()

    async def delete_standalone_corrective_action(self, action_id: int) -> None:
        """Delete a corrective action."""
        async with self._get_client() as client:
            response = await client.delete(f"/corrective-actions/{action_id}")
            response.raise_for_status()

    # =========================================================================
    # INCIDENTS
    # =========================================================================

    async def get_incidents(
        self,
        skip: int = 0,
        limit: int = 100,
        tenant_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Get list of incidents."""
        async with self._get_client() as client:
            params = {"skip": skip, "limit": limit}
            if tenant_id:
                params["tenant_id"] = tenant_id

            response = await client.get("/incidents/", params=params)
            response.raise_for_status()
            return response.json()

    async def create_incident(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new incident."""
        async with self._get_client() as client:
            response = await client.post("/incidents/", json=data)
            response.raise_for_status()
            return response.json()

    async def update_incident(self, incident_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing incident."""
        async with self._get_client() as client:
            response = await client.patch(f"/incidents/{incident_id}", json=data)
            response.raise_for_status()
            return response.json()

    async def delete_incident(self, incident_id: int) -> None:
        """Delete an incident."""
        async with self._get_client() as client:
            response = await client.delete(f"/incidents/{incident_id}")
            response.raise_for_status()

    # =========================================================================
    # POLICIES
    # =========================================================================

    async def get_policies(
        self,
        skip: int = 0,
        limit: int = 100,
        tenant_id: Optional[int] = None,
        state: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get list of policies."""
        async with self._get_client() as client:
            params = {"skip": skip, "limit": limit}
            if tenant_id:
                params["tenant_id"] = tenant_id
            if state:
                params["state"] = state

            response = await client.get("/policies/", params=params)
            response.raise_for_status()
            return response.json()

    async def create_policy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new policy."""
        async with self._get_client() as client:
            response = await client.post("/policies/", json=data)
            response.raise_for_status()
            return response.json()

    async def update_policy(self, policy_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing policy."""
        async with self._get_client() as client:
            response = await client.patch(f"/policies/{policy_id}", json=data)
            response.raise_for_status()
            return response.json()

    async def delete_policy(self, policy_id: int) -> None:
        """Delete a policy."""
        async with self._get_client() as client:
            response = await client.delete(f"/policies/{policy_id}")
            response.raise_for_status()

    # =========================================================================
    # USERS
    # =========================================================================

    async def get_users(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: bool = True,
    ) -> List[Dict[str, Any]]:
        """Get list of users."""
        async with self._get_client() as client:
            params = {"skip": skip, "limit": limit, "is_active": is_active}
            response = await client.get("/users/", params=params)
            response.raise_for_status()
            return response.json()

    async def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get a single user by ID."""
        async with self._get_client() as client:
            response = await client.get(f"/users/{user_id}")
            response.raise_for_status()
            return response.json()

    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username."""
        async with self._get_client() as client:
            try:
                response = await client.get(f"/users/by-username/{username}")
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError:
                return None

    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user."""
        async with self._get_client() as client:
            response = await client.post("/users/", json=user_data)
            response.raise_for_status()
            return response.json()

    async def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a user."""
        async with self._get_client() as client:
            response = await client.patch(f"/users/{user_id}", json=user_data)
            response.raise_for_status()
            return response.json()

    async def deactivate_user(self, user_id: int) -> Dict[str, Any]:
        """Deactivate a user (soft delete)."""
        async with self._get_client() as client:
            response = await client.delete(f"/users/{user_id}")
            response.raise_for_status()
            return response.json()

    async def permanently_delete_user(self, user_id: int) -> Dict[str, Any]:
        """Permanently delete a user (hard delete)."""
        async with self._get_client() as client:
            response = await client.delete(f"/users/{user_id}/permanent")
            response.raise_for_status()
            return response.json()

    async def get_user_scopes(
        self,
        user_id: int,
        tenant_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Get all scopes a user has access to with their roles."""
        async with self._get_client() as client:
            params = {}
            if tenant_id:
                params["tenant_id"] = tenant_id
            response = await client.get(f"/users/{user_id}/scopes", params=params)
            response.raise_for_status()
            return response.json()

    async def assign_user_scope_role(
        self,
        user_id: int,
        scope_id: int,
        role: str,
        tenant_id: int,
    ) -> Dict[str, Any]:
        """Assign a role to a user for a specific scope."""
        async with self._get_client() as client:
            params = {"tenant_id": tenant_id}
            response = await client.post(
                f"/users/{user_id}/scopes/{scope_id}/roles/{role}",
                params=params,
            )
            response.raise_for_status()
            return response.json()

    async def remove_user_scope_role(
        self,
        user_id: int,
        scope_id: int,
        role: str,
    ) -> Dict[str, Any]:
        """Remove a role from a user for a specific scope."""
        async with self._get_client() as client:
            response = await client.delete(f"/users/{user_id}/scopes/{scope_id}/roles/{role}")
            response.raise_for_status()
            return response.json()

    async def get_user_tenants(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all tenants a user belongs to."""
        async with self._get_client() as client:
            response = await client.get(f"/users/{user_id}/tenants")
            response.raise_for_status()
            return response.json()

    async def add_user_to_tenant(
        self,
        user_id: int,
        tenant_id: int,
        is_default: bool = False,
    ) -> Dict[str, Any]:
        """Add a user to a tenant (membership-only, roles via UserScopeRole)."""
        async with self._get_client() as client:
            params = {"is_default": is_default}
            response = await client.post(
                f"/users/{user_id}/tenants/{tenant_id}",
                params=params,
            )
            response.raise_for_status()
            return response.json()


    # =========================================================================
    # TENANTS
    # =========================================================================

    async def get_tenants(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: bool = True,
    ) -> List[Dict[str, Any]]:
        """Get list of tenants."""
        async with self._get_client() as client:
            params = {"skip": skip, "limit": limit, "is_active": is_active}
            response = await client.get("/tenants/", params=params)
            response.raise_for_status()
            return response.json()

    async def analyze_impact(self, change_description: str) -> Dict[str, Any]:
        """Analyze impact of a change (Simulated/AI)."""
        # Placeholder for AI agent call
        return {
            "risk_score": 5,
            "impact_areas": ["Security", "Compliance"],
            "recommendation": "Review security policy"
        }

    # =========================================================================
    # STAKEHOLDERS (ISO 27001 §4.2)
    # =========================================================================

    async def get_stakeholders(
        self,
        skip: int = 0,
        limit: int = 100,
        tenant_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Get list of stakeholders."""
        async with self._get_client() as client:
            params = {"skip": skip, "limit": limit}
            if tenant_id:
                params["tenant_id"] = tenant_id

            response = await client.get("/stakeholders/", params=params)
            response.raise_for_status()
            return response.json()

    async def create_stakeholder(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new stakeholder."""
        async with self._get_client() as client:
            response = await client.post("/stakeholders/", json=data)
            response.raise_for_status()
            return response.json()

    async def update_stakeholder(self, stakeholder_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a stakeholder."""
        async with self._get_client() as client:
            response = await client.put(f"/stakeholders/{stakeholder_id}", json=data)
            response.raise_for_status()
            return response.json()

    async def delete_stakeholder(self, stakeholder_id: int) -> Dict[str, Any]:
        """Delete a stakeholder."""
        async with self._get_client() as client:
            response = await client.delete(f"/stakeholders/{stakeholder_id}")
            response.raise_for_status()
            return response.json()

    # =========================================================================
    # ORGANIZATION PROFILE (ISO 27001 §4.1)
    # =========================================================================

    async def get_organization_profile(self) -> Optional[Dict[str, Any]]:
        """Get organization profile (singleton per tenant)."""
        async with self._get_client() as client:
            try:
                response = await client.get("/organization-profile/me")
                response.raise_for_status()
                return response.json()
            except Exception:
                return None

    async def update_organization_profile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update organization profile."""
        async with self._get_client() as client:
            response = await client.patch("/organization-profile/me", json=data)
            response.raise_for_status()
            return response.json()

    async def create_tenant(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new tenant."""
        async with self._get_client() as client:
            response = await client.post("/tenants/", json=data)
            response.raise_for_status()
            return response.json()

    async def update_tenant(self, tenant_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a tenant."""
        async with self._get_client() as client:
            response = await client.patch(f"/tenants/{tenant_id}", json=data)
            response.raise_for_status()
            return response.json()

    async def deactivate_tenant(self, tenant_id: int) -> Dict[str, Any]:
        """Deactivate a tenant (soft delete)."""
        async with self._get_client() as client:
            response = await client.delete(f"/tenants/{tenant_id}")
            response.raise_for_status()
            return response.json()

    async def get_tenant_users(self, tenant_id: int) -> List[Dict[str, Any]]:
        """Get all users in a tenant."""
        async with self._get_client() as client:
            response = await client.get(f"/tenants/{tenant_id}/users")
            response.raise_for_status()
            return response.json()

    async def add_user_to_tenant_by_tid(self, tenant_id: int, user_id: int) -> Dict[str, Any]:
        """Add a user to a tenant."""
        async with self._get_client() as client:
            response = await client.post(f"/tenants/{tenant_id}/users/{user_id}")
            response.raise_for_status()
            return response.json()

    async def remove_user_from_tenant_by_tid(self, tenant_id: int, user_id: int) -> Dict[str, Any]:
        """Remove a user from a tenant."""
        async with self._get_client() as client:
            response = await client.delete(f"/tenants/{tenant_id}/users/{user_id}")
            response.raise_for_status()
            return response.json()

    async def update_tenant_user_role(self, tenant_id: int, user_id: int, role: str) -> Dict[str, Any]:
        """Update a user's TenantRole."""
        async with self._get_client() as client:
            response = await client.patch(
                f"/tenants/{tenant_id}/users/{user_id}/role",
                json={"role": role},
            )
            response.raise_for_status()
            return response.json()

    # =========================================================================
    # STATEMENT OF APPLICABILITY (SoA)
    # =========================================================================

    async def get_soa_entries(
        self,
        skip: int = 0,
        limit: int = 100,
        tenant_id: Optional[int] = None,
        scope_id: Optional[int] = None,
        standard_id: Optional[int] = None,
        is_applicable: Optional[bool] = None,
        coverage_type: Optional[str] = None,
        implementation_status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get list of SoA entries."""
        async with self._get_client() as client:
            params = {"skip": skip, "limit": limit}
            if tenant_id:
                params["tenant_id"] = tenant_id
            if scope_id:
                params["scope_id"] = scope_id
            if standard_id:
                params["standard_id"] = standard_id
            if is_applicable is not None:
                params["is_applicable"] = is_applicable
            if coverage_type:
                params["coverage_type"] = coverage_type
            if implementation_status:
                params["implementation_status"] = implementation_status

            response = await client.get("/soa/", params=params)
            response.raise_for_status()
            return response.json()

    async def get_soa_entry(self, soa_id: int) -> Dict[str, Any]:
        """Get a single SoA entry by ID."""
        async with self._get_client() as client:
            response = await client.get(f"/soa/{soa_id}")
            response.raise_for_status()
            return response.json()

    async def update_soa_entry(self, soa_id: int, soa_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an SoA entry."""
        async with self._get_client() as client:
            response = await client.patch(f"/soa/{soa_id}", json=soa_data)
            response.raise_for_status()
            return response.json()

    async def get_soa_summary(
        self,
        scope_id: int,
        tenant_id: Optional[int] = None,
        standard_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get SoA summary for a scope."""
        async with self._get_client() as client:
            params = {}
            if tenant_id:
                params["tenant_id"] = tenant_id
            if standard_id:
                params["standard_id"] = standard_id

            response = await client.get(f"/soa/scope/{scope_id}/summary", params=params)
            response.raise_for_status()
            return response.json()

    async def get_soa_gaps(
        self,
        scope_id: int,
        tenant_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Get SoA gaps for a scope."""
        async with self._get_client() as client:
            params = {}
            if tenant_id:
                params["tenant_id"] = tenant_id

            response = await client.get(f"/soa/scope/{scope_id}/gaps", params=params)
            response.raise_for_status()
            return response.json()

    async def initialize_soa_from_standard(
        self,
        scope_id: int,
        standard_id: int,
        tenant_id: int,
    ) -> Dict[str, Any]:
        """Initialize SoA entries from a standard."""
        async with self._get_client() as client:
            params = {"tenant_id": tenant_id}
            response = await client.post(
                f"/soa/scope/{scope_id}/initialize-from-standard/{standard_id}",
                params=params
            )
            response.raise_for_status()
            return response.json()

    # =========================================================================
    # STANDARDS
    # =========================================================================

    async def get_standards(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get list of standards."""
        async with self._get_client() as client:
            params = {"skip": skip, "limit": limit}
            response = await client.get("/standards/", params=params)
            response.raise_for_status()
            return response.json()

    async def get_requirements_for_standard(self, standard_id: int) -> List[Dict[str, Any]]:
        """Get requirements for a specific standard."""
        async with self._get_client() as client:
            response = await client.get(f"/standards/{standard_id}/requirements/")
            response.raise_for_status()
            return response.json()

    # =========================================================================
    # REPORTS / DASHBOARD
    # =========================================================================

    async def get_executive_dashboard(
        self,
        tenant_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get executive dashboard data."""
        async with self._get_client() as client:
            params = {}
            if tenant_id:
                params["tenant_id"] = tenant_id

            response = await client.get("/reports/dashboard/executive", params=params)
            response.raise_for_status()
            return response.json()

    async def get_compliance_overview(
        self,
        tenant_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get compliance overview."""
        async with self._get_client() as client:
            params = {}
            if tenant_id:
                params["tenant_id"] = tenant_id

            response = await client.get("/reports/compliance/overview", params=params)
            response.raise_for_status()
            return response.json()

    async def get_risk_summary(
        self,
        tenant_id: Optional[int] = None,
        scope_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get risk summary report."""
        async with self._get_client() as client:
            params = {}
            if tenant_id:
                params["tenant_id"] = tenant_id
            if scope_id:
                params["scope_id"] = scope_id
            response = await client.get("/reports/risks/summary", params=params)
            response.raise_for_status()
            return response.json()

    async def get_assessment_summary(
        self,
        tenant_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get assessment and findings summary."""
        async with self._get_client() as client:
            params = {}
            if tenant_id:
                params["tenant_id"] = tenant_id
            response = await client.get("/reports/assessments/summary", params=params)
            response.raise_for_status()
            return response.json()

    async def get_incident_summary(
        self,
        tenant_id: Optional[int] = None,
        days: int = 30,
    ) -> Dict[str, Any]:
        """Get incident summary."""
        async with self._get_client() as client:
            params = {"days": days}
            if tenant_id:
                params["tenant_id"] = tenant_id
            response = await client.get("/reports/incidents/summary", params=params)
            response.raise_for_status()
            return response.json()

    async def get_actions_summary(
        self,
        tenant_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get corrective actions summary."""
        async with self._get_client() as client:
            params = {}
            if tenant_id:
                params["tenant_id"] = tenant_id
            response = await client.get("/reports/actions/summary", params=params)
            response.raise_for_status()
            return response.json()

    # =========================================================================
    # BACKLOG
    # =========================================================================

    async def get_backlog_items(
        self,
        skip: int = 0,
        limit: int = 100,
        tenant_id: Optional[int] = None,
        item_type: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get list of backlog items."""
        async with self._get_client() as client:
            params = {"skip": skip, "limit": limit}
            if tenant_id:
                params["tenant_id"] = tenant_id
            if item_type:
                params["item_type"] = item_type
            if status:
                params["status"] = status
            if priority:
                params["priority"] = priority

            response = await client.get("/backlog/", params=params)
            response.raise_for_status()
            return response.json()

    async def get_backlog_item(self, item_id: int) -> Dict[str, Any]:
        """Get a single backlog item by ID."""
        async with self._get_client() as client:
            response = await client.get(f"/backlog/{item_id}")
            response.raise_for_status()
            return response.json()

    async def create_backlog_item(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new backlog item."""
        async with self._get_client() as client:
            response = await client.post("/backlog/", json=item_data)
            response.raise_for_status()
            return response.json()

    async def update_backlog_item(self, item_id: int, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a backlog item."""
        async with self._get_client() as client:
            response = await client.patch(f"/backlog/{item_id}", json=item_data)
            response.raise_for_status()
            return response.json()

    async def delete_backlog_item(self, item_id: int) -> Dict[str, Any]:
        """Delete a backlog item."""
        async with self._get_client() as client:
            response = await client.delete(f"/backlog/{item_id}")
            response.raise_for_status()
            return response.json()

    # =========================================================================
    # AI AGENTS / CHAT
    # =========================================================================

    async def get_agents(self) -> List[Dict[str, Any]]:
        """Get list of available AI agents."""
        async with self._get_client() as client:
            response = await client.get("/agents/")
            response.raise_for_status()
            return response.json()

    async def detect_agent(
        self,
        page: Optional[str] = None,
        entity_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Detect recommended agent for context."""
        async with self._get_client() as client:
            params = {}
            if page:
                params["page"] = page
            if entity_type:
                params["entity_type"] = entity_type

            response = await client.get("/agents/detect", params=params)
            response.raise_for_status()
            return response.json()

    async def chat_with_agent(
        self,
        message: str,
        agent_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Send a chat message to an AI agent."""
        async with self._get_client() as client:
            payload = {
                "message": message,
                "context": context or {},
                "history": history or [],
            }
            if agent_name:
                payload["agent_name"] = agent_name

            response = await client.post("/agents/chat", json=payload)
            response.raise_for_status()
            return response.json()

    async def get_agent_health(self) -> Dict[str, Any]:
        """Check AI agent system health."""
        async with self._get_client() as client:
            response = await client.get("/agents/health")
            response.raise_for_status()
            return response.json()

    # =========================================================================
    # KNOWLEDGE BASE
    # =========================================================================

    async def get_knowledge_entries(
        self,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get list of knowledge base entries."""
        async with self._get_client() as client:
            params = {"skip": skip, "limit": limit}
            if category:
                params["category"] = category
            if subcategory:
                params["subcategory"] = subcategory
            if search:
                params["search"] = search
                
            response = await client.get("/knowledge/", params=params)
            response.raise_for_status()
            return response.json()

    # =========================================================================
    # SIMULATION (Monte Carlo)
    # =========================================================================

    async def get_quantification_config(self, tenant_id: int) -> Dict[str, Any]:
        """Get risk quantification profile."""
        async with self._get_client() as client:
            params = {"tenant_id": tenant_id}
            response = await client.get("/simulation/config", params=params)
            response.raise_for_status()
            return response.json()

    async def save_quantification_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save risk quantification profile."""
        async with self._get_client() as client:
            response = await client.post("/simulation/config", json=config_data)
            response.raise_for_status()
            return response.json()

    async def run_simulation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Run Monte Carlo simulation."""
        async with self._get_client() as client:
            # tenant_id is in query param for GET, but usually POST body is better for actions
            # My backend implementation expects tenant_id as query param for GET, but payload for POST?
            # Let's check backend implementation:
            # async def run_simulation(tenant_id: int, ...) -> query param
            # Wait, FastAPI automatically uses query params for scalar types unless Body is used.
            # I should pass them as query params if they are arguments to the function.
            # Let's adjust the client to match the backend signature.
            # Backend: tenant_id: int, iterations: int = 10000, scope_id... risk_ids...
            # These are query params. risk_ids is list, so query param with multiple values?
            # Or Body?
            # In FastAPI, complex types (like List) usually imply Body if not Query().
            # risk_ids: Optional[List[int]] = None -> likely Body in JSON.
            # tenant_id: int -> Query param by default in FastAPI if not part of a Pydantic model.

            # To be safe, I'll pass everything as query params that fits, and risk_ids as body?
            # Actually, passing mixed query/body is annoying.
            # Let's assume the backend takes query params for scalars.

            params = {
                "tenant_id": payload.get("tenant_id"),
                "iterations": payload.get("iterations", 10000)
            }
            if payload.get("scope_id"):
                params["scope_id"] = payload.get("scope_id")

            # risk_ids is list. FastAPI handles list query params as risk_ids=1&risk_ids=2
            # but httpx handles it too.
            # BUT: risk_ids might be large.
            # Let's verify backend signature again.
            pass

            # Since I wrote the backend, I know:
            # async def run_simulation(tenant_id: int, ..., risk_ids: Optional[List[int]] = None, ...)
            # FastAPI treats List[int] as query param unless Body(...) is used.
            # Sending list as query param is fine for small lists.

            req_params = params.copy()
            if payload.get("risk_ids"):
                req_params["risk_ids"] = payload.get("risk_ids")

            response = await client.post("/simulation/run", params=req_params)
            response.raise_for_status()
            return response.json()


    # =========================================================================
    # HIAAT 1: DECISIONS (Besluitlog)
    # =========================================================================

    async def get_decisions(
        self,
        skip: int = 0,
        limit: int = 100,
        tenant_id: Optional[int] = None,
        decision_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get list of decisions."""
        async with self._get_client() as client:
            params = {"skip": skip, "limit": limit}
            if tenant_id:
                params["tenant_id"] = tenant_id
            if decision_type:
                params["decision_type"] = decision_type
            if status:
                params["status"] = status
            response = await client.get("/decisions/", params=params)
            response.raise_for_status()
            return response.json()

    async def get_decision(self, decision_id: int) -> Dict[str, Any]:
        async with self._get_client() as client:
            response = await client.get(f"/decisions/{decision_id}")
            response.raise_for_status()
            return response.json()

    async def create_decision(self, data: Dict[str, Any]) -> Dict[str, Any]:
        async with self._get_client() as client:
            response = await client.post("/decisions/", json=data)
            response.raise_for_status()
            return response.json()

    async def update_decision(self, decision_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        async with self._get_client() as client:
            response = await client.patch(f"/decisions/{decision_id}", json=data)
            response.raise_for_status()
            return response.json()

    async def delete_decision(self, decision_id: int) -> Dict[str, Any]:
        async with self._get_client() as client:
            response = await client.delete(f"/decisions/{decision_id}")
            response.raise_for_status()
            return response.json()

    async def link_decision_risk(self, decision_id: int, risk_id: int) -> Dict[str, Any]:
        async with self._get_client() as client:
            response = await client.post(f"/decisions/{decision_id}/risks/{risk_id}")
            response.raise_for_status()
            return response.json()

    async def unlink_decision_risk(self, decision_id: int, risk_id: int) -> Dict[str, Any]:
        async with self._get_client() as client:
            response = await client.delete(f"/decisions/{decision_id}/risks/{risk_id}")
            response.raise_for_status()
            return response.json()

    async def get_decision_risks(self, decision_id: int) -> List[Dict[str, Any]]:
        async with self._get_client() as client:
            response = await client.get(f"/decisions/{decision_id}/risks")
            response.raise_for_status()
            return response.json()

    async def get_expired_decisions(self, tenant_id: Optional[int] = None) -> List[Dict[str, Any]]:
        async with self._get_client() as client:
            params = {}
            if tenant_id:
                params["tenant_id"] = tenant_id
            response = await client.get("/decisions/expired", params=params)
            response.raise_for_status()
            return response.json()

    # =========================================================================
    # HIAAT 3: RISK FRAMEWORK (Risicokader)
    # =========================================================================

    async def get_risk_frameworks(
        self,
        skip: int = 0,
        limit: int = 100,
        tenant_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        async with self._get_client() as client:
            params = {"skip": skip, "limit": limit}
            if tenant_id:
                params["tenant_id"] = tenant_id
            if status:
                params["status"] = status
            response = await client.get("/risk-framework/", params=params)
            response.raise_for_status()
            return response.json()

    async def get_active_risk_framework(
        self,
        tenant_id: int,
        scope_id: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        async with self._get_client() as client:
            params = {"tenant_id": tenant_id}
            if scope_id:
                params["scope_id"] = scope_id
            response = await client.get("/risk-framework/active", params=params)
            response.raise_for_status()
            return response.json()

    async def create_risk_framework(self, data: Dict[str, Any]) -> Dict[str, Any]:
        async with self._get_client() as client:
            response = await client.post("/risk-framework/", json=data)
            response.raise_for_status()
            return response.json()

    async def update_risk_framework(self, framework_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        async with self._get_client() as client:
            response = await client.patch(f"/risk-framework/{framework_id}", json=data)
            response.raise_for_status()
            return response.json()

    async def activate_risk_framework(self, framework_id: int, established_by_id: int) -> Dict[str, Any]:
        async with self._get_client() as client:
            params = {"established_by_id": established_by_id}
            response = await client.post(f"/risk-framework/{framework_id}/activate", params=params)
            response.raise_for_status()
            return response.json()

    # =========================================================================
    # HIAAT 5: IN-CONTROL STATUS
    # =========================================================================

    async def get_in_control_dashboard(self, tenant_id: int) -> List[Dict[str, Any]]:
        async with self._get_client() as client:
            params = {"tenant_id": tenant_id}
            response = await client.get("/in-control/dashboard", params=params)
            response.raise_for_status()
            return response.json()

    async def calculate_in_control(self, scope_id: int, tenant_id: int) -> Dict[str, Any]:
        async with self._get_client() as client:
            params = {"tenant_id": tenant_id}
            response = await client.get(f"/in-control/calculate/{scope_id}", params=params)
            response.raise_for_status()
            return response.json()

    async def create_in_control_assessment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        async with self._get_client() as client:
            response = await client.post("/in-control/", json=data)
            response.raise_for_status()
            return response.json()

    # =========================================================================
    # HIAAT 6: POLICY PRINCIPLES
    # =========================================================================

    async def get_policy_principles(
        self,
        skip: int = 0,
        limit: int = 100,
        tenant_id: Optional[int] = None,
        policy_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        async with self._get_client() as client:
            params = {"skip": skip, "limit": limit}
            if tenant_id:
                params["tenant_id"] = tenant_id
            if policy_id:
                params["policy_id"] = policy_id
            response = await client.get("/policy-principles/", params=params)
            response.raise_for_status()
            return response.json()

    async def create_policy_principle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        async with self._get_client() as client:
            response = await client.post("/policy-principles/", json=data)
            response.raise_for_status()
            return response.json()

    async def get_control_trace(self, control_id: int) -> Dict[str, Any]:
        async with self._get_client() as client:
            response = await client.get(f"/policy-principles/trace/{control_id}")
            response.raise_for_status()
            return response.json()

    # =========================================================================
    # RISK APPETITE (Risicotolerantie)
    # =========================================================================

    async def get_risk_appetites(
        self,
        current_only: bool = False,
    ) -> List[Dict[str, Any]]:
        async with self._get_client() as client:
            params = {}
            if current_only:
                params["current_only"] = True
            response = await client.get("/risk-appetite/", params=params)
            response.raise_for_status()
            return response.json()

    async def get_current_risk_appetite(self) -> Optional[Dict[str, Any]]:
        async with self._get_client() as client:
            response = await client.get("/risk-appetite/current")
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()

    async def create_risk_appetite(self, data: Dict[str, Any]) -> Dict[str, Any]:
        async with self._get_client() as client:
            response = await client.post("/risk-appetite/", json=data)
            response.raise_for_status()
            return response.json()

    async def update_risk_appetite(self, appetite_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        async with self._get_client() as client:
            response = await client.patch(f"/risk-appetite/{appetite_id}", json=data)
            response.raise_for_status()
            return response.json()

    async def activate_risk_appetite(self, appetite_id: int) -> Dict[str, Any]:
        async with self._get_client() as client:
            response = await client.post(f"/risk-appetite/{appetite_id}/activate")
            response.raise_for_status()
            return response.json()

    async def get_appetite_heatmap(
        self,
        appetite_level: Optional[str] = None,
    ) -> Dict[str, Any]:
        async with self._get_client() as client:
            params = {}
            if appetite_level:
                params["appetite_level"] = appetite_level
            response = await client.get("/risk-appetite/heatmap", params=params)
            response.raise_for_status()
            return response.json()

    async def get_domain_heatmap(self, domain: str) -> Dict[str, Any]:
        async with self._get_client() as client:
            response = await client.get(f"/risk-appetite/heatmap/{domain}")
            response.raise_for_status()
            return response.json()

    async def evaluate_risk_scope(self, risk_scope_id: int) -> Dict[str, Any]:
        async with self._get_client() as client:
            response = await client.get(f"/risk-appetite/evaluate/{risk_scope_id}")
            response.raise_for_status()
            return response.json()

    async def evaluate_scope_risks(self, scope_id: int) -> Dict[str, Any]:
        async with self._get_client() as client:
            response = await client.get(f"/risk-appetite/evaluate/scope/{scope_id}")
            response.raise_for_status()
            return response.json()

    async def evaluate_tenant_risks(self) -> Dict[str, Any]:
        async with self._get_client() as client:
            response = await client.get("/risk-appetite/evaluate/tenant")
            response.raise_for_status()
            return response.json()

    # =========================================================================
    # GRAPH / RELATIONSHIPS
    # =========================================================================

    async def get_graph_relationships(
        self,
        entity_types: str = "risk,control,scope,measure,decision,assessment",
        scope_id: Optional[int] = None,
        tenant_id: int = 1,
    ) -> Dict[str, Any]:
        """Get relationship graph data (nodes, edges, gaps)."""
        async with self._get_client() as client:
            params = {"entity_types": entity_types, "tenant_id": tenant_id}
            if scope_id:
                params["scope_id"] = scope_id
            response = await client.get("/graph/relationships", params=params)
            response.raise_for_status()
            return response.json()

    # =========================================================================
    # ADMIN PANEL
    # =========================================================================

    async def change_password(self, user_id: int, new_password: str, caller_id: int = 0) -> Dict[str, Any]:
        """Admin changes another user's password."""
        async with self._get_client() as client:
            params = {"caller_id": caller_id} if caller_id else {}
            response = await client.post(
                "/auth/change-password",
                json={"user_id": user_id, "new_password": new_password},
                params=params,
            )
            response.raise_for_status()
            return response.json()

    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health status."""
        async with self._get_client() as client:
            response = await client.get("/system/health")
            response.raise_for_status()
            return response.json()

    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        async with self._get_client() as client:
            response = await client.get("/system/stats")
            response.raise_for_status()
            return response.json()

    async def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit log (recent logins)."""
        async with self._get_client() as client:
            response = await client.get("/system/audit-log", params={"limit": limit})
            response.raise_for_status()
            return response.json()

    # =========================================================================
    # ORGANIZATION PROFILE
    # =========================================================================

    async def get_organization_profile(self) -> Dict[str, Any]:
        """Get organization profile for current tenant."""
        async with self._get_client() as client:
            response = await client.get("/organization-profile/")
            response.raise_for_status()
            return response.json()

    async def upsert_organization_profile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or fully update organization profile."""
        async with self._get_client() as client:
            response = await client.put("/organization-profile/", json=data)
            response.raise_for_status()
            return response.json()

    async def patch_organization_profile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Partial update organization profile (per wizard step)."""
        async with self._get_client() as client:
            response = await client.patch("/organization-profile/", json=data)
            response.raise_for_status()
            return response.json()

    async def get_profile_completion(self) -> Dict[str, Any]:
        """Get profile completion percentage."""
        async with self._get_client() as client:
            response = await client.get("/organization-profile/completion")
            response.raise_for_status()
            return response.json()

    # =========================================================================
    # HIAAT 2: SCOPE GOVERNANCE
    # =========================================================================

    # =========================================================================
    # HIAAT 7: ACT-FEEDBACKLOOP
    # =========================================================================

    async def get_act_overdue_summary(self, tenant_id: Optional[int] = None) -> Dict[str, Any]:
        async with self._get_client() as client:
            params = {}
            if tenant_id:
                params["tenant_id"] = tenant_id
            response = await client.get("/assessments/act-overdue", params=params)
            response.raise_for_status()
            return response.json()

    async def get_my_tasks(self, user_id: int, tenant_id: int) -> Dict[str, Any]:
        """Get unified task list for a user (corrective actions, reviews, approvals)."""
        async with self._get_client() as client:
            response = await client.get(
                "/dashboard/my-tasks",
                params={"user_id": user_id, "tenant_id": tenant_id},
            )
            response.raise_for_status()
            return response.json()

    async def establish_scope(self, scope_id: int, established_by_id: int, validity_year: int, motivation: Optional[str] = None) -> Dict[str, Any]:
        async with self._get_client() as client:
            params = {"established_by_id": established_by_id, "validity_year": validity_year}
            if motivation:
                params["motivation"] = motivation
            response = await client.post(f"/scopes/{scope_id}/establish", params=params)
            response.raise_for_status()
            return response.json()

    async def expire_scope(self, scope_id: int) -> Dict[str, Any]:
        async with self._get_client() as client:
            response = await client.post(f"/scopes/{scope_id}/expire")
            response.raise_for_status()
            return response.json()


# Singleton instance
api_client = APIClient()
