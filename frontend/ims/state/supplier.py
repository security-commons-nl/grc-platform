"""
Supplier State - handles supplier/vendor management (Scopes of type SUPPLIER)
"""
import reflex as rx
from typing import List, Dict, Any, Optional
from ims.api.client import api_client


class SupplierState(rx.State):
    """Supplier management state - wraps Scope with type=SUPPLIER."""

    suppliers: List[Dict[str, Any]] = []
    parent_scopes: List[Dict[str, Any]] = []

    # Loading
    is_loading: bool = False
    error: str = ""
    success_message: str = ""

    # Dialog state
    show_form_dialog: bool = False
    is_editing: bool = False
    editing_supplier_id: Optional[int] = None

    # Form fields - Basic
    form_name: str = ""
    form_description: str = ""
    form_owner: str = ""
    form_parent_id: str = "0"

    # Form fields - Supplier specific
    form_vendor_contact_name: str = ""
    form_vendor_contact_email: str = ""
    form_contract_start_date: str = ""
    form_contract_end_date: str = ""

    # Delete confirmation
    show_delete_dialog: bool = False
    deleting_supplier_id: Optional[int] = None
    deleting_supplier_name: str = ""

    # ==========================================================================
    # COMPUTED PROPERTIES
    # ==========================================================================

    @rx.var
    def total_suppliers(self) -> int:
        return len(self.suppliers)

    @rx.var
    def active_contracts(self) -> int:
        """Count suppliers with active contracts (end date in future or not set)."""
        # Simplified - in real app would check dates
        return len([s for s in self.suppliers if s.get("contract_end_date")])

    @rx.var
    def expiring_soon(self) -> int:
        """Count suppliers with contracts expiring within 90 days."""
        # Simplified placeholder
        return 0

    @rx.var
    def available_parents(self) -> List[Dict[str, Any]]:
        """Get scopes that can be parents for suppliers."""
        return [
            {
                "id": str(s.get("id")) if s.get("id") else "0",
                "name": s.get("name") or "Onbekend", 
                "type": s.get("type")
            }
            for s in self.parent_scopes
            if s.get("type") in ["Organization", "Cluster", "Department", "Process"] and str(s.get("id"))
        ]

    # ==========================================================================
    # LOAD METHODS
    # ==========================================================================

    async def load_suppliers(self):
        """Load suppliers from API."""
        self.is_loading = True
        self.error = ""
        self.success_message = ""

        try:
            self.suppliers = await api_client.get_scopes(scope_type="Supplier")
            self.parent_scopes = await api_client.get_scopes()
        except Exception as e:
            self.error = f"Fout bij laden: {str(e)}"
            self.suppliers = []
        finally:
            self.is_loading = False

    # ==========================================================================
    # FORM METHODS
    # ==========================================================================

    def _reset_form(self):
        """Reset form fields."""
        self.form_name = ""
        self.form_description = ""
        self.form_owner = ""
        self.form_parent_id = "0"
        self.form_vendor_contact_name = ""
        self.form_vendor_contact_email = ""
        self.form_contract_start_date = ""
        self.form_contract_end_date = ""
        self.error = ""

    def open_create_dialog(self):
        """Open dialog for creating a new supplier."""
        self.is_editing = False
        self.editing_supplier_id = None
        self._reset_form()
        self.show_form_dialog = True

    def open_edit_dialog(self, supplier_id: int):
        """Open dialog for editing an existing supplier."""
        for supplier in self.suppliers:
            if supplier.get("id") == supplier_id:
                self.is_editing = True
                self.editing_supplier_id = supplier_id
                self.form_name = supplier.get("name", "")
                self.form_description = supplier.get("description", "") or ""
                self.form_owner = supplier.get("owner", "")
                self.form_parent_id = str(supplier.get("parent_id", "")) if supplier.get("parent_id") else "0"
                self.form_vendor_contact_name = supplier.get("vendor_contact_name", "") or ""
                self.form_vendor_contact_email = supplier.get("vendor_contact_email", "") or ""
                # Date handling would need proper formatting
                self.form_contract_start_date = ""
                self.form_contract_end_date = ""
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

    def set_form_vendor_contact_name(self, value: str):
        self.form_vendor_contact_name = value

    def set_form_vendor_contact_email(self, value: str):
        self.form_vendor_contact_email = value

    def set_form_contract_start_date(self, value: str):
        self.form_contract_start_date = value

    def set_form_contract_end_date(self, value: str):
        self.form_contract_end_date = value

    # ==========================================================================
    # CRUD METHODS
    # ==========================================================================

    async def save_supplier(self):
        """Save supplier (create or update)."""
        if not self.form_name.strip():
            self.error = "Naam is verplicht"
            return
        if not self.form_owner.strip():
            self.error = "Interne eigenaar is verplicht"
            return

        try:
            data = {
                "name": self.form_name.strip(),
                "type": "Supplier",
                "description": self.form_description.strip() or None,
                "owner": self.form_owner.strip(),
                "parent_id": int(self.form_parent_id) if self.form_parent_id and self.form_parent_id != "0" else None,
                "vendor_contact_name": self.form_vendor_contact_name.strip() or None,
                "vendor_contact_email": self.form_vendor_contact_email.strip() or None,
                "tenant_id": 1,
            }

            if self.is_editing and self.editing_supplier_id:
                await api_client.update_scope(self.editing_supplier_id, data)
                self.success_message = "Leverancier bijgewerkt"
            else:
                await api_client.create_scope(data)
                self.success_message = "Leverancier aangemaakt"

            self.show_form_dialog = False
            self._reset_form()
            await self.load_suppliers()

        except Exception as e:
            self.error = f"Fout bij opslaan: {str(e)}"

    # ==========================================================================
    # DELETE METHODS
    # ==========================================================================

    def open_delete_dialog(self, supplier_id: int):
        """Open delete confirmation dialog."""
        for supplier in self.suppliers:
            if supplier.get("id") == supplier_id:
                self.deleting_supplier_id = supplier_id
                self.deleting_supplier_name = supplier.get("name", "")
                self.show_delete_dialog = True
                break

    def close_delete_dialog(self):
        self.show_delete_dialog = False
        self.deleting_supplier_id = None
        self.deleting_supplier_name = ""

    async def confirm_delete(self):
        """Confirm and execute delete."""
        if not self.deleting_supplier_id:
            return

        try:
            await api_client.delete_scope(self.deleting_supplier_id)
            self.success_message = "Leverancier verwijderd"
            self.close_delete_dialog()
            await self.load_suppliers()
        except Exception as e:
            self.error = f"Fout bij verwijderen: {str(e)}"
            self.close_delete_dialog()
