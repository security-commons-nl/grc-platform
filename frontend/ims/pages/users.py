"""
Users Page - User management with RBAC role assignment
"""
import reflex as rx
from ims.state.user import UserState
from ims.state.auth import AuthState
from ims.components.layout import layout


# Role translations (Three Lines model)
ROLE_LABELS = {
    "Beheerder": "Beheerder",
    "Coordinator": "Coördinator",
    "Eigenaar": "Eigenaar",
    "Medewerker": "Medewerker",
    "Toezichthouder": "Toezichthouder",
}

ROLE_COLORS = {
    "Beheerder": "red",
    "Coordinator": "blue",
    "Eigenaar": "purple",
    "Medewerker": "green",
    "Toezichthouder": "orange",
}


def role_badge(role: str) -> rx.Component:
    """Badge for user role (Three Lines model)."""
    return rx.match(
        role,
        ("Beheerder", rx.badge("Beheerder", color_scheme="red", variant="soft")),
        ("Coordinator", rx.badge("Coördinator", color_scheme="blue", variant="soft")),
        ("Eigenaar", rx.badge("Eigenaar", color_scheme="purple", variant="soft")),
        ("Medewerker", rx.badge("Medewerker", color_scheme="green", variant="soft")),
        ("Toezichthouder", rx.badge("Toezichthouder", color_scheme="orange", variant="soft")),
        rx.badge(role, color_scheme="gray", variant="outline"),
    )


def status_badge(is_active: bool) -> rx.Component:
    """Badge for user status."""
    return rx.cond(
        is_active,
        rx.badge("Actief", color_scheme="green", variant="soft"),
        rx.badge("Inactief", color_scheme="gray", variant="soft"),
    )


def user_row(user: dict) -> rx.Component:
    """Single row in users table."""
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
                    align_items="start",
                    spacing="0",
                ),
                spacing="2",
            ),
        ),
        rx.table.cell(
            rx.text(user["email"], size="2"),
        ),
        rx.table.cell(
            rx.vstack(
                rx.cond(
                    user["department"] != None,
                    rx.text(user["department"], size="2"),
                    rx.text("-", size="2", color="gray"),
                ),
                rx.cond(
                    user["job_title"] != None,
                    rx.text(user["job_title"], size="1", color="gray"),
                ),
                align_items="start",
                spacing="0",
            ),
        ),
        rx.table.cell(
            rx.hstack(
                status_badge(user["is_active"]),
                rx.cond(
                    user["is_superuser"],
                    rx.badge(
                        rx.hstack(rx.icon("shield", size=10), rx.text("Super"), spacing="1"),
                        color_scheme="red",
                        variant="surface",
                        size="1",
                    ),
                ),
                spacing="1",
            ),
        ),
        rx.table.cell(
            rx.hstack(
                rx.tooltip(
                    rx.icon_button(
                        rx.icon("key", size=14),
                        variant="ghost",
                        size="1",
                        on_click=lambda: UserState.open_role_dialog(user["id"]),
                    ),
                    content="Rollen beheren",
                ),
                rx.icon_button(
                    rx.icon("pencil", size=14),
                    variant="ghost",
                    size="1",
                    on_click=lambda: UserState.open_edit_dialog(user["id"]),
                ),
                rx.icon_button(
                    rx.icon("user-x", size=14),
                    variant="ghost",
                    size="1",
                    color_scheme="red",
                    on_click=lambda: UserState.open_delete_dialog(user["id"]),
                ),
                spacing="1",
            ),
        ),
        _hover={"background": "var(--gray-a3)"},
    )


def user_mobile_card(user: dict) -> rx.Component:
    """Mobile card view for a single user."""
    return rx.card(
        rx.vstack(
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
                    rx.text(user["email"], size="1", color="gray"),
                    align_items="start",
                    spacing="0",
                    flex="1",
                ),
                rx.hstack(
                    rx.icon_button(
                        rx.icon("pencil", size=14),
                        variant="ghost",
                        size="1",
                        on_click=lambda: UserState.open_edit_dialog(user["id"]),
                    ),
                    rx.icon_button(
                        rx.icon("user-x", size=14),
                        variant="ghost",
                        size="1",
                        color_scheme="red",
                        on_click=lambda: UserState.open_delete_dialog(user["id"]),
                    ),
                    spacing="1",
                ),
                width="100%",
                align="center",
                spacing="2",
            ),
            rx.hstack(
                status_badge(user["is_active"]),
                rx.cond(
                    user["is_superuser"],
                    rx.badge(
                        rx.hstack(rx.icon("shield", size=10), rx.text("Super"), spacing="1"),
                        color_scheme="red",
                        variant="surface",
                        size="1",
                    ),
                ),
                rx.cond(
                    user["department"] != None,
                    rx.text(user["department"], size="1", color="gray"),
                ),
                spacing="2",
                wrap="wrap",
            ),
            spacing="2",
            width="100%",
        ),
        width="100%",
    )


def users_table() -> rx.Component:
    """Users data table."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Gebruiker"),
                rx.table.column_header_cell("E-mail"),
                rx.table.column_header_cell("Afdeling"),
                rx.table.column_header_cell("Status", width="140px"),
                rx.table.column_header_cell("Acties", width="120px"),
            ),
        ),
        rx.table.body(
            rx.cond(
                UserState.is_loading,
                rx.table.row(
                    rx.table.cell(
                        rx.center(
                            rx.spinner(size="2"),
                            width="100%",
                            padding="40px",
                        ),
                        col_span=5,
                    ),
                ),
                rx.cond(
                    UserState.users.length() > 0,
                    rx.foreach(UserState.users, user_row),
                    rx.table.row(
                        rx.table.cell(
                            rx.center(
                                rx.vstack(
                                    rx.icon("users", size=32, color="gray"),
                                    rx.text("Geen gebruikers gevonden", color="gray"),
                                    rx.button(
                                        rx.icon("plus", size=14),
                                        "Voeg eerste gebruiker toe",
                                        variant="soft",
                                        size="2",
                                        margin_top="8px",
                                        on_click=UserState.open_create_dialog,
                                    ),
                                    spacing="2",
                                ),
                                width="100%",
                                padding="40px",
                            ),
                            col_span=5,
                        ),
                    ),
                ),
            ),
        ),
        width="100%",
    )


def filter_bar() -> rx.Component:
    """Filter bar for users."""
    return rx.flex(
        rx.select.root(
            rx.select.trigger(placeholder="Filter op status"),
            rx.select.content(
                rx.select.item("Actieve gebruikers", value="ACTIEF"),
                rx.select.item("Inactieve gebruikers", value="INACTIEF"),
                rx.select.item("Alle gebruikers", value="ALLE"),
            ),
            value=UserState.filter_active,
            on_change=UserState.set_filter_active,
            size="2",
            default_value="ACTIEF",
            width=rx.breakpoints(initial="100%", md="auto"),
        ),
        rx.button(
            rx.icon("x", size=14),
            "Reset",
            variant="ghost",
            size="2",
            on_click=UserState.clear_filters,
            width=rx.breakpoints(initial="100%", md="auto"),
        ),
        rx.spacer(display=rx.breakpoints(initial="none", md="block")),
        rx.button(
            rx.icon("user-plus", size=14),
            "Nieuwe Gebruiker",
            size="2",
            on_click=UserState.open_create_dialog,
            width=rx.breakpoints(initial="100%", md="auto"),
        ),
        wrap="wrap",
        gap="2",
        width="100%",
    )


def stat_cards() -> rx.Component:
    """Statistics cards."""
    return rx.grid(
        rx.card(
            rx.hstack(
                rx.icon("users", size=20, color="var(--blue-9)"),
                rx.vstack(
                    rx.text("Actief", size="1", color="gray"),
                    rx.text(UserState.active_count, size="4", weight="bold"),
                    spacing="0",
                    align_items="start",
                ),
                spacing="3",
            ),
            padding="12px",
        ),
        rx.card(
            rx.hstack(
                rx.icon("user-x", size=20, color="var(--gray-9)"),
                rx.vstack(
                    rx.text("Inactief", size="1", color="gray"),
                    rx.text(UserState.inactive_count, size="4", weight="bold"),
                    spacing="0",
                    align_items="start",
                ),
                spacing="3",
            ),
            padding="12px",
        ),
        rx.card(
            rx.hstack(
                rx.icon("shield", size=20, color="var(--red-9)"),
                rx.vstack(
                    rx.text("Superusers", size="1", color="gray"),
                    rx.text(UserState.admin_count, size="4", weight="bold"),
                    spacing="0",
                    align_items="start",
                ),
                spacing="3",
            ),
            padding="12px",
        ),
        columns=rx.breakpoints(initial="1", sm="3"),
        spacing="3",
        width="100%",
    )


def user_form_dialog() -> rx.Component:
    """Dialog for creating/editing a user."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(
                    UserState.is_editing,
                    "Gebruiker Bewerken",
                    "Nieuwe Gebruiker",
                ),
            ),
            rx.dialog.description(
                rx.cond(
                    UserState.is_editing,
                    "Bewerk de gegevens van deze gebruiker.",
                    "Voeg een nieuwe gebruiker toe aan het systeem.",
                ),
                size="2",
                margin_bottom="16px",
            ),

            rx.cond(
                UserState.error != "",
                rx.callout(
                    UserState.error,
                    icon="circle-alert",
                    color="red",
                    margin_bottom="16px",
                ),
            ),

            rx.vstack(
                # Account info section
                rx.text("Accountgegevens", weight="bold", size="3"),

                rx.flex(
                    rx.vstack(
                        rx.text("Gebruikersnaam *", size="2", weight="medium"),
                        rx.input(
                            placeholder="bijv. jdoe",
                            value=UserState.form_username,
                            on_change=UserState.set_form_username,
                            width="100%",
                        ),
                        align_items="start",
                        flex="1",
                        min_width="200px",
                    ),
                    rx.vstack(
                        rx.text("E-mail *", size="2", weight="medium"),
                        rx.input(
                            placeholder="bijv. j.doe@organisatie.nl",
                            value=UserState.form_email,
                            on_change=UserState.set_form_email,
                            width="100%",
                            type="email",
                        ),
                        align_items="start",
                        flex="1",
                        min_width="200px",
                    ),
                    wrap="wrap",
                    gap="3",
                    width="100%",
                ),

                rx.divider(),

                # Personal info section
                rx.text("Persoonsgegevens", weight="bold", size="3"),

                rx.vstack(
                    rx.text("Volledige naam", size="2", weight="medium"),
                    rx.input(
                        placeholder="bijv. Jan Doe",
                        value=UserState.form_full_name,
                        on_change=UserState.set_form_full_name,
                        width="100%",
                    ),
                    align_items="start",
                    width="100%",
                ),

                rx.flex(
                    rx.vstack(
                        rx.text("Afdeling", size="2", weight="medium"),
                        rx.input(
                            placeholder="bijv. ICT",
                            value=UserState.form_department,
                            on_change=UserState.set_form_department,
                            width="100%",
                        ),
                        align_items="start",
                        flex="1",
                        min_width="200px",
                    ),
                    rx.vstack(
                        rx.text("Functie", size="2", weight="medium"),
                        rx.input(
                            placeholder="bijv. Security Officer",
                            value=UserState.form_job_title,
                            on_change=UserState.set_form_job_title,
                            width="100%",
                        ),
                        align_items="start",
                        flex="1",
                        min_width="200px",
                    ),
                    wrap="wrap",
                    gap="3",
                    width="100%",
                ),

                rx.vstack(
                    rx.text("Telefoonnummer", size="2", weight="medium"),
                    rx.input(
                        placeholder="bijv. 06-12345678",
                        value=UserState.form_phone,
                        on_change=UserState.set_form_phone,
                        width="100%",
                        type="tel",
                    ),
                    align_items="start",
                    width="100%",
                ),

                rx.divider(),

                # Preferences section
                rx.text("Voorkeuren", weight="bold", size="3"),

                rx.flex(
                    rx.vstack(
                        rx.text("Thema", size="2", weight="medium"),
                        rx.select.root(
                            rx.select.trigger(placeholder="Selecteer thema"),
                            rx.select.content(
                                rx.select.item("Systeem", value="SYSTEM"),
                                rx.select.item("Licht", value="LIGHT"),
                                rx.select.item("Donker", value="DARK"),
                            ),
                            value=UserState.form_theme,
                            on_change=UserState.set_form_theme,
                        ),
                        align_items="start",
                        flex="1",
                        min_width="200px",
                    ),
                    rx.vstack(
                        rx.text("Taal", size="2", weight="medium"),
                        rx.select.root(
                            rx.select.trigger(placeholder="Selecteer taal"),
                            rx.select.content(
                                rx.select.item("Nederlands", value="NL"),
                                rx.select.item("Engels", value="EN"),
                            ),
                            value=UserState.form_language,
                            on_change=UserState.set_form_language,
                        ),
                        align_items="start",
                        flex="1",
                        min_width="200px",
                    ),
                    wrap="wrap",
                    gap="3",
                    width="100%",
                ),

                rx.divider(),

                # Status section
                rx.text("Status & Rechten", weight="bold", size="3"),

                rx.hstack(
                    rx.checkbox(
                        checked=UserState.form_is_active,
                        on_change=UserState.set_form_is_active,
                    ),
                    rx.vstack(
                        rx.text("Actief", weight="medium"),
                        rx.text("Gebruiker kan inloggen", size="1", color="gray"),
                        spacing="0",
                    ),
                    align_items="center",
                    spacing="2",
                ),

                rx.hstack(
                    rx.checkbox(
                        checked=UserState.form_is_superuser,
                        on_change=UserState.set_form_is_superuser,
                    ),
                    rx.vstack(
                        rx.text("Superuser", weight="medium"),
                        rx.text("Volledige toegang tot alle tenants", size="1", color="gray"),
                        spacing="0",
                    ),
                    align_items="center",
                    spacing="2",
                ),

                spacing="3",
                width="100%",
            ),

            rx.hstack(
                rx.dialog.close(
                    rx.button(
                        "Annuleren",
                        variant="soft",
                        color_scheme="gray",
                        on_click=UserState.close_form_dialog,
                    ),
                ),
                rx.button(
                    rx.cond(UserState.is_editing, "Opslaan", "Aanmaken"),
                    on_click=UserState.save_user,
                ),
                spacing="3",
                justify="end",
                margin_top="16px",
            ),

            max_width=rx.breakpoints(initial="95vw", md="600px"),
        ),
        open=UserState.show_form_dialog,
    )


def scope_role_item(scope_data: dict) -> rx.Component:
    """Display a scope with its assigned roles."""
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text(scope_data["scope"]["name"].to(str), weight="medium", size="2"),
                rx.text(scope_data["scope"]["scope_type"].to(str), size="1", color="gray"),
                align_items="start",
                spacing="0",
            ),
            rx.spacer(),
            rx.hstack(
                rx.foreach(
                    scope_data["roles"].to(list),
                    lambda role: rx.hstack(
                        role_badge(role),
                        rx.icon_button(
                            rx.icon("x", size=10),
                            variant="ghost",
                            size="1",
                            on_click=lambda: UserState.remove_role(scope_data["scope"]["id"], role),
                        ),
                        spacing="1",
                    ),
                ),
                spacing="2",
            ),
            width="100%",
        ),
        padding="8px",
        border_radius="md",
        background="var(--gray-a2)",
        margin_bottom="8px",
    )


def role_assignment_dialog() -> rx.Component:
    """Dialog for managing user's scope roles."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Rollen Beheren"),
            rx.dialog.description(
                rx.hstack(
                    rx.text("Gebruiker: "),
                    rx.text(UserState.role_dialog_user_name, weight="bold"),
                    spacing="1",
                ),
                size="2",
                margin_bottom="16px",
            ),

            rx.cond(
                UserState.error != "",
                rx.callout(
                    UserState.error,
                    icon="circle-alert",
                    color="red",
                    margin_bottom="16px",
                ),
            ),

            rx.cond(
                UserState.success_message != "",
                rx.callout(
                    UserState.success_message,
                    icon="circle-check",
                    color="green",
                    margin_bottom="16px",
                ),
            ),

            rx.vstack(
                # Current roles section
                rx.text("Huidige Rollen", weight="bold", size="3"),

                rx.cond(
                    UserState.selected_user_scopes.length() > 0,
                    rx.box(
                        rx.foreach(UserState.selected_user_scopes, scope_role_item),
                        width="100%",
                        max_height="200px",
                        overflow_y="auto",
                    ),
                    rx.text("Geen rollen toegewezen", size="2", color="gray"),
                ),

                rx.divider(),

                # Add new role section
                rx.text("Nieuwe Rol Toewijzen", weight="bold", size="3"),

                rx.flex(
                    rx.vstack(
                        rx.text("Scope", size="2", weight="medium"),
                        rx.select.root(
                            rx.select.trigger(placeholder="Selecteer scope"),
                            rx.select.content(
                                rx.foreach(
                                    UserState.scopes,
                                    lambda scope: rx.select.item(
                                        scope["name"],
                                        value=scope["id"].to_string(),
                                    ),
                                ),
                            ),
                            value=UserState.form_scope_id,
                            on_change=UserState.set_form_scope_id,
                        ),
                        align_items="start",
                        flex="1",
                        min_width="200px",
                    ),
                    rx.vstack(
                        rx.text("Rol", size="2", weight="medium"),
                        rx.select.root(
                            rx.select.trigger(placeholder="Selecteer rol"),
                            rx.select.content(
                                rx.select.item("Beheerder", value="Beheerder"),
                                rx.select.item("Coördinator", value="Coordinator"),
                                rx.select.item("Eigenaar", value="Eigenaar"),
                                rx.select.item("Medewerker", value="Medewerker"),
                                rx.select.item("Toezichthouder", value="Toezichthouder"),
                            ),
                            value=UserState.form_role,
                            on_change=UserState.set_form_role,
                        ),
                        align_items="start",
                        flex="1",
                        min_width="200px",
                    ),
                    rx.button(
                        rx.icon("plus", size=14),
                        "Toevoegen",
                        size="2",
                        on_click=UserState.assign_role,
                        align_self="end",
                    ),
                    wrap="wrap",
                    gap="3",
                    width="100%",
                    align_items="end",
                ),

                spacing="4",
                width="100%",
            ),

            rx.hstack(
                rx.dialog.close(
                    rx.button(
                        "Sluiten",
                        variant="soft",
                        color_scheme="gray",
                        on_click=UserState.close_role_dialog,
                    ),
                ),
                spacing="3",
                justify="end",
                margin_top="16px",
            ),

            max_width=rx.breakpoints(initial="95vw", md="700px"),
        ),
        open=UserState.show_role_dialog,
    )


def delete_confirm_dialog() -> rx.Component:
    """Dialog for confirming user deactivation."""
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Gebruiker Deactiveren"),
            rx.alert_dialog.description(
                rx.vstack(
                    rx.text("Weet u zeker dat u deze gebruiker wilt deactiveren?"),
                    rx.text(UserState.deleting_user_name, weight="bold", color="red"),
                    rx.text(
                        "De gebruiker kan niet meer inloggen maar gegevens blijven behouden.",
                        size="2",
                        color="gray",
                    ),
                    spacing="2",
                    align_items="start",
                ),
            ),
            rx.hstack(
                rx.alert_dialog.cancel(
                    rx.button(
                        "Annuleren",
                        variant="soft",
                        color_scheme="gray",
                        on_click=UserState.close_delete_dialog,
                    ),
                ),
                rx.alert_dialog.action(
                    rx.button(
                        "Deactiveren",
                        color_scheme="red",
                        on_click=UserState.confirm_delete,
                    ),
                ),
                spacing="3",
                justify="end",
                margin_top="16px",
            ),
        ),
        open=UserState.show_delete_dialog,
    )


def users_content() -> rx.Component:
    """Users page content."""
    return rx.vstack(
        rx.cond(
            UserState.success_message != "",
            rx.callout(
                UserState.success_message,
                icon="circle-check",
                color="green",
                margin_bottom="16px",
            ),
        ),
        rx.cond(
            UserState.error != "",
            rx.callout(
                UserState.error,
                icon="circle-alert",
                color="red",
                margin_bottom="16px",
            ),
        ),

        stat_cards(),
        filter_bar(),

        # Table (desktop)
        rx.box(
            rx.card(
                users_table(),
                padding="0",
            ),
            width="100%",
            margin_top="16px",
            display=rx.breakpoints(initial="none", md="block"),
        ),
        # Mobile cards
        rx.box(
            rx.vstack(
                rx.cond(
                    UserState.is_loading,
                    rx.center(rx.spinner(size="2"), padding="40px"),
                    rx.cond(
                        UserState.users.length() > 0,
                        rx.foreach(UserState.users, user_mobile_card),
                        rx.center(rx.text("Geen gebruikers gevonden", color="gray"), padding="40px"),
                    ),
                ),
                spacing="2",
                width="100%",
            ),
            width="100%",
            margin_top="16px",
            display=rx.breakpoints(initial="block", md="none"),
        ),

        # Dialogs
        user_form_dialog(),
        # role_assignment_dialog(),
        delete_confirm_dialog(),

        width="100%",
        spacing="4",
        on_mount=UserState.load_users,
    )


def users_page() -> rx.Component:
    """Users page with layout."""
    return layout(
        rx.cond(
            AuthState.can_manage_users,
            users_content(),
            rx.callout(
                "Je hebt onvoldoende rechten om deze pagina te bekijken.",
                icon="shield-alert",
                color_scheme="red",
                size="3",
            ),
        ),
        title="Gebruikers",
        subtitle="Beheer gebruikers en roltoewijzingen (RBAC)",
    )
