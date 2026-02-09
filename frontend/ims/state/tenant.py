"""
Tenant State - handles tenant (organization) management for superusers
"""
import re
import reflex as rx
from typing import List, Dict, Any, Optional
from ims.api.client import api_client
from ims.state.auth import AuthState


class TenantState(rx.State):
    """Tenant management state (superuser only)."""

    tenants: List[Dict[str, Any]] = []
    tenant_users: List[Dict[str, Any]] = []
    all_users: List[Dict[str, Any]] = []

    # Filters
    filter_active: str = "ACTIEF"  # ACTIEF, INACTIEF, ALLE

    # Form dialog
    show_form_dialog: bool = False
    is_editing: bool = False
    editing_tenant_id: Optional[int] = None

    # Form fields
    form_name: str = ""
    form_slug: str = ""
    form_description: str = ""
    form_contact_email: str = ""
    form_is_active: bool = True

    # Members dialog
    show_members_dialog: bool = False
    members_tenant_id: Optional[int] = None
    members_tenant_name: str = ""

    # Delete dialog
    show_delete_dialog: bool = False
    deleting_tenant_id: Optional[int] = None
    deleting_tenant_name: str = ""

    # Messages
    success_message: str = ""
    error: str = ""
    is_loading: bool = False

    # ==========================================================================
    # COMPUTED VARS
    # ==========================================================================

    @rx.var
    def active_count(self) -> int:
        return len([t for t in self.tenants if t.get("is_active", True)])

    @rx.var
    def inactive_count(self) -> int:
        return len([t for t in self.tenants if not t.get("is_active", True)])

    @rx.var
    def total_count(self) -> int:
        return len(self.tenants)

    @rx.var
    def available_users(self) -> List[Dict[str, Any]]:
        """Users not yet member of the selected tenant."""
        member_ids = {u.get("user_id") for u in self.tenant_users}
        return [u for u in self.all_users if u.get("id") not in member_ids]

    # ==========================================================================
    # LOAD
    # ==========================================================================

    async def load_tenants(self):
        """Load tenants from API."""
        self.is_loading = True
        self.error = ""
        self.success_message = ""

        try:
            if self.filter_active == "INACTIEF":
                self.tenants = await api_client.get_tenants(is_active=False)
            elif self.filter_active == "ALLE":
                active = await api_client.get_tenants(is_active=True)
                inactive = await api_client.get_tenants(is_active=False)
                self.tenants = active + inactive
            else:
                self.tenants = await api_client.get_tenants(is_active=True)
        except Exception as e:
            self.error = f"Kan organisaties niet laden: {str(e)}"
            self.tenants = []
        finally:
            self.is_loading = False

    def set_filter_active(self, value: str):
        self.filter_active = value
        return TenantState.load_tenants

    def clear_filters(self):
        self.filter_active = "ACTIEF"
        return TenantState.load_tenants

    # ==========================================================================
    # FORM METHODS
    # ==========================================================================

    def _reset_form(self):
        self.form_name = ""
        self.form_slug = ""
        self.form_description = ""
        self.form_contact_email = ""
        self.form_is_active = True
        self.error = ""

    def open_create_dialog(self):
        self.is_editing = False
        self.editing_tenant_id = None
        self._reset_form()
        self.show_form_dialog = True

    def open_edit_dialog(self, tenant_id: int):
        for t in self.tenants:
            if t.get("id") == tenant_id:
                self.is_editing = True
                self.editing_tenant_id = tenant_id
                self.form_name = t.get("name", "")
                self.form_slug = t.get("slug", "")
                self.form_description = t.get("description", "") or ""
                self.form_contact_email = t.get("contact_email", "") or ""
                self.form_is_active = t.get("is_active", True)
                self.error = ""
                self.show_form_dialog = True
                break

    def close_form_dialog(self):
        self.show_form_dialog = False
        self._reset_form()

    def set_form_name(self, value: str):
        self.form_name = value
        if not self.is_editing:
            self.form_slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

    def set_form_slug(self, value: str):
        self.form_slug = value

    def set_form_description(self, value: str):
        self.form_description = value

    def set_form_contact_email(self, value: str):
        self.form_contact_email = value

    def set_form_is_active(self, value: bool):
        self.form_is_active = value

    async def save_tenant(self):
        """Create or update a tenant."""
        if not self.form_name.strip():
            self.error = "Naam is verplicht"
            return
        if not self.form_slug.strip():
            self.error = "Slug is verplicht"
            return

        try:
            data = {
                "name": self.form_name.strip(),
                "slug": self.form_slug.strip(),
                "description": self.form_description.strip() or None,
                "contact_email": self.form_contact_email.strip() or None,
                "is_active": self.form_is_active,
            }

            if self.is_editing and self.editing_tenant_id:
                await api_client.update_tenant(self.editing_tenant_id, data)
                self.success_message = "Organisatie bijgewerkt"
            else:
                await api_client.create_tenant(data)
                self.success_message = "Organisatie aangemaakt"

            self.show_form_dialog = False
            self._reset_form()
            await self.load_tenants()
        except Exception as e:
            self.error = f"Fout bij opslaan: {str(e)}"

    # ==========================================================================
    # DELETE (DEACTIVATE) METHODS
    # ==========================================================================

    def open_delete_dialog(self, tenant_id: int):
        for t in self.tenants:
            if t.get("id") == tenant_id:
                self.deleting_tenant_id = tenant_id
                self.deleting_tenant_name = t.get("name", "")
                self.show_delete_dialog = True
                break

    def close_delete_dialog(self):
        self.show_delete_dialog = False
        self.deleting_tenant_id = None
        self.deleting_tenant_name = ""

    async def confirm_delete(self):
        if not self.deleting_tenant_id:
            return
        try:
            await api_client.deactivate_tenant(self.deleting_tenant_id)
            self.success_message = "Organisatie gedeactiveerd"
            self.close_delete_dialog()
            await self.load_tenants()
        except Exception as e:
            self.error = f"Fout bij deactiveren: {str(e)}"
            self.close_delete_dialog()

    # ==========================================================================
    # MEMBERS DIALOG
    # ==========================================================================

    async def open_members_dialog(self, tenant_id: int):
        for t in self.tenants:
            if t.get("id") == tenant_id:
                self.members_tenant_id = tenant_id
                self.members_tenant_name = t.get("name", "")
                self.error = ""
                self.success_message = ""

                try:
                    self.tenant_users = await api_client.get_tenant_users(tenant_id)
                except Exception as e:
                    self.tenant_users = []
                    self.error = f"Kan leden niet laden: {str(e)}"

                try:
                    self.all_users = await api_client.get_users(is_active=True)
                except Exception:
                    self.all_users = []

                self.show_members_dialog = True
                break

    def close_members_dialog(self):
        self.show_members_dialog = False
        self.members_tenant_id = None
        self.members_tenant_name = ""
        self.tenant_users = []
        self.all_users = []

    async def add_member(self, user_id: str):
        """Add a user to the tenant."""
        if not self.members_tenant_id or not user_id:
            return
        try:
            await api_client.add_user_to_tenant_by_tid(self.members_tenant_id, int(user_id))
            self.success_message = "Lid toegevoegd"
            self.tenant_users = await api_client.get_tenant_users(self.members_tenant_id)
        except Exception as e:
            self.error = f"Fout bij toevoegen lid: {str(e)}"

    async def remove_member(self, user_id: int):
        """Remove a user from the tenant."""
        if not self.members_tenant_id:
            return
        try:
            await api_client.remove_user_from_tenant_by_tid(self.members_tenant_id, user_id)
            self.success_message = "Lid verwijderd"
            self.tenant_users = await api_client.get_tenant_users(self.members_tenant_id)
        except Exception as e:
            self.error = f"Fout bij verwijderen lid: {str(e)}"

    async def change_member_role(self, user_id: int, role: str):
        """Change a member's TenantRole."""
        if not self.members_tenant_id:
            return
        try:
            await api_client.update_tenant_user_role(self.members_tenant_id, user_id, role)
            self.success_message = f"Rol gewijzigd naar {role}"
            self.tenant_users = await api_client.get_tenant_users(self.members_tenant_id)
        except Exception as e:
            self.error = f"Fout bij wijzigen rol: {str(e)}"
