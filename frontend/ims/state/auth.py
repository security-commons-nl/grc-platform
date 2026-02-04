"""
Auth State - handles user authentication with persistence
"""
import reflex as rx
from typing import Dict, Any
import json


class AuthState(rx.State):
    """Authentication state with localStorage persistence."""

    # User info (persisted in localStorage)
    _user_json: str = rx.LocalStorage(name="ims_user")

    # Login form
    username: str = ""
    password: str = ""
    login_error: str = ""
    is_logging_in: bool = False

    @rx.var
    def user(self) -> Dict[str, Any]:
        """Get user from localStorage."""
        if self._user_json:
            try:
                return json.loads(self._user_json)
            except:
                return {}
        return {}

    @rx.var
    def is_authenticated(self) -> bool:
        """Check if user is logged in."""
        return bool(self._user_json and self._user_json != "")

    @rx.var
    def user_display_name(self) -> str:
        """Get user's display name."""
        user = self.user
        if user:
            return user.get("full_name") or user.get("username", "User")
        return "Guest"

    @rx.var
    def user_email(self) -> str:
        """Get user's email."""
        user = self.user
        return user.get("email", "") if user else ""

    async def login(self):
        """
        Attempt to log in.
        For now, this is a simple simulation - accepts any username.
        """
        self.is_logging_in = True
        self.login_error = ""

        if not self.username.strip():
            self.login_error = "Gebruikersnaam is verplicht"
            self.is_logging_in = False
            return

        # Simulate successful login - store in localStorage
        user_data = {
            "id": 1,
            "username": self.username,
            "full_name": self.username.title(),
            "email": f"{self.username}@example.com",
            "is_active": True,
        }
        self._user_json = json.dumps(user_data)
        self.is_logging_in = False
        self.username = ""
        self.password = ""

        # Redirect to dashboard
        return rx.redirect("/")

    def logout(self):
        """Log out the current user."""
        self._user_json = ""
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
