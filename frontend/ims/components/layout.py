"""
Layout Components - Responsive sidebar navigation

Desktop (md+): sidebar always visible, part of flex layout.
Mobile (<md):  hamburger in top bar, sidebar slides in as overlay.
               Auto-closes on navigation. Backdrop click closes.
"""
import reflex as rx
from ims.state.auth import AuthState
from ims.state.base import BaseState
from ims.state.chat import ChatState
from ims.components.chat_island import chat_island


# ---------------------------------------------------------------------------
# Navigation link helpers
# ---------------------------------------------------------------------------

def sidebar_nav_link(label: str, href: str, icon: str) -> rx.Component:
    """Nav link — closes mobile sidebar on click (no-op on desktop)."""
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
        underline="none",
        high_contrast=True,
        on_click=BaseState.close_sidebar,
    )


def _section_header(label: str, is_open_var, toggle_handler):
    """Clickable section header with chevron."""
    return rx.hstack(
        rx.text(label, size="1", weight="bold", color="gray"),
        rx.spacer(),
        rx.cond(
            is_open_var,
            rx.icon("chevron-down", size=14, color="gray"),
            rx.icon("chevron-right", size=14, color="gray"),
        ),
        on_click=toggle_handler,
        cursor="pointer",
        padding="8px 12px 4px",
        width="100%",
        align="center",
        _hover={"background": "var(--gray-a2)"},
        border_radius="md",
    )


def _build_nav_links(link_fn):
    """Build the full list of navigation items.

    Sections are collapsible. MS Hub is always visible at the top.
    """
    return [
        # MS Hub — strategic overview, not for Medewerker
        rx.cond(
            AuthState.can_discover,
            link_fn("MS Hub", "/ms-hub", "layout-grid"),
        ),
        link_fn("Dashboard", "/", "layout-dashboard"),
        rx.divider(margin_y="4px"),
        # DOEN
        _section_header("DOEN", BaseState.menu_doen_open, BaseState.toggle_menu_doen),
        rx.cond(
            BaseState.menu_doen_open,
            rx.fragment(
                link_fn("Mijn Taken", "/tasks", "list-checks"),
                link_fn("Risico's", "/risks", "triangle-alert"),
                link_fn("Controls", "/controls", "shield-check"),
                link_fn("Assessments", "/assessments", "clipboard-check"),
                link_fn("Incidenten", "/incidents", "circle-alert"),
                link_fn("Verbeteracties", "/corrective-actions", "list-checks"),
            ),
        ),
        # ONTDEKKEN — only for Eigenaar+, Toezichthouder
        rx.cond(
            AuthState.can_discover,
            rx.fragment(
                rx.divider(margin_y="4px"),
                _section_header("ONTDEKKEN", BaseState.menu_ontdekken_open, BaseState.toggle_menu_ontdekken),
                rx.cond(
                    BaseState.menu_ontdekken_open,
                    rx.fragment(
                        link_fn("Compliance", "/compliance", "clipboard-list"),
                        link_fn("Besluiten", "/decisions", "stamp"),
                        link_fn("Frameworks", "/frameworks", "library"),
                        link_fn("Maatregelen", "/measures", "book-open"),
                        link_fn("Uitgangspunten", "/policy-principles", "link-2"),
                        link_fn("Risicokader", "/risk-framework", "ruler"),
                        link_fn("Analyses", "/simulation", "chart-bar"),
                        link_fn("Relaties", "/relaties", "network"),
                        link_fn("Rapportage", "/reports", "file-chart-column"),
                        link_fn("Backlog", "/backlog", "list-todo"),
                    ),
                ),
            ),
        ),
        # INRICHTEN — only for configurers
        rx.cond(
            AuthState.can_configure,
            rx.fragment(
                rx.divider(margin_y="4px"),
                _section_header("INRICHTEN", BaseState.menu_inrichten_open, BaseState.toggle_menu_inrichten),
                rx.cond(
                    BaseState.menu_inrichten_open,
                    rx.fragment(
                        link_fn("Mijn Organisatie", "/organization", "landmark"),
                        # IMS Implementatie — collapsible sub-section
                        rx.box(
                            rx.hstack(
                                rx.icon("package", size=20),
                                rx.text("IMS Implementatie", size="2"),
                                rx.spacer(),
                                rx.cond(
                                    BaseState.menu_ims_impl_open,
                                    rx.icon("chevron-down", size=14, color="gray"),
                                    rx.icon("chevron-right", size=14, color="gray"),
                                ),
                                width="100%",
                                padding="8px 12px",
                                border_radius="md",
                                _hover={"background": "var(--gray-a3)"},
                                cursor="pointer",
                                align="center",
                            ),
                            on_click=BaseState.toggle_menu_ims_impl,
                            width="100%",
                        ),
                        rx.cond(
                            BaseState.menu_ims_impl_open,
                            rx.box(
                                link_fn("ISMS Implementatie", "/isms-implementer", "list-start"),
                                padding_left="20px",
                                width="100%",
                            ),
                        ),
                        link_fn("Risicotolerantie", "/risk-appetite", "gauge"),
                        link_fn("Beleid", "/policies", "file-text"),
                        link_fn("Scopes", "/scopes", "git-branch"),
                        link_fn("Assets", "/assets", "server"),
                        link_fn("Leveranciers", "/suppliers", "building-2"),
                    ),
                ),
            ),
        ),
        # BEHEER — only for user managers
        rx.cond(
            AuthState.can_manage_users,
            rx.fragment(
                rx.divider(margin_y="4px"),
                _section_header("BEHEER", BaseState.menu_beheer_open, BaseState.toggle_menu_beheer),
                rx.cond(
                    BaseState.menu_beheer_open,
                    rx.fragment(
                        link_fn("Gebruikers", "/users", "users"),
                        rx.cond(
                            AuthState.is_superuser,
                            link_fn("Organisaties", "/tenants", "building"),
                        ),
                        rx.cond(
                            AuthState.is_admin,
                            link_fn("Beheer", "/admin", "settings"),
                        ),
                    ),
                ),
            ),
        ),
    ]


# ---------------------------------------------------------------------------
# Sidebar content (shared between desktop and mobile)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Sidebar content (shared between desktop and mobile)
# ---------------------------------------------------------------------------

def _sidebar_inner() -> rx.Component:
    """Sidebar content: header, navigation, user section."""
    return rx.vstack(
        # Header
        rx.hstack(
            rx.icon("shield-check", size=24, color="var(--accent-9)", flex_shrink="0"),
            rx.vstack(
                rx.text("IMS", size="5", weight="bold"),
                # Tenant switcher (multi-tenant) or static name (single tenant)
                rx.cond(
                    AuthState.has_multiple_tenants,
                    rx.el.select(
                        rx.foreach(
                            AuthState.tenants,
                            lambda t: rx.el.option(t["name"], value=t["id"].to(str)),
                        ),
                        value=AuthState.tenant_id.to(str),
                        on_change=AuthState.switch_tenant,
                        style={
                            "font_size": "12px",
                            "background": "transparent",
                            "border": "none",
                            "color": "var(--gray-11)",
                            "cursor": "pointer",
                            "padding": "0",
                        },
                    ),
                    rx.cond(
                        AuthState.tenant_name != "",
                        rx.text(AuthState.tenant_name, size="1", color="gray", trim="both"),
                    ),
                ),
                spacing="0",
                align_items="start",
            ),
            rx.spacer(),
            # X button — only visible on mobile (sm, md-1)
            rx.icon_button(
                rx.icon("x", size=20),
                variant="ghost",
                size="2",
                on_click=BaseState.close_sidebar,
                display=["flex", "flex", "none", "none", "none"],
            ),
            width="100%",
            padding="16px",
            spacing="2",
            align="start",
        ),
        rx.divider(),

        # Navigation
        rx.vstack(
            *_build_nav_links(sidebar_nav_link),
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
    )


# ---------------------------------------------------------------------------
# Desktop sidebar — always visible on md+
# ---------------------------------------------------------------------------

def desktop_sidebar() -> rx.Component:
    """Permanent sidebar for desktop — part of flex layout, pushes content."""
    return rx.box(
        _sidebar_inner(),
        display=["none", "none", "flex", "flex", "flex"],
        width="260px",
        min_width="260px",
        background="var(--gray-a2)",
        border_right="1px solid var(--gray-a5)",
    )


# ---------------------------------------------------------------------------
# Mobile sidebar — overlay + backdrop, controlled by state
# ---------------------------------------------------------------------------

def mobile_sidebar() -> rx.Component:
    """Overlay sidebar for mobile — slides over content with backdrop."""
    return rx.fragment(
        # Backdrop
        rx.box(
            position="fixed",
            inset="0",
            background="rgba(0,0,0,0.4)",
            z_index="40",
            on_click=BaseState.close_sidebar,
        ),
        # Sidebar panel
        rx.box(
            _sidebar_inner(),
            position="fixed",
            left="0",
            top="0",
            width="85vw",
            max_width="320px",
            height="100vh",
            background="var(--color-background)",
            border_right="1px solid var(--gray-a5)",
            z_index="50",
        ),
    )


# ---------------------------------------------------------------------------
# Top bar — hamburger menu, only visible on mobile
# ---------------------------------------------------------------------------

def top_bar() -> rx.Component:
    """Sticky top bar with hamburger — mobile only."""
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
        display=["block", "block", "none", "none", "none"],
        border_bottom="1px solid var(--gray-a5)",
        background="var(--color-background)",
        position="sticky",
        top="0",
        z_index="10",
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
        padding=["12px 16px", "12px 16px", "24px", "24px", "24px"],
        border_bottom="1px solid var(--gray-a5)",
    )


def layout(content: rx.Component, title: str = "", subtitle: str = "") -> rx.Component:
    """Responsive layout: permanent desktop sidebar + mobile hamburger overlay.

    Desktop (md+): sidebar always visible, pushes content.
    Mobile (<md):  hamburger top bar, sidebar overlay on toggle.
    """
    return rx.cond(
        AuthState.is_authenticated,
        rx.fragment(
            rx.hstack(
                # Desktop sidebar (always visible on md+, hidden on mobile)
                desktop_sidebar(),
                # Main content
                rx.box(
                    top_bar(),
                    rx.cond(
                        title != "",
                        page_header(title, subtitle),
                        rx.fragment(),
                    ),
                    rx.box(
                        content,
                        padding=["12px", "12px", "24px", "24px", "24px"],
                        overflow_y="auto",
                        flex="1",
                    ),
                    flex="1",
                    height="100vh",
                    overflow="hidden",
                    display="flex",
                    flex_direction="column",
                    on_mount=ChatState.sync_page_context,
                ),
                width="100%",
                spacing="0",
            ),
            # Mobile sidebar overlay (only rendered when open)
            rx.cond(
                BaseState.sidebar_open,
                mobile_sidebar(),
                rx.fragment(),
            ),
            chat_island(),
        ),
        # Not (yet) authenticated
        rx.fragment(
            rx.center(
                rx.spinner(size="3"),
                height="100vh",
            ),
            rx.script(
                "if(!localStorage.getItem('ims_user'))window.location.href='/login';"
            ),
        ),
    )
