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

    # Form fields (legacy)
    form_title: str = ""
    form_description: str = ""
    form_type: str = "Functioneel"
    form_priority: str = "Middel"
    form_status: str = "Nieuw"
    
    # User Story form fields (new)
    form_user_role: str = "Process Owner"
    form_user_want: str = ""
    form_user_so_that: str = ""
    
    # Delete confirmation
    show_delete_dialog: bool = False
    deleting_item_id: Optional[int] = None
    deleting_item_title: str = ""
    
    # Kanban column definitions
    KANBAN_STATUSES: List[str] = ["Nieuw", "In Review", "Goedgekeurd", "In Uitvoering", "Gereed"]

    @rx.var
    def items_by_status(self) -> Dict[str, List[Dict[str, Any]]]:
        """Group items by status for Kanban view."""
        grouped = {status: [] for status in self.KANBAN_STATUSES}
        for item in self.items:
            status = item.get("status", "Nieuw")
            if status in grouped:
                grouped[status].append(item)
        return grouped
    
    @rx.var
    def items_nieuw(self) -> List[Dict[str, Any]]:
        return [i for i in self.items if i.get("status") == "Nieuw"]
    
    @rx.var
    def items_review(self) -> List[Dict[str, Any]]:
        return [i for i in self.items if i.get("status") == "In Review"]
    
    @rx.var
    def items_approved(self) -> List[Dict[str, Any]]:
        return [i for i in self.items if i.get("status") == "Goedgekeurd"]
    
    @rx.var
    def items_in_progress(self) -> List[Dict[str, Any]]:
        return [i for i in self.items if i.get("status") == "In Uitvoering"]
    
    @rx.var
    def items_done(self) -> List[Dict[str, Any]]:
        return [i for i in self.items if i.get("status") == "Gereed"]

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
        # User Story fields
        self.form_user_role = "Process Owner"
        self.form_user_want = ""
        self.form_user_so_that = ""
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
    
    # User Story field setters
    def set_form_user_role(self, value: str):
        self.form_user_role = value
    
    def set_form_user_want(self, value: str):
        self.form_user_want = value
    
    def set_form_user_so_that(self, value: str):
        self.form_user_so_that = value

    # ==========================================================================
    # CRUD METHODS
    # ==========================================================================

    async def save_item(self):
        """Save item (create or update)."""
        self.error = ""
        self.success_message = ""

        # Validation - need at least the "want" part of the user story
        if not self.form_user_want.strip():
            self.error = "Beschrijf wat je wilt ('...wil ik...')"
            return

        # Auto-generate title from User Story
        title = f"Als {self.form_user_role}, wil ik {self.form_user_want[:50]}"
        if len(self.form_user_want) > 50:
            title += "..."
        
        # Build description from user story parts
        description = f"Als {self.form_user_role}, wil ik {self.form_user_want}"
        if self.form_user_so_that.strip():
            description += f", zodat ik {self.form_user_so_that}"

        item_data = {
            "title": title,
            "description": description,
            "item_type": self.form_type,
            "tenant_id": 1,
            # User Story fields
            "user_role": self.form_user_role,
            "user_want": self.form_user_want.strip(),
            "user_so_that": self.form_user_so_that.strip(),
        }
        
        # Only admin can set priority/status
        auth_state = await self.get_state(AuthState)
        is_admin = auth_state.is_admin
        
        if is_admin:
            item_data["priority"] = self.form_priority
            item_data["status"] = self.form_status
        else:
            # Non-admins always submit as "Nieuw" with default priority
            item_data["priority"] = "Middel"
            item_data["status"] = "Nieuw"
        
        # Add submitter info on create
        if not self.is_editing:
            user = auth_state.user
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
