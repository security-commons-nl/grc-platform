"""
Measure State - handles control measures data
"""
import reflex as rx
from typing import List, Dict, Any, Optional
from ims.api.client import api_client


class MeasureState(rx.State):
    """Measure management state."""

    measures: List[Dict[str, Any]] = []
    selected_measure: Dict[str, Any] = {}

    # Filters
    filter_status: str = "ALLE"

    # Loading
    is_loading: bool = False
    error: str = ""

    @rx.var
    def active_count(self) -> int:
        return len([m for m in self.measures if m.get("status") == "ACTIVE"])

    @rx.var
    def implemented_count(self) -> int:
        return len([m for m in self.measures if m.get("status") == "CLOSED"])

    async def load_measures(self):
        """Load measures from API."""
        self.is_loading = True
        self.error = ""

        try:
            params = {}
            if self.filter_status and self.filter_status != "ALLE":
                params["status"] = self.filter_status

            self.measures = await api_client.get_measures(**params)
        except Exception as e:
            self.error = f"Kan maatregelen niet laden: {str(e)}"
            self.measures = []
        finally:
            self.is_loading = False

    def set_filter_status(self, status: str):
        """Set status filter."""
        self.filter_status = status
        return MeasureState.load_measures

    def clear_filters(self):
        """Clear all filters."""
        self.filter_status = "ALLE"
        return MeasureState.load_measures
