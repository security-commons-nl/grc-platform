"""
Measures Page - Control measures management
"""
import reflex as rx
from ims.state.measure import MeasureState
from ims.components.layout import layout


def status_badge(status: str) -> rx.Component:
    """Badge for measure status."""
    return rx.match(
        status,
        ("DRAFT", rx.badge("Gepland", color_scheme="gray", variant="soft")),
        ("ACTIVE", rx.badge("In uitvoering", color_scheme="blue", variant="soft")),
        ("CLOSED", rx.badge("Geïmplementeerd", color_scheme="green", variant="soft")),
        rx.badge(status, color_scheme="gray", variant="outline"),
    )


def measure_row(measure: dict) -> rx.Component:
    """Single row in measures table."""
    return rx.table.row(
        rx.table.cell(
            rx.text(measure["id"], size="2", color="gray"),
        ),
        rx.table.cell(
            rx.vstack(
                rx.text(measure["title"], weight="medium", size="2"),
                rx.text(
                    measure["description"],
                    size="1",
                    color="gray",
                    no_of_lines=1,
                ),
                align_items="start",
                spacing="0",
            ),
        ),
        rx.table.cell(status_badge(measure["status"])),
        rx.table.cell(
            rx.cond(
                measure["effectiveness_percentage"] != None,
                rx.hstack(
                    rx.text(measure["effectiveness_percentage"], size="2"),
                    rx.text("%", size="2", color="gray"),
                    spacing="0",
                ),
                rx.text("-", size="2", color="gray"),
            ),
        ),
        rx.table.cell(
            rx.hstack(
                rx.icon_button(
                    rx.icon("eye", size=14),
                    variant="ghost",
                    size="1",
                ),
                rx.icon_button(
                    rx.icon("link", size=14),
                    variant="ghost",
                    size="1",
                ),
                spacing="1",
            ),
        ),
        _hover={"background": "var(--gray-a3)"},
    )


def measures_table() -> rx.Component:
    """Measures data table."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("ID", width="60px"),
                rx.table.column_header_cell("Maatregel"),
                rx.table.column_header_cell("Status", width="130px"),
                rx.table.column_header_cell("Effectiviteit", width="120px"),
                rx.table.column_header_cell("Acties", width="100px"),
            ),
        ),
        rx.table.body(
            rx.cond(
                MeasureState.is_loading,
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
                    MeasureState.measures.length() > 0,
                    rx.foreach(MeasureState.measures, measure_row),
                    rx.table.row(
                        rx.table.cell(
                            rx.center(
                                rx.vstack(
                                    rx.icon("shield", size=32, color="gray"),
                                    rx.text("Geen maatregelen gevonden", color="gray"),
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
    """Filter bar for measures."""
    return rx.hstack(
        rx.select.root(
            rx.select.trigger(placeholder="Filter op status"),
            rx.select.content(
                rx.select.item("Alle statussen", value="ALLE"),
                rx.select.item("Gepland", value="DRAFT"),
                rx.select.item("In uitvoering", value="ACTIVE"),
                rx.select.item("Geïmplementeerd", value="CLOSED"),
            ),
            value=MeasureState.filter_status,
            on_change=MeasureState.set_filter_status,
            size="2",
            default_value="ALLE",
        ),
        rx.button(
            rx.icon("x", size=14),
            "Reset",
            variant="ghost",
            size="2",
            on_click=MeasureState.clear_filters,
        ),
        rx.spacer(),
        rx.button(
            rx.icon("plus", size=14),
            "Nieuwe Maatregel",
            size="2",
        ),
        width="100%",
        spacing="2",
    )


def stat_cards() -> rx.Component:
    """Statistics cards."""
    return rx.hstack(
        rx.card(
            rx.hstack(
                rx.icon("clock", size=20, color="var(--blue-9)"),
                rx.vstack(
                    rx.text("In uitvoering", size="1", color="gray"),
                    rx.text(MeasureState.active_count, size="4", weight="bold"),
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
                    rx.text("Geïmplementeerd", size="1", color="gray"),
                    rx.text(MeasureState.implemented_count, size="4", weight="bold"),
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


def measures_content() -> rx.Component:
    """Measures page content."""
    return rx.vstack(
        rx.cond(
            MeasureState.error != "",
            rx.callout(
                MeasureState.error,
                icon="circle-alert",
                color="red",
                margin_bottom="16px",
            ),
        ),
        stat_cards(),
        filter_bar(),
        rx.box(
            rx.card(
                measures_table(),
                padding="0",
            ),
            width="100%",
            margin_top="16px",
        ),
        width="100%",
        spacing="4",
        on_mount=MeasureState.load_measures,
    )


def measures_page() -> rx.Component:
    """Measures page with layout."""
    return layout(
        measures_content(),
        title="Maatregelen",
        subtitle="Beheersmaatregelen en controles",
    )
