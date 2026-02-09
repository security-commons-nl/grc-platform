"""
Auth State - handles user authentication with persistence
"""
import reflex as rx
from typing import Dict, Any, List
import json

from ims.api.client import api_client


class AuthState(rx.State):
    """Authentication state with localStorage persistence."""

    # User info (persisted in localStorage)
    user_json: str = rx.LocalStorage(name="ims_user")

    # Active tenant (persisted — no _ prefix!)
    active_tenant_id: int = rx.LocalStorage(name="ims_tenant_id")

    # Login form
    username: str = ""
    password: str = ""
    login_error: str = ""
    is_logging_in: bool = False

    @rx.var
    def user(self) -> Dict[str, Any]:
        """Get user from localStorage."""
        if self.user_json:
            try:
                return json.loads(self.user_json)
            except:
                pass

        return {}

    @rx.var
    def is_authenticated(self) -> bool:
        """Check if user is logged in."""
        return self.user_json != ""

    @rx.var
    def user_display_name(self) -> str:
        """Get user's display name."""
        user = self.user
        if user and user.get("username"):
            return user.get("full_name") or user.get("username", "Gebruiker")
        return "Gast"

    @rx.var
    def user_email(self) -> str:
        """Get user's email."""
        user = self.user
        return user.get("email", "") if user else ""

    @rx.var
    def tenant_name(self) -> str:
        """Get active tenant name."""
        user = self.user
        if not user:
            return ""
        tenants = user.get("tenants", [])
        tid = self.tenant_id
        for t in tenants:
            if t.get("id") == tid:
                return t.get("name", "")
        # Fallback to stored tenant_name
        return user.get("tenant_name", "")

    @rx.var
    def global_roles(self) -> list:
        """Get user's global roles from login response."""
        user = self.user
        return user.get("global_roles", []) if user else []

    @rx.var
    def permissions(self) -> Dict[str, Any]:
        """Get user's permissions from login response."""
        user = self.user
        return user.get("permissions", {}) if user else {}

    @rx.var
    def is_admin(self) -> bool:
        """Check if user is admin (superuser or Beheerder role)."""
        user = self.user
        if not user:
            return False
        if user.get("is_superuser", False):
            return True
        return "Beheerder" in user.get("global_roles", [])

    @rx.var
    def can_edit(self) -> bool:
        """Can create/edit/delete operational items (risks, controls, etc.)."""
        user = self.user
        if not user:
            return False
        if user.get("permissions", {}).get("can_edit", False):
            return True
        return self.is_admin

    @rx.var
    def can_configure(self) -> bool:
        """Can manage policies, scopes, assets, suppliers."""
        user = self.user
        if not user:
            return False
        if user.get("permissions", {}).get("can_configure", False):
            return True
        return self.is_admin

    @rx.var
    def can_manage_users(self) -> bool:
        """Can manage users and system configuration."""
        user = self.user
        if not user:
            return False
        if user.get("permissions", {}).get("can_manage_users", False):
            return True
        return self.is_admin

    @rx.var
    def can_write_findings(self) -> bool:
        """Can create audit findings (Toezichthouder, Coordinator, Beheerder)."""
        user = self.user
        if not user:
            return False
        if user.get("permissions", {}).get("can_write_findings", False):
            return True
        return self.is_admin

    @rx.var
    def can_discover(self) -> bool:
        """Can access ONTDEKKEN section and MS Hub (Eigenaar+, Toezichthouder)."""
        user = self.user
        if not user:
            return False
        perms = user.get("permissions", {})
        if perms.get("can_configure", False) or perms.get("can_write_findings", False):
            return True
        return self.is_admin

    @rx.var
    def user_id(self) -> int:
        """Get current user's ID."""
        user = self.user
        return user.get("id", 0) if user else 0

    @rx.var
    def tenant_id(self) -> int:
        """Get the active tenant_id (from localStorage or default from login)."""
        # If active_tenant_id was explicitly set (and non-zero), use it
        if self.active_tenant_id and self.active_tenant_id > 0:
            return self.active_tenant_id
        # Fall back to default_tenant_id from login response
        user = self.user
        if user:
            return user.get("default_tenant_id", 0) or 0
        return 0

    @rx.var
    def tenants(self) -> List[Dict[str, Any]]:
        """Get list of tenant memberships from login response."""
        user = self.user
        if not user:
            return []
        return user.get("tenants", [])

    @rx.var
    def has_multiple_tenants(self) -> bool:
        """Check if user belongs to more than one tenant."""
        return len(self.tenants) > 1

    async def login(self):
        """Authenticate against the backend API."""
        self.is_logging_in = True
        self.login_error = ""

        if not self.username.strip():
            self.login_error = "Gebruikersnaam is verplicht"
            self.is_logging_in = False
            return

        if not self.password.strip():
            self.login_error = "Wachtwoord is verplicht"
            self.is_logging_in = False
            return

        try:
            user_data = await api_client.login(self.username, self.password)
        except Exception:
            self.login_error = "Ongeldige gebruikersnaam of wachtwoord"
            self.is_logging_in = False
            return

        # Store authenticated user in localStorage
        self.user_json = json.dumps(user_data)

        # Set active tenant to default
        default_tid = user_data.get("default_tenant_id", 0)
        self.active_tenant_id = default_tid or 0

        self.is_logging_in = False
        self.username = ""
        self.password = ""

        # Redirect to dashboard
        return rx.redirect("/")

    def logout(self):
        """Log out the current user."""
        self.user_json = ""
        self.active_tenant_id = 0
        return rx.redirect("/login")

    def switch_tenant(self, tenant_id: str):
        """Switch to a different tenant. Triggers page reload for data refresh."""
        self.active_tenant_id = int(tenant_id)
        return rx.redirect(rx.State.router.page.raw_path)

    def set_username(self, value: str):
        """Set username from input."""
        self.username = value

    def set_password(self, value: str):
        """Set password from input."""
        self.password = value

    def redirect_to_login(self):
        """Redirect to login page — only if still unauthenticated after hydration."""
        if not self.user_json:
            return rx.redirect("/login")
