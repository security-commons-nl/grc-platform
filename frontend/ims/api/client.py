"""
API Client for IMS Backend
Uses httpx for async HTTP requests
"""
import httpx
from typing import Optional, List, Dict, Any

API_BASE_URL = "http://localhost:8000/api/v1"


class APIClient:
    """Async API client for IMS backend."""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.timeout = httpx.Timeout(30.0)

    def _get_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)

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
    # MEASURES
    # =========================================================================

    async def get_measures(
        self,
        skip: int = 0,
        limit: int = 100,
        tenant_id: Optional[int] = None,
        scope_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Get list of measures."""
        async with self._get_client() as client:
            params = {"skip": skip, "limit": limit}
            if tenant_id:
                params["tenant_id"] = tenant_id
            if scope_id:
                params["scope_id"] = scope_id

            response = await client.get("/risks/measures/", params=params)
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
    # USERS (for auth simulation)
    # =========================================================================

    async def get_users(self) -> List[Dict[str, Any]]:
        """Get list of users."""
        async with self._get_client() as client:
            response = await client.get("/users/")
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


# Singleton instance
api_client = APIClient()
