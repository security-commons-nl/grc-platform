"""
Risk State - handles risk management data
"""
import reflex as rx
from typing import List, Dict, Any, Optional
from ims.api.client import api_client


class RiskState(rx.State):
    """Risk management state."""

    # Risk list
    risks: List[Dict[str, Any]] = []
    selected_risk: Dict[str, Any] = {}

    # Heatmap data
    heatmap_data: Dict[str, Any] = {
        "heatmap": {
            "MITIGATE": [],
            "ASSURANCE": [],
            "MONITOR": [],
            "ACCEPT": [],
            "UNCLASSIFIED": [],
        },
        "counts": {},
        "total": 0,
    }

    # Filters
    filter_quadrant: str = ""
    filter_scope_id: Optional[int] = None

    # Loading
    is_loading: bool = False
    error: str = ""

    # Computed properties for heatmap quadrants
    @rx.var
    def mitigate_risks(self) -> List[Dict[str, Any]]:
        """Risks in MITIGATE quadrant."""
        return self.heatmap_data.get("heatmap", {}).get("MITIGATE", [])

    @rx.var
    def assurance_risks(self) -> List[Dict[str, Any]]:
        """Risks in ASSURANCE quadrant."""
        return self.heatmap_data.get("heatmap", {}).get("ASSURANCE", [])

    @rx.var
    def monitor_risks(self) -> List[Dict[str, Any]]:
        """Risks in MONITOR quadrant."""
        return self.heatmap_data.get("heatmap", {}).get("MONITOR", [])

    @rx.var
    def accept_risks(self) -> List[Dict[str, Any]]:
        """Risks in ACCEPT quadrant."""
        return self.heatmap_data.get("heatmap", {}).get("ACCEPT", [])

    @rx.var
    def unclassified_risks(self) -> List[Dict[str, Any]]:
        """Risks without quadrant."""
        return self.heatmap_data.get("heatmap", {}).get("UNCLASSIFIED", [])

    @rx.var
    def total_risks(self) -> int:
        """Total number of risks."""
        return self.heatmap_data.get("total", 0)

    async def load_risks(self):
        """Load risks from API."""
        self.is_loading = True
        self.error = ""

        try:
            params = {}
            if self.filter_quadrant:
                params["quadrant"] = self.filter_quadrant
            if self.filter_scope_id:
                params["scope_id"] = self.filter_scope_id

            self.risks = await api_client.get_risks(**params)
        except Exception as e:
            self.error = f"Fout bij laden risico's: {str(e)}"
            self.risks = []
        finally:
            self.is_loading = False

    async def load_heatmap(self):
        """Load heatmap data from API."""
        self.is_loading = True
        self.error = ""

        try:
            self.heatmap_data = await api_client.get_risk_heatmap()
        except Exception as e:
            self.error = f"Fout bij laden heatmap: {str(e)}"
            self.heatmap_data = {
                "heatmap": {
                    "MITIGATE": [],
                    "ASSURANCE": [],
                    "MONITOR": [],
                    "ACCEPT": [],
                    "UNCLASSIFIED": [],
                },
                "counts": {},
                "total": 0,
            }
        finally:
            self.is_loading = False

    async def load_risk_detail(self, risk_id: int):
        """Load single risk detail."""
        self.is_loading = True
        try:
            self.selected_risk = await api_client.get_risk(risk_id)
        except Exception as e:
            self.error = f"Fout bij laden risico: {str(e)}"
            self.selected_risk = {}
        finally:
            self.is_loading = False

    def set_filter_quadrant(self, quadrant: str):
        """Set quadrant filter."""
        self.filter_quadrant = quadrant
        return RiskState.load_risks

    def clear_filters(self):
        """Clear all filters."""
        self.filter_quadrant = ""
        self.filter_scope_id = None
        return RiskState.load_risks
