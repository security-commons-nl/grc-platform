"""
Scope State - handles scope/organization hierarchy data
"""
import reflex as rx
from typing import List, Dict, Any, Optional
from ims.api.client import api_client


class ScopeState(rx.State):
    """Scope management state."""

    scopes: List[Dict[str, Any]] = []
    selected_scope: Dict[str, Any] = {}
    scope_tree: Dict[str, Any] = {}

    # Filters
    filter_type: str = "ALLE"

    # Loading
    is_loading: bool = False
    error: str = ""
    success_message: str = ""

    # Dialog state
    show_form_dialog: bool = False
    is_editing: bool = False
    editing_scope_id: Optional[int] = None

    # Form fields - Basic (always shown)
    form_name: str = ""
    form_type: str = "Process"
    form_description: str = ""
    form_owner: str = ""
    form_parent_id: str = ""  # String for select, convert to int

    # Form fields - Asset specific
    form_asset_type: str = ""
    form_location: str = ""
    form_data_classification: str = "Internal"

    # Form fields - Supplier specific
    form_vendor_contact_name: str = ""
    form_vendor_contact_email: str = ""

    # Form fields - BIA/BCM (for Process/Asset)
    form_availability_rating: str = "Internal"
    form_integrity_rating: str = "Internal"
    form_confidentiality_rating: str = "Internal"
    form_rto_hours: str = ""
    form_rpo_hours: str = ""
    form_mtpd_hours: str = ""

    # Delete confirmation
    show_delete_dialog: bool = False
    deleting_scope_id: Optional[int] = None
    deleting_scope_name: str = ""

    # ==========================================================================
    # COMPUTED PROPERTIES
    # ==========================================================================

    @rx.var
    def organization_count(self) -> int:
        return len([s for s in self.scopes if s.get("type") == "Organization"])

    @rx.var
    def process_count(self) -> int:
        return len([s for s in self.scopes if s.get("type") == "Process"])

    @rx.var
    def asset_count(self) -> int:
        return len([s for s in self.scopes if s.get("type") == "Asset"])

    @rx.var
    def supplier_count(self) -> int:
        return len([s for s in self.scopes if s.get("type") == "Supplier"])

    @rx.var
    def available_parents(self) -> List[Dict[str, Any]]:
        """Get scopes that can be parents (exclude current if editing)."""
        return [
            {"id": str(s.get("id")), "name": s.get("name"), "type": s.get("type")}
            for s in self.scopes
            if s.get("id") != self.editing_scope_id
        ]

    @rx.var
    def show_asset_fields(self) -> bool:
        return self.form_type == "Asset"

    @rx.var
    def show_supplier_fields(self) -> bool:
        return self.form_type == "Supplier"

    @rx.var
    def show_bia_fields(self) -> bool:
        return self.form_type in ["Process", "Asset", "Department"]

    # ==========================================================================
    # LOAD METHODS
    # ==========================================================================

    async def load_scopes(self):
        """Load scopes from API."""
        self.is_loading = True
        self.error = ""
        self.success_message = ""

        try:
            params = {}
            if self.filter_type and self.filter_type != "ALLE":
                params["scope_type"] = self.filter_type

            self.scopes = await api_client.get_scopes(**params)
        except Exception:
            self.scopes = []
        finally:
            self.is_loading = False

    # ==========================================================================
    # FILTER METHODS
    # ==========================================================================

    def set_filter_type(self, type_value: str):
        """Set type filter."""
        self.filter_type = type_value
        return ScopeState.load_scopes

    def clear_filters(self):
        """Clear all filters."""
        self.filter_type = "ALLE"
        return ScopeState.load_scopes

    # ==========================================================================
    # FORM DIALOG METHODS
    # ==========================================================================

    def open_create_dialog(self):
        """Open dialog for creating a new scope."""
        self.is_editing = False
        self.editing_scope_id = None
        self._reset_form()
        self.show_form_dialog = True

    def open_edit_dialog(self, scope_id: int):
        """Open dialog for editing an existing scope."""
        for scope in self.scopes:
            if scope.get("id") == scope_id:
                self.is_editing = True
                self.editing_scope_id = scope_id

                # Basic fields
                self.form_name = scope.get("name", "")
                self.form_type = scope.get("type", "Process")
                self.form_description = scope.get("description", "") or ""
                self.form_owner = scope.get("owner", "") or ""
                self.form_parent_id = str(scope.get("parent_id", "")) if scope.get("parent_id") else ""

                # Asset fields
                self.form_asset_type = scope.get("asset_type", "") or ""
                self.form_location = scope.get("location", "") or ""
                self.form_data_classification = scope.get("data_classification", "Internal") or "Internal"

                # Supplier fields
                self.form_vendor_contact_name = scope.get("vendor_contact_name", "") or ""
                self.form_vendor_contact_email = scope.get("vendor_contact_email", "") or ""

                # BIA fields
                self.form_availability_rating = scope.get("availability_rating", "Internal") or "Internal"
                self.form_integrity_rating = scope.get("integrity_rating", "Internal") or "Internal"
                self.form_confidentiality_rating = scope.get("confidentiality_rating", "Internal") or "Internal"
                self.form_rto_hours = str(scope.get("rto_hours", "")) if scope.get("rto_hours") else ""
                self.form_rpo_hours = str(scope.get("rpo_hours", "")) if scope.get("rpo_hours") else ""
                self.form_mtpd_hours = str(scope.get("mtpd_hours", "")) if scope.get("mtpd_hours") else ""

                self.show_form_dialog = True
                break

    def close_form_dialog(self):
        """Close the form dialog."""
        self.show_form_dialog = False
        self._reset_form()

    def _reset_form(self):
        """Reset all form fields."""
        self.form_name = ""
        self.form_type = "Process"
        self.form_description = ""
        self.form_owner = ""
        self.form_parent_id = ""

        self.form_asset_type = ""
        self.form_location = ""
        self.form_data_classification = "Internal"

        self.form_vendor_contact_name = ""
        self.form_vendor_contact_email = ""

        self.form_availability_rating = "Internal"
        self.form_integrity_rating = "Internal"
        self.form_confidentiality_rating = "Internal"
        self.form_rto_hours = ""
        self.form_rpo_hours = ""
        self.form_mtpd_hours = ""

        self.error = ""
        self.success_message = ""

    # Form field setters
    def set_form_name(self, value: str):
        self.form_name = value

    def set_form_type(self, value: str):
        self.form_type = value

    def set_form_description(self, value: str):
        self.form_description = value

    def set_form_owner(self, value: str):
        self.form_owner = value

    def set_form_parent_id(self, value: str):
        self.form_parent_id = value

    def set_form_asset_type(self, value: str):
        self.form_asset_type = value

    def set_form_location(self, value: str):
        self.form_location = value

    def set_form_data_classification(self, value: str):
        self.form_data_classification = value

    def set_form_vendor_contact_name(self, value: str):
        self.form_vendor_contact_name = value

    def set_form_vendor_contact_email(self, value: str):
        self.form_vendor_contact_email = value

    def set_form_availability_rating(self, value: str):
        self.form_availability_rating = value

    def set_form_integrity_rating(self, value: str):
        self.form_integrity_rating = value

    def set_form_confidentiality_rating(self, value: str):
        self.form_confidentiality_rating = value

    def set_form_rto_hours(self, value: str):
        self.form_rto_hours = value

    def set_form_rpo_hours(self, value: str):
        self.form_rpo_hours = value

    def set_form_mtpd_hours(self, value: str):
        self.form_mtpd_hours = value

    # ==========================================================================
    # CRUD METHODS
    # ==========================================================================

    async def save_scope(self):
        """Save scope (create or update)."""
        self.error = ""
        self.success_message = ""

        # Validation
        if not self.form_name.strip():
            self.error = "Naam is verplicht"
            return

        if not self.form_owner.strip():
            self.error = "Eigenaar is verplicht"
            return

        scope_data = {
            "name": self.form_name.strip(),
            "type": self.form_type,
            "description": self.form_description.strip() or None,
            "owner": self.form_owner.strip(),
            "tenant_id": 1,  # Default tenant for now
        }

        # Parent ID
        if self.form_parent_id and self.form_parent_id != "NONE":
            try:
                scope_data["parent_id"] = int(self.form_parent_id)
            except ValueError:
                pass

        # Asset-specific fields
        if self.form_type == "Asset":
            if self.form_asset_type and self.form_asset_type != "NONE":
                scope_data["asset_type"] = self.form_asset_type
            if self.form_location:
                scope_data["location"] = self.form_location.strip()
            if self.form_data_classification:
                scope_data["data_classification"] = self.form_data_classification

        # Supplier-specific fields
        if self.form_type == "Supplier":
            if self.form_vendor_contact_name:
                scope_data["vendor_contact_name"] = self.form_vendor_contact_name.strip()
            if self.form_vendor_contact_email:
                scope_data["vendor_contact_email"] = self.form_vendor_contact_email.strip()

        # BIA fields (for Process, Asset, Department)
        if self.form_type in ["Process", "Asset", "Department"]:
            scope_data["availability_rating"] = self.form_availability_rating
            scope_data["integrity_rating"] = self.form_integrity_rating
            scope_data["confidentiality_rating"] = self.form_confidentiality_rating

            if self.form_rto_hours:
                try:
                    scope_data["rto_hours"] = int(self.form_rto_hours)
                except ValueError:
                    pass
            if self.form_rpo_hours:
                try:
                    scope_data["rpo_hours"] = int(self.form_rpo_hours)
                except ValueError:
                    pass
            if self.form_mtpd_hours:
                try:
                    scope_data["mtpd_hours"] = int(self.form_mtpd_hours)
                except ValueError:
                    pass

        try:
            if self.is_editing and self.editing_scope_id:
                await api_client.update_scope(self.editing_scope_id, scope_data)
                self.success_message = "Scope bijgewerkt"
            else:
                await api_client.create_scope(scope_data)
                self.success_message = "Scope aangemaakt"

            self.show_form_dialog = False
            self._reset_form()
            return ScopeState.load_scopes
        except Exception as e:
            self.error = f"Fout bij opslaan: {str(e)}"

    # ==========================================================================
    # DELETE METHODS
    # ==========================================================================

    def open_delete_dialog(self, scope_id: int):
        """Open delete confirmation dialog."""
        for scope in self.scopes:
            if scope.get("id") == scope_id:
                self.deleting_scope_id = scope_id
                self.deleting_scope_name = scope.get("name", "")
                self.show_delete_dialog = True
                break

    def close_delete_dialog(self):
        """Close delete confirmation dialog."""
        self.show_delete_dialog = False
        self.deleting_scope_id = None
        self.deleting_scope_name = ""

    async def confirm_delete(self):
        """Delete the scope after confirmation."""
        if not self.deleting_scope_id:
            return

        try:
            await api_client.delete_scope(self.deleting_scope_id)
            self.success_message = "Scope verwijderd"
            self.show_delete_dialog = False
            self.deleting_scope_id = None
            self.deleting_scope_name = ""
            return ScopeState.load_scopes
        except Exception as e:
            self.error = f"Fout bij verwijderen: {str(e)}"
            self.show_delete_dialog = False
