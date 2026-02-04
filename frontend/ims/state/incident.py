"""
Incident State - handles incident management data
"""
import reflex as rx
from typing import List, Dict, Any, Optional
from ims.api.client import api_client


class IncidentState(rx.State):
    """Incident management state."""

    incidents: List[Dict[str, Any]] = []
    selected_incident: Dict[str, Any] = {}

    # Filters
    filter_status: str = "ALLE"
    filter_data_breach: str = "ALLE"

    # Loading
    is_loading: bool = False
    error: str = ""

    @rx.var
    def open_count(self) -> int:
        return len([i for i in self.incidents if i.get("status") in ["DRAFT", "ACTIVE"]])

    @rx.var
    def data_breach_count(self) -> int:
        return len([i for i in self.incidents if i.get("is_data_breach")])

    @rx.var
    def overdue_breaches(self) -> List[Dict[str, Any]]:
        """Data breaches past notification deadline."""
        return [
            i for i in self.incidents
            if i.get("is_data_breach") and not i.get("notified_to_authority")
        ]

    async def load_incidents(self):
        """Load incidents from API."""
        self.is_loading = True
        self.error = ""

        try:
            params = {}
            if self.filter_status and self.filter_status != "ALLE":
                params["status"] = self.filter_status
            if self.filter_data_breach == "JA":
                params["is_data_breach"] = True
            elif self.filter_data_breach == "NEE":
                params["is_data_breach"] = False

            self.incidents = await api_client.get_incidents(**params)
        except Exception as e:
            self.error = f"Kan incidenten niet laden: {str(e)}"
            self.incidents = []
        finally:
            self.is_loading = False

    def set_filter_status(self, status: str):
        """Set status filter."""
        self.filter_status = status
        return IncidentState.load_incidents

    def set_filter_data_breach(self, value: str):
        """Set data breach filter."""
        self.filter_data_breach = value
        return IncidentState.load_incidents

    def clear_filters(self):
        """Clear all filters."""
        self.filter_status = "ALLE"
        self.filter_data_breach = "ALLE"
        return IncidentState.load_incidents
