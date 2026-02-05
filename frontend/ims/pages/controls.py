"""
Controls Page - Context-specific control implementations
"""
import reflex as rx
from ims.state.control import ControlState
from ims.components.layout import layout


def status_badge(status: str) -> rx.Component:
    """Badge for control status."""
    return rx.match(
        status,
        ("Draft", rx.badge("Concept", color_scheme="gray", variant="soft")),
        ("Active", rx.badge("Actief", color_scheme="blue", variant="soft")),
        ("Deprecated", rx.badge("Vervallen", color_scheme="orange", variant="soft")),
        ("Closed", rx.badge("Afgesloten", color_scheme="green", variant="soft")),
        rx.badge(status, color_scheme="gray", variant="outline"),
    )


def control_type_badge(control_type: str) -> rx.Component:
    """Badge for control type."""
    return rx.match(
        control_type,
        ("Preventive", rx.badge("Preventief", color_scheme="blue", variant="outline", size="1")),
        ("Detective", rx.badge("Detectief", color_scheme="yellow", variant="outline", size="1")),
        ("Corrective", rx.badge("Correctief", color_scheme="orange", variant="outline", size="1")),
        rx.badge("-", color_scheme="gray", variant="outline", size="1"),
    )


def get_scope_name(control, scopes) -> str:
    """Get scope name for a control by looking up scope_id in scopes list."""
    scope_id = control.get("scope_id")
    if not scope_id:
        return "-"
    
    # Find matching scope in scopes list
    for scope in scopes:
        if scope.get("id") == scope_id:
            return scope.get("name", "-")
    
    return "-"


def control_row(control: dict) -> rx.Component:
    """Single row in controls table."""
    return rx.table.row(
        rx.table.cell(
            rx.text(control["id"], size="2", color="gray"),
        ),
        rx.table.cell(
            rx.vstack(
                rx.text(control["title"], weight="medium", size="2"),
                rx.text(
                    control["description"],
                    size="1",
                    color="gray",
                    no_of_lines=1,
                ),
                align_items="start",
                spacing="0",
            ),
        ),
        rx.table.cell(
            rx.text(
                get_scope_name(control, ControlState.scopes),
                size="2",
                color="gray" if not control.get("scope_id") else "default",
            ),
        ),
        rx.table.cell(status_badge(control["status"])),
        rx.table.cell(control_type_badge(control["control_type"])),
        rx.table.cell(
            rx.cond(
                control["effectiveness_percentage"],
                rx.hstack(
                    rx.text(control["effectiveness_percentage"], size="2"),
                    rx.text("%", size="2", color="gray"),
                    spacing="0",
                ),
                rx.text("-", size="2", color="gray"),
            ),
        ),
        rx.table.cell(
            rx.hstack(
                rx.icon_button(
                    rx.icon("pencil", size=14),
                    variant="ghost",
                    size="1",
                    on_click=lambda: ControlState.open_edit_dialog(control["id"]),
                ),
                rx.icon_button(
                    rx.icon("trash-2", size=14),
                    variant="ghost",
                    size="1",
                    color_scheme="red",
                    on_click=lambda: ControlState.open_delete_dialog(control["id"]),
                ),
                spacing="1",
            ),
        ),
        _hover={"background": "var(--gray-a3)"},
    )


def controls_table() -> rx.Component:
    """Controls data table."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("ID", width="60px"),
                rx.table.column_header_cell("Control"),
                rx.table.column_header_cell("Scope / Asset", width="150px"),
                rx.table.column_header_cell("Status", width="120px"),
                rx.table.column_header_cell("Type", width="100px"),
                rx.table.column_header_cell("Effectiviteit", width="100px"),
                rx.table.column_header_cell("Acties", width="100px"),
            ),
        ),
        rx.table.body(
            rx.cond(
                ControlState.is_loading,
                rx.table.row(
                    rx.table.cell(
                        rx.center(
                            rx.spinner(size="2"),
                            width="100%",
                            padding="40px",
                        ),
                        col_span=7,
                    ),
                ),
                rx.cond(
                    ControlState.controls.length() > 0,
                    rx.foreach(ControlState.controls, control_row),
                    rx.table.row(
                        rx.table.cell(
                            rx.center(
                                rx.vstack(
                                    rx.icon("shield-check", size=32, color="gray"),
                                    rx.text("Geen controls gevonden", color="gray"),
                                    spacing="2",
                                ),
                                width="100%",
                                padding="40px",
                            ),
                            col_span=7,
                        ),
                    ),
                ),
            ),
        ),
        width="100%",
    )


def filter_bar() -> rx.Component:
    """Filter bar for controls."""
    return rx.hstack(
        rx.select.root(
            rx.select.trigger(placeholder="Filter op status"),
            rx.select.content(
                rx.select.item("Alle statussen", value="ALLE"),
                rx.select.item("Concept", value="Draft"),
                rx.select.item("Actief", value="Active"),
                rx.select.item("Afgesloten", value="Closed"),
            ),
            value=ControlState.filter_status,
            on_change=ControlState.set_filter_status,
            size="2",
            default_value="ALLE",
        ),
        rx.button(
            rx.icon("x", size=14),
            "Reset",
            variant="ghost",
            size="2",
            on_click=ControlState.clear_filters,
        ),
        rx.spacer(),
        rx.button(
            rx.icon("plus", size=14),
            "Nieuwe Control",
            size="2",
            on_click=ControlState.open_create_dialog,
        ),
        width="100%",
        spacing="2",
    )


def stat_cards() -> rx.Component:
    """Statistics cards."""
    return rx.hstack(
        rx.card(
            rx.hstack(
                rx.icon("file-pen", size=20, color="var(--gray-9)"),
                rx.vstack(
                    rx.text("Concept", size="1", color="gray"),
                    rx.text(ControlState.draft_count, size="4", weight="bold"),
                    spacing="0",
                    align_items="start",
                ),
                spacing="3",
            ),
            padding="12px",
        ),
        rx.card(
            rx.hstack(
                rx.icon("shield-check", size=20, color="var(--blue-9)"),
                rx.vstack(
                    rx.text("Actief", size="1", color="gray"),
                    rx.text(ControlState.active_count, size="4", weight="bold"),
                    spacing="0",
                    align_items="start",
                ),
                spacing="3",
            ),
            padding="12px",
        ),
        rx.card(
            rx.hstack(
                rx.icon("circle-check", size=20, color="var(--green-9)"),
                rx.vstack(
                    rx.text("Afgesloten", size="1", color="gray"),
                    rx.text(ControlState.implemented_count, size="4", weight="bold"),
                    spacing="0",
                    align_items="start",
                ),
                spacing="3",
            ),
            padding="12px",
        ),
        spacing="3",
        width="100%",
    )


def control_form_dialog() -> rx.Component:
    """Dialog for creating/editing a control."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(
                    ControlState.is_editing,
                    "Control Bewerken",
                    "Nieuwe Control",
                ),
            ),
            rx.dialog.description(
                "Beheer context-specifieke control implementaties.",
                size="2",
                margin_bottom="16px",
            ),

            rx.cond(
                ControlState.error != "",
                rx.callout(
                    ControlState.error,
                    icon="circle-alert",
                    color="red",
                    margin_bottom="16px",
                ),
            ),

            rx.vstack(
                # Basic info
                rx.text("Control Details", weight="bold", size="3"),

                rx.vstack(
                    rx.text("Titel *", size="2", weight="medium"),
                    rx.input(
                        placeholder="Bijv. Azure AD MFA voor admins",
                        value=ControlState.form_title,
                        on_change=ControlState.set_form_title,
                        width="100%",
                    ),
                    align_items="start",
                    width="100%",
                ),

                rx.vstack(
                    rx.text("Beschrijving", size="2", weight="medium"),
                    rx.text_area(
                        placeholder="Hoe is deze control geimplementeerd?",
                        value=ControlState.form_description,
                        on_change=ControlState.set_form_description,
                        width="100%",
                        rows="3",
                    ),
                    align_items="start",
                    width="100%",
                ),

                rx.hstack(
                    rx.vstack(
                        rx.text("Status", size="2", weight="medium"),
                        rx.select.root(
                            rx.select.trigger(placeholder="Status"),
                            rx.select.content(
                                rx.select.item("Concept", value="Draft"),
                                rx.select.item("Actief", value="Active"),
                                rx.select.item("Afgesloten", value="Closed"),
                            ),
                            value=ControlState.form_status,
                            on_change=ControlState.set_form_status,
                        ),
                        align_items="start",
                        flex="1",
                    ),
                    rx.vstack(
                        rx.text("Type", size="2", weight="medium"),
                        rx.select.root(
                            rx.select.trigger(placeholder="Type"),
                            rx.select.content(
                                rx.select.item("Preventief", value="Preventive"),
                                rx.select.item("Detectief", value="Detective"),
                                rx.select.item("Correctief", value="Corrective"),
                            ),
                            value=ControlState.form_control_type,
                            on_change=ControlState.set_form_control_type,
                        ),
                        align_items="start",
                        flex="1",
                    ),
                    spacing="3",
                    width="100%",
                ),

                rx.vstack(
                    rx.text("Automatiseringsniveau", size="2", weight="medium"),
                    rx.select.root(
                        rx.select.trigger(placeholder="Niveau"),
                        rx.select.content(
                            rx.select.item("Handmatig", value="Manual"),
                            rx.select.item("Semi-geautomatiseerd", value="Semi-automated"),
                            rx.select.item("Volledig geautomatiseerd", value="Automated"),
                        ),
                        value=ControlState.form_automation_level,
                        on_change=ControlState.set_form_automation_level,
                    ),
                    align_items="start",
                    width="100%",
                ),

                rx.vstack(
                    rx.text("Gekoppeld aan Scope/Asset", size="2", weight="medium"),
                    rx.select.root(
                        rx.select.trigger(placeholder="Selecteer scope of asset..."),
                        rx.select.content(
                            rx.select.item("Geen koppeling", value="0"),
                            rx.foreach(
                                ControlState.scopes,
                                lambda scope: rx.select.item(
                                    scope["name"],
                                    value=scope["id"].to_string(),
                                ),
                            ),
                        ),
                        value=ControlState.form_scope_id,
                        on_change=ControlState.set_form_scope_id,
                    ),
                    align_items="start",
                    width="100%",
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
                        on_click=ControlState.close_form_dialog,
                    ),
                ),
                rx.button(
                    rx.cond(ControlState.is_editing, "Opslaan", "Toevoegen"),
                    on_click=ControlState.save_control,
                ),
                spacing="3",
                justify="end",
                margin_top="16px",
            ),

            max_width="550px",
        ),
        open=ControlState.show_form_dialog,
    )


def delete_confirm_dialog() -> rx.Component:
    """Dialog for confirming control deletion."""
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Control Verwijderen"),
            rx.alert_dialog.description(
                rx.vstack(
                    rx.text("Weet u zeker dat u deze control wilt verwijderen?"),
                    rx.text(ControlState.deleting_control_name, weight="bold", color="red"),
                    rx.text("Deze actie kan niet ongedaan worden gemaakt.", size="2", color="gray"),
                    spacing="2",
                    align_items="start",
                ),
            ),
            rx.hstack(
                rx.alert_dialog.cancel(
                    rx.button("Annuleren", variant="soft", color_scheme="gray", on_click=ControlState.close_delete_dialog),
                ),
                rx.alert_dialog.action(
                    rx.button("Verwijderen", color_scheme="red", on_click=ControlState.confirm_delete),
                ),
                spacing="3",
                justify="end",
                margin_top="16px",
            ),
        ),
        open=ControlState.show_delete_dialog,
    )


def controls_content() -> rx.Component:
    """Controls page content."""
    return rx.vstack(
        rx.cond(
            ControlState.success_message != "",
            rx.callout(
                ControlState.success_message,
                icon="circle-check",
                color="green",
                margin_bottom="16px",
            ),
        ),
        rx.cond(
            ControlState.error != "",
            rx.callout(
                ControlState.error,
                icon="circle-alert",
                color="red",
                margin_bottom="16px",
            ),
        ),
        stat_cards(),
        filter_bar(),
        rx.box(
            rx.card(
                controls_table(),
                padding="0",
            ),
            width="100%",
            margin_top="16px",
        ),

        # Dialogs
        control_form_dialog(),
        delete_confirm_dialog(),

        width="100%",
        spacing="4",
        on_mount=ControlState.load_controls,
    )


def controls_page() -> rx.Component:
    """Controls page with layout."""
    return layout(
        controls_content(),
        title="Controls",
        subtitle="Context-specifieke implementaties van maatregelen",
    )
