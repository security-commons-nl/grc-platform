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


# Singleton instance
api_client = APIClient()
