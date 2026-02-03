"""
Base State - shared state across the application
"""
import reflex as rx
from typing import Optional


class BaseState(rx.State):
    """Base state with common functionality."""

    # Current tenant context
    current_tenant_id: int = 1

    # Loading states
    is_loading: bool = False
    error_message: str = ""

    # Toast notifications
    toast_message: str = ""
    toast_type: str = "info"  # info, success, error, warning

    def set_loading(self, loading: bool):
        """Set loading state."""
        self.is_loading = loading

    def set_error(self, message: str):
        """Set error message."""
        self.error_message = message
        self.toast_message = message
        self.toast_type = "error"

    def clear_error(self):
        """Clear error message."""
        self.error_message = ""

    def show_toast(self, message: str, toast_type: str = "info"):
        """Show toast notification."""
        self.toast_message = message
        self.toast_type = toast_type

    def clear_toast(self):
        """Clear toast."""
        self.toast_message = ""
