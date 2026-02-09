"""
Dashboard Page - Main landing page after login
"""
import reflex as rx
from ims.state.auth import AuthState
from ims.state.risk import RiskState
from ims.state.dashboard import DashboardState
from ims.state.journey import JourneyState
from ims.state.organization_profile import OrganizationProfileState
from ims.state.in_control import InControlState
from ims.components.layout import layout
from ims.components.heatmap import risk_heatmap
from ims.components.guidance import pdca_ring_widget


def stat_card(title: str, value: rx.Var, icon: str, color: str) -> rx.Component:
    """Statistics card for dashboard."""
    return rx.card(
        rx.hstack(
            rx.box(
                rx.icon(icon, size=24, color=f"var(--{color}-9)"),
                padding="12px",
                background=f"var(--{color}-a3)",
                border_radius="lg",
            ),
            rx.vstack(
                rx.text(title, size="2", color="gray"),
                rx.text(value, size="5", weight="bold"),
                align_items="start",
                spacing="0",
            ),
            spacing="3",
        ),
        padding="16px",
    )


def _ic_metric_pill(label: str, value: rx.Var, color: str) -> rx.Component:
    """Small inline metric pill for in-control cards."""
    return rx.cond(
        value.to(int) > 0,
        rx.badge(rx.text(rx.fragment(value, " ", label), size="1"), color_scheme=color, variant="outline", size="1"),
        rx.fragment(),
    )


def _ic_scope_card(item: dict) -> rx.Component:
    """Compact scope status card for dashboard."""
    return rx.card(
        rx.hstack(
            rx.vstack(
                rx.text(item["scope_name"], weight="bold", size="2"),
                rx.flex(
                    _ic_metric_pill("risico's", item["open_risks_count"], "blue"),
                    _ic_metric_pill("hoog/kritiek", item["high_risks_count"], "red"),
                    _ic_metric_pill("bevindingen", item["open_findings_count"], "orange"),
                    _ic_metric_pill("verlopen acties", item["overdue_actions_count"], "crimson"),
                    _ic_metric_pill("ongetest", item["missing_controls_count"], "gray"),
                    gap="2", wrap="wrap",
                ),
                spacing="1", align_items="start", flex="1",
            ),
            rx.match(
                item["level"],
                ("In control", rx.badge(
                    rx.hstack(rx.icon("circle-check", size=12), rx.text("In control", size="1"), spacing="1"),
                    color_scheme="green", variant="soft",
                )),
                ("Beperkt in control", rx.badge(
                    rx.hstack(rx.icon("alert-triangle", size=12), rx.text("Beperkt", size="1"), spacing="1"),
                    color_scheme="orange", variant="soft",
                )),
                ("Niet in control", rx.badge(
                    rx.hstack(rx.icon("circle-x", size=12), rx.text("Niet in control", size="1"), spacing="1"),
                    color_scheme="red", variant="soft",
                )),
                rx.badge("Niet beoordeeld", color_scheme="gray", variant="outline", size="1"),
            ),
            width="100%", align="center", spacing="3",
        ),
        padding="12px",
    )


def _in_control_section() -> rx.Component:
    """In-Control status section for the dashboard."""
    return rx.box(
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.icon("gauge", size=20, color="var(--accent-9)"),
                    rx.heading("In-Control Status", size="4"),
                    rx.spacer(),
                    rx.cond(
                        InControlState.not_in_control_count > 0,
                        rx.badge(
                            rx.fragment(InControlState.not_in_control_count, " niet in control"),
                            color_scheme="red", variant="solid",
                        ),
                    ),
                    rx.cond(
                        InControlState.limited_count > 0,
                        rx.badge(
                            rx.fragment(InControlState.limited_count, " beperkt"),
                            color_scheme="orange", variant="soft",
                        ),
                    ),
                    rx.cond(
                        InControlState.in_control_count > 0,
                        rx.badge(
                            rx.fragment(InControlState.in_control_count, " in control"),
                            color_scheme="green", variant="soft",
                        ),
                    ),
                    width="100%", align="center",
                ),
                rx.cond(
                    InControlState.is_loading,
                    rx.center(rx.spinner(size="2"), padding="20px"),
                    rx.cond(
                        InControlState.dashboard_items.length() > 0,
                        rx.vstack(
                            rx.foreach(InControlState.dashboard_items, _ic_scope_card),
                            spacing="2", width="100%",
                        ),
                        rx.center(
                            rx.text("Geen scopes gevonden", size="2", color="gray"),
                            padding="20px",
                        ),
                    ),
                ),
                spacing="3", align_items="stretch",
            ),
            padding="20px",
        ),
        width="100%",
        margin_top="24px",
    )


def dashboard_content() -> rx.Component:
    """Dashboard main content."""
    return rx.vstack(
        # Welcome message
        rx.hstack(
            rx.vstack(
                rx.heading(
                    rx.fragment("Welkom, ", AuthState.user_display_name),
                    size="6",
                ),
                rx.text(
                    "Hier is een overzicht van uw GRC status.",
                    size="2",
                    color="gray",
                ),
                align_items="start",
            ),
            rx.spacer(),
            rx.button(
                rx.icon("refresh-cw", size=16),
                "Vernieuwen",
                variant="soft",
                on_click=RiskState.load_heatmap,
            ),
            width="100%",
            padding_bottom="24px",
        ),

        # Organization profile onboarding nudge
        rx.cond(
            ~OrganizationProfileState.wizard_completed,
            rx.callout(
                rx.hstack(
                    rx.vstack(
                        rx.text("Welkom! Vul je organisatieprofiel in voor betere aanbevelingen van de AI-assistent.", size="2"),
                        spacing="1",
                        align_items="start",
                    ),
                    rx.spacer(),
                    rx.link(
                        rx.button(
                            "Start profiel wizard",
                            rx.icon("arrow-right", size=14),
                            size="2",
                        ),
                        href="/organization",
                    ),
                    width="100%",
                    align="center",
                ),
                icon="landmark",
                color_scheme="blue",
                width="100%",
            ),
        ),

        # PDCA Journey progress widget
        pdca_ring_widget(),

        # ACT-feedbackloop warning (Hiaat 7)
        rx.cond(
            DashboardState.has_act_warnings,
            rx.callout(
                rx.vstack(
                    rx.text("ACT-feedbackloop: openstaande acties vereist", weight="bold"),
                    rx.hstack(
                        rx.cond(
                            DashboardState.blocked_count > 0,
                            rx.badge(
                                rx.fragment(DashboardState.blocked_count, " bevindingen wachten op afronding acties"),
                                color_scheme="orange", variant="soft",
                            ),
                        ),
                        rx.cond(
                            DashboardState.no_action_count > 0,
                            rx.badge(
                                rx.fragment(DashboardState.no_action_count, " bevindingen zonder corrigerende maatregel"),
                                color_scheme="red", variant="soft",
                            ),
                        ),
                        spacing="2", wrap="wrap",
                    ),
                    spacing="2",
                ),
                icon="alert-triangle",
                color_scheme="orange",
                margin_bottom="16px",
            ),
        ),

        # Stats row
        rx.grid(
            stat_card("Totaal Risico's", RiskState.total_risks, "triangle-alert", "orange"),
            stat_card("Te Mitigeren", RiskState.mitigate_risks.length(), "shield-alert", "red"),
            stat_card("Zekerheid", RiskState.assurance_risks.length(), "shield-check", "blue"),
            stat_card("Geaccepteerd", RiskState.accept_risks.length(), "circle-check", "green"),
            columns=rx.breakpoints(initial="1", sm="2", md="4"),
            spacing="4",
            width="100%",
        ),

        # In-Control status per scope
        _in_control_section(),

        # My Tasks section
        rx.cond(
            DashboardState.has_tasks,
            rx.box(
                rx.card(
                    rx.vstack(
                        rx.hstack(
                            rx.icon("list-checks", size=20, color="var(--accent-9)"),
                            rx.heading("Mijn Taken", size="4"),
                            rx.spacer(),
                            rx.cond(
                                DashboardState.tasks_overdue > 0,
                                rx.badge(
                                    rx.fragment(DashboardState.tasks_overdue, " te laat"),
                                    color_scheme="red", variant="solid",
                                ),
                            ),
                            rx.cond(
                                DashboardState.tasks_due_soon > 0,
                                rx.badge(
                                    rx.fragment(DashboardState.tasks_due_soon, " binnenkort"),
                                    color_scheme="orange", variant="soft",
                                ),
                            ),
                            width="100%",
                            align="center",
                        ),
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("Type"),
                                    rx.table.column_header_cell("Titel"),
                                    rx.table.column_header_cell("Status"),
                                    rx.table.column_header_cell("Prioriteit"),
                                ),
                            ),
                            rx.table.body(
                                rx.foreach(
                                    DashboardState.my_tasks,
                                    lambda task: rx.table.row(
                                        rx.table.cell(
                                            rx.badge(
                                                task["type"],
                                                variant="soft",
                                                color_scheme=rx.cond(
                                                    task["type"] == "Approval",
                                                    "purple",
                                                    rx.cond(
                                                        task["type"] == "Corrective Action",
                                                        "red",
                                                        "blue",
                                                    ),
                                                ),
                                                size="1",
                                            ),
                                        ),
                                        rx.table.cell(rx.text(task["title"], size="2")),
                                        rx.table.cell(rx.text(task["status"], size="2", color="gray")),
                                        rx.table.cell(
                                            rx.badge(
                                                task["priority"],
                                                variant="soft",
                                                color_scheme=rx.cond(
                                                    task["priority"] == "High",
                                                    "red",
                                                    rx.cond(
                                                        task["priority"] == "Medium",
                                                        "orange",
                                                        "gray",
                                                    ),
                                                ),
                                                size="1",
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                            width="100%",
                        ),
                        spacing="3",
                        align_items="stretch",
                    ),
                    padding="20px",
                ),
                width="100%",
                margin_top="24px",
            ),
        ),

        # Heatmap
        rx.box(
            rx.card(
                risk_heatmap(),
                padding="20px",
            ),
            width="100%",
            margin_top="24px",
        ),

        # Quick actions
        rx.box(
            rx.card(
                rx.vstack(
                    rx.heading("Snelle Acties", size="4"),
                    rx.flex(
                        rx.button(
                            rx.icon("plus", size=16),
                            "Nieuw Risico",
                            variant="soft",
                            on_click=rx.redirect("/risks"),
                        ),
                        rx.button(
                            rx.icon("clipboard-check", size=16),
                            "Start Assessment",
                            variant="soft",
                            on_click=rx.redirect("/assessments"),
                        ),
                        rx.button(
                            rx.icon("circle-alert", size=16),
                            "Meld Incident",
                            variant="soft",
                            color_scheme="red",
                            on_click=rx.redirect("/incidents"),
                        ),
                        wrap="wrap",
                        gap="2",
                    ),
                    align_items="start",
                    spacing="3",
                ),
                padding="20px",
            ),
            width="100%",
            margin_top="24px",
        ),

        width="100%",
        spacing="0",
        on_mount=[RiskState.load_heatmap, DashboardState.load_dashboard_data, JourneyState.load_journey_data, InControlState.load_dashboard],
    )


def dashboard_page() -> rx.Component:
    """Dashboard page with layout."""
    return layout(
        dashboard_content(),
    )
