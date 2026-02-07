"""
Admin Page - System administration with 4 tabs
Overzicht, Wachtwoordbeheer, Systeemstatus, Audit Log
"""
import reflex as rx
from ims.state.admin import AdminState
from ims.state.auth import AuthState
from ims.components.layout import layout


def stat_card(label: str, value: rx.Var, icon: str, color: str) -> rx.Component:
    """Single stat card."""
    return rx.card(
        rx.hstack(
            rx.icon(icon, size=24, color=f"var(--{color}-9)"),
            rx.vstack(
                rx.text(label, size="1", color="gray"),
                rx.text(value, size="5", weight="bold"),
                spacing="0",
                align_items="start",
            ),
            spacing="3",
            align="center",
        ),
        padding="16px",
    )


def overview_tab() -> rx.Component:
    """Overzicht tab — user statistics."""
    return rx.vstack(
        rx.grid(
            stat_card("Totaal gebruikers", AdminState.stats["total_users"].to(str), "users", "blue"),
            stat_card("Actief", AdminState.stats["active_users"].to(str), "user-check", "green"),
            stat_card("Beheerders", AdminState.stats["admin_users"].to(str), "shield", "red"),
            stat_card("Inactief", AdminState.stats["inactive_users"].to(str), "user-x", "gray"),
            columns=rx.breakpoints(initial="1", sm="2", md="4"),
            spacing="4",
            width="100%",
        ),
        spacing="4",
        width="100%",
    )


def pw_user_row(user: dict) -> rx.Component:
    """Row in password management table."""
    return rx.table.row(
        rx.table.cell(
            rx.hstack(
                rx.avatar(
                    fallback=rx.cond(
                        user["full_name"] != None,
                        user["full_name"].to(str)[0],
                        user["username"].to(str)[0],
                    ),
                    size="2",
                ),
                rx.vstack(
                    rx.text(
                        rx.cond(
                            user["full_name"] != None,
                            user["full_name"],
                            user["username"],
                        ),
                        weight="medium",
                        size="2",
                    ),
                    rx.text(user["username"], size="1", color="gray"),
                    spacing="0",
                    align_items="start",
                ),
                spacing="2",
            ),
        ),
        rx.table.cell(rx.text(user["email"], size="2")),
        rx.table.cell(
            rx.button(
                rx.icon("key", size=14),
                "Reset",
                variant="soft",
                size="1",
                color_scheme="orange",
                on_click=AdminState.open_pw_dialog(user["id"], user["username"]),
            ),
        ),
        _hover={"background": "var(--gray-a3)"},
    )


def password_tab() -> rx.Component:
    """Wachtwoordbeheer tab."""
    return rx.vstack(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Gebruiker"),
                    rx.table.column_header_cell("E-mail"),
                    rx.table.column_header_cell("Actie", width="120px"),
                ),
            ),
            rx.table.body(
                rx.foreach(AdminState.users_for_pw, pw_user_row),
            ),
            width="100%",
        ),
        password_dialog(),
        width="100%",
        spacing="4",
    )


def password_dialog() -> rx.Component:
    """Dialog for resetting a user's password."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Wachtwoord Resetten"),
            rx.dialog.description(
                rx.hstack(
                    rx.text("Gebruiker: "),
                    rx.text(AdminState.pw_target_username, weight="bold"),
                    spacing="1",
                ),
                size="2",
                margin_bottom="16px",
            ),

            rx.cond(
                AdminState.pw_error != "",
                rx.callout(
                    AdminState.pw_error,
                    icon="circle-alert",
                    color="red",
                    margin_bottom="12px",
                ),
            ),

            rx.cond(
                AdminState.pw_success != "",
                rx.callout(
                    AdminState.pw_success,
                    icon="circle-check",
                    color="green",
                    margin_bottom="12px",
                ),
            ),

            rx.vstack(
                rx.text("Nieuw wachtwoord", size="2", weight="medium"),
                rx.input(
                    placeholder="Minimaal 8 tekens",
                    value=AdminState.pw_new_password,
                    on_change=AdminState.set_pw_new_password,
                    type="password",
                    width="100%",
                ),
                spacing="2",
                width="100%",
            ),

            rx.hstack(
                rx.dialog.close(
                    rx.button(
                        "Annuleren",
                        variant="soft",
                        color_scheme="gray",
                        on_click=AdminState.close_pw_dialog,
                    ),
                ),
                rx.button(
                    "Wachtwoord Wijzigen",
                    color_scheme="orange",
                    on_click=AdminState.change_user_password,
                ),
                spacing="3",
                justify="end",
                margin_top="16px",
            ),

            max_width="400px",
        ),
        open=AdminState.show_pw_dialog,
    )


def health_status_card(
    label: str,
    status: rx.Var,
    detail: rx.Var,
    icon: str,
) -> rx.Component:
    """Health status card for a service."""
    return rx.card(
        rx.hstack(
            rx.icon(icon, size=24),
            rx.vstack(
                rx.text(label, weight="bold", size="3"),
                rx.hstack(
                    rx.cond(
                        status == "ok",
                        rx.badge("Online", color_scheme="green", variant="soft"),
                        rx.cond(
                            status == "offline",
                            rx.badge("Offline", color_scheme="gray", variant="soft"),
                            rx.badge("Fout", color_scheme="red", variant="soft"),
                        ),
                    ),
                    rx.text(detail, size="1", color="gray"),
                    spacing="2",
                ),
                spacing="1",
                align_items="start",
            ),
            spacing="3",
            align="center",
        ),
        padding="16px",
        width="100%",
    )


def health_tab() -> rx.Component:
    """Systeemstatus tab."""
    return rx.vstack(
        rx.grid(
            health_status_card(
                "Database",
                AdminState.health_data["database"]["status"].to(str),
                AdminState.health_data["database"]["status"].to(str),
                "database",
            ),
            health_status_card(
                "Ollama (AI)",
                AdminState.health_data["ollama"]["status"].to(str),
                AdminState.health_data["ollama"]["url"].to(str),
                "brain",
            ),
            columns=rx.breakpoints(initial="1", md="2"),
            spacing="4",
            width="100%",
        ),
        rx.card(
            rx.hstack(
                rx.icon("info", size=20, color="var(--blue-9)"),
                rx.vstack(
                    rx.text("API Versie", size="1", color="gray"),
                    rx.text(AdminState.health_data["version"].to(str), size="3", weight="bold"),
                    spacing="0",
                    align_items="start",
                ),
                rx.spacer(),
                rx.vstack(
                    rx.text("Laatste check", size="1", color="gray"),
                    rx.text(AdminState.health_data["timestamp"].to(str), size="2"),
                    spacing="0",
                    align_items="start",
                ),
                spacing="3",
                width="100%",
            ),
            padding="16px",
            width="100%",
        ),
        rx.button(
            rx.icon("refresh-cw", size=14),
            "Vernieuwen",
            variant="soft",
            size="2",
            on_click=AdminState.load_health,
        ),
        spacing="4",
        width="100%",
    )


def audit_row(entry: dict) -> rx.Component:
    """Row in audit log table."""
    return rx.table.row(
        rx.table.cell(
            rx.hstack(
                rx.avatar(
                    fallback=rx.cond(
                        entry["full_name"] != None,
                        entry["full_name"].to(str)[0],
                        entry["username"].to(str)[0],
                    ),
                    size="1",
                ),
                rx.text(entry["username"], size="2"),
                spacing="2",
            ),
        ),
        rx.table.cell(
            rx.text(
                rx.cond(
                    entry["full_name"] != None,
                    entry["full_name"],
                    "-",
                ),
                size="2",
            ),
        ),
        rx.table.cell(
            rx.text(entry["last_login"], size="2"),
        ),
        rx.table.cell(
            rx.cond(
                entry["is_active"],
                rx.badge("Actief", color_scheme="green", variant="soft", size="1"),
                rx.badge("Inactief", color_scheme="gray", variant="soft", size="1"),
            ),
        ),
        _hover={"background": "var(--gray-a3)"},
    )


def audit_tab() -> rx.Component:
    """Audit Log tab."""
    return rx.vstack(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Gebruiker"),
                    rx.table.column_header_cell("Naam"),
                    rx.table.column_header_cell("Laatste Login"),
                    rx.table.column_header_cell("Status", width="100px"),
                ),
            ),
            rx.table.body(
                rx.foreach(AdminState.audit_entries, audit_row),
            ),
            width="100%",
        ),
        width="100%",
    )


def admin_content() -> rx.Component:
    """Admin panel content with 4 tabs."""
    return rx.vstack(
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger(
                    rx.hstack(rx.icon("layout-dashboard", size=14), rx.text("Overzicht"), spacing="1"),
                    value="overzicht",
                ),
                rx.tabs.trigger(
                    rx.hstack(rx.icon("key", size=14), rx.text("Wachtwoorden"), spacing="1"),
                    value="wachtwoorden",
                ),
                rx.tabs.trigger(
                    rx.hstack(rx.icon("activity", size=14), rx.text("Systeemstatus"), spacing="1"),
                    value="systeemstatus",
                ),
                rx.tabs.trigger(
                    rx.hstack(rx.icon("scroll-text", size=14), rx.text("Audit Log"), spacing="1"),
                    value="audit",
                ),
            ),
            rx.tabs.content(
                rx.box(overview_tab(), padding_top="16px"),
                value="overzicht",
            ),
            rx.tabs.content(
                rx.box(password_tab(), padding_top="16px"),
                value="wachtwoorden",
            ),
            rx.tabs.content(
                rx.box(health_tab(), padding_top="16px"),
                value="systeemstatus",
            ),
            rx.tabs.content(
                rx.box(audit_tab(), padding_top="16px"),
                value="audit",
            ),
            default_value="overzicht",
            width="100%",
        ),
        width="100%",
        spacing="4",
        on_mount=AdminState.load_all,
    )


def admin_page() -> rx.Component:
    """Admin page with access guard."""
    return layout(
        rx.cond(
            AuthState.is_admin,
            admin_content(),
            rx.center(
                rx.callout(
                    "Geen toegang. Alleen beheerders hebben toegang tot dit paneel.",
                    icon="shield-alert",
                    color="red",
                    size="3",
                ),
                padding="40px",
            ),
        ),
        title="Beheer",
        subtitle="Systeembeheer en administratie",
    )
