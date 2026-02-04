"""
Incidents Page - Incident and data breach management
"""
import reflex as rx
from ims.state.incident import IncidentState
from ims.components.layout import layout


def severity_badge(severity: str) -> rx.Component:
    """Badge for incident severity."""
    return rx.match(
        severity,
        ("LOW", rx.badge("Laag", color_scheme="green", variant="soft")),
        ("MEDIUM", rx.badge("Gemiddeld", color_scheme="yellow", variant="soft")),
        ("HIGH", rx.badge("Hoog", color_scheme="orange", variant="soft")),
        ("CRITICAL", rx.badge("Kritiek", color_scheme="red", variant="soft")),
        rx.badge(severity, color_scheme="gray", variant="outline"),
    )


def status_badge(status: str) -> rx.Component:
    """Badge for incident status."""
    return rx.match(
        status,
        ("DRAFT", rx.badge("Nieuw", color_scheme="gray", variant="soft")),
        ("ACTIVE", rx.badge("In behandeling", color_scheme="blue", variant="soft")),
        ("CLOSED", rx.badge("Opgelost", color_scheme="green", variant="soft")),
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
                rx.icon_button(
                    rx.icon("eye", size=14),
                    variant="ghost",
                    size="1",
                ),
                rx.icon_button(
                    rx.icon("check", size=14),
                    variant="ghost",
                    size="1",
                ),
                spacing="1",
            ),
        ),
        _hover={"background": "var(--gray-a3)"},
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
    return rx.hstack(
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
        ),
        rx.button(
            rx.icon("x", size=14),
            "Reset",
            variant="ghost",
            size="2",
            on_click=IncidentState.clear_filters,
        ),
        rx.spacer(),
        rx.button(
            rx.icon("plus", size=14),
            "Meld Incident",
            size="2",
            color_scheme="red",
        ),
        width="100%",
        spacing="2",
    )


def stat_cards() -> rx.Component:
    """Statistics cards."""
    return rx.hstack(
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


def incidents_content() -> rx.Component:
    """Incidents page content."""
    return rx.vstack(
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
        rx.box(
            rx.card(
                incidents_table(),
                padding="0",
            ),
            width="100%",
            margin_top="16px",
        ),
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
