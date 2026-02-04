"""
Asset State - handles asset register data (Scopes of type ASSET)
"""
import reflex as rx
from typing import List, Dict, Any, Optional
from ims.api.client import api_client


class AssetState(rx.State):
    """Asset management state - wraps Scope with type=ASSET."""

    assets: List[Dict[str, Any]] = []
    parent_scopes: List[Dict[str, Any]] = []  # For parent selection

    # Loading
    is_loading: bool = False
    error: str = ""
    success_message: str = ""

    # Filters
    filter_asset_type: str = "ALLE"
    filter_classification: str = "ALLE"

    # Dialog state
    show_form_dialog: bool = False
    is_editing: bool = False
    editing_asset_id: Optional[int] = None

    # Form fields
    form_name: str = ""
    form_description: str = ""
    form_owner: str = ""
    form_parent_id: str = ""
    form_asset_type: str = "Software"
    form_location: str = ""
    form_data_classification: str = "Internal"

    # BIA fields
    form_availability_rating: str = "Internal"
    form_integrity_rating: str = "Internal"
    form_confidentiality_rating: str = "Internal"
    form_rto_hours: str = ""
    form_rpo_hours: str = ""

    # Delete confirmation
    show_delete_dialog: bool = False
    deleting_asset_id: Optional[int] = None
    deleting_asset_name: str = ""

    # ==========================================================================
    # COMPUTED PROPERTIES
    # ==========================================================================

    @rx.var
    def total_assets(self) -> int:
        return len(self.assets)

    @rx.var
    def hardware_count(self) -> int:
        return len([a for a in self.assets if a.get("asset_type") == "Hardware"])

    @rx.var
    def software_count(self) -> int:
        return len([a for a in self.assets if a.get("asset_type") == "Software"])

    @rx.var
    def data_count(self) -> int:
        return len([a for a in self.assets if a.get("asset_type") == "Data"])

    @rx.var
    def filtered_assets(self) -> List[Dict[str, Any]]:
        """Get filtered assets."""
        result = self.assets

        if self.filter_asset_type != "ALLE":
            result = [a for a in result if a.get("asset_type") == self.filter_asset_type]

        if self.filter_classification != "ALLE":
            result = [a for a in result if a.get("data_classification") == self.filter_classification]

        return result

    @rx.var
    def available_parents(self) -> List[Dict[str, Any]]:
        """Get scopes that can be parents for assets."""
        return [
            {"id": str(s.get("id")), "name": s.get("name"), "type": s.get("type")}
            for s in self.parent_scopes
            if s.get("type") in ["Organization", "Cluster", "Department", "Process"]
        ]

    # ==========================================================================
    # LOAD METHODS
    # ==========================================================================

    async def load_assets(self):
        """Load assets from API."""
        self.is_loading = True
        self.error = ""
        self.success_message = ""

        try:
            # Load assets (scopes with type=ASSET)
            self.assets = await api_client.get_scopes(scope_type="Asset")
            # Load parent scopes for selection
            self.parent_scopes = await api_client.get_scopes()
        except Exception as e:
            self.error = f"Fout bij laden: {str(e)}"
            self.assets = []
        finally:
            self.is_loading = False

    # ==========================================================================
    # FILTER METHODS
    # ==========================================================================

    def set_filter_asset_type(self, value: str):
        self.filter_asset_type = value

    def set_filter_classification(self, value: str):
        self.filter_classification = value

    def clear_filters(self):
        self.filter_asset_type = "ALLE"
        self.filter_classification = "ALLE"

    # ==========================================================================
    # FORM METHODS
    # ==========================================================================

    def _reset_form(self):
        """Reset form fields."""
        self.form_name = ""
        self.form_description = ""
        self.form_owner = ""
        self.form_parent_id = ""
        self.form_asset_type = "Software"
        self.form_location = ""
        self.form_data_classification = "Internal"
        self.form_availability_rating = "Internal"
        self.form_integrity_rating = "Internal"
        self.form_confidentiality_rating = "Internal"
        self.form_rto_hours = ""
        self.form_rpo_hours = ""
        self.error = ""

    def open_create_dialog(self):
        """Open dialog for creating a new asset."""
        self.is_editing = False
        self.editing_asset_id = None
        self._reset_form()
        self.show_form_dialog = True

    def open_edit_dialog(self, asset_id: int):
        """Open dialog for editing an existing asset."""
        for asset in self.assets:
            if asset.get("id") == asset_id:
                self.is_editing = True
                self.editing_asset_id = asset_id
                self.form_name = asset.get("name", "")
                self.form_description = asset.get("description", "") or ""
                self.form_owner = asset.get("owner", "")
                self.form_parent_id = str(asset.get("parent_id", "")) if asset.get("parent_id") else ""
                self.form_asset_type = asset.get("asset_type", "Software") or "Software"
                self.form_location = asset.get("location", "") or ""
                self.form_data_classification = asset.get("data_classification", "Internal") or "Internal"
                self.form_availability_rating = asset.get("availability_rating", "Internal") or "Internal"
                self.form_integrity_rating = asset.get("integrity_rating", "Internal") or "Internal"
                self.form_confidentiality_rating = asset.get("confidentiality_rating", "Internal") or "Internal"
                self.form_rto_hours = str(asset.get("rto_hours", "")) if asset.get("rto_hours") else ""
                self.form_rpo_hours = str(asset.get("rpo_hours", "")) if asset.get("rpo_hours") else ""
                self.show_form_dialog = True
                break

    def close_form_dialog(self):
        self.show_form_dialog = False
        self._reset_form()

    # Form field setters
    def set_form_name(self, value: str):
        self.form_name = value

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

    # ==========================================================================
    # CRUD METHODS
    # ==========================================================================

    async def save_asset(self):
        """Save asset (create or update)."""
        if not self.form_name.strip():
            self.error = "Naam is verplicht"
            return
        if not self.form_owner.strip():
            self.error = "Eigenaar is verplicht"
            return

        try:
            data = {
                "name": self.form_name.strip(),
                "type": "Asset",  # Always Asset
                "description": self.form_description.strip() or None,
                "owner": self.form_owner.strip(),
                "parent_id": int(self.form_parent_id) if self.form_parent_id else None,
                "asset_type": self.form_asset_type or None,
                "location": self.form_location.strip() or None,
                "data_classification": self.form_data_classification or None,
                "availability_rating": self.form_availability_rating or None,
                "integrity_rating": self.form_integrity_rating or None,
                "confidentiality_rating": self.form_confidentiality_rating or None,
                "rto_hours": int(self.form_rto_hours) if self.form_rto_hours else None,
                "rpo_hours": int(self.form_rpo_hours) if self.form_rpo_hours else None,
                "tenant_id": 1,  # Default tenant
            }

            if self.is_editing and self.editing_asset_id:
                await api_client.update_scope(self.editing_asset_id, data)
                self.success_message = "Asset bijgewerkt"
            else:
                await api_client.create_scope(data)
                self.success_message = "Asset aangemaakt"

            self.show_form_dialog = False
            self._reset_form()
            await self.load_assets()

        except Exception as e:
            self.error = f"Fout bij opslaan: {str(e)}"

    # ==========================================================================
    # DELETE METHODS
    # ==========================================================================

    def open_delete_dialog(self, asset_id: int):
        """Open delete confirmation dialog."""
        for asset in self.assets:
            if asset.get("id") == asset_id:
                self.deleting_asset_id = asset_id
                self.deleting_asset_name = asset.get("name", "")
                self.show_delete_dialog = True
                break

    def close_delete_dialog(self):
        self.show_delete_dialog = False
        self.deleting_asset_id = None
        self.deleting_asset_name = ""

    async def confirm_delete(self):
        """Confirm and execute delete."""
        if not self.deleting_asset_id:
            return

        try:
            await api_client.delete_scope(self.deleting_asset_id)
            self.success_message = "Asset verwijderd"
            self.close_delete_dialog()
            await self.load_assets()
        except Exception as e:
            self.error = f"Fout bij verwijderen: {str(e)}"
            self.close_delete_dialog()
