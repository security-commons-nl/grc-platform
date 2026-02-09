"""
Tenants Page - Organization management for superusers
"""
import reflex as rx
from ims.state.tenant import TenantState
from ims.state.auth import AuthState
from ims.components.layout import layout


ROLE_COLORS = {
    "OWNER": "purple",
    "ADMIN": "blue",
    "MEMBER": "green",
}

ROLE_LABELS = {
    "OWNER": "Eigenaar",
    "ADMIN": "Beheerder",
    "MEMBER": "Lid",
}


def tenant_role_badge(role: str) -> rx.Component:
    """Badge for TenantRole."""
    return rx.match(
        role,
        ("OWNER", rx.badge("Eigenaar", color_scheme="purple", variant="soft")),
        ("ADMIN", rx.badge("Beheerder", color_scheme="blue", variant="soft")),
        ("MEMBER", rx.badge("Lid", color_scheme="green", variant="soft")),
        rx.badge(role, color_scheme="gray", variant="outline"),
    )


def status_badge(is_active: bool) -> rx.Component:
    return rx.cond(
        is_active,
        rx.badge("Actief", color_scheme="green", variant="soft"),
        rx.badge("Inactief", color_scheme="gray", variant="soft"),
    )


def tenant_row(tenant: dict) -> rx.Component:
    """Single row in tenants table."""
    return rx.table.row(
        rx.table.cell(
            rx.vstack(
                rx.text(tenant["name"], weight="medium", size="2"),
                rx.text(tenant["slug"], size="1", color="gray"),
                align_items="start",
                spacing="0",
            ),
        ),
        rx.table.cell(
            rx.cond(
                tenant["contact_email"] != None,
                rx.text(tenant["contact_email"], size="2"),
                rx.text("-", size="2", color="gray"),
            ),
        ),
        rx.table.cell(
            status_badge(tenant["is_active"]),
        ),
        rx.table.cell(
            rx.hstack(
                rx.icon_button(
                    rx.icon("users", size=14),
                    variant="ghost",
                    size="1",
                    on_click=lambda: TenantState.open_members_dialog(tenant["id"]),
                ),
                rx.icon_button(
                    rx.icon("pencil", size=14),
                    variant="ghost",
                    size="1",
                    on_click=lambda: TenantState.open_edit_dialog(tenant["id"]),
                ),
                rx.icon_button(
                    rx.icon("user-x", size=14),
                    variant="ghost",
                    size="1",
                    color_scheme="orange",
                    on_click=lambda: TenantState.open_delete_dialog(tenant["id"]),
                ),
                spacing="1",
            ),
        ),
        _hover={"background": "var(--gray-a3)"},
    )


def tenant_mobile_card(tenant: dict) -> rx.Component:
    """Mobile card view for a single tenant."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(tenant["name"], weight="medium", size="2"),
                    rx.text(tenant["slug"], size="1", color="gray"),
                    align_items="start",
                    spacing="0",
                    flex="1",
                ),
                rx.hstack(
                    rx.icon_button(
                        rx.icon("users", size=14),
                        variant="ghost",
                        size="1",
                        on_click=lambda: TenantState.open_members_dialog(tenant["id"]),
                    ),
                    rx.icon_button(
                        rx.icon("pencil", size=14),
                        variant="ghost",
                        size="1",
                        on_click=lambda: TenantState.open_edit_dialog(tenant["id"]),
                    ),
                    rx.icon_button(
                        rx.icon("user-x", size=14),
                        variant="ghost",
                        size="1",
                        color_scheme="orange",
                        on_click=lambda: TenantState.open_delete_dialog(tenant["id"]),
                    ),
                    spacing="1",
                ),
                width="100%",
                align="center",
                spacing="2",
            ),
            rx.hstack(
                status_badge(tenant["is_active"]),
                rx.cond(
                    tenant["contact_email"] != None,
                    rx.text(tenant["contact_email"], size="1", color="gray"),
                ),
                spacing="2",
                wrap="wrap",
            ),
            spacing="2",
            width="100%",
        ),
        width="100%",
    )


def tenants_table() -> rx.Component:
    """Tenants data table."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Organisatie"),
                rx.table.column_header_cell("Contact"),
                rx.table.column_header_cell("Status", width="120px"),
                rx.table.column_header_cell("Acties", width="120px"),
            ),
        ),
        rx.table.body(
            rx.cond(
                TenantState.is_loading,
                rx.table.row(
                    rx.table.cell(
                        rx.center(
                            rx.spinner(size="2"),
                            width="100%",
                            padding="40px",
                        ),
                        col_span=4,
                    ),
                ),
                rx.cond(
                    TenantState.tenants.length() > 0,
                    rx.foreach(TenantState.tenants, tenant_row),
                    rx.table.row(
                        rx.table.cell(
                            rx.center(
                                rx.vstack(
                                    rx.icon("building", size=32, color="gray"),
                                    rx.text("Geen organisaties gevonden", color="gray"),
                                    rx.button(
                                        rx.icon("plus", size=14),
                                        "Nieuwe organisatie",
                                        variant="soft",
                                        size="2",
                                        margin_top="8px",
                                        on_click=TenantState.open_create_dialog,
                                    ),
                                    spacing="2",
                                ),
                                width="100%",
                                padding="40px",
                            ),
                            col_span=4,
                        ),
                    ),
                ),
            ),
        ),
        width="100%",
    )


def filter_bar() -> rx.Component:
    return rx.flex(
        rx.select.root(
            rx.select.trigger(placeholder="Filter op status"),
            rx.select.content(
                rx.select.item("Actieve organisaties", value="ACTIEF"),
                rx.select.item("Inactieve organisaties", value="INACTIEF"),
                rx.select.item("Alle organisaties", value="ALLE"),
            ),
            value=TenantState.filter_active,
            on_change=TenantState.set_filter_active,
            size="2",
            default_value="ACTIEF",
            width=rx.breakpoints(initial="100%", md="auto"),
        ),
        rx.button(
            rx.icon("x", size=14),
            "Reset",
            variant="ghost",
            size="2",
            on_click=TenantState.clear_filters,
            width=rx.breakpoints(initial="100%", md="auto"),
        ),
        rx.spacer(display=rx.breakpoints(initial="none", md="block")),
        rx.button(
            rx.icon("building", size=14),
            "Nieuwe Organisatie",
            size="2",
            on_click=TenantState.open_create_dialog,
            width=rx.breakpoints(initial="100%", md="auto"),
        ),
        wrap="wrap",
        gap="2",
        width="100%",
    )


def stat_cards() -> rx.Component:
    return rx.grid(
        rx.card(
            rx.hstack(
                rx.icon("building", size=20, color="var(--blue-9)"),
                rx.vstack(
                    rx.text("Totaal", size="1", color="gray"),
                    rx.text(TenantState.total_count, size="4", weight="bold"),
                    spacing="0",
                    align_items="start",
                ),
                spacing="3",
            ),
            padding="12px",
        ),
        rx.card(
            rx.hstack(
                rx.icon("building", size=20, color="var(--green-9)"),
                rx.vstack(
                    rx.text("Actief", size="1", color="gray"),
                    rx.text(TenantState.active_count, size="4", weight="bold"),
                    spacing="0",
                    align_items="start",
                ),
                spacing="3",
            ),
            padding="12px",
        ),
        rx.card(
            rx.hstack(
                rx.icon("building", size=20, color="var(--gray-9)"),
                rx.vstack(
                    rx.text("Inactief", size="1", color="gray"),
                    rx.text(TenantState.inactive_count, size="4", weight="bold"),
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


def tenant_form_dialog() -> rx.Component:
    """Dialog for creating/editing a tenant."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(
                    TenantState.is_editing,
                    "Organisatie Bewerken",
                    "Nieuwe Organisatie",
                ),
            ),
            rx.dialog.description(
                rx.cond(
                    TenantState.is_editing,
                    "Bewerk de gegevens van deze organisatie.",
                    "Voeg een nieuwe organisatie toe.",
                ),
                size="2",
                margin_bottom="16px",
            ),

            rx.cond(
                TenantState.error != "",
                rx.callout(
                    TenantState.error,
                    icon="circle-alert",
                    color="red",
                    margin_bottom="16px",
                ),
            ),

            rx.vstack(
                rx.vstack(
                    rx.text("Naam *", size="2", weight="medium"),
                    rx.input(
                        placeholder="bijv. Gemeente Amsterdam",
                        value=TenantState.form_name,
                        on_change=TenantState.set_form_name,
                        width="100%",
                    ),
                    align_items="start",
                    width="100%",
                ),

                rx.vstack(
                    rx.text("Slug *", size="2", weight="medium"),
                    rx.input(
                        placeholder="bijv. gemeente-amsterdam",
                        value=TenantState.form_slug,
                        on_change=TenantState.set_form_slug,
                        width="100%",
                    ),
                    rx.text("Wordt automatisch gegenereerd uit de naam", size="1", color="gray"),
                    align_items="start",
                    width="100%",
                ),

                rx.vstack(
                    rx.text("Beschrijving", size="2", weight="medium"),
                    rx.text_area(
                        placeholder="Korte beschrijving van de organisatie",
                        value=TenantState.form_description,
                        on_change=TenantState.set_form_description,
                        width="100%",
                        rows="3",
                    ),
                    align_items="start",
                    width="100%",
                ),

                rx.vstack(
                    rx.text("Contact e-mail", size="2", weight="medium"),
                    rx.input(
                        placeholder="bijv. info@organisatie.nl",
                        value=TenantState.form_contact_email,
                        on_change=TenantState.set_form_contact_email,
                        width="100%",
                        type="email",
                    ),
                    align_items="start",
                    width="100%",
                ),

                rx.hstack(
                    rx.checkbox(
                        checked=TenantState.form_is_active,
                        on_change=TenantState.set_form_is_active,
                    ),
                    rx.vstack(
                        rx.text("Actief", weight="medium"),
                        rx.text("Organisatie is beschikbaar voor gebruik", size="1", color="gray"),
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
                        on_click=TenantState.close_form_dialog,
                    ),
                ),
                rx.button(
                    rx.cond(TenantState.is_editing, "Opslaan", "Aanmaken"),
                    on_click=TenantState.save_tenant,
                ),
                spacing="3",
                justify="end",
                margin_top="16px",
            ),

            max_width=rx.breakpoints(initial="95vw", md="500px"),
        ),
        open=TenantState.show_form_dialog,
    )


def member_row(member: dict) -> rx.Component:
    """Row for a tenant member in the members dialog."""
    return rx.hstack(
        rx.vstack(
            rx.text(
                rx.cond(
                    member["user_id"] != None,
                    member["user_id"].to(str),
                    "-",
                ),
                weight="medium",
                size="2",
            ),
            align_items="start",
            spacing="0",
            flex="1",
        ),
        tenant_role_badge(member["role"]),
        rx.select.root(
            rx.select.trigger(placeholder="Rol"),
            rx.select.content(
                rx.select.item("Eigenaar", value="OWNER"),
                rx.select.item("Beheerder", value="ADMIN"),
                rx.select.item("Lid", value="MEMBER"),
            ),
            value=member["role"],
            on_change=lambda role: TenantState.change_member_role(member["user_id"], role),
            size="1",
        ),
        rx.icon_button(
            rx.icon("x", size=12),
            variant="ghost",
            size="1",
            color_scheme="red",
            on_click=lambda: TenantState.remove_member(member["user_id"]),
        ),
        width="100%",
        padding="8px",
        border_radius="md",
        background="var(--gray-a2)",
        align="center",
        spacing="2",
    )


def members_dialog() -> rx.Component:
    """Dialog for managing tenant members."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Leden Beheren"),
            rx.dialog.description(
                rx.hstack(
                    rx.text("Organisatie: "),
                    rx.text(TenantState.members_tenant_name, weight="bold"),
                    spacing="1",
                ),
                size="2",
                margin_bottom="16px",
            ),

            rx.cond(
                TenantState.error != "",
                rx.callout(
                    TenantState.error,
                    icon="circle-alert",
                    color="red",
                    margin_bottom="16px",
                ),
            ),

            rx.cond(
                TenantState.success_message != "",
                rx.callout(
                    TenantState.success_message,
                    icon="circle-check",
                    color="green",
                    margin_bottom="16px",
                ),
            ),

            rx.vstack(
                rx.text("Huidige Leden", weight="bold", size="3"),

                rx.cond(
                    TenantState.tenant_users.length() > 0,
                    rx.box(
                        rx.vstack(
                            rx.foreach(TenantState.tenant_users, member_row),
                            spacing="2",
                            width="100%",
                        ),
                        width="100%",
                        max_height="250px",
                        overflow_y="auto",
                    ),
                    rx.text("Geen leden", size="2", color="gray"),
                ),

                rx.divider(),

                rx.text("Lid Toevoegen", weight="bold", size="3"),

                rx.cond(
                    TenantState.available_users.length() > 0,
                    rx.hstack(
                        rx.select.root(
                            rx.select.trigger(placeholder="Selecteer gebruiker"),
                            rx.select.content(
                                rx.foreach(
                                    TenantState.available_users,
                                    lambda u: rx.select.item(
                                        rx.cond(
                                            u["full_name"] != None,
                                            u["full_name"],
                                            u["username"],
                                        ),
                                        value=u["id"].to_string(),
                                    ),
                                ),
                            ),
                            on_change=TenantState.add_member,
                            size="2",
                            width="100%",
                        ),
                        width="100%",
                    ),
                    rx.text("Alle gebruikers zijn al lid", size="2", color="gray"),
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
                        on_click=TenantState.close_members_dialog,
                    ),
                ),
                spacing="3",
                justify="end",
                margin_top="16px",
            ),

            max_width=rx.breakpoints(initial="95vw", md="600px"),
        ),
        open=TenantState.show_members_dialog,
    )


def delete_confirm_dialog() -> rx.Component:
    """Dialog for confirming tenant deactivation."""
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Organisatie Deactiveren"),
            rx.alert_dialog.description(
                rx.vstack(
                    rx.text("Weet u zeker dat u deze organisatie wilt deactiveren?"),
                    rx.text(TenantState.deleting_tenant_name, weight="bold", color="red"),
                    rx.text(
                        "De organisatie wordt inactief maar gegevens blijven behouden.",
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
                        on_click=TenantState.close_delete_dialog,
                    ),
                ),
                rx.alert_dialog.action(
                    rx.button(
                        "Deactiveren",
                        color_scheme="red",
                        on_click=TenantState.confirm_delete,
                    ),
                ),
                spacing="3",
                justify="end",
                margin_top="16px",
            ),
        ),
        open=TenantState.show_delete_dialog,
    )


def tenants_content() -> rx.Component:
    """Tenants page content."""
    return rx.vstack(
        rx.cond(
            TenantState.success_message != "",
            rx.callout(
                TenantState.success_message,
                icon="circle-check",
                color="green",
                margin_bottom="16px",
            ),
        ),
        rx.cond(
            TenantState.error != "",
            rx.callout(
                TenantState.error,
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
                tenants_table(),
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
                    TenantState.is_loading,
                    rx.center(rx.spinner(size="2"), padding="40px"),
                    rx.cond(
                        TenantState.tenants.length() > 0,
                        rx.foreach(TenantState.tenants, tenant_mobile_card),
                        rx.center(rx.text("Geen organisaties gevonden", color="gray"), padding="40px"),
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
        tenant_form_dialog(),
        members_dialog(),
        delete_confirm_dialog(),

        width="100%",
        spacing="4",
        on_mount=TenantState.load_tenants,
    )


def tenants_page() -> rx.Component:
    """Tenants page with layout."""
    return layout(
        rx.cond(
            AuthState.is_superuser,
            tenants_content(),
            rx.callout(
                "Je hebt onvoldoende rechten om deze pagina te bekijken.",
                icon="shield-alert",
                color_scheme="red",
                size="3",
            ),
        ),
        title="Organisaties",
        subtitle="Beheer tenants en hun leden (superuser only)",
    )
