"""
Leidse IMS — Overzichtspagina
Professional overview of the integrated management system (ISMS, PIMS, BCMS, AIMS).
"""
import reflex as rx
from ims.state.ms_hub import MsHubState
from ims.components.layout import layout


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ims_kpi_pill(
    icon: str, label: str, value: rx.Var, color: str = "indigo",
) -> rx.Component:
    """Compact KPI card for the overview row."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon(icon, size=16, color=f"var(--{color}-9)"),
                rx.text(label, size="1", color="var(--gray-11)"),
                spacing="1",
                align="center",
            ),
            rx.text(value, size="5", weight="bold", color=f"var(--{color}-11)"),
            spacing="1",
            align_items="start",
        ),
        background="linear-gradient(135deg, var(--gray-1), var(--gray-3))",
        border=f"1px solid var(--{color}-a4)",
        border_radius="var(--radius-3)",
        padding="16px",
        width="100%",
    )


def ms_metric_row(
    icon: str, label: str, value: str, color: str = "gray",
) -> rx.Component:
    """Icon + label + value row inside a management system card."""
    return rx.hstack(
        rx.icon(icon, size=14, color=f"var(--{color}-9)"),
        rx.text(label, size="2", color="var(--gray-11)"),
        rx.spacer(),
        rx.text(value, size="2", weight="bold"),
        width="100%",
        align="center",
    )


def ms_card(
    icon: str,
    title: str,
    description: str,
    accent_color: str,
    status: str,
    status_scheme: str,
    metrics: list[rx.Component],
    route: str,
    button_label: str = "Open dashboard",
) -> rx.Component:
    """Management system card with colored accent bar."""
    return rx.box(
        rx.vstack(
            # Accent bar
            rx.box(
                width="100%",
                height="3px",
                background=f"var(--{accent_color}-9)",
                border_radius="var(--radius-3) var(--radius-3) 0 0",
            ),
            rx.vstack(
                # Header
                rx.hstack(
                    rx.box(
                        rx.icon(icon, size=20, color="white"),
                        background=f"var(--{accent_color}-9)",
                        padding="8px",
                        border_radius="var(--radius-2)",
                    ),
                    rx.vstack(
                        rx.text(title, size="3", weight="bold"),
                        rx.text(description, size="1", color="var(--gray-10)"),
                        spacing="0",
                        align_items="start",
                    ),
                    rx.spacer(),
                    rx.badge(
                        status,
                        color_scheme=status_scheme,
                        variant="soft",
                        size="1",
                    ),
                    width="100%",
                    align="center",
                ),
                rx.divider(),
                # Metrics
                *metrics,
                # Link button
                rx.link(
                    rx.button(
                        button_label,
                        rx.icon("arrow-right", size=14),
                        variant="soft",
                        color_scheme=accent_color,
                        size="1",
                        width="100%",
                        cursor="pointer",
                    ),
                    href=route,
                    width="100%",
                    text_decoration="none",
                ),
                spacing="3",
                width="100%",
                padding="20px",
            ),
            spacing="0",
            width="100%",
        ),
        background="linear-gradient(135deg, var(--gray-1), var(--gray-3))",
        border="1px solid var(--gray-a4)",
        border_radius="var(--radius-3)",
        overflow="hidden",
        width="100%",
    )


# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------

def hero_banner() -> rx.Component:
    """Dark gradient hero with title and subtitle."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("shield-check", size=32, color="var(--indigo-4)"),
                rx.heading(
                    "Het Leidse IMS",
                    size="7",
                    weight="bold",
                    color="white",
                ),
                align="center",
                spacing="3",
            ),
            rx.text(
                "Het Geïntegreerd Managementsysteem — "
                "informatiebeveiliging, privacy, bedrijfscontinuïteit en AI-governance "
                "in één samenhangend raamwerk.",
                size="3",
                color="var(--indigo-4)",
                max_width="720px",
            ),
            spacing="3",
            align_items="start",
            padding="40px 32px",
        ),
        background="linear-gradient(135deg, var(--indigo-9), var(--indigo-11), var(--slate-12))",
        border_radius="var(--radius-3)",
        width="100%",
    )


def kpi_row() -> rx.Component:
    """Five KPI pills in a responsive grid."""
    return rx.grid(
        ims_kpi_pill(
            "clipboard-check", "Compliance",
            rx.fragment(MsHubState.compliance_pct.to(str), "%"),
            "green",
        ),
        ims_kpi_pill(
            "triangle-alert", "Risico's",
            MsHubState.total_risks.to(str),
            "red",
        ),
        ims_kpi_pill(
            "shield-check", "Controls",
            MsHubState.active_controls.to(str),
            "blue",
        ),
        ims_kpi_pill(
            "search", "Bevindingen",
            MsHubState.open_findings.to(str),
            "orange",
        ),
        ims_kpi_pill(
            "circle-alert", "Incidenten",
            MsHubState.open_incidents.to(str),
            "red",
        ),
        columns=rx.breakpoints(initial="2", sm="3", md="5"),
        spacing="3",
        width="100%",
    )


def isms_card() -> rx.Component:
    """ISMS card with live metrics from MsHubState."""
    return ms_card(
        icon="shield",
        title="ISMS",
        description="Informatiebeveiliging — ISO 27001 & BIO 2.0",
        accent_color="indigo",
        status="Actief",
        status_scheme="green",
        metrics=[
            ms_metric_row(
                "clipboard-check", "Compliance",
                MsHubState.compliance_pct.to(str) + "%", "green",
            ),
            ms_metric_row(
                "triangle-alert", "Risico's",
                MsHubState.total_risks.to(str), "red",
            ),
            ms_metric_row(
                "shield-check", "Controls",
                MsHubState.active_controls.to(str), "blue",
            ),
        ],
        route="/isms-dashboard",
        button_label="ISMS Dashboard",
    )


def pims_card() -> rx.Component:
    """PIMS card — privacy management (in development)."""
    return ms_card(
        icon="eye-off",
        title="PIMS",
        description="Privacy — AVG/GDPR & ISO 27701",
        accent_color="violet",
        status="In ontwikkeling",
        status_scheme="violet",
        metrics=[
            ms_metric_row("file-text", "Verwerkingsregister", "—", "violet"),
            ms_metric_row("scan", "DPIA's", "—", "violet"),
            ms_metric_row("users", "Betrokkenenrechten", "—", "violet"),
        ],
        route="/pims-dashboard",
        button_label="PIMS Dashboard",
    )


def bcms_card() -> rx.Component:
    """BCMS card — business continuity (planned)."""
    return ms_card(
        icon="activity",
        title="BCMS",
        description="Bedrijfscontinuïteit — ISO 22301",
        accent_color="amber",
        status="Gepland",
        status_scheme="orange",
        metrics=[
            ms_metric_row("bar-chart-3", "BIA's", "—", "amber"),
            ms_metric_row("file-text", "Continuïteitsplannen", "—", "amber"),
            ms_metric_row("clock", "RTO/RPO-analyse", "—", "amber"),
        ],
        route="/bcms-dashboard",
        button_label="BCMS Dashboard",
    )


def aims_card() -> rx.Component:
    """AIMS card — AI governance (planned)."""
    return ms_card(
        icon="brain",
        title="AIMS",
        description="AI-governance — EU AI Act & ISO 42001",
        accent_color="teal",
        status="Gepland",
        status_scheme="cyan",
        metrics=[
            ms_metric_row("list-checks", "AI-register", "—", "teal"),
            ms_metric_row("scale", "Risicoclassificatie", "—", "teal"),
            ms_metric_row("check-square", "Conformiteitsbeoordeling", "—", "teal"),
        ],
        route="/aims-dashboard",
        button_label="AIMS Dashboard",
    )


def ms_cards_grid() -> rx.Component:
    """2×2 grid of management system cards."""
    return rx.grid(
        isms_card(),
        pims_card(),
        bcms_card(),
        aims_card(),
        columns=rx.breakpoints(initial="1", md="2"),
        spacing="4",
        width="100%",
    )


def integration_callout() -> rx.Component:
    """Card explaining how the four systems integrate."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("link", size=20, color="var(--indigo-9)"),
                rx.text("Geïntegreerde aanpak", size="3", weight="bold"),
                spacing="2",
                align="center",
            ),
            rx.text(
                "Het Leidse IMS combineert vier managementsystemen in één samenhangend "
                "raamwerk. Scopes, risico's, controls en de PDCA-cyclus worden gedeeld "
                "tussen ISMS, PIMS, BCMS en AIMS. Hierdoor worden dubbel werk en "
                "tegenstrijdigheden vermeden, en kan de organisatie efficiënt voldoen "
                "aan meerdere normen tegelijk.",
                size="2",
                color="var(--gray-11)",
                line_height="1.7",
            ),
            rx.grid(
                rx.hstack(
                    rx.icon("git-branch", size=14, color="var(--blue-9)"),
                    rx.text("Gedeelde scopes", size="2"),
                    spacing="2", align="center",
                ),
                rx.hstack(
                    rx.icon("triangle-alert", size=14, color="var(--red-9)"),
                    rx.text("Gedeeld risicomanagement", size="2"),
                    spacing="2", align="center",
                ),
                rx.hstack(
                    rx.icon("shield-check", size=14, color="var(--green-9)"),
                    rx.text("Gedeelde controls", size="2"),
                    spacing="2", align="center",
                ),
                rx.hstack(
                    rx.icon("refresh-cw", size=14, color="var(--orange-9)"),
                    rx.text("Gedeelde PDCA-cyclus", size="2"),
                    spacing="2", align="center",
                ),
                columns=rx.breakpoints(initial="1", sm="2", md="4"),
                spacing="3",
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
        background="linear-gradient(135deg, var(--gray-1), var(--gray-3))",
        border="1px solid var(--gray-a4)",
        border_radius="var(--radius-3)",
        padding="24px",
        width="100%",
    )


def _norm_badge(label: str, color: str) -> rx.Component:
    """Single standard/framework badge."""
    return rx.badge(label, color_scheme=color, variant="outline", size="2")


def standards_section() -> rx.Component:
    """Badges for all applicable standards and frameworks."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("book-open", size=20, color="var(--indigo-9)"),
                rx.text("Normen & Kaders", size="3", weight="bold"),
                spacing="2",
                align="center",
            ),
            # ISMS
            rx.vstack(
                rx.text("ISMS", size="1", weight="bold", color="var(--indigo-9)"),
                rx.flex(
                    _norm_badge("ISO 27001:2022", "indigo"),
                    _norm_badge("BIO 2.0", "indigo"),
                    _norm_badge("NIS2", "indigo"),
                    gap="2",
                    wrap="wrap",
                ),
                spacing="1",
                align_items="start",
            ),
            # PIMS
            rx.vstack(
                rx.text("PIMS", size="1", weight="bold", color="var(--violet-9)"),
                rx.flex(
                    _norm_badge("AVG / GDPR", "violet"),
                    _norm_badge("ISO 27701:2019", "violet"),
                    gap="2",
                    wrap="wrap",
                ),
                spacing="1",
                align_items="start",
            ),
            # BCMS
            rx.vstack(
                rx.text("BCMS", size="1", weight="bold", color="var(--amber-9)"),
                rx.flex(
                    _norm_badge("ISO 22301:2019", "orange"),
                    gap="2",
                    wrap="wrap",
                ),
                spacing="1",
                align_items="start",
            ),
            # AIMS
            rx.vstack(
                rx.text("AIMS", size="1", weight="bold", color="var(--teal-9)"),
                rx.flex(
                    _norm_badge("EU AI Act", "teal"),
                    _norm_badge("ISO 42001:2023", "teal"),
                    gap="2",
                    wrap="wrap",
                ),
                spacing="1",
                align_items="start",
            ),
            spacing="4",
            width="100%",
        ),
        background="linear-gradient(135deg, var(--gray-1), var(--gray-3))",
        border="1px solid var(--gray-a4)",
        border_radius="var(--radius-3)",
        padding="24px",
        width="100%",
    )


def quick_actions() -> rx.Component:
    """Quick-action buttons row."""
    return rx.hstack(
        rx.link(
            rx.button(
                rx.icon("layout-dashboard", size=14),
                "MS Hub",
                variant="soft",
                size="2",
                cursor="pointer",
            ),
            href="/ms-hub",
            text_decoration="none",
        ),
        rx.link(
            rx.button(
                rx.icon("bar-chart-3", size=14),
                "Rapportage",
                variant="soft",
                size="2",
                cursor="pointer",
            ),
            href="/reports",
            text_decoration="none",
        ),
        rx.button(
            rx.icon("refresh-cw", size=14),
            "Vernieuwen",
            variant="soft",
            size="2",
            on_click=MsHubState.load_all,
        ),
        spacing="3",
        flex_wrap="wrap",
    )


# ---------------------------------------------------------------------------
# Main page
# ---------------------------------------------------------------------------

def leidse_ims_content() -> rx.Component:
    """Full Leidse IMS overview content."""
    return rx.vstack(
        hero_banner(),
        # Error callout
        rx.cond(
            MsHubState.error != "",
            rx.callout(
                MsHubState.error,
                icon="circle-alert",
                color_scheme="red",
                width="100%",
            ),
        ),
        # Loading or content
        rx.cond(
            MsHubState.is_loading,
            rx.center(rx.spinner(size="3"), padding="40px", width="100%"),
            rx.vstack(
                kpi_row(),
                ms_cards_grid(),
                integration_callout(),
                standards_section(),
                spacing="5",
                width="100%",
            ),
        ),
        quick_actions(),
        spacing="5",
        width="100%",
        on_mount=MsHubState.load_all,
    )


def leidse_ims_page() -> rx.Component:
    """Leidse IMS - Overzichtspagina."""
    return layout(
        leidse_ims_content(),
        title="Het Leidse IMS",
        subtitle="Integrated Management System",
    )
