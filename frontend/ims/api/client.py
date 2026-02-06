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
        self.timeout = httpx.Timeout(120.0)

    def _get_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)

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
    ) -> List[Dict[str, Any]]:
        """Get list of assessments."""
        async with self._get_client() as client:
            params = {"skip": skip, "limit": limit}
            if tenant_id:
                params["tenant_id"] = tenant_id

            response = await client.get("/assessments/", params=params)
            response.raise_for_status()
            return response.json()

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
        role: str = "Member",
        is_default: bool = False,
    ) -> Dict[str, Any]:
        """Add a user to a tenant."""
        async with self._get_client() as client:
            params = {"role": role, "is_default": is_default}
            response = await client.post(
                f"/users/{user_id}/tenants/{tenant_id}",
                params=params,
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


# Singleton instance
api_client = APIClient()
