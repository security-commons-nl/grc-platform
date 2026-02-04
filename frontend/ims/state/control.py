"""
Control State - handles context-specific control implementations
"""
import reflex as rx
from typing import List, Dict, Any, Optional
from ims.api.client import api_client


class ControlState(rx.State):
    """Control management state."""

    controls: List[Dict[str, Any]] = []
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
    form_status: str = "DRAFT"
    form_control_type: str = "Preventive"
    form_automation_level: str = "Manual"
    form_scope_id: str = ""

    # Delete confirmation
    show_delete_dialog: bool = False
    deleting_control_id: Optional[int] = None
    deleting_control_name: str = ""

    # Success/Error messages
    success_message: str = ""

    @rx.var
    def active_count(self) -> int:
        return len([c for c in self.controls if c.get("status") == "ACTIVE"])

    @rx.var
    def implemented_count(self) -> int:
        return len([c for c in self.controls if c.get("status") == "CLOSED"])

    @rx.var
    def draft_count(self) -> int:
        return len([c for c in self.controls if c.get("status") == "DRAFT"])

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
        self.form_status = "DRAFT"
        self.form_control_type = "Preventive"
        self.form_automation_level = "Manual"
        self.form_scope_id = ""
        self.error = ""

    def open_create_dialog(self):
        """Open dialog for creating a new control."""
        self.is_editing = False
        self.editing_control_id = None
        self._reset_form()
        self.show_form_dialog = True

    def open_edit_dialog(self, control_id: int):
        """Open dialog for editing an existing control."""
        for control in self.controls:
            if control.get("id") == control_id:
                self.is_editing = True
                self.editing_control_id = control_id
                self.form_title = control.get("title", "")
                self.form_description = control.get("description", "") or ""
                self.form_status = control.get("status", "DRAFT")
                self.form_control_type = control.get("control_type", "Preventive") or "Preventive"
                self.form_automation_level = control.get("automation_level", "Manual") or "Manual"
                self.show_form_dialog = True
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

    # ==========================================================================
    # CRUD METHODS
    # ==========================================================================

    async def save_control(self):
        """Save control (create or update)."""
        if not self.form_title.strip():
            self.error = "Titel is verplicht"
            return

        try:
            data = {
                "title": self.form_title.strip(),
                "description": self.form_description.strip() or None,
                "status": self.form_status,
                "control_type": self.form_control_type,
                "automation_level": self.form_automation_level,
                "tenant_id": 1,
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
