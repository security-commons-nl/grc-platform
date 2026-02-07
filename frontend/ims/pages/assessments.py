"""
Assessments Page - Verification/Audit management
"""
import reflex as rx
from ims.state.assessment import AssessmentState
from ims.components.layout import layout


def type_badge(assessment_type: str) -> rx.Component:
    """Badge for assessment type."""
    return rx.match(
        assessment_type,
        ("DPIA", rx.badge(
            rx.hstack(rx.icon("shield", size=12), rx.text("DPIA"), spacing="1"),
            color_scheme="purple", variant="soft"
        )),
        ("PENTEST", rx.badge(
            rx.hstack(rx.icon("bug", size=12), rx.text("Pentest"), spacing="1"),
            color_scheme="red", variant="soft"
        )),
        ("AUDIT", rx.badge(
            rx.hstack(rx.icon("clipboard-check", size=12), rx.text("Audit"), spacing="1"),
            color_scheme="blue", variant="soft"
        )),
        ("SELF_ASSESSMENT", rx.badge(
            rx.hstack(rx.icon("user-check", size=12), rx.text("Self-Assessment"), spacing="1"),
            color_scheme="green", variant="soft"
        )),
        rx.badge(assessment_type, color_scheme="gray", variant="outline"),
    )


def status_badge(status: str) -> rx.Component:
    """Badge for assessment status."""
    return rx.match(
        status,
        ("DRAFT", rx.badge("Gepland", color_scheme="gray", variant="soft")),
        ("ACTIVE", rx.badge("Actief", color_scheme="blue", variant="soft")),
        ("CLOSED", rx.badge("Afgerond", color_scheme="green", variant="soft")),
        rx.badge(status, color_scheme="gray", variant="outline"),
    )


def assessment_row(assessment: dict) -> rx.Component:
    """Single row in assessments table."""
    return rx.table.row(
        rx.table.cell(
            rx.text(assessment["id"], size="2", color="gray"),
        ),
        rx.table.cell(
            rx.vstack(
                rx.text(assessment["title"], weight="medium", size="2"),
                rx.text(
                    assessment["description"],
                    size="1",
                    color="gray",
                    no_of_lines=1,
                ),
                align_items="start",
                spacing="0",
            ),
        ),
        rx.table.cell(type_badge(assessment["type"])),
        rx.table.cell(status_badge(assessment["status"])),
        rx.table.cell(
            rx.hstack(
                rx.icon_button(
                    rx.icon("eye", size=14),
                    variant="ghost",
                    size="1",
                ),
                rx.icon_button(
                    rx.icon("play", size=14),
                    variant="ghost",
                    size="1",
                ),
                spacing="1",
            ),
        ),
        _hover={"background": "var(--gray-a3)"},
    )


def assessment_mobile_card(assessment: dict) -> rx.Component:
    """Mobile card view for a single assessment."""
    return rx.card(
        rx.vstack(
            rx.text(assessment["title"], weight="medium", size="2"),
            rx.text(assessment["description"], size="1", color="gray", no_of_lines=2),
            rx.hstack(
                type_badge(assessment["type"]),
                status_badge(assessment["status"]),
                spacing="2",
                wrap="wrap",
            ),
            spacing="2",
            width="100%",
        ),
        width="100%",
    )


def assessments_table() -> rx.Component:
    """Assessments data table."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("ID", width="60px"),
                rx.table.column_header_cell("Assessment"),
                rx.table.column_header_cell("Type", width="140px"),
                rx.table.column_header_cell("Status", width="100px"),
                rx.table.column_header_cell("Acties", width="100px"),
            ),
        ),
        rx.table.body(
            rx.cond(
                AssessmentState.is_loading,
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
                    AssessmentState.assessments.length() > 0,
                    rx.foreach(AssessmentState.assessments, assessment_row),
                    rx.table.row(
                        rx.table.cell(
                            rx.center(
                                rx.vstack(
                                    rx.icon("clipboard-check", size=32, color="gray"),
                                    rx.text("Geen assessments gevonden", color="gray"),
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
    """Filter bar for assessments."""
    return rx.flex(
        rx.select.root(
            rx.select.trigger(placeholder="Filter op type"),
            rx.select.content(
                rx.select.item("Alle types", value="ALLE"),
                rx.select.item("DPIA", value="DPIA"),
                rx.select.item("Pentest", value="PENTEST"),
                rx.select.item("Audit", value="AUDIT"),
                rx.select.item("Self-Assessment", value="SELF_ASSESSMENT"),
            ),
            value=AssessmentState.filter_type,
            on_change=AssessmentState.set_filter_type,
            size="2",
            default_value="ALLE",
            width=rx.breakpoints(initial="100%", md="auto"),
        ),
        rx.select.root(
            rx.select.trigger(placeholder="Filter op status"),
            rx.select.content(
                rx.select.item("Alle statussen", value="ALLE"),
                rx.select.item("Gepland", value="DRAFT"),
                rx.select.item("Actief", value="ACTIVE"),
                rx.select.item("Afgerond", value="CLOSED"),
            ),
            value=AssessmentState.filter_status,
            on_change=AssessmentState.set_filter_status,
            size="2",
            default_value="ALLE",
            width=rx.breakpoints(initial="100%", md="auto"),
        ),
        rx.button(
            rx.icon("x", size=14),
            "Reset",
            variant="ghost",
            size="2",
            on_click=AssessmentState.clear_filters,
            width=rx.breakpoints(initial="100%", md="auto"),
        ),
        rx.spacer(display=rx.breakpoints(initial="none", md="block")),
        rx.button(
            rx.icon("plus", size=14),
            "Nieuw Assessment",
            size="2",
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
                rx.icon("circle-play", size=20, color="var(--blue-9)"),
                rx.vstack(
                    rx.text("Actief", size="1", color="gray"),
                    rx.text(AssessmentState.active_count, size="4", weight="bold"),
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
                    rx.text("Afgerond", size="1", color="gray"),
                    rx.text(AssessmentState.completed_count, size="4", weight="bold"),
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


def assessments_content() -> rx.Component:
    """Assessments page content."""
    return rx.vstack(
        rx.cond(
            AssessmentState.error != "",
            rx.callout(
                AssessmentState.error,
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
                assessments_table(),
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
                    AssessmentState.is_loading,
                    rx.center(rx.spinner(size="2"), padding="40px"),
                    rx.cond(
                        AssessmentState.assessments.length() > 0,
                        rx.foreach(AssessmentState.assessments, assessment_mobile_card),
                        rx.center(rx.text("Geen assessments gevonden", color="gray"), padding="40px"),
                    ),
                ),
                spacing="2",
                width="100%",
            ),
            width="100%",
            margin_top="16px",
            display=rx.breakpoints(initial="block", md="none"),
        ),
        width="100%",
        spacing="4",
        on_mount=AssessmentState.load_assessments,
    )


def assessments_page() -> rx.Component:
    """Assessments page with layout."""
    return layout(
        assessments_content(),
        title="Assessments",
        subtitle="DPIA's, Pentests, Audits en Self-Assessments",
    )
