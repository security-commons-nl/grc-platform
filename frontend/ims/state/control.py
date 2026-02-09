"""
Control State - handles context-specific control implementations
"""
import reflex as rx
from typing import List, Dict, Any, Optional
from ims.api.client import api_client
from ims.state.auth import AuthState


class ControlState(rx.State):
    """Control management state."""

    controls: List[Dict[str, Any]] = []
    scopes: List[Dict[str, Any]] = []  # Available scopes for linking
    selected_control: Dict[str, Any] = {}

    # Filters
    filter_status: str = "ALLE"

    # Loading
    is_loading: bool = False
    error: str = ""

    # Dialog state
    show_form_dialog: bool = False
    is_editing: bool = False
    editing_control_id: Optional[int] = None

    # Form fields
    form_title: str = ""
    form_description: str = ""
    form_status: str = "Draft"
    form_control_type: str = "Preventive"
    form_automation_level: str = "Manual"
    form_scope_id: str = "0"

    # Risk linkage
    linked_risks: List[Dict[str, Any]] = []
    all_risks: List[Dict[str, Any]] = []
    selected_risk_id_to_link: str = ""

    # Scope-contextualized risk linkage
    linked_risk_scopes: List[Dict[str, Any]] = []

    # Delete confirmation
    show_delete_dialog: bool = False
    deleting_control_id: Optional[int] = None
    deleting_control_name: str = ""

    # Success/Error messages
    success_message: str = ""

    @rx.var
    def active_count(self) -> int:
        return len([c for c in self.controls if c.get("status") == "Active"])

    @rx.var
    def implemented_count(self) -> int:
        return len([c for c in self.controls if c.get("status") == "Closed"])

    @rx.var
    def draft_count(self) -> int:
        return len([c for c in self.controls if c.get("status") == "Draft"])

    @rx.var
    def available_risks(self) -> List[Dict[str, Any]]:
        """Risks not yet linked to the current control."""
        linked_ids = {str(r.get("id")) for r in self.linked_risks}
        return [r for r in self.all_risks if str(r.get("id")) not in linked_ids]

    async def load_controls(self):
        """Load controls from API."""
        self.is_loading = True
        self.error = ""
        self.success_message = ""

        try:
            params = {}
            if self.filter_status and self.filter_status != "ALLE":
                params["status"] = self.filter_status

            self.controls = await api_client.get_controls(**params)
            # Also load scopes for the dropdown
            self.scopes = await api_client.get_scopes()

            # Enrich controls with scope name for display
            scope_map = {str(s["id"]): s["name"] for s in self.scopes}
            for control in self.controls:
                scope_id = str(control.get("scope_id", ""))
                if scope_id and scope_id != "0" and scope_id != "None":
                    control["scope_name"] = scope_map.get(scope_id, "-")
                else:
                    control["scope_name"] = "-"

        except Exception as e:
            self.error = f"Kan controls niet laden: {str(e)}"
            self.controls = []
        finally:
            self.is_loading = False

    def set_filter_status(self, status: str):
        """Set status filter."""
        self.filter_status = status
        return ControlState.load_controls

    def clear_filters(self):
        """Clear all filters."""
        self.filter_status = "ALLE"
        return ControlState.load_controls

    # ==========================================================================
    # FORM METHODS
    # ==========================================================================

    def _reset_form(self):
        """Reset form fields."""
        self.form_title = ""
        self.form_description = ""
        self.form_status = "Draft"
        self.form_control_type = "Preventive"
        self.form_automation_level = "Manual"
        self.form_scope_id = "0"
        self.error = ""

    def open_create_dialog(self):
        """Open dialog for creating a new control."""
        self.is_editing = False
        self.editing_control_id = None
        self.linked_risks = []
        self.all_risks = []
        self._reset_form()
        self.show_form_dialog = True

    async def open_edit_dialog(self, control_id: int):
        """Open dialog for editing an existing control."""
        # Reset linkage data
        self.linked_risks = []
        self.all_risks = []
        self.selected_risk_id_to_link = ""

        for control in self.controls:
            if control.get("id") == control_id:
                self.is_editing = True
                self.editing_control_id = control_id
                self.form_title = control.get("title", "")
                self.form_description = control.get("description", "") or ""
                # Normalize status to Title Case (Active, Draft, Closed)
                status = control.get("status", "Draft")
                self.form_status = status.capitalize() if status else "Draft"
                
                self.form_control_type = control.get("control_type", "Preventive") or "Preventive"
                self.form_automation_level = control.get("automation_level", "Manual") or "Manual"
                self.form_scope_id = str(control.get("scope_id", "")) if control.get("scope_id") else "0"
                self.show_form_dialog = True

                # Load linked and all risks
                await self.load_linked_risks(control_id)
                await self.load_all_risks()
                break

    def close_form_dialog(self):
        self.show_form_dialog = False
        self._reset_form()

    # Form field setters
    def set_form_title(self, value: str):
        self.form_title = value

    def set_form_description(self, value: str):
        self.form_description = value

    def set_form_status(self, value: str):
        self.form_status = value

    def set_form_control_type(self, value: str):
        self.form_control_type = value

    def set_form_automation_level(self, value: str):
        self.form_automation_level = value

    def set_form_scope_id(self, value: str):
        self.form_scope_id = value

    # ==========================================================================
    # LINKING METHODS
    # ==========================================================================

    async def load_linked_risks(self, control_id: int):
        """Load risks linked to this control."""
        try:
            self.linked_risks = await api_client.get_control_risks(control_id)
        except Exception:
            self.linked_risks = []

    async def load_all_risks(self):
        """Load all risks for selection."""
        try:
            self.all_risks = await api_client.get_risks()
        except Exception:
            self.all_risks = []

    async def link_risk(self):
        """Link selected risk to current control."""
        if not self.editing_control_id or not self.selected_risk_id_to_link:
            return

        try:
            await api_client.link_control_risk(
                self.editing_control_id,
                int(self.selected_risk_id_to_link)
            )
            self.success_message = "Risico gekoppeld"
            await self.load_linked_risks(self.editing_control_id)
            self.selected_risk_id_to_link = ""
        except Exception as e:
            self.error = f"Fout bij koppelen: {str(e)}"

    async def unlink_risk(self, risk_id: int):
        """Unlink risk from current control."""
        if not self.editing_control_id:
            return

        try:
            await api_client.unlink_control_risk(self.editing_control_id, risk_id)
            self.success_message = "Risico ontkoppeld"
            await self.load_linked_risks(self.editing_control_id)
        except Exception as e:
            self.error = f"Fout bij ontkoppelen: {str(e)}"

    async def load_linked_risk_scopes(self, control_id: int):
        """Load scope-contextualized risks linked to this control."""
        try:
            async with api_client._get_client() as client:
                response = await client.get(f"/controls/{control_id}/risk-scopes")
                response.raise_for_status()
                self.linked_risk_scopes = response.json()
        except Exception:
            self.linked_risk_scopes = []

    # ==========================================================================
    # CRUD METHODS
    # ==========================================================================

    async def save_control(self):
        """Save control (create or update)."""
        if not self.form_title.strip():
            self.error = "Titel is verplicht"
            return

        auth = await self.get_state(AuthState)
        tid = auth.tenant_id

        try:
            data = {
                "title": self.form_title.strip(),
                "description": self.form_description.strip() or None,
                "status": self.form_status,
                "control_type": self.form_control_type,
                "automation_level": self.form_automation_level,
                "scope_id": int(self.form_scope_id) if self.form_scope_id and self.form_scope_id != "0" else None,
                "tenant_id": tid,
            }

            if self.is_editing and self.editing_control_id:
                await api_client.update_control(self.editing_control_id, data)
                self.success_message = "Control bijgewerkt"
            else:
                await api_client.create_control(data)
                self.success_message = "Control aangemaakt"

            self.show_form_dialog = False
            self._reset_form()
            await self.load_controls()

        except Exception as e:
            self.error = f"Fout bij opslaan: {str(e)}"

    # ==========================================================================
    # DELETE METHODS
    # ==========================================================================

    def open_delete_dialog(self, control_id: int):
        """Open delete confirmation dialog."""
        for control in self.controls:
            if control.get("id") == control_id:
                self.deleting_control_id = control_id
                self.deleting_control_name = control.get("title", "")
                self.show_delete_dialog = True
                break

    def close_delete_dialog(self):
        self.show_delete_dialog = False
        self.deleting_control_id = None
        self.deleting_control_name = ""

    async def confirm_delete(self):
        """Confirm and execute delete."""
        if not self.deleting_control_id:
            return

        try:
            await api_client.delete_control(self.deleting_control_id)
            self.success_message = "Control verwijderd"
            self.close_delete_dialog()
            await self.load_controls()
        except Exception as e:
            self.error = f"Fout bij verwijderen: {str(e)}"
            self.close_delete_dialog()
