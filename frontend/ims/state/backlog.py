"""
Backlog State - handles backlog item data
"""
import reflex as rx
from typing import List, Dict, Any, Optional
from ims.api.client import api_client
from ims.state.auth import AuthState

class BacklogState(rx.State):
    """Backlog management state."""

    # Backlog list
    items: List[Dict[str, Any]] = []
    
    # Filters
    filter_type: str = "ALLE"
    filter_status: str = "ALLE"
    filter_priority: str = "ALLE"

    # Loading
    is_loading: bool = False
    error: str = ""
    success_message: str = ""

    # Dialog state
    show_form_dialog: bool = False
    is_editing: bool = False
    editing_item_id: Optional[int] = None

    # Form fields
    form_title: str = ""
    form_description: str = ""
    form_type: str = "Functioneel"
    form_priority: str = "Middel"
    form_status: str = "Nieuw"
    
    # Delete confirmation
    show_delete_dialog: bool = False
    deleting_item_id: Optional[int] = None
    deleting_item_title: str = ""

    @rx.var
    def is_admin(self) -> bool:
        """Check if current user is admin (simulated)."""
        # In a real app check permissions/roles
        # For now, simplistic check or assume user ID 1 is admin
        user = AuthState.user(self)
        if not user:
            return False
            
        # Simulating simple admin check - user ID 1 or username "admin"
        return user.get("id") == 1 or user.get("username", "").lower() == "admin"

    # ==========================================================================
    # LOAD METHODS
    # ==========================================================================

    async def load_items(self):
        """Load backlog items from API."""
        self.is_loading = True
        self.error = ""
        self.success_message = ""

        try:
            params = {}
            if self.filter_type and self.filter_type != "ALLE":
                params["item_type"] = self.filter_type
            if self.filter_status and self.filter_status != "ALLE":
                params["status"] = self.filter_status
            if self.filter_priority and self.filter_priority != "ALLE":
                params["priority"] = self.filter_priority

            self.items = await api_client.get_backlog_items(**params)
        except Exception as e:
            self.error = f"Fout bij laden backlog: {str(e)}"
            self.items = []
        finally:
            self.is_loading = False

    # ==========================================================================
    # FILTER METHODS
    # ==========================================================================

    def set_filter_type(self, value: str):
        self.filter_type = value
        return BacklogState.load_items

    def set_filter_status(self, value: str):
        self.filter_status = value
        return BacklogState.load_items

    def set_filter_priority(self, value: str):
        self.filter_priority = value
        return BacklogState.load_items
        
    def clear_filters(self):
        self.filter_type = "ALLE"
        self.filter_status = "ALLE"
        self.filter_priority = "ALLE"
        return BacklogState.load_items

    # ==========================================================================
    # FORM DIALOG METHODS
    # ==========================================================================

    def open_create_dialog(self):
        """Open dialog for creating a new item."""
        self.is_editing = False
        self.editing_item_id = None
        self._reset_form()
        self.show_form_dialog = True

    def open_edit_dialog(self, item_id: int):
        """Open dialog for editing an existing item."""
        # Find the item in the list
        for item in self.items:
            if item.get("id") == item_id:
                self.is_editing = True
                self.editing_item_id = item_id
                self.form_title = item.get("title", "")
                self.form_description = item.get("description", "")
                self.form_type = item.get("item_type", "Functioneel")
                self.form_priority = item.get("priority", "Middel")
                self.form_status = item.get("status", "Nieuw")
                self.show_form_dialog = True
                break

    def close_form_dialog(self):
        """Close the form dialog."""
        self.show_form_dialog = False
        self._reset_form()

    def _reset_form(self):
        """Reset all form fields."""
        self.form_title = ""
        self.form_description = ""
        self.form_type = "Functioneel"
        self.form_priority = "Middel"
        self.form_status = "Nieuw"
        self.error = ""
        self.success_message = ""

    # Form field setters
    def set_form_title(self, value: str):
        self.form_title = value

    def set_form_description(self, value: str):
        self.form_description = value

    def set_form_type(self, value: str):
        self.form_type = value

    def set_form_priority(self, value: str):
        self.form_priority = value
        
    def set_form_status(self, value: str):
        self.form_status = value

    # ==========================================================================
    # CRUD METHODS
    # ==========================================================================

    async def save_item(self):
        """Save item (create or update)."""
        self.error = ""
        self.success_message = ""

        # Validation
        if not self.form_title.strip():
            self.error = "Titel is verplicht"
            return

        item_data = {
            "title": self.form_title.strip(),
            "description": self.form_description.strip(),
            "item_type": self.form_type,
            "tenant_id": 1, 
        }
        
        # Only admin (or during create) can set priority/status?
        # For now, let's treat update as full update, but UI will restrict fields
        item_data["priority"] = self.form_priority
        item_data["status"] = self.form_status
        
        # Add submitter info on create
        if not self.is_editing:
            user = AuthState.user(self)
            if user:
                item_data["submitted_by_id"] = user.get("id")
                item_data["submitter_name"] = user.get("full_name")

        try:
            if self.is_editing and self.editing_item_id:
                await api_client.update_backlog_item(self.editing_item_id, item_data)
                self.success_message = "Item bijgewerkt"
            else:
                await api_client.create_backlog_item(item_data)
                self.success_message = "Item aangemaakt"

            self.show_form_dialog = False
            self._reset_form()
            # Reload the list
            return BacklogState.load_items
        except Exception as e:
            self.error = f"Fout bij opslaan: {str(e)}"

    # ==========================================================================
    # DELETE METHODS
    # ==========================================================================

    def open_delete_dialog(self, item_id: int):
        """Open delete confirmation dialog."""
        for item in self.items:
            if item.get("id") == item_id:
                self.deleting_item_id = item_id
                self.deleting_item_title = item.get("title", "")
                self.show_delete_dialog = True
                break

    def close_delete_dialog(self):
        """Close delete confirmation dialog."""
        self.show_delete_dialog = False
        self.deleting_item_id = None
        self.deleting_item_title = ""

    async def confirm_delete(self):
        """Delete the item after confirmation."""
        if not self.deleting_item_id:
            return

        try:
            await api_client.delete_backlog_item(self.deleting_item_id)
            self.success_message = "Item verwijderd"
            self.show_delete_dialog = False
            self.deleting_item_id = None
            self.deleting_item_title = ""
            return BacklogState.load_items
        except Exception as e:
            self.error = f"Fout bij verwijderen: {str(e)}"
            self.show_delete_dialog = False
