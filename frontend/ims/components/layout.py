"""
Layout Components - Hamburger navigation with optional pin-to-sidebar
Single menu: drawer (default) or pinned sidebar (user toggle)
"""
import reflex as rx
from ims.state.auth import AuthState
from ims.state.base import BaseState
from ims.components.chat_island import chat_island


# ---------------------------------------------------------------------------
# Navigation link helpers
# ---------------------------------------------------------------------------

def nav_link(label: str, href: str, icon: str) -> rx.Component:
    """Navigation link in pinned sidebar."""
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


def drawer_nav_link(label: str, href: str, icon: str) -> rx.Component:
    """Navigation link in drawer — closes drawer on click."""
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


def _build_nav_links(link_fn, label_pad: str = "8px 12px 2px"):
    """Build the full list of navigation items for a given link function."""
    return [
        # DOEN
        rx.text("DOEN", size="1", weight="bold", color="gray", padding=label_pad),
        link_fn("Dashboard", "/", "layout-dashboard"),
        link_fn("Risico's", "/risks", "triangle-alert"),
        link_fn("Controls", "/controls", "shield-check"),
        link_fn("Compliance", "/compliance", "clipboard-list"),
        link_fn("Assessments", "/assessments", "clipboard-check"),
        link_fn("Incidenten", "/incidents", "circle-alert"),
        link_fn("Besluiten", "/decisions", "stamp"),
        link_fn("In-Control", "/in-control", "gauge"),
        rx.divider(margin_y="4px"),
        # ONTDEKKEN
        rx.text("ONTDEKKEN", size="1", weight="bold", color="gray", padding=label_pad),
        link_fn("Frameworks", "/frameworks", "library"),
        link_fn("Maatregelen", "/measures", "book-open"),
        link_fn("Uitgangspunten", "/policy-principles", "link-2"),
        link_fn("Risicokader", "/risk-framework", "ruler"),
        link_fn("Analyses", "/simulation", "chart-bar"),
        rx.divider(margin_y="4px"),
        # BEHEER
        rx.text("BEHEER", size="1", weight="bold", color="gray", padding=label_pad),
        link_fn("Beleid", "/policies", "file-text"),
        link_fn("Scopes", "/scopes", "git-branch"),
        link_fn("Assets", "/assets", "server"),
        link_fn("Leveranciers", "/suppliers", "building-2"),
        link_fn("Backlog", "/backlog", "list-todo"),
        link_fn("Gebruikers", "/users", "users"),
        rx.cond(
            AuthState.is_admin,
            link_fn("Beheer", "/admin", "settings"),
        ),
    ]


# ---------------------------------------------------------------------------
# Top bar (hamburger) — shown in unpinned mode
# ---------------------------------------------------------------------------

def top_bar() -> rx.Component:
    """Sticky top bar with hamburger menu."""
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
    )


# ---------------------------------------------------------------------------
# Drawer (slide-out) — default unpinned navigation
# ---------------------------------------------------------------------------

def nav_drawer() -> rx.Component:
    """Slide-out navigation drawer with pin button."""
    return rx.drawer.root(
        rx.drawer.overlay(),
        rx.drawer.content(
            rx.vstack(
                # Header
                rx.hstack(
                    rx.icon("shield-check", size=28, color="var(--accent-9)"),
                    rx.text("IMS", size="5", weight="bold"),
                    rx.spacer(),
                    rx.tooltip(
                        rx.icon_button(
                            rx.icon("pin", size=18),
                            variant="ghost",
                            size="2",
                            on_click=BaseState.pin_sidebar,
                        ),
                        content="Menu vastzetten",
                    ),
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
                    *_build_nav_links(drawer_nav_link, label_pad="8px 16px 2px"),
                    spacing="0",
                    width="100%",
                    padding="8px",
                    overflow_y="auto",
                    flex="1",
                ),

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


# ---------------------------------------------------------------------------
# Pinned sidebar — permanent left sidebar when user pins navigation
# ---------------------------------------------------------------------------

def pinned_sidebar() -> rx.Component:
    """Permanent pinned sidebar navigation."""
    return rx.box(
        rx.vstack(
            # Header with unpin button
            rx.hstack(
                rx.icon("shield-check", size=28, color="var(--accent-9)"),
                rx.text("IMS", size="5", weight="bold"),
                rx.spacer(),
                rx.tooltip(
                    rx.icon_button(
                        rx.icon("pin-off", size=18),
                        variant="ghost",
                        size="2",
                        on_click=BaseState.unpin_sidebar,
                    ),
                    content="Menu losmaken",
                ),
                padding="16px",
                width="100%",
                align="center",
            ),
            rx.divider(),

            # Navigation
            rx.vstack(
                *_build_nav_links(nav_link),
                spacing="1",
                width="100%",
                padding="8px",
                overflow_y="auto",
                flex="1",
            ),

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


# ---------------------------------------------------------------------------
# Page header + main layout
# ---------------------------------------------------------------------------

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
    """Main layout wrapper with hamburger navigation and optional pinned sidebar."""
    return rx.cond(
        AuthState.is_authenticated,
        rx.fragment(
            rx.cond(
                BaseState.sidebar_pinned,
                # Pinned mode: permanent sidebar + content
                rx.hstack(
                    pinned_sidebar(),
                    rx.box(
                        rx.cond(
                            title != "",
                            page_header(title, subtitle),
                        ),
                        rx.box(
                            content,
                            padding=rx.breakpoints(initial="12px", md="24px"),
                            overflow_y="auto",
                            flex="1",
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
                # Unpinned mode: top bar + drawer overlay + content
                rx.fragment(
                    nav_drawer(),
                    rx.box(
                        top_bar(),
                        rx.cond(
                            title != "",
                            page_header(title, subtitle),
                        ),
                        rx.box(
                            content,
                            padding=rx.breakpoints(initial="12px", md="24px"),
                            overflow_y="auto",
                            flex="1",
                        ),
                        height="100vh",
                        overflow="hidden",
                        display="flex",
                        flex_direction="column",
                    ),
                ),
            ),
            chat_island(),
        ),
        # Not authenticated — redirect to login
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
