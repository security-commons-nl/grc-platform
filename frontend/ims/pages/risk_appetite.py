"""
Risk Appetite Page — Risicotolerantie
Onder INRICHTEN: organisatie-brede appetite instellen met live heatmap preview.
"""
import reflex as rx
from ims.components.layout import layout
from ims.state.risk_appetite import RiskAppetiteState, APPETITE_LEVELS
from ims.state.auth import AuthState

S = RiskAppetiteState

# Risk level options for threshold dropdowns
RISK_LEVELS = [
    ("Laag", "LOW"),
    ("Midden", "MEDIUM"),
    ("Hoog", "HIGH"),
    ("Kritiek", "CRITICAL"),
]

# Zone colors
ZONE_COLORS = {
    "acceptable": "var(--green-a4)",
    "conditional": "var(--amber-a4)",
    "escalation": "var(--orange-a4)",
    "unacceptable": "var(--red-a4)",
}

ZONE_LABELS = {
    "acceptable": "Acceptabel",
    "conditional": "Voorwaardelijk",
    "escalation": "Escalatie",
    "unacceptable": "Onacceptabel",
}


# =============================================================================
# HELPER: Appetite Select
# =============================================================================

def appetite_select(
    label: str,
    value: rx.Var,
    on_change,
    required: bool = False,
) -> rx.Component:
    options = [] if required else [("— Organisatie-breed —", "")]
    options += APPETITE_LEVELS
    return rx.box(
        rx.text(label, size="2", weight="medium", margin_bottom="4px"),
        rx.select(
            [o[0] for o in options],
            value=rx.cond(
                value == "AVERSE", "Risicomijdend",
                rx.cond(value == "MINIMAL", "Minimaal",
                rx.cond(value == "CAUTIOUS", "Voorzichtig",
                rx.cond(value == "MODERATE", "Gematigd",
                rx.cond(value == "OPEN", "Open",
                rx.cond(value == "HUNGRY", "Risicozoekend",
                    rx.cond(value == "", "— Organisatie-breed —", value)
                )))))
            ),
            on_change=lambda v: on_change(
                rx.cond(v == "Risicomijdend", "AVERSE",
                rx.cond(v == "Minimaal", "MINIMAL",
                rx.cond(v == "Voorzichtig", "CAUTIOUS",
                rx.cond(v == "Gematigd", "MODERATE",
                rx.cond(v == "Open", "OPEN",
                rx.cond(v == "Risicozoekend", "HUNGRY",
                    rx.cond(v == "— Organisatie-breed —", "", v)
                ))))))
            ),
            size="2",
            width="100%",
        ),
        width="100%",
    )


def risk_level_select(
    label: str,
    value: rx.Var,
    on_change,
) -> rx.Component:
    return rx.box(
        rx.text(label, size="2", weight="medium", margin_bottom="4px"),
        rx.select(
            [o[0] for o in RISK_LEVELS],
            value=rx.cond(
                value == "LOW", "Laag",
                rx.cond(value == "MEDIUM", "Midden",
                rx.cond(value == "HIGH", "Hoog",
                rx.cond(value == "CRITICAL", "Kritiek", value)
                ))
            ),
            on_change=lambda v: on_change(
                rx.cond(v == "Laag", "LOW",
                rx.cond(v == "Midden", "MEDIUM",
                rx.cond(v == "Hoog", "HIGH",
                rx.cond(v == "Kritiek", "CRITICAL", v)
                )))
            ),
            size="2",
            width="100%",
        ),
        width="100%",
    )


# =============================================================================
# HEATMAP PREVIEW (4×4)
# =============================================================================

def heatmap_cell(cell: dict) -> rx.Component:
    """Single cell in the 4×4 appetite heatmap."""
    return rx.box(
        rx.text(
            cell["score"],
            size="3",
            weight="bold",
            color="var(--gray-12)",
        ),
        display="flex",
        align_items="center",
        justify_content="center",
        width="100%",
        aspect_ratio="1",
        border_radius="md",
        background=rx.match(
            cell["zone"],
            ("acceptable", "var(--green-a4)"),
            ("conditional", "var(--amber-a4)"),
            ("escalation", "var(--orange-a4)"),
            ("unacceptable", "var(--red-a4)"),
            "var(--gray-a3)",
        ),
        border="1px solid var(--gray-a5)",
    )


def heatmap_row(row: list) -> rx.Component:
    """One row of the heatmap (4 cells)."""
    return rx.hstack(
        rx.foreach(row, heatmap_cell),
        spacing="2",
        width="100%",
    )


def appetite_heatmap() -> rx.Component:
    """4×4 heatmap preview that updates based on appetite level."""
    return rx.box(
        rx.vstack(
            rx.heading("Risicomatrix", size="3"),
            rx.text("Kleuring op basis van risicotolerantie", size="1", color="gray"),

            # Impact labels (top)
            rx.hstack(
                rx.box(width="40px"),  # spacer
                rx.hstack(
                    rx.text("Laag", size="1", color="gray"),
                    rx.spacer(),
                    rx.text("Kritiek", size="1", color="gray"),
                    width="100%",
                ),
                width="100%",
            ),
            rx.text("Impact →", size="1", color="gray", align="center"),

            # Matrix rows (likelihood 4→1, high to low)
            rx.hstack(
                # Y-axis
                rx.box(
                    rx.text(
                        "Kans →",
                        size="1",
                        color="gray",
                        style={"writing-mode": "vertical-rl", "transform": "rotate(180deg)"},
                    ),
                    width="40px",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                ),
                # Grid: rows are likelihood (top=4/critical, bottom=1/low)
                rx.vstack(
                    rx.cond(
                        S.heatmap_matrix.length() > 0,
                        rx.fragment(
                            heatmap_row(S.heatmap_matrix[3]),  # likelihood 4
                            heatmap_row(S.heatmap_matrix[2]),  # likelihood 3
                            heatmap_row(S.heatmap_matrix[1]),  # likelihood 2
                            heatmap_row(S.heatmap_matrix[0]),  # likelihood 1
                        ),
                        rx.text("Geen data", size="2", color="gray"),
                    ),
                    spacing="2",
                    width="100%",
                ),
                width="100%",
            ),

            # Legend
            rx.hstack(
                rx.hstack(
                    rx.box(width="12px", height="12px", background="var(--green-a4)", border_radius="sm"),
                    rx.text("Acceptabel", size="1"),
                    spacing="1",
                ),
                rx.hstack(
                    rx.box(width="12px", height="12px", background="var(--amber-a4)", border_radius="sm"),
                    rx.text("Voorwaardelijk", size="1"),
                    spacing="1",
                ),
                rx.hstack(
                    rx.box(width="12px", height="12px", background="var(--orange-a4)", border_radius="sm"),
                    rx.text("Escalatie", size="1"),
                    spacing="1",
                ),
                rx.hstack(
                    rx.box(width="12px", height="12px", background="var(--red-a4)", border_radius="sm"),
                    rx.text("Onacceptabel", size="1"),
                    spacing="1",
                ),
                spacing="4",
                wrap="wrap",
                margin_top="8px",
            ),

            spacing="2",
            width="100%",
        ),
        padding="20px",
        background="var(--gray-a2)",
        border_radius="lg",
        border="1px solid var(--gray-a5)",
    )


# =============================================================================
# EVALUATION STATS (Tenant-breed)
# =============================================================================

def stat_card(label: str, value: rx.Var, color: str) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text(value, size="6", weight="bold", color=color),
            rx.text(label, size="1", color="gray"),
            align_items="center",
            spacing="1",
        ),
        padding="16px",
        background="var(--gray-a2)",
        border_radius="lg",
        border="1px solid var(--gray-a5)",
        flex="1",
        min_width="100px",
    )


def evaluation_stats() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.heading("Risicotoetsing", size="3"),
            rx.text("Alle risico's getoetst aan huidige appetite", size="1", color="gray"),
            rx.hstack(
                stat_card("Acceptabel", S.eval_acceptable, "var(--green-11)"),
                stat_card("Voorwaardelijk", S.eval_conditional, "var(--amber-11)"),
                stat_card("Escalatie", S.eval_escalation, "var(--orange-11)"),
                stat_card("Onacceptabel", S.eval_unacceptable, "var(--red-11)"),
                stat_card("Niet beoordeeld", S.eval_not_assessed, "var(--gray-11)"),
                spacing="3",
                wrap="wrap",
                width="100%",
            ),
            rx.cond(
                S.eval_decision_count > 0,
                rx.callout(
                    rx.text(
                        rx.text.strong(S.eval_decision_count),
                        " risico('s) vereisen een managementbesluit.",
                    ),
                    icon="alert-triangle",
                    color="orange",
                ),
            ),
            spacing="3",
            width="100%",
        ),
        padding="20px",
        background="var(--gray-a2)",
        border_radius="lg",
        border="1px solid var(--gray-a5)",
    )


# =============================================================================
# CURRENT APPETITE DISPLAY
# =============================================================================

def domain_pill(label: str, value: str) -> rx.Component:
    """Show a domain appetite pill if set."""
    return rx.cond(
        value != "",
        rx.badge(
            rx.text(label + ": ", size="1"),
            rx.text(value, size="1", weight="bold"),
            variant="surface",
            size="1",
        ),
    )


def appetite_display() -> rx.Component:
    """Display current appetite settings."""
    a = S.appetite
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading("Huidige instelling", size="3"),
                    rx.text("Versie ", size="1", color="gray"),
                    align_items="start",
                ),
                rx.spacer(),
                rx.button(
                    rx.icon("pencil", size=14),
                    "Bewerken",
                    on_click=S.open_edit_dialog,
                    variant="outline",
                    size="2",
                ),
                width="100%",
            ),

            # Overall
            rx.hstack(
                rx.text("Algehele risicobereidheid:", size="2", weight="medium"),
                rx.badge(
                    S.appetite_label,
                    size="2",
                    color_scheme="indigo",
                ),
                spacing="2",
            ),

            # Domain pills
            rx.hstack(
                domain_pill("ISMS", a["isms_appetite"].to(str)),
                domain_pill("Privacy", a["pims_appetite"].to(str)),
                domain_pill("BCM", a["bcms_appetite"].to(str)),
                domain_pill("Financieel", a["financial_appetite"].to(str)),
                domain_pill("Reputatie", a["reputational_appetite"].to(str)),
                domain_pill("Compliance", a["compliance_appetite"].to(str)),
                spacing="2",
                wrap="wrap",
            ),

            # Thresholds
            rx.separator(),
            rx.grid(
                rx.box(
                    rx.text("Auto-acceptatie", size="1", color="gray"),
                    rx.text(a["auto_accept_threshold"].to(str), size="2", weight="bold"),
                ),
                rx.box(
                    rx.text("Escalatiedrempel", size="1", color="gray"),
                    rx.text(a["escalation_threshold"].to(str), size="2", weight="bold"),
                ),
                rx.box(
                    rx.text("Max score", size="1", color="gray"),
                    rx.text(a["max_acceptable_risk_score"].to(str), size="2", weight="bold"),
                ),
                rx.box(
                    rx.text("Financieel plafond", size="1", color="gray"),
                    rx.text(a["financial_threshold_value"].to(str), size="2", weight="bold"),
                ),
                columns=rx.breakpoints(initial="2", md="4"),
                spacing="3",
                width="100%",
            ),

            # Statement
            rx.cond(
                a["appetite_statement"].to(str) != "",
                rx.box(
                    rx.text("Appetite statement", size="1", color="gray", margin_bottom="4px"),
                    rx.text(a["appetite_statement"].to(str), size="2"),
                    padding="12px",
                    background="var(--gray-a2)",
                    border_radius="md",
                    width="100%",
                ),
            ),

            spacing="3",
            width="100%",
        ),
        padding="20px",
        background="white",
        border_radius="lg",
        border="1px solid var(--gray-a5)",
    )


# =============================================================================
# FORM DIALOG
# =============================================================================

def appetite_form_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(S.is_editing, "Risicotolerantie bewerken", "Risicotolerantie instellen"),
            ),
            rx.scroll_area(
                rx.vstack(
                    # Overall appetite
                    appetite_select(
                        "Algehele risicobereidheid *",
                        S.form_overall,
                        S.set_form_overall,
                        required=True,
                    ),

                    rx.separator(),
                    rx.text("Domein-specifieke appetite", size="2", weight="bold"),
                    rx.text("Laat leeg om de organisatie-brede instelling te gebruiken.", size="1", color="gray"),

                    rx.grid(
                        appetite_select("ISMS", S.form_isms, S.set_form_isms),
                        appetite_select("Privacy", S.form_pims, S.set_form_pims),
                        appetite_select("BCM", S.form_bcms, S.set_form_bcms),
                        appetite_select("Financieel", S.form_financial, S.set_form_financial),
                        appetite_select("Reputatie", S.form_reputational, S.set_form_reputational),
                        appetite_select("Compliance", S.form_compliance, S.set_form_compliance),
                        columns=rx.breakpoints(initial="1", md="2"),
                        spacing="3",
                        width="100%",
                    ),

                    rx.separator(),
                    rx.text("Drempelwaarden", size="2", weight="bold"),

                    rx.grid(
                        risk_level_select("Auto-acceptatie drempel", S.form_auto_accept, S.set_form_auto_accept),
                        risk_level_select("Escalatiedrempel", S.form_escalation, S.set_form_escalation),
                        rx.box(
                            rx.text("Max acceptabele score (1-16)", size="2", weight="medium", margin_bottom="4px"),
                            rx.input(
                                value=S.form_max_score.to(str),
                                on_change=S.set_form_max_score,
                                type="number",
                                min="1",
                                max="16",
                                size="2",
                                width="100%",
                            ),
                        ),
                        rx.box(
                            rx.text("Financieel plafond (€)", size="2", weight="medium", margin_bottom="4px"),
                            rx.input(
                                value=S.form_financial_threshold.to(str),
                                on_change=S.set_form_financial_threshold,
                                type="number",
                                placeholder="bijv. 50000",
                                size="2",
                                width="100%",
                            ),
                        ),
                        columns=rx.breakpoints(initial="1", md="2"),
                        spacing="3",
                        width="100%",
                    ),

                    rx.separator(),
                    rx.box(
                        rx.text("Appetite statement", size="2", weight="medium", margin_bottom="4px"),
                        rx.text_area(
                            value=S.form_statement,
                            on_change=S.set_form_statement,
                            placeholder="Beschrijf de risicohouding van de organisatie...",
                            rows="3",
                            width="100%",
                        ),
                        width="100%",
                    ),

                    # Error
                    rx.cond(
                        S.error != "",
                        rx.callout(S.error, icon="alert-circle", color="red"),
                    ),

                    spacing="3",
                    width="100%",
                    padding_bottom="16px",
                ),
                max_height="65vh",
            ),
            rx.hstack(
                rx.dialog.close(
                    rx.button("Annuleren", variant="outline", on_click=S.close_form_dialog),
                ),
                rx.spacer(),
                rx.button(
                    rx.cond(S.is_editing, "Opslaan", "Instellen"),
                    on_click=S.save_appetite,
                ),
                width="100%",
                margin_top="12px",
            ),
            max_width="640px",
        ),
        open=S.show_form_dialog,
    )


# =============================================================================
# EMPTY STATE
# =============================================================================

def empty_state() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.icon("gauge", size=48, color="var(--gray-8)"),
            rx.heading("Geen risicotolerantie ingesteld", size="4"),
            rx.text(
                "Stel de risicobereidheid van uw organisatie in om de risicomatrix "
                "dynamisch te kleuren en risico's automatisch te toetsen.",
                size="2",
                color="gray",
                max_width="400px",
                align="center",
            ),
            rx.button(
                rx.icon("plus", size=14),
                "Risicotolerantie instellen",
                on_click=S.open_create_dialog,
                size="3",
            ),
            align_items="center",
            spacing="3",
            padding="60px 20px",
        ),
        width="100%",
        display="flex",
        justify_content="center",
    )


# =============================================================================
# PAGE
# =============================================================================

def risk_appetite_content() -> rx.Component:
    return rx.cond(
        AuthState.can_configure,
        rx.vstack(
            # Status messages
            rx.cond(
                S.success_message != "",
                rx.callout(S.success_message, icon="check", color="green"),
            ),
            rx.cond(
                S.error != "",
                rx.callout(S.error, icon="alert-circle", color="red"),
            ),

            # Loading
            rx.cond(
                S.is_loading,
                rx.center(rx.spinner(size="3"), padding="60px"),
                rx.cond(
                    S.has_appetite,
                    # Has appetite → show dashboard
                    rx.vstack(
                        appetite_display(),
                        rx.grid(
                            appetite_heatmap(),
                            evaluation_stats(),
                            columns=rx.breakpoints(initial="1", lg="2"),
                            spacing="4",
                            width="100%",
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    # No appetite → empty state
                    empty_state(),
                ),
            ),

            # Form dialog (always mounted)
            appetite_form_dialog(),

            spacing="4",
            width="100%",
            on_mount=S.load_appetite,
        ),
        # No access
        rx.callout(
            "Je hebt geen toegang tot deze pagina.",
            icon="lock",
            color="red",
        ),
    )


def risk_appetite_page() -> rx.Component:
    return layout(
        risk_appetite_content(),
        title="Risicotolerantie",
        subtitle="Organisatie-brede risicobereidheid en dynamische matrix",
    )
