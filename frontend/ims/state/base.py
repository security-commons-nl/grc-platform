"""
Base State - shared state across the application
"""
import reflex as rx
from typing import Optional


class BaseState(rx.State):
    """Base state with common functionality."""

    # Loading states
    is_loading: bool = False
    error_message: str = ""

    # Toast notifications
    toast_message: str = ""
    toast_type: str = "info"  # info, success, error, warning

    # Mobile sidebar toggle (desktop sidebar is always visible via CSS)
    sidebar_open: bool = False

    # Journey stepper (collapsible on MS Hub)
    journey_expanded: bool = True

    # Collapsible menu sections
    menu_doen_open: bool = True
    menu_ontdekken_open: bool = False
    menu_inrichten_open: bool = False
    menu_ims_impl_open: bool = False
    menu_beheer_open: bool = False

    def toggle_sidebar(self):
        """Toggle mobile sidebar."""
        self.sidebar_open = not self.sidebar_open

    def close_sidebar(self):
        """Close mobile sidebar."""
        self.sidebar_open = False

    def toggle_journey_expanded(self):
        """Toggle journey stepper visibility."""
        self.journey_expanded = not self.journey_expanded

    def toggle_menu_doen(self):
        self.menu_doen_open = not self.menu_doen_open

    def toggle_menu_ontdekken(self):
        self.menu_ontdekken_open = not self.menu_ontdekken_open

    def toggle_menu_inrichten(self):
        self.menu_inrichten_open = not self.menu_inrichten_open

    def toggle_menu_ims_impl(self):
        self.menu_ims_impl_open = not self.menu_ims_impl_open

    def toggle_menu_beheer(self):
        self.menu_beheer_open = not self.menu_beheer_open

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
