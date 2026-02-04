"""
Layout Components - Main layout with sidebar navigation
"""
import reflex as rx
from ims.state.auth import AuthState


def nav_link(label: str, href: str, icon: str) -> rx.Component:
    """Navigation link in sidebar."""
    return rx.link(
        rx.hstack(
            rx.icon(icon, size=20),
            rx.text(label, size="2"),
            width="100%",
            padding="8px 12px",
            border_radius="md",
            _hover={"background": "var(--gray-a3)"},
        ),
        href=href,
        width="100%",
        text_decoration="none",
        color="inherit",
    )


def sidebar() -> rx.Component:
    """Sidebar navigation."""
    return rx.box(
        rx.vstack(
            # Logo / Title
            rx.hstack(
                rx.icon("shield-check", size=28, color="var(--accent-9)"),
                rx.text("IMS", size="5", weight="bold"),
                padding="16px",
                width="100%",
            ),
            rx.divider(),

            # Navigation
            rx.vstack(
                nav_link("Dashboard", "/", "layout-dashboard"),
                nav_link("Risico's", "/risks", "triangle-alert"),
                nav_link("Maatregelen", "/measures", "shield"),
                nav_link("Compliance", "/compliance", "clipboard-list"),
                nav_link("Assessments", "/assessments", "clipboard-check"),
                nav_link("Incidenten", "/incidents", "circle-alert"),
                nav_link("Beleid", "/policies", "file-text"),
                nav_link("Scopes", "/scopes", "git-branch"),
                nav_link("Assets", "/assets", "server"),
                nav_link("Leveranciers", "/suppliers", "building-2"),
                nav_link("Backlog", "/backlog", "list-todo"),
                spacing="1",
                width="100%",
                padding="8px",
            ),

            rx.spacer(),
            rx.divider(),

            # User section
            rx.hstack(
                rx.avatar(
                    fallback=AuthState.user_display_name[0],
                    size="2",
                ),
                rx.vstack(
                    rx.text(AuthState.user_display_name, size="2", weight="medium"),
                    rx.text(AuthState.user_email, size="1", color="gray"),
                    spacing="0",
                    align_items="start",
                ),
                rx.spacer(),
                rx.icon_button(
                    rx.icon("log-out", size=16),
                    variant="ghost",
                    size="1",
                    on_click=AuthState.logout,
                ),
                width="100%",
                padding="12px",
            ),

            height="100vh",
            width="100%",
            align_items="stretch",
        ),
        width="240px",
        min_width="240px",
        background="var(--gray-a2)",
        border_right="1px solid var(--gray-a5)",
    )


def page_header(title: str, subtitle: str = "") -> rx.Component:
    """Page header with title."""
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.heading(title, size="6"),
                rx.cond(
                    subtitle != "",
                    rx.text(subtitle, size="2", color="gray"),
                ),
                align_items="start",
                spacing="1",
            ),
            rx.spacer(),
            width="100%",
        ),
        padding="24px",
        border_bottom="1px solid var(--gray-a5)",
    )


def layout(content: rx.Component, title: str = "", subtitle: str = "") -> rx.Component:
    """Main layout wrapper with sidebar."""
    return rx.cond(
        AuthState.is_authenticated,
        rx.hstack(
            sidebar(),
            rx.box(
                rx.cond(
                    title != "",
                    page_header(title, subtitle),
                ),
                rx.box(
                    content,
                    padding="24px",
                    overflow_y="auto",
                ),
                flex="1",
                height="100vh",
                overflow="hidden",
                display="flex",
                flex_direction="column",
            ),
            width="100%",
            spacing="0",
        ),
        # Show login redirect message when not authenticated
        rx.center(
            rx.vstack(
                rx.spinner(size="3"),
                rx.text("Redirecting to login...", color="gray"),
                spacing="3",
            ),
            height="100vh",
            on_mount=AuthState.redirect_to_login,
        ),
    )
