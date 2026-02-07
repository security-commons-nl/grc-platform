"""
Rapportage Hub — overview of all GRC report data
"""
import reflex as rx
from ims.state.report import ReportState
from ims.components.layout import layout


def kpi_card(label: str, value: rx.Var, icon: str, color: str, subtitle: rx.Var | str = "") -> rx.Component:
    """KPI stat card."""
    return rx.card(
        rx.hstack(
            rx.box(
                rx.icon(icon, size=22, color="white"),
                background=f"var(--{color}-9)",
                padding="10px",
                border_radius="var(--radius-3)",
            ),
            rx.vstack(
                rx.text(label, size="1", color="gray"),
                rx.text(value, size="5", weight="bold"),
                rx.cond(
                    subtitle != "",
                    rx.text(subtitle, size="1", color="gray"),
                ),
                spacing="0",
                align_items="start",
            ),
            spacing="3",
            align="center",
        ),
        padding="16px",
    )


def progress_bar(label: str, value: rx.Var, total: rx.Var, color: str) -> rx.Component:
    """Horizontal progress bar with label."""
    return rx.vstack(
        rx.hstack(
            rx.text(label, size="2"),
            rx.spacer(),
            rx.text(rx.fragment(value, " / ", total), size="2", color="gray"),
            width="100%",
        ),
        rx.progress(value=value, max=total, color_scheme=color, width="100%"),
        spacing="1",
        width="100%",
    )


# ---------------------------------------------------------------------------
# Report sections
# ---------------------------------------------------------------------------

def executive_section() -> rx.Component:
    """Executive KPI overview."""
    return rx.vstack(
        rx.hstack(
            rx.icon("bar-chart-3", size=20),
            rx.text("Executive Overzicht", size="4", weight="bold"),
            spacing="2",
            align="center",
        ),
        rx.grid(
            kpi_card("Risico's", ReportState.total_risks.to(str), "triangle-alert", "blue"),
            kpi_card("Hoog/Kritiek", ReportState.high_critical_risks.to(str), "alert-triangle", "red"),
            kpi_card(
                "Compliance",
                rx.fragment(ReportState.compliance_pct.to(str), "%"),
                "clipboard-check",
                "green",
            ),
            kpi_card("Open Incidenten", ReportState.open_incidents.to(str), "circle-alert", "orange"),
            kpi_card(
                "Beleidsdocumenten",
                ReportState.total_policies.to(str),
                "file-text",
                "indigo",
                rx.fragment(ReportState.published_policies.to(str), " gepubliceerd"),
            ),
            kpi_card(
                "Maatregelen",
                ReportState.active_measures.to(str),
                "shield-check",
                "green",
                rx.fragment("Effectiviteit: ", ReportState.avg_effectiveness.to(str), "%"),
            ),
            columns=rx.breakpoints(initial="1", sm="2", lg="3"),
            spacing="4",
            width="100%",
        ),
        spacing="3",
        width="100%",
    )


def risk_section() -> rx.Component:
    """Risk quadrant breakdown."""
    return rx.vstack(
        rx.hstack(
            rx.icon("triangle-alert", size=20),
            rx.text("Risicoverdeling", size="4", weight="bold"),
            spacing="2",
            align="center",
        ),
        rx.grid(
            rx.card(
                rx.hstack(
                    rx.box(width="12px", height="12px", border_radius="50%", background="var(--red-9)"),
                    rx.text("Mitigate", size="2", weight="medium"),
                    rx.spacer(),
                    rx.text(ReportState.risk_mitigate.to(str), size="4", weight="bold"),
                    align="center", width="100%",
                ),
                padding="14px",
            ),
            rx.card(
                rx.hstack(
                    rx.box(width="12px", height="12px", border_radius="50%", background="var(--blue-9)"),
                    rx.text("Assurance", size="2", weight="medium"),
                    rx.spacer(),
                    rx.text(ReportState.risk_assurance.to(str), size="4", weight="bold"),
                    align="center", width="100%",
                ),
                padding="14px",
            ),
            rx.card(
                rx.hstack(
                    rx.box(width="12px", height="12px", border_radius="50%", background="var(--yellow-9)"),
                    rx.text("Monitor", size="2", weight="medium"),
                    rx.spacer(),
                    rx.text(ReportState.risk_monitor.to(str), size="4", weight="bold"),
                    align="center", width="100%",
                ),
                padding="14px",
            ),
            rx.card(
                rx.hstack(
                    rx.box(width="12px", height="12px", border_radius="50%", background="var(--green-9)"),
                    rx.text("Accept", size="2", weight="medium"),
                    rx.spacer(),
                    rx.text(ReportState.risk_accept.to(str), size="4", weight="bold"),
                    align="center", width="100%",
                ),
                padding="14px",
            ),
            columns=rx.breakpoints(initial="2", md="4"),
            spacing="4",
            width="100%",
        ),
        spacing="3",
        width="100%",
    )


def compliance_section() -> rx.Component:
    """Compliance status."""
    return rx.vstack(
        rx.hstack(
            rx.icon("clipboard-list", size=20),
            rx.text("Compliance Status", size="4", weight="bold"),
            spacing="2",
            align="center",
        ),
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.text("Totaal toepasbaar", size="2"),
                    rx.spacer(),
                    rx.text(ReportState.compliance_applicable.to(str), size="2", weight="bold"),
                    width="100%",
                ),
                progress_bar(
                    "Geimplementeerd",
                    ReportState.compliance_implemented,
                    ReportState.compliance_applicable,
                    "green",
                ),
                progress_bar(
                    "In uitvoering",
                    ReportState.compliance_in_progress,
                    ReportState.compliance_applicable,
                    "blue",
                ),
                rx.hstack(
                    rx.icon("alert-triangle", size=16, color="var(--orange-9)"),
                    rx.text("Niet gestart / gaps: ", size="2"),
                    rx.text(ReportState.compliance_gaps.to(str), size="2", weight="bold", color="var(--orange-9)"),
                    spacing="2",
                    align="center",
                ),
                spacing="3",
                width="100%",
            ),
            padding="20px",
            width="100%",
        ),
        spacing="3",
        width="100%",
    )


def assessments_section() -> rx.Component:
    """Assessments and findings."""
    return rx.vstack(
        rx.hstack(
            rx.icon("clipboard-check", size=20),
            rx.text("Assessments & Bevindingen", size="4", weight="bold"),
            spacing="2",
            align="center",
        ),
        rx.grid(
            kpi_card("Totaal Assessments", ReportState.total_assessments.to(str), "clipboard-check", "indigo"),
            kpi_card("Actief", ReportState.active_assessments.to(str), "play", "blue"),
            kpi_card("Open Bevindingen", ReportState.open_findings.to(str), "search", "orange"),
            columns=rx.breakpoints(initial="1", sm="3"),
            spacing="4",
            width="100%",
        ),
        spacing="3",
        width="100%",
    )


def actions_section() -> rx.Component:
    """Corrective actions summary."""
    return rx.vstack(
        rx.hstack(
            rx.icon("list-checks", size=20),
            rx.text("Verbeteracties", size="4", weight="bold"),
            spacing="2",
            align="center",
        ),
        rx.grid(
            kpi_card("Totaal", ReportState.total_actions.to(str), "list-checks", "blue"),
            kpi_card("Open", ReportState.open_actions.to(str), "clock", "orange"),
            kpi_card("Verlopen", ReportState.overdue_actions.to(str), "alert-triangle", "red"),
            kpi_card(
                "Afgerond",
                rx.fragment(ReportState.completion_rate.to(str), "%"),
                "circle-check",
                "green",
            ),
            columns=rx.breakpoints(initial="2", md="4"),
            spacing="4",
            width="100%",
        ),
        spacing="3",
        width="100%",
    )


# ---------------------------------------------------------------------------
# Main page
# ---------------------------------------------------------------------------

def reports_content() -> rx.Component:
    """Reports hub content."""
    return rx.vstack(
        rx.cond(
            ReportState.error != "",
            rx.callout(
                ReportState.error,
                icon="circle-alert",
                color="red",
                width="100%",
            ),
        ),
        rx.cond(
            ReportState.is_loading,
            rx.center(rx.spinner(size="3"), padding="40px", width="100%"),
            rx.vstack(
                executive_section(),
                rx.divider(),
                risk_section(),
                rx.divider(),
                compliance_section(),
                rx.divider(),
                assessments_section(),
                rx.divider(),
                actions_section(),
                spacing="6",
                width="100%",
            ),
        ),
        rx.hstack(
            rx.button(
                rx.icon("refresh-cw", size=14),
                "Vernieuwen",
                variant="soft",
                size="2",
                on_click=ReportState.load_all,
            ),
            spacing="3",
        ),
        spacing="4",
        width="100%",
        on_mount=ReportState.load_all,
    )


def reports_page() -> rx.Component:
    """Reports page."""
    return layout(
        reports_content(),
        title="Rapportage",
        subtitle="Overzicht van alle GRC-rapportagedata",
    )
