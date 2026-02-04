"""
Policy State - handles policy management data
"""
import reflex as rx
from typing import List, Dict, Any, Optional
from ims.api.client import api_client
from ims.components.deadline import enrich_with_multiple_deadlines


class PolicyState(rx.State):
    """Policy management state."""

    policies: List[Dict[str, Any]] = []
    selected_policy: Dict[str, Any] = {}

    # Filters
    filter_state: str = "ALLE"

    # Loading
    is_loading: bool = False
    error: str = ""

    # ==========================================================================
    # COMPUTED VARS - Counts by workflow state
    # ==========================================================================

    @rx.var
    def draft_count(self) -> int:
        return len([p for p in self.policies if p.get("state") == "Draft"])

    @rx.var
    def review_count(self) -> int:
        return len([p for p in self.policies if p.get("state") == "Review"])

    @rx.var
    def published_count(self) -> int:
        return len([p for p in self.policies if p.get("state") == "Published"])

    # ==========================================================================
    # COMPUTED VARS - Deadline status counts
    # ==========================================================================

    @rx.var
    def danger_count(self) -> int:
        """Count of policies with overdue deadlines."""
        return len([p for p in self.policies if p.get("_deadline_status") == "danger"])

    @rx.var
    def warning_count(self) -> int:
        """Count of policies with approaching deadlines."""
        return len([p for p in self.policies if p.get("_deadline_status") == "warning"])

    @rx.var
    def action_required_count(self) -> int:
        """Total items requiring attention (danger + warning)."""
        return self.danger_count + self.warning_count

    # ==========================================================================
    # DATA LOADING
    # ==========================================================================

    async def load_policies(self):
        """Load policies from API."""
        self.is_loading = True
        self.error = ""

        try:
            params = {}
            if self.filter_state and self.filter_state != "ALLE":
                params["state"] = self.filter_state

            policies = await api_client.get_policies(**params)

            # Enrich with deadline status (checks both review_date and expiration_date)
            self.policies = enrich_with_multiple_deadlines(
                policies,
                deadline_fields=["review_date", "expiration_date"]
            )
        except Exception as e:
            self.error = f"Kan beleid niet laden: {str(e)}"
            self.policies = []
        finally:
            self.is_loading = False

    # ==========================================================================
    # FILTERS
    # ==========================================================================

    def set_filter_state(self, state: str):
        """Set state filter."""
        self.filter_state = state
        return PolicyState.load_policies

    def clear_filters(self):
        """Clear all filters."""
        self.filter_state = "ALLE"
        return PolicyState.load_policies
