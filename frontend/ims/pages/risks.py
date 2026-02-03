"""
Risks List Page
"""
import reflex as rx
from ims.state.risk import RiskState
from ims.components.layout import layout


def risk_row(risk: dict) -> rx.Component:
    """Single row in risks table. Note: risk is a Var when used in foreach."""
    return rx.table.row(
        rx.table.cell(
            rx.text(risk["id"], size="2", color="gray"),
        ),
        rx.table.cell(
            rx.vstack(
                rx.text(risk["title"], weight="medium", size="2"),
                rx.text(
                    risk["description"],
                    size="1",
                    color="gray",
                    no_of_lines=1,
                ),
                align_items="start",
                spacing="0",
            ),
        ),
        rx.table.cell(
            rx.match(
                risk["attention_quadrant"],
                ("MITIGATE", rx.badge(
                    rx.hstack(rx.icon("shield-alert", size=12), rx.text("Mitigeren"), spacing="1"),
                    color_scheme="red", variant="soft"
                )),
                ("ASSURANCE", rx.badge(
                    rx.hstack(rx.icon("shield-check", size=12), rx.text("Zekerheid"), spacing="1"),
                    color_scheme="blue", variant="soft"
                )),
                ("MONITOR", rx.badge(
                    rx.hstack(rx.icon("eye", size=12), rx.text("Monitoren"), spacing="1"),
                    color_scheme="yellow", variant="soft"
                )),
                ("ACCEPT", rx.badge(
                    rx.hstack(rx.icon("circle-check", size=12), rx.text("Accepteren"), spacing="1"),
                    color_scheme="green", variant="soft"
                )),
                rx.badge("Niet ingedeeld", color_scheme="gray", variant="outline"),
            ),
        ),
        rx.table.cell(
            rx.match(
                risk["inherent_impact"],
                ("Low", rx.badge("Low", color_scheme="green", variant="soft")),
                ("Medium", rx.badge("Medium", color_scheme="yellow", variant="soft")),
                ("High", rx.badge("High", color_scheme="orange", variant="soft")),
                ("Critical", rx.badge("Critical", color_scheme="red", variant="soft")),
                rx.badge("N/A", color_scheme="gray", variant="soft"),
            ),
        ),
        rx.table.cell(
            rx.text(risk["inherent_risk_score"], size="2"),
        ),
        rx.table.cell(
            rx.cond(
                risk["risk_accepted"],
                rx.badge("Geaccepteerd", color_scheme="green", variant="soft"),
                rx.badge("Open", color_scheme="gray", variant="outline"),
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
                    rx.icon("pencil", size=14),
                    variant="ghost",
                    size="1",
                ),
                spacing="1",
            ),
        ),
        _hover={"background": "var(--gray-a3)"},
    )


def risks_table() -> rx.Component:
    """Risks data table."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("ID", width="60px"),
                rx.table.column_header_cell("Risico"),
                rx.table.column_header_cell("Kwadrant", width="140px"),
                rx.table.column_header_cell("Impact", width="100px"),
                rx.table.column_header_cell("Score", width="80px"),
                rx.table.column_header_cell("Status", width="120px"),
                rx.table.column_header_cell("Acties", width="100px"),
            ),
        ),
        rx.table.body(
            rx.cond(
                RiskState.is_loading,
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
                    RiskState.risks.length() > 0,
                    rx.foreach(RiskState.risks, risk_row),
                    rx.table.row(
                        rx.table.cell(
                            rx.center(
                                rx.vstack(
                                    rx.icon("inbox", size=32, color="gray"),
                                    rx.text("Geen risico's gevonden", color="gray"),
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
    """Filter bar for risks."""
    return rx.hstack(
        rx.select(
            ["", "MITIGATE", "ASSURANCE", "MONITOR", "ACCEPT"],
            placeholder="Filter op kwadrant",
            value=RiskState.filter_quadrant,
            on_change=RiskState.set_filter_quadrant,
            size="2",
        ),
        rx.button(
            rx.icon("x", size=14),
            "Reset filters",
            variant="ghost",
            size="2",
            on_click=RiskState.clear_filters,
        ),
        rx.spacer(),
        rx.button(
            rx.icon("plus", size=14),
            "Nieuw Risico",
            size="2",
        ),
        width="100%",
        spacing="2",
    )


def risks_content() -> rx.Component:
    """Risks page content."""
    return rx.vstack(
        # Error message
        rx.cond(
            RiskState.error != "",
            rx.callout(
                RiskState.error,
                icon="circle-alert",
                color="red",
                margin_bottom="16px",
            ),
        ),

        # Filter bar
        filter_bar(),

        # Table
        rx.box(
            rx.card(
                risks_table(),
                padding="0",
            ),
            width="100%",
            margin_top="16px",
        ),

        width="100%",
        on_mount=RiskState.load_risks,
    )


def risks_page() -> rx.Component:
    """Risks page with layout."""
    return layout(
        risks_content(),
        title="Risico's",
        subtitle="Beheer en monitor uw risico's",
    )
