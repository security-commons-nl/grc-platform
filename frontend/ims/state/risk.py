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
    filter_quadrant: str = "ALLE"
    filter_scope_id: Optional[int] = None

    # Loading
    is_loading: bool = False
    error: str = ""
    success_message: str = ""

    # Dialog state
    show_form_dialog: bool = False
    is_editing: bool = False
    editing_risk_id: Optional[int] = None

    # Form fields
    form_title: str = ""
    form_description: str = ""
    form_inherent_likelihood: str = "MEDIUM"
    form_inherent_impact: str = "MEDIUM"
    form_attention_quadrant: str = "NONE"
    form_treatment_justification: str = ""

    # Control linkage
    linked_controls: List[Dict[str, Any]] = []
    all_controls: List[Dict[str, Any]] = []
    selected_control_id_to_link: Optional[str] = None

    # Delete confirmation
    show_delete_dialog: bool = False
    deleting_risk_id: Optional[int] = None
    deleting_risk_title: str = ""

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

    # ==========================================================================
    # LOAD METHODS
    # ==========================================================================

    async def load_risks(self):
        """Load risks from API."""
        self.is_loading = True
        self.error = ""
        self.success_message = ""

        try:
            params = {}
            if self.filter_quadrant and self.filter_quadrant != "ALLE":
                params["quadrant"] = self.filter_quadrant
            if self.filter_scope_id:
                params["scope_id"] = self.filter_scope_id

            self.risks = await api_client.get_risks(**params)
        except Exception:
            # Silently fail - just show empty list
            self.risks = []
        finally:
            self.is_loading = False

    async def load_heatmap(self):
        """Load heatmap data from API."""
        self.is_loading = True
        self.error = ""
        self.success_message = ""

        try:
            self.heatmap_data = await api_client.get_risk_heatmap()
        except Exception:
            # Silently fail - just show empty heatmap
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

    # ==========================================================================
    # FILTER METHODS
    # ==========================================================================

    def set_filter_quadrant(self, quadrant: str):
        """Set quadrant filter."""
        self.filter_quadrant = quadrant
        return RiskState.load_risks

    def clear_filters(self):
        """Clear all filters."""
        self.filter_quadrant = "ALLE"
        self.filter_scope_id = None
        return RiskState.load_risks

    # ==========================================================================
    # FORM DIALOG METHODS
    # ==========================================================================

    def open_create_dialog(self):
        """Open dialog for creating a new risk."""
        self.is_editing = False
        self.editing_risk_id = None
        self.linked_controls = []
        self.all_controls = []
        self._reset_form()
        self.show_form_dialog = True

    async def open_edit_dialog(self, risk_id: int):
        """Open dialog for editing an existing risk."""
        # Reset linkage data
        self.linked_controls = []
        self.all_controls = []
        self.selected_control_id_to_link = None

        # Mapping from API values (Dutch) to form values (enum names)
        quadrant_api_to_form = {
            "Mitigeren": "MITIGATE",
            "Zekerheid verkrijgen": "ASSURANCE",
            "Meten & monitoren": "MONITOR",
            "Accepteren": "ACCEPT",
        }
        level_api_to_form = {
            "Low": "LOW",
            "Medium": "MEDIUM",
            "High": "HIGH",
            "Critical": "CRITICAL",
        }

        # Find the risk in the list
        for risk in self.risks:
            if risk.get("id") == risk_id:
                self.is_editing = True
                self.editing_risk_id = risk_id
                self.form_title = risk.get("title", "")
                self.form_description = risk.get("description", "")
                # Convert API values to form values
                likelihood = risk.get("inherent_likelihood", "MEDIUM")
                self.form_inherent_likelihood = level_api_to_form.get(likelihood, likelihood)
                impact = risk.get("inherent_impact", "MEDIUM")
                self.form_inherent_impact = level_api_to_form.get(impact, impact)
                quadrant = risk.get("attention_quadrant")
                self.form_attention_quadrant = quadrant_api_to_form.get(quadrant, "NONE") if quadrant else "NONE"
                self.form_treatment_justification = risk.get("treatment_justification", "") or ""
                self.show_form_dialog = True

                # Load linked and all controls
                await self.load_linked_controls(risk_id)
                await self.load_all_controls()
                break

    def close_form_dialog(self):
        """Close the form dialog."""
        self.show_form_dialog = False
        self._reset_form()

    def _reset_form(self):
        """Reset all form fields."""
        self.form_title = ""
        self.form_description = ""
        self.form_inherent_likelihood = "MEDIUM"
        self.form_inherent_impact = "MEDIUM"
        self.form_attention_quadrant = "NONE"
        self.form_treatment_justification = ""
        self.error = ""
        self.success_message = ""

    # Form field setters
    def set_form_title(self, value: str):
        self.form_title = value

    def set_form_description(self, value: str):
        self.form_description = value

    def set_form_inherent_likelihood(self, value: str):
        self.form_inherent_likelihood = value

    def set_form_inherent_impact(self, value: str):
        self.form_inherent_impact = value

    def set_risk_matrix_cell(self, likelihood: str, impact: str):
        """Set both likelihood and impact from matrix click."""
        self.form_inherent_likelihood = likelihood
        self.form_inherent_impact = impact

    def set_form_attention_quadrant(self, value: str):
        self.form_attention_quadrant = value

    def set_form_treatment_justification(self, value: str):
        self.form_treatment_justification = value

    # ==========================================================================
    # LINKING METHODS
    # ==========================================================================

    async def load_linked_controls(self, risk_id: int):
        """Load controls linked to this risk."""
        try:
            self.linked_controls = await api_client.get_risk_controls(risk_id)
        except Exception:
            self.linked_controls = []

    async def load_all_controls(self):
        """Load all controls for selection."""
        try:
            self.all_controls = await api_client.get_controls()
        except Exception:
            self.all_controls = []

    async def link_control(self):
        """Link selected control to current risk."""
        if not self.editing_risk_id or not self.selected_control_id_to_link:
            return

        try:
            await api_client.link_risk_control(
                self.editing_risk_id,
                int(self.selected_control_id_to_link)
            )
            self.success_message = "Control gekoppeld"
            await self.load_linked_controls(self.editing_risk_id)
            self.selected_control_id_to_link = None
        except Exception as e:
            self.error = f"Fout bij koppelen: {str(e)}"

    async def unlink_control(self, control_id: int):
        """Unlink control from current risk."""
        if not self.editing_risk_id:
            return

        try:
            await api_client.unlink_risk_control(self.editing_risk_id, control_id)
            self.success_message = "Control ontkoppeld"
            await self.load_linked_controls(self.editing_risk_id)
        except Exception as e:
            self.error = f"Fout bij ontkoppelen: {str(e)}"

    # ==========================================================================
    # CRUD METHODS
    # ==========================================================================

    async def save_risk(self):
        """Save risk (create or update)."""
        self.error = ""
        self.success_message = ""

        # Validation
        if not self.form_title.strip():
            self.error = "Titel is verplicht"
            return

        # Map form values to API enum values
        # RiskLevel: "LOW" -> "Low", "MEDIUM" -> "Medium", etc.
        level_form_to_api = {
            "LOW": "Low",
            "MEDIUM": "Medium",
            "HIGH": "High",
            "CRITICAL": "Critical",
        }
        # AttentionQuadrant: "MITIGATE" -> "Mitigeren", etc.
        quadrant_form_to_api = {
            "MITIGATE": "Mitigeren",
            "ASSURANCE": "Zekerheid verkrijgen",
            "MONITOR": "Meten & monitoren",
            "ACCEPT": "Accepteren",
        }

        risk_data = {
            "title": self.form_title.strip(),
            "description": self.form_description.strip(),
            "inherent_likelihood": level_form_to_api.get(self.form_inherent_likelihood, self.form_inherent_likelihood),
            "inherent_impact": level_form_to_api.get(self.form_inherent_impact, self.form_inherent_impact),
            "tenant_id": 1,  # Default tenant for now
        }

        if self.form_attention_quadrant and self.form_attention_quadrant != "NONE":
            risk_data["attention_quadrant"] = quadrant_form_to_api.get(self.form_attention_quadrant, self.form_attention_quadrant)
        if self.form_treatment_justification:
            risk_data["treatment_justification"] = self.form_treatment_justification

        try:
            if self.is_editing and self.editing_risk_id:
                await api_client.update_risk(self.editing_risk_id, risk_data)
                self.success_message = "Risico bijgewerkt"
            else:
                await api_client.create_risk(risk_data)
                self.success_message = "Risico aangemaakt"

            self.show_form_dialog = False
            self._reset_form()
            # Reload the list
            return RiskState.load_risks
        except Exception as e:
            self.error = f"Fout bij opslaan: {str(e)}"

    # ==========================================================================
    # DELETE METHODS
    # ==========================================================================

    def open_delete_dialog(self, risk_id: int):
        """Open delete confirmation dialog."""
        for risk in self.risks:
            if risk.get("id") == risk_id:
                self.deleting_risk_id = risk_id
                self.deleting_risk_title = risk.get("title", "")
                self.show_delete_dialog = True
                break

    def close_delete_dialog(self):
        """Close delete confirmation dialog."""
        self.show_delete_dialog = False
        self.deleting_risk_id = None
        self.deleting_risk_title = ""

    async def confirm_delete(self):
        """Delete the risk after confirmation."""
        if not self.deleting_risk_id:
            return

        try:
            await api_client.delete_risk(self.deleting_risk_id)
            self.success_message = "Risico verwijderd"
            self.show_delete_dialog = False
            self.deleting_risk_id = None
            self.deleting_risk_title = ""
            return RiskState.load_risks
        except Exception as e:
            self.error = f"Fout bij verwijderen: {str(e)}"
            self.show_delete_dialog = False
