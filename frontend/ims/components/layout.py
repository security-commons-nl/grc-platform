"""
Layout Components - Main layout with sidebar navigation
Responsive: desktop sidebar + mobile drawer
"""
import reflex as rx
from ims.state.auth import AuthState
from ims.state.base import BaseState
from ims.components.chat_island import chat_island


def nav_link(label: str, href: str, icon: str) -> rx.Component:
    """Navigation link in sidebar (desktop)."""
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


def mobile_nav_link(label: str, href: str, icon: str) -> rx.Component:
    """Navigation link in mobile drawer with larger touch targets."""
    return rx.link(
        rx.hstack(
            rx.icon(icon, size=20),
            rx.text(label, size="3"),
            width="100%",
            padding="14px 16px",
            border_radius="md",
            _hover={"background": "var(--gray-a3)"},
        ),
        href=href,
        width="100%",
        text_decoration="none",
        color="inherit",
        on_click=BaseState.close_sidebar,
    )


def sidebar() -> rx.Component:
    """Sidebar navigation (desktop only)."""
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

            # Navigation — DOEN
            rx.vstack(
                rx.text("DOEN", size="1", weight="bold", color="gray", padding="8px 12px 2px"),
                nav_link("Dashboard", "/", "layout-dashboard"),
                nav_link("Risico's", "/risks", "triangle-alert"),
                nav_link("Controls", "/controls", "shield-check"),
                nav_link("Compliance", "/compliance", "clipboard-list"),
                nav_link("Assessments", "/assessments", "clipboard-check"),
                nav_link("Incidenten", "/incidents", "circle-alert"),
                nav_link("Besluiten", "/decisions", "stamp"),
                nav_link("In-Control", "/in-control", "gauge"),
                spacing="1",
                width="100%",
                padding="8px 8px 0",
            ),
            rx.divider(margin_y="4px"),
            # Navigation — ONTDEKKEN
            rx.vstack(
                rx.text("ONTDEKKEN", size="1", weight="bold", color="gray", padding="8px 12px 2px"),
                nav_link("Frameworks", "/frameworks", "library"),
                nav_link("Maatregelen", "/measures", "book-open"),
                nav_link("Uitgangspunten", "/policy-principles", "link-2"),
                nav_link("Risicokader", "/risk-framework", "ruler"),
                nav_link("Analyses", "/simulation", "chart-bar"),
                spacing="1",
                width="100%",
                padding="0 8px",
            ),
            rx.divider(margin_y="4px"),
            # Navigation — BEHEER
            rx.vstack(
                rx.text("BEHEER", size="1", weight="bold", color="gray", padding="8px 12px 2px"),
                nav_link("Beleid", "/policies", "file-text"),
                nav_link("Scopes", "/scopes", "git-branch"),
                nav_link("Assets", "/assets", "server"),
                nav_link("Leveranciers", "/suppliers", "building-2"),
                nav_link("Backlog", "/backlog", "list-todo"),
                nav_link("Gebruikers", "/users", "users"),
                rx.cond(
                    AuthState.is_admin,
                    nav_link("Beheer", "/admin", "settings"),
                ),
                spacing="1",
                width="100%",
                padding="0 8px 8px",
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
                    rx.color_mode_cond(
                        light=rx.icon("moon", size=16),
                        dark=rx.icon("sun", size=16),
                    ),
                    variant="ghost",
                    size="1",
                    on_click=rx.toggle_color_mode,
                ),
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


def mobile_top_bar() -> rx.Component:
    """Sticky top bar for mobile with hamburger menu."""
    return rx.box(
        rx.hstack(
            rx.icon_button(
                rx.icon("menu", size=22),
                variant="ghost",
                size="3",
                on_click=BaseState.toggle_sidebar,
            ),
            rx.hstack(
                rx.icon("shield-check", size=22, color="var(--accent-9)"),
                rx.text("IMS", size="4", weight="bold"),
                spacing="2",
                align="center",
            ),
            rx.spacer(),
            rx.icon_button(
                rx.color_mode_cond(
                    light=rx.icon("moon", size=16),
                    dark=rx.icon("sun", size=16),
                ),
                variant="ghost",
                size="2",
                on_click=rx.toggle_color_mode,
            ),
            width="100%",
            padding="8px 12px",
            align="center",
        ),
        border_bottom="1px solid var(--gray-a5)",
        background="var(--color-background)",
        position="sticky",
        top="0",
        z_index="10",
        class_name="block md:hidden",
    )


def mobile_drawer() -> rx.Component:
    """Mobile navigation drawer."""
    return rx.drawer.root(
        rx.drawer.overlay(),
        rx.drawer.content(
            rx.vstack(
                # Header
                rx.hstack(
                    rx.icon("shield-check", size=28, color="var(--accent-9)"),
                    rx.text("IMS", size="5", weight="bold"),
                    rx.spacer(),
                    rx.icon_button(
                        rx.icon("x", size=20),
                        variant="ghost",
                        size="2",
                        on_click=BaseState.close_sidebar,
                    ),
                    width="100%",
                    padding="16px",
                    align="center",
                ),
                rx.divider(),

                # Navigation links
                rx.vstack(
                    rx.text("DOEN", size="1", weight="bold", color="gray", padding="8px 16px 2px"),
                    mobile_nav_link("Dashboard", "/", "layout-dashboard"),
                    mobile_nav_link("Risico's", "/risks", "triangle-alert"),
                    mobile_nav_link("Controls", "/controls", "shield-check"),
                    mobile_nav_link("Compliance", "/compliance", "clipboard-list"),
                    mobile_nav_link("Assessments", "/assessments", "clipboard-check"),
                    mobile_nav_link("Incidenten", "/incidents", "circle-alert"),
                    mobile_nav_link("Besluiten", "/decisions", "stamp"),
                    mobile_nav_link("In-Control", "/in-control", "gauge"),
                    rx.divider(),
                    rx.text("ONTDEKKEN", size="1", weight="bold", color="gray", padding="8px 16px 2px"),
                    mobile_nav_link("Frameworks", "/frameworks", "library"),
                    mobile_nav_link("Maatregelen", "/measures", "book-open"),
                    mobile_nav_link("Uitgangspunten", "/policy-principles", "link-2"),
                    mobile_nav_link("Risicokader", "/risk-framework", "ruler"),
                    mobile_nav_link("Analyses", "/simulation", "chart-bar"),
                    rx.divider(),
                    rx.text("BEHEER", size="1", weight="bold", color="gray", padding="8px 16px 2px"),
                    mobile_nav_link("Beleid", "/policies", "file-text"),
                    mobile_nav_link("Scopes", "/scopes", "git-branch"),
                    mobile_nav_link("Assets", "/assets", "server"),
                    mobile_nav_link("Leveranciers", "/suppliers", "building-2"),
                    mobile_nav_link("Backlog", "/backlog", "list-todo"),
                    mobile_nav_link("Gebruikers", "/users", "users"),
                    rx.cond(
                        AuthState.is_admin,
                        mobile_nav_link("Beheer", "/admin", "settings"),
                    ),
                    spacing="0",
                    width="100%",
                    padding="8px",
                    overflow_y="auto",
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

                height="100%",
                width="100%",
                align_items="stretch",
            ),
            background="var(--color-background)",
            width="280px",
            height="100vh",
        ),
        open=BaseState.sidebar_open,
        on_open_change=lambda open: rx.cond(~open, BaseState.close_sidebar(), rx.noop()),
        direction="left",
    )


def page_header(title: str, subtitle: str = "") -> rx.Component:
    """Page header with title — responsive padding and font size."""
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.heading(title, size=rx.breakpoints(initial="5", md="6")),
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
        padding=rx.breakpoints(initial="12px 16px", md="24px"),
        border_bottom="1px solid var(--gray-a5)",
    )


def layout(content: rx.Component, title: str = "", subtitle: str = "") -> rx.Component:
    """Main layout wrapper with responsive sidebar and AI chat island."""
    return rx.cond(
        AuthState.is_authenticated,
        rx.fragment(
            mobile_drawer(),
            rx.hstack(
                rx.box(sidebar(), class_name="hidden md:block"),
                rx.box(
                    mobile_top_bar(),
                    rx.cond(
                        title != "",
                        page_header(title, subtitle),
                    ),
                    rx.box(
                        content,
                        padding=rx.breakpoints(initial="12px", md="24px"),
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
            chat_island(),
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
