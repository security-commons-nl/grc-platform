"""
Assessment State - handles assessment/verification data
"""
import reflex as rx
from typing import List, Dict, Any, Optional
from ims.api.client import api_client


class AssessmentState(rx.State):
    """Assessment management state."""

    assessments: List[Dict[str, Any]] = []
    selected_assessment: Dict[str, Any] = {}

    # Filters
    filter_type: str = "ALLE"
    filter_status: str = "ALLE"

    # Loading
    is_loading: bool = False
    error: str = ""

    @rx.var
    def active_count(self) -> int:
        return len([a for a in self.assessments if a.get("status") == "ACTIVE"])

    @rx.var
    def completed_count(self) -> int:
        return len([a for a in self.assessments if a.get("status") == "CLOSED"])

    async def load_assessments(self):
        """Load assessments from API."""
        self.is_loading = True
        self.error = ""

        try:
            params = {}
            if self.filter_type and self.filter_type != "ALLE":
                params["assessment_type"] = self.filter_type
            if self.filter_status and self.filter_status != "ALLE":
                params["status"] = self.filter_status

            self.assessments = await api_client.get_assessments(**params)
        except Exception as e:
            self.error = f"Kan assessments niet laden: {str(e)}"
            self.assessments = []
        finally:
            self.is_loading = False

    def set_filter_type(self, type_value: str):
        """Set type filter."""
        self.filter_type = type_value
        return AssessmentState.load_assessments

    def set_filter_status(self, status: str):
        """Set status filter."""
        self.filter_status = status
        return AssessmentState.load_assessments

    def clear_filters(self):
        """Clear all filters."""
        self.filter_type = "ALLE"
        self.filter_status = "ALLE"
        return AssessmentState.load_assessments
