"""
Auth State - handles user authentication
"""
import reflex as rx
from typing import Optional, Dict, Any


class AuthState(rx.State):
    """Authentication state."""

    # User info
    user: Dict[str, Any] = {}
    is_authenticated: bool = False

    # Login form
    username: str = ""
    password: str = ""
    login_error: str = ""
    is_logging_in: bool = False

    @rx.var
    def user_display_name(self) -> str:
        """Get user's display name."""
        if self.user:
            return self.user.get("full_name") or self.user.get("username", "User")
        return "Guest"

    @rx.var
    def user_email(self) -> str:
        """Get user's email."""
        return self.user.get("email", "") if self.user else ""

    async def login(self):
        """
        Attempt to log in.
        For now, this is a simple simulation - accepts any username.
        TODO: Implement proper JWT auth when backend supports it.
        """
        self.is_logging_in = True
        self.login_error = ""

        if not self.username.strip():
            self.login_error = "Gebruikersnaam is verplicht"
            self.is_logging_in = False
            return

        # Simulate successful login
        # In production, this would call the auth API
        self.user = {
            "id": 1,
            "username": self.username,
            "full_name": self.username.title(),
            "email": f"{self.username}@example.com",
            "is_active": True,
        }
        self.is_authenticated = True
        self.is_logging_in = False
        self.username = ""
        self.password = ""

        # Redirect to dashboard
        return rx.redirect("/")

    def logout(self):
        """Log out the current user."""
        self.user = {}
        self.is_authenticated = False
        return rx.redirect("/login")

    def set_username(self, value: str):
        """Set username from input."""
        self.username = value

    def set_password(self, value: str):
        """Set password from input."""
        self.password = value

    def redirect_to_login(self):
        """Redirect to login page (used by layout when not authenticated)."""
        return rx.redirect("/login")
