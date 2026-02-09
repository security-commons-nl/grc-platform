"""
MS Hub — PDCA overview page
Shows Context + Plan/Do/Check/Act phase cards with metrics and quick links.
Includes a 7-step journey stepper for onboarding guidance.
"""
import reflex as rx
from ims.state.ms_hub import MsHubState
from ims.state.base import BaseState
from ims.state.journey import JourneyState
from ims.components.layout import layout
from ims.components.guidance import journey_stepper
from ims.state.auth import AuthState


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def metric_row(icon: str, label: str, value: rx.Var, color: str = "gray") -> rx.Component:
    """Single metric line inside a phase card."""
    return rx.hstack(
        rx.icon(icon, size=16, color=f"var(--{color}-9)"),
        rx.text(label, size="2"),
        rx.spacer(),
        rx.text(value, size="2", weight="bold"),
        width="100%",
        align="center",
    )


def quick_link(label: str, href: str) -> rx.Component:
    """Small navigation button inside a phase card."""
    return rx.link(
        rx.button(label, variant="soft", size="1"),
        href=href,
        text_decoration="none",
    )


def status_badge(is_ok: rx.Var) -> rx.Component:
    """Green 'Actief' or orange 'Aandacht nodig' badge."""
    return rx.cond(
        is_ok,
        rx.badge("Actief", color_scheme="green", variant="soft"),
        rx.badge("Aandacht nodig", color_scheme="orange", variant="soft"),
    )


def phase_card(
    icon: str,
    title: str,
    description: str,
    is_ok: rx.Var,
    metrics: list[rx.Component],
    links: list[rx.Component],
    color: str = "blue",
) -> rx.Component:
    """Reusable PDCA phase card."""
    return rx.card(
        rx.vstack(
            # Header
            rx.hstack(
                rx.box(
                    rx.icon(icon, size=20, color="white"),
                    background=f"var(--{color}-9)",
                    padding="8px",
                    border_radius="var(--radius-2)",
                ),
                rx.vstack(
                    rx.text(title, size="3", weight="bold"),
                    rx.text(description, size="1", color="gray"),
                    spacing="0",
                    align_items="start",
                ),
                rx.spacer(),
                status_badge(is_ok),
                width="100%",
                align="center",
            ),
            rx.divider(),
            # Metrics
            *metrics,
            # Quick links
            rx.hstack(
                *links,
                spacing="2",
                flex_wrap="wrap",
            ),
            spacing="3",
            width="100%",
        ),
        padding="20px",
        width="100%",
    )


# ---------------------------------------------------------------------------
# Phase cards
# ---------------------------------------------------------------------------

def context_card() -> rx.Component:
    return phase_card(
        icon="building-2",
        title="Context & Scope",
        description="Organisatiecontext en toepassingsgebied",
        is_ok=MsHubState.context_ok,
        color="slate",
        metrics=[
            metric_row("git-branch", "Scopes", MsHubState.total_scopes.to(str), "blue"),
            metric_row(
                "file-text",
                "Beleid",
                rx.fragment(
                    MsHubState.total_policies.to(str),
                    " (",
                    MsHubState.published_policies.to(str),
                    " gepubliceerd)",
                ),
                "indigo",
            ),
        ],
        links=[
            quick_link("Scopes", "/scopes"),
            quick_link("Beleid", "/policies"),
        ],
    )


def plan_card() -> rx.Component:
    return phase_card(
        icon="target",
        title="PLAN - Voorbereiden",
        description="Risico's identificeren, beleid en compliance inrichten",
        is_ok=MsHubState.plan_ok,
        color="blue",
        metrics=[
            metric_row(
                "triangle-alert",
                "Risico's",
                rx.fragment(
                    MsHubState.total_risks.to(str),
                    " (",
                    MsHubState.high_critical_risks.to(str),
                    " hoog/kritiek)",
                ),
                "red",
            ),
            metric_row(
                "clipboard-check",
                "Compliance",
                rx.fragment(MsHubState.compliance_pct.to(str), "%"),
                "green",
            ),
            metric_row(
                "check-square",
                "Geimplementeerd",
                rx.fragment(
                    MsHubState.compliance_implemented.to(str),
                    " / ",
                    MsHubState.compliance_applicable.to(str),
                ),
                "blue",
            ),
        ],
        links=[
            quick_link("Risico's", "/risks"),
            quick_link("Compliance", "/compliance"),
            quick_link("Risicokader", "/risk-framework"),
            quick_link("Besluiten", "/decisions"),
        ],
    )


def do_card() -> rx.Component:
    return phase_card(
        icon="play",
        title="DO - Uitvoeren",
        description="Controls implementeren en maatregelen activeren",
        is_ok=MsHubState.do_ok,
        color="green",
        metrics=[
            metric_row("shield-check", "Controls", MsHubState.active_controls.to(str), "green"),
            metric_row(
                "book-open",
                "Maatregelen",
                rx.fragment(
                    MsHubState.active_measures.to(str),
                    " actief (eff: ",
                    MsHubState.avg_effectiveness.to(str),
                    "%)",
                ),
                "blue",
            ),
        ],
        links=[
            quick_link("Controls", "/controls"),
            quick_link("Maatregelen", "/measures"),
        ],
    )


def check_card() -> rx.Component:
    return phase_card(
        icon="search",
        title="CHECK - Controleren",
        description="Assessments uitvoeren en bevindingen vastleggen",
        is_ok=MsHubState.check_ok,
        color="orange",
        metrics=[
            metric_row(
                "clipboard-check",
                "Assessments",
                rx.fragment(
                    MsHubState.total_assessments.to(str),
                    " (",
                    MsHubState.active_assessments.to(str),
                    " actief)",
                ),
                "indigo",
            ),
            metric_row("alert-triangle", "Open bevindingen", MsHubState.open_findings.to(str), "orange"),
        ],
        links=[
            quick_link("Assessments", "/assessments"),
            quick_link("In-Control", "/in-control"),
            quick_link("Rapportage", "/reports"),
        ],
    )


def act_card() -> rx.Component:
    return phase_card(
        icon="refresh-cw",
        title="ACT - Verbeteren",
        description="Incidenten afhandelen en verbeteracties uitvoeren",
        is_ok=MsHubState.act_ok,
        color="red",
        metrics=[
            metric_row("circle-alert", "Open incidenten", MsHubState.open_incidents.to(str), "red"),
            metric_row(
                "list-checks",
                "Acties",
                rx.fragment(
                    MsHubState.open_actions.to(str),
                    " open (",
                    MsHubState.overdue_actions.to(str),
                    " verlopen)",
                ),
                "orange",
            ),
            metric_row(
                "circle-check",
                "Afronding",
                rx.fragment(MsHubState.completion_rate.to(str), "%"),
                "green",
            ),
        ],
        links=[
            quick_link("Incidenten", "/incidents"),
            quick_link("Backlog", "/backlog"),
        ],
    )


# ---------------------------------------------------------------------------
# Main page
# ---------------------------------------------------------------------------

def journey_section() -> rx.Component:
    """Collapsible journey stepper with progress header."""
    return rx.card(
        rx.vstack(
            # Header with toggle
            rx.hstack(
                rx.icon("compass", size=20, color="var(--accent-9)"),
                rx.text("Inrichtingspad", size="3", weight="bold"),
                rx.spacer(),
                rx.text(
                    rx.fragment(JourneyState.overall_progress_pct, "%"),
                    size="3",
                    weight="bold",
                    color="var(--accent-9)",
                ),
                rx.icon_button(
                    rx.cond(
                        BaseState.journey_expanded,
                        rx.icon("chevron-up", size=16),
                        rx.icon("chevron-down", size=16),
                    ),
                    variant="ghost",
                    size="1",
                    on_click=BaseState.toggle_journey_expanded,
                ),
                width="100%",
                align="center",
            ),
            # Progress bar (always visible)
            rx.box(
                rx.box(
                    width=rx.cond(
                        JourneyState.overall_progress_pct > 0,
                        JourneyState.overall_progress_pct.to(str) + "%",
                        "0%",
                    ),
                    height="100%",
                    background="var(--accent-9)",
                    border_radius="4px",
                    transition="width 0.5s ease",
                ),
                width="100%",
                height="8px",
                background="var(--gray-a4)",
                border_radius="4px",
                overflow="hidden",
            ),
            # Stepper (collapsible)
            rx.cond(
                BaseState.journey_expanded,
                rx.box(
                    journey_stepper(),
                    width="100%",
                    padding_top="8px",
                ),
            ),
            spacing="3",
            width="100%",
        ),
        padding="20px",
        width="100%",
    )


def ms_hub_content() -> rx.Component:
    """MS Hub content."""
    return rx.vstack(
        # Journey stepper
        journey_section(),
        # Intro callout
        rx.callout(
            rx.text(
                "De MS Hub toont waar je staat in het PDCA-proces. "
                "Elke fase laat de voortgang zien en wijst naar wat aandacht nodig heeft.",
                size="2",
            ),
            icon="info",
            color_scheme="blue",
            width="100%",
        ),
        rx.cond(
            MsHubState.error != "",
            rx.callout(
                MsHubState.error,
                icon="circle-alert",
                color_scheme="red",
                width="100%",
            ),
        ),
        rx.cond(
            MsHubState.is_loading,
            rx.center(rx.spinner(size="3"), padding="40px", width="100%"),
            rx.vstack(
                # Context card — full width
                context_card(),
                # PLAN + DO side by side on desktop
                rx.grid(
                    plan_card(),
                    do_card(),
                    columns=rx.breakpoints(initial="1", md="2"),
                    spacing="4",
                    width="100%",
                ),
                # CHECK + ACT side by side on desktop
                rx.grid(
                    check_card(),
                    act_card(),
                    columns=rx.breakpoints(initial="1", md="2"),
                    spacing="4",
                    width="100%",
                ),
                spacing="4",
                width="100%",
            ),
        ),
        rx.hstack(
            rx.button(
                rx.icon("refresh-cw", size=14),
                "Vernieuwen",
                variant="soft",
                size="2",
                on_click=[MsHubState.load_all, JourneyState.load_journey_data],
            ),
            spacing="3",
        ),
        spacing="4",
        width="100%",
        on_mount=[MsHubState.load_all, JourneyState.load_journey_data],
    )


def _no_access() -> rx.Component:
    """Access denied callout for restricted pages."""
    return rx.center(
        rx.callout(
            "Je hebt onvoldoende rechten om deze pagina te bekijken.",
            icon="shield-alert",
            color_scheme="red",
        ),
        padding="48px",
    )


def ms_hub_page() -> rx.Component:
    """MS Hub page."""
    return layout(
        rx.cond(AuthState.can_discover, ms_hub_content(), _no_access()),
        title="MS Hub",
        subtitle="PDCA-overzicht van je managementsysteem",
    )
