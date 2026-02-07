"""
Incidents Page - Incident and data breach management
"""
import reflex as rx
from ims.state.incident import IncidentState
from ims.state.auth import AuthState
from ims.components.layout import layout


def severity_badge(severity: str) -> rx.Component:
    """Badge for incident severity."""
    return rx.match(
        severity,
        ("Low", rx.badge("Laag", color_scheme="green", variant="soft")),
        ("Medium", rx.badge("Gemiddeld", color_scheme="yellow", variant="soft")),
        ("High", rx.badge("Hoog", color_scheme="orange", variant="soft")),
        ("Critical", rx.badge("Kritiek", color_scheme="red", variant="soft")),
        ("Observation", rx.badge("Observatie", color_scheme="gray", variant="soft")),
        rx.badge(severity, color_scheme="gray", variant="outline"),
    )


def status_badge(status: str) -> rx.Component:
    """Badge for incident status."""
    return rx.match(
        status,
        ("Draft", rx.badge("Nieuw", color_scheme="gray", variant="soft")),
        ("Active", rx.badge("In behandeling", color_scheme="blue", variant="soft")),
        ("Deprecated", rx.badge("Vervallen", color_scheme="orange", variant="soft")),
        ("Closed", rx.badge("Opgelost", color_scheme="green", variant="soft")),
        rx.badge(status, color_scheme="gray", variant="outline"),
    )


def incident_row(incident: dict) -> rx.Component:
    """Single row in incidents table."""
    return rx.table.row(
        rx.table.cell(
            rx.text(incident["id"], size="2", color="gray"),
        ),
        rx.table.cell(
            rx.vstack(
                rx.hstack(
                    rx.text(incident["title"], weight="medium", size="2"),
                    rx.cond(
                        incident["is_data_breach"],
                        rx.badge(
                            rx.hstack(rx.icon("triangle-alert", size=10), rx.text("Datalek"), spacing="1"),
                            color_scheme="red",
                            variant="surface",
                            size="1",
                        ),
                    ),
                    spacing="2",
                ),
                rx.text(
                    incident["description"],
                    size="1",
                    color="gray",
                    no_of_lines=1,
                ),
                align_items="start",
                spacing="0",
            ),
        ),
        rx.table.cell(severity_badge(incident["severity"])),
        rx.table.cell(status_badge(incident["status"])),
        rx.table.cell(
            rx.hstack(
                rx.cond(
                    AuthState.can_edit,
                    rx.icon_button(
                        rx.icon("pencil", size=14),
                        variant="ghost",
                        size="1",
                        on_click=lambda: IncidentState.open_edit_dialog(incident["id"]),
                    ),
                ),
                rx.cond(
                    AuthState.can_edit,
                    rx.icon_button(
                        rx.icon("trash-2", size=14),
                        variant="ghost",
                        size="1",
                        color_scheme="red",
                        on_click=lambda: IncidentState.open_delete_dialog(incident["id"]),
                    ),
                ),
                spacing="1",
            ),
        ),
        _hover={"background": "var(--gray-a3)"},
    )


def incident_mobile_card(incident: dict) -> rx.Component:
    """Mobile card view for a single incident."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text(incident["title"], weight="medium", size="2", flex="1"),
                rx.hstack(
                    rx.icon_button(
                        rx.icon("pencil", size=14),
                        variant="ghost",
                        size="1",
                        on_click=lambda: IncidentState.open_edit_dialog(incident["id"]),
                    ),
                    rx.icon_button(
                        rx.icon("trash-2", size=14),
                        variant="ghost",
                        size="1",
                        color_scheme="red",
                        on_click=lambda: IncidentState.open_delete_dialog(incident["id"]),
                    ),
                    spacing="1",
                ),
                width="100%",
                align="center",
            ),
            rx.text(incident["description"], size="1", color="gray", no_of_lines=2),
            rx.hstack(
                severity_badge(incident["severity"]),
                status_badge(incident["status"]),
                rx.cond(
                    incident["is_data_breach"],
                    rx.badge(
                        rx.hstack(rx.icon("triangle-alert", size=10), rx.text("Datalek"), spacing="1"),
                        color_scheme="red",
                        variant="surface",
                        size="1",
                    ),
                ),
                spacing="2",
                wrap="wrap",
            ),
            spacing="2",
            width="100%",
        ),
        width="100%",
    )


def incidents_table() -> rx.Component:
    """Incidents data table."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("ID", width="60px"),
                rx.table.column_header_cell("Incident"),
                rx.table.column_header_cell("Ernst", width="100px"),
                rx.table.column_header_cell("Status", width="120px"),
                rx.table.column_header_cell("Acties", width="100px"),
            ),
        ),
        rx.table.body(
            rx.cond(
                IncidentState.is_loading,
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
                    IncidentState.incidents.length() > 0,
                    rx.foreach(IncidentState.incidents, incident_row),
                    rx.table.row(
                        rx.table.cell(
                            rx.center(
                                rx.vstack(
                                    rx.icon("circle-alert", size=32, color="gray"),
                                    rx.text("Geen incidenten gevonden", color="gray"),
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
    """Filter bar for incidents."""
    return rx.flex(
        rx.select.root(
            rx.select.trigger(placeholder="Filter op status"),
            rx.select.content(
                rx.select.item("Alle statussen", value="ALLE"),
                rx.select.item("Nieuw", value="DRAFT"),
                rx.select.item("In behandeling", value="ACTIVE"),
                rx.select.item("Opgelost", value="CLOSED"),
            ),
            value=IncidentState.filter_status,
            on_change=IncidentState.set_filter_status,
            size="2",
            default_value="ALLE",
            width=rx.breakpoints(initial="100%", md="auto"),
        ),
        rx.select.root(
            rx.select.trigger(placeholder="Datalek"),
            rx.select.content(
                rx.select.item("Alle incidenten", value="ALLE"),
                rx.select.item("Alleen datalekken", value="JA"),
                rx.select.item("Geen datalekken", value="NEE"),
            ),
            value=IncidentState.filter_data_breach,
            on_change=IncidentState.set_filter_data_breach,
            size="2",
            default_value="ALLE",
            width=rx.breakpoints(initial="100%", md="auto"),
        ),
        rx.button(
            rx.icon("x", size=14),
            "Reset",
            variant="ghost",
            size="2",
            on_click=IncidentState.clear_filters,
            width=rx.breakpoints(initial="100%", md="auto"),
        ),
        rx.spacer(display=rx.breakpoints(initial="none", md="block")),
        rx.cond(
            AuthState.can_edit,
            rx.button(
                rx.icon("plus", size=14),
                "Meld Incident",
                size="2",
                color_scheme="red",
                on_click=IncidentState.open_create_dialog,
                width=rx.breakpoints(initial="100%", md="auto"),
            ),
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
                rx.icon("circle-alert", size=20, color="var(--orange-9)"),
                rx.vstack(
                    rx.text("Open", size="1", color="gray"),
                    rx.text(IncidentState.open_count, size="4", weight="bold"),
                    spacing="0",
                    align_items="start",
                ),
                spacing="3",
            ),
            padding="12px",
        ),
        rx.card(
            rx.hstack(
                rx.icon("triangle-alert", size=20, color="var(--red-9)"),
                rx.vstack(
                    rx.text("Datalekken", size="1", color="gray"),
                    rx.text(IncidentState.data_breach_count, size="4", weight="bold"),
                    spacing="0",
                    align_items="start",
                ),
                spacing="3",
            ),
            padding="12px",
        ),
        columns=rx.breakpoints(initial="1", sm="2"),
        spacing="3",
        width="100%",
    )


def data_breach_warning() -> rx.Component:
    """Warning for overdue data breach notifications."""
    return rx.cond(
        IncidentState.overdue_breaches.length() > 0,
        rx.callout(
            rx.vstack(
                rx.text("AVG Melding Vereist!", weight="bold"),
                rx.text(
                    "Er zijn datalekken die binnen 72 uur gemeld moeten worden aan de Autoriteit Persoonsgegevens.",
                    size="2",
                ),
                align_items="start",
                spacing="1",
            ),
            icon="triangle-alert",
            color="red",
            margin_bottom="16px",
        ),
    )


def incident_form_dialog() -> rx.Component:
    """Dialog for creating/editing an incident."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(
                    IncidentState.is_editing,
                    "Incident Bewerken",
                    "Incident Melden",
                ),
            ),
            rx.dialog.description(
                "Rapporteer een nieuw beveiligingsincident of datalek.",
                size="2",
                margin_bottom="16px",
            ),

            rx.cond(
                IncidentState.error != "",
                rx.callout(
                    IncidentState.error,
                    icon="circle-alert",
                    color="red",
                    margin_bottom="16px",
                ),
            ),

            rx.vstack(
                # Basic info
                rx.text("Incident Details", weight="bold", size="3"),

                rx.vstack(
                    rx.text("Titel *", size="2", weight="medium"),
                    rx.input(
                        placeholder="Korte samenvatting van het incident",
                        value=IncidentState.form_title,
                        on_change=IncidentState.set_form_title,
                        width="100%",
                    ),
                    align_items="start",
                    width="100%",
                ),

                rx.vstack(
                    rx.text("Beschrijving *", size="2", weight="medium"),
                    rx.text_area(
                        placeholder="Beschrijf wat er is gebeurd...",
                        value=IncidentState.form_description,
                        on_change=IncidentState.set_form_description,
                        width="100%",
                        rows="4",
                    ),
                    align_items="start",
                    width="100%",
                ),

                rx.flex(
                    rx.vstack(
                        rx.text("Ernst", size="2", weight="medium"),
                        rx.select.root(
                            rx.select.trigger(placeholder="Selecteer ernst"),
                            rx.select.content(
                                rx.select.item("Laag", value="LOW"),
                                rx.select.item("Gemiddeld", value="MEDIUM"),
                                rx.select.item("Hoog", value="HIGH"),
                                rx.select.item("Kritiek", value="CRITICAL"),
                            ),
                            value=IncidentState.form_severity,
                            on_change=IncidentState.set_form_severity,
                        ),
                        align_items="start",
                        flex="1",
                        min_width="200px",
                    ),
                    rx.vstack(
                        rx.text("Status", size="2", weight="medium"),
                        rx.select.root(
                            rx.select.trigger(placeholder="Status"),
                            rx.select.content(
                                rx.select.item("Nieuw", value="DRAFT"),
                                rx.select.item("In behandeling", value="ACTIVE"),
                                rx.select.item("Opgelost", value="CLOSED"),
                            ),
                            value=IncidentState.form_status,
                            on_change=IncidentState.set_form_status,
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

                rx.hstack(
                    rx.checkbox(
                        checked=IncidentState.form_is_data_breach,
                        on_change=IncidentState.set_form_is_data_breach,
                    ),
                    rx.vstack(
                        rx.text("Dit is een datalek (AVG)", weight="medium"),
                        rx.text("Er zijn persoonsgegevens betrokken bij dit incident", size="1", color="gray"),
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
                        on_click=IncidentState.close_form_dialog,
                    ),
                ),
                rx.button(
                    rx.cond(IncidentState.is_editing, "Opslaan", "Melden"),
                    on_click=IncidentState.save_incident,
                    color_scheme="red",
                ),
                spacing="3",
                justify="end",
                margin_top="16px",
            ),

            max_width=rx.breakpoints(initial="95vw", md="600px"),
        ),
        open=IncidentState.show_form_dialog,
    )


def delete_confirm_dialog() -> rx.Component:
    """Dialog for confirming incident deletion."""
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Incident Verwijderen"),
            rx.alert_dialog.description(
                rx.vstack(
                    rx.text("Weet u zeker dat u dit incident wilt verwijderen?"),
                    rx.text(IncidentState.deleting_incident_title, weight="bold", color="red"),
                    rx.text("Deze actie kan niet ongedaan worden gemaakt.", size="2", color="gray"),
                    spacing="2",
                    align_items="start",
                ),
            ),
            rx.hstack(
                rx.alert_dialog.cancel(
                    rx.button("Annuleren", variant="soft", color_scheme="gray", on_click=IncidentState.close_delete_dialog),
                ),
                rx.alert_dialog.action(
                    rx.button("Verwijderen", color_scheme="red", on_click=IncidentState.confirm_delete),
                ),
                spacing="3",
                justify="end",
                margin_top="16px",
            ),
        ),
        open=IncidentState.show_delete_dialog,
    )


def incidents_content() -> rx.Component:
    """Incidents page content."""
    return rx.vstack(
        rx.cond(
            IncidentState.success_message != "",
            rx.callout(
                IncidentState.success_message,
                icon="circle-check",
                color="green",
                margin_bottom="16px",
            ),
        ),
        rx.cond(
            IncidentState.error != "",
            rx.callout(
                IncidentState.error,
                icon="circle-alert",
                color="red",
                margin_bottom="16px",
            ),
        ),
        data_breach_warning(),
        stat_cards(),
        filter_bar(),
        # Table (desktop)
        rx.box(
            rx.card(
                incidents_table(),
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
                    IncidentState.is_loading,
                    rx.center(rx.spinner(size="2"), padding="40px"),
                    rx.cond(
                        IncidentState.incidents.length() > 0,
                        rx.foreach(IncidentState.incidents, incident_mobile_card),
                        rx.center(rx.text("Geen incidenten gevonden", color="gray"), padding="40px"),
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
        incident_form_dialog(),
        delete_confirm_dialog(),
        
        width="100%",
        spacing="4",
        on_mount=IncidentState.load_incidents,
    )


def incidents_page() -> rx.Component:
    """Incidents page with layout."""
    return layout(
        incidents_content(),
        title="Incidenten",
        subtitle="Incidentbeheer en datalekregistratie (AVG)",
    )
