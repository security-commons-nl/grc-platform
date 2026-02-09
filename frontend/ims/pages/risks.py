"""
Risks List Page with CRUD functionality
"""
import reflex as rx
from ims.state.risk import RiskState
from ims.state.auth import AuthState
from ims.state.journey import JourneyState
from ims.components.layout import layout
from ims.components.guidance import next_step_hint


# Risk matrix colors based on score (likelihood_idx + impact_idx)
MATRIX_COLORS = {
    0: "#22c55e",  # Green - Very Low
    1: "#84cc16",  # Light Green - Low
    2: "#eab308",  # Yellow - Medium
    3: "#f97316",  # Orange - High
    4: "#ef4444",  # Red - Very High
    5: "#dc2626",  # Dark Red - Critical
    6: "#b91c1c",  # Darker Red - Extreme
}

LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
LEVEL_LABELS = ["Laag", "Gem.", "Hoog", "Krit."]


def get_cell_color(likelihood_idx: int, impact_idx: int) -> str:
    """Get color for a matrix cell based on risk score."""
    score = likelihood_idx + impact_idx
    return MATRIX_COLORS.get(score, "#gray")


LEVEL_LABELS_NL = {
    "LOW": "Laag",
    "MEDIUM": "Gemiddeld",
    "HIGH": "Hoog",
    "CRITICAL": "Kritiek",
}


def risk_matrix_cell(likelihood: str, impact: str, likelihood_idx: int, impact_idx: int) -> rx.Component:
    """Single clickable cell in the risk matrix."""
    color = get_cell_color(likelihood_idx, impact_idx)
    is_selected = (RiskState.form_inherent_likelihood == likelihood) & (RiskState.form_inherent_impact == impact)

    # Create tooltip text
    likelihood_label = LEVEL_LABELS_NL.get(likelihood, likelihood)
    impact_label = LEVEL_LABELS_NL.get(impact, impact)
    tooltip_text = f"Kans: {likelihood_label}, Impact: {impact_label}"

    return rx.tooltip(
        rx.box(
            rx.cond(
                is_selected,
                rx.icon("check", size=14, color="white"),
                rx.text(""),
            ),
            width="32px",
            height="32px",
            background=color,
            border_radius="4px",
            cursor="pointer",
            display="flex",
            align_items="center",
            justify_content="center",
            opacity=rx.cond(is_selected, "1", "0.6"),
            border=rx.cond(is_selected, "2px solid white", "1px solid transparent"),
            _hover={"opacity": "1", "transform": "scale(1.1)"},
            on_click=lambda: RiskState.set_risk_matrix_cell(likelihood, impact),
        ),
        content=tooltip_text,
    )



def selected_risk_display() -> rx.Component:
    """Display selected risk textually."""
    return rx.vstack(
        rx.text("Geselecteerd:", size="2", weight="medium", color="gray"),
        rx.divider(),
        
        # Likelihood display
        rx.box(
            rx.text("Kans (Likelihood)", size="1", color="gray", margin_bottom="2px"),
            rx.match(
                RiskState.form_inherent_likelihood,
                ("LOW", rx.badge("Laag", color_scheme="green", variant="soft", size="2")),
                ("MEDIUM", rx.badge("Gemiddeld", color_scheme="yellow", variant="soft", size="2")),
                ("HIGH", rx.badge("Hoog", color_scheme="orange", variant="soft", size="2")),
                ("CRITICAL", rx.badge("Kritiek", color_scheme="red", variant="soft", size="2")),
                rx.text(RiskState.form_inherent_likelihood)
            ),
            width="100%",
        ),
        
        # Impact display
        rx.box(
            rx.text("Impact", size="1", color="gray", margin_bottom="2px"),
            rx.match(
                RiskState.form_inherent_impact,
                ("LOW", rx.badge("Laag", color_scheme="green", variant="soft", size="2")),
                ("MEDIUM", rx.badge("Gemiddeld", color_scheme="yellow", variant="soft", size="2")),
                ("HIGH", rx.badge("Hoog", color_scheme="orange", variant="soft", size="2")),
                ("CRITICAL", rx.badge("Kritiek", color_scheme="red", variant="soft", size="2")),
                rx.text(RiskState.form_inherent_impact)
            ),
            width="100%",
        ),
        
        spacing="3",
        width="200px",  # Fixed width for the side panel
        padding="8px",
    )


def risk_matrix() -> rx.Component:
    """Clickable 4x4 risk matrix for selecting likelihood and impact."""
    return rx.vstack(
        rx.hstack(
            rx.text("Risicomatrix", size="2", weight="medium"),
            rx.tooltip(
                rx.icon("info", size=14, color="gray"),
                content="Klik in de matrix om de kans en impact van het risico te bepalen.",
            ),
            spacing="1",
            align="center",
        ),
        rx.text("Klik op een cel om kans en impact te selecteren", size="1", color="gray"),
        rx.hstack(
            # Y-axis label
            rx.vstack(
                rx.text("Kans", size="1", color="gray", style={"writing_mode": "vertical-rl", "transform": "rotate(180deg)"}),
                height="100%",
                justify="center",
                padding_right="4px",
            ),
            # Matrix grid
            rx.vstack(
                # Row 4 (CRITICAL likelihood) - top row
                rx.hstack(
                    rx.text("K", size="1", color="gray", width="24px"),
                    risk_matrix_cell("CRITICAL", "LOW", 3, 0),
                    risk_matrix_cell("CRITICAL", "MEDIUM", 3, 1),
                    risk_matrix_cell("CRITICAL", "HIGH", 3, 2),
                    risk_matrix_cell("CRITICAL", "CRITICAL", 3, 3),
                    spacing="1",
                ),
                # Row 3 (HIGH likelihood)
                rx.hstack(
                    rx.text("H", size="1", color="gray", width="24px"),
                    risk_matrix_cell("HIGH", "LOW", 2, 0),
                    risk_matrix_cell("HIGH", "MEDIUM", 2, 1),
                    risk_matrix_cell("HIGH", "HIGH", 2, 2),
                    risk_matrix_cell("HIGH", "CRITICAL", 2, 3),
                    spacing="1",
                ),
                # Row 2 (MEDIUM likelihood)
                rx.hstack(
                    rx.text("G", size="1", color="gray", width="24px"),
                    risk_matrix_cell("MEDIUM", "LOW", 1, 0),
                    risk_matrix_cell("MEDIUM", "MEDIUM", 1, 1),
                    risk_matrix_cell("MEDIUM", "HIGH", 1, 2),
                    risk_matrix_cell("MEDIUM", "CRITICAL", 1, 3),
                    spacing="1",
                ),
                # Row 1 (LOW likelihood) - bottom row
                rx.hstack(
                    rx.text("L", size="1", color="gray", width="24px"),
                    risk_matrix_cell("LOW", "LOW", 0, 0),
                    risk_matrix_cell("LOW", "MEDIUM", 0, 1),
                    risk_matrix_cell("LOW", "HIGH", 0, 2),
                    risk_matrix_cell("LOW", "CRITICAL", 0, 3),
                    spacing="1",
                ),
                # X-axis labels
                rx.hstack(
                    rx.text("", width="24px"),
                    rx.text("L", size="1", color="gray", width="32px", text_align="center"),
                    rx.text("G", size="1", color="gray", width="32px", text_align="center"),
                    rx.text("H", size="1", color="gray", width="32px", text_align="center"),
                    rx.text("K", size="1", color="gray", width="32px", text_align="center"),
                    spacing="1",
                ),
                rx.text("Impact", size="1", color="gray", text_align="center", width="100%"),
                spacing="1",
            ),
            spacing="1",
            align="start",
        ),
        spacing="2",
        padding="8px",
        background="var(--gray-a2)",
        border_radius="8px",
        width="100%", # Make it take available width in its container
    )


def risk_form_dialog() -> rx.Component:
    """Dialog for creating/editing a risk."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(
                    RiskState.is_editing,
                    "Risico Bewerken",
                    "Nieuw Risico",
                ),
            ),
            rx.dialog.description(
                rx.cond(
                    RiskState.is_editing,
                    "Bewerk de gegevens van dit risico.",
                    "Voeg een nieuw risico toe aan het register.",
                ),
                size="2",
                margin_bottom="16px",
            ),

            # Error message in dialog
            rx.cond(
                RiskState.error != "",
                rx.callout(
                    RiskState.error,
                    icon="circle-alert",
                    color="red",
                    margin_bottom="16px",
                ),
            ),

            # Form fields
            rx.vstack(
                # Title
                rx.vstack(
                    rx.hstack(
                        rx.text("Titel *", size="2", weight="medium"),
                        rx.tooltip(
                            rx.icon("info", size=14, color="gray"),
                            content="[Tooltip tekst voor Titel]",
                        ),
                        spacing="1",
                        align="center",
                    ),
                    rx.input(
                        placeholder="Bijv. Ransomware aanval",
                        value=RiskState.form_title,
                        on_change=RiskState.set_form_title,
                        width="100%",
                    ),
                    align_items="start",
                    width="100%",
                ),

                # Description
                rx.vstack(
                    rx.hstack(
                        rx.text("Beschrijving", size="2", weight="medium"),
                        rx.tooltip(
                            rx.icon("info", size=14, color="gray"),
                            content="[Tooltip tekst voor Beschrijving]",
                        ),
                        spacing="1",
                        align="center",
                    ),
                    rx.text_area(
                        placeholder="Beschrijf het risico...",
                        value=RiskState.form_description,
                        on_change=RiskState.set_form_description,
                        width="100%",
                        rows="3",
                    ),
                    align_items="start",
                    width="100%",
                ),

                # Risk Matrix and Selection Display (responsive)
                rx.flex(
                    rx.box(risk_matrix(), flex="1", min_width="220px"),
                    rx.box(selected_risk_display(), min_width="150px"),
                    wrap="wrap",
                    gap="4",
                    width="100%",
                    align_items="start",
                ),

                # Quadrant
                rx.vstack(
                    rx.hstack(
                        rx.text("Behandeling", size="2", weight="medium"),
                        rx.tooltip(
                            rx.icon("info", size=14, color="gray"),
                            content="[Tooltip tekst voor Behandeling]",
                        ),
                        spacing="1",
                        align="center",
                    ),
                    rx.select.root(
                        rx.select.trigger(placeholder="Selecteer behandeling"),
                        rx.select.content(
                            rx.select.item("Geen", value="NONE"),
                            rx.select.item("Mitigeren", value="MITIGATE"),
                            rx.select.item("Zekerheid", value="ASSURANCE"),
                            rx.select.item("Monitoren", value="MONITOR"),
                            rx.select.item("Accepteren", value="ACCEPT"),
                        ),
                        value=RiskState.form_attention_quadrant,
                        on_change=RiskState.set_form_attention_quadrant,
                    ),
                    align_items="start",
                    width="100%",
                ),



                # Treatment justification
                rx.vstack(
                    rx.hstack(
                        rx.text("Behandeling: onderbouwing", size="2", weight="medium"),
                        rx.tooltip(
                            rx.icon("info", size=14, color="gray"),
                            content="[Tooltip tekst voor Onderbouwing]",
                        ),
                        spacing="1",
                        align="center",
                    ),
                    rx.text_area(
                        placeholder="Waarom deze behandeling?",
                        value=RiskState.form_treatment_justification,
                        on_change=RiskState.set_form_treatment_justification,
                        width="100%",
                        rows="2",
                    ),
                    align_items="start",
                    width="100%",
                ),

                # Linked Controls Section
                rx.vstack(
                    rx.divider(),
                    rx.text("Gekoppelde Controls", size="2", weight="medium"),

                    # List of linked controls
                    rx.cond(
                        RiskState.linked_controls.length() > 0,
                        rx.vstack(
                            rx.foreach(
                                RiskState.linked_controls,
                                lambda control: rx.hstack(
                                    rx.icon("shield-check", size=16, color="green"),
                                    rx.text(control["title"], size="2", flex="1"),
                                    rx.icon_button(
                                        rx.icon("x", size=14),
                                        variant="ghost",
                                        size="1",
                                        color_scheme="red",
                                        on_click=lambda: RiskState.unlink_control(control["id"]),
                                    ),
                                    width="100%",
                                    align_items="center",
                                    padding="4px 8px",
                                    background="var(--gray-a2)",
                                    border_radius="4px",
                                ),
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        rx.text("Nog geen controls gekoppeld.", size="1", color="gray", font_style="italic"),
                    ),

                    # Add new link
                    rx.hstack(
                        rx.select.root(
                            rx.select.trigger(placeholder="Selecteer control om te koppelen..."),
                            rx.select.content(
                                rx.foreach(
                                    RiskState.all_controls,
                                    lambda c: rx.select.item(c["title"], value=c["id"].to_string()),
                                ),
                            ),
                            value=RiskState.selected_control_id_to_link,
                            on_change=RiskState.set_selected_control_id_to_link,
                            width="100%",
                        ),
                        rx.button(
                            "Koppelen",
                            on_click=RiskState.link_control,
                            disabled=~RiskState.selected_control_id_to_link,
                        ),
                        width="100%",
                        spacing="2",
                        margin_top="8px",
                    ),

                    spacing="3",
                    width="100%",
                    align_items="start",
                ),

                # Scope Contextualisatie
                rx.vstack(
                    rx.divider(),
                    rx.text("Scope-contextualisatie", size="2", weight="medium"),
                    rx.text(
                        "Dit risico kan in meerdere scopes voorkomen met eigen scores en behandeling.",
                        size="1", color="gray",
                    ),

                    # List of linked scopes
                    rx.cond(
                        RiskState.risk_scopes.length() > 0,
                        rx.vstack(
                            rx.foreach(
                                RiskState.risk_scopes,
                                lambda rs: rx.hstack(
                                    rx.icon("layers", size=16, color="blue"),
                                    rx.vstack(
                                        rx.text(
                                            rx.cond(
                                                rs["scope_id"],
                                                f"Scope #{rs['scope_id']}",
                                                "Onbekend",
                                            ),
                                            size="2", weight="medium",
                                        ),
                                        rx.text(
                                            rx.cond(
                                                rs["acceptance_status"],
                                                rs["acceptance_status"],
                                                "Voorgesteld",
                                            ),
                                            size="1", color="gray",
                                        ),
                                        spacing="0",
                                    ),
                                    rx.spacer(),
                                    rx.icon_button(
                                        rx.icon("x", size=14),
                                        variant="ghost",
                                        size="1",
                                        color_scheme="red",
                                        on_click=lambda: RiskState.unlink_scope(rs["scope_id"]),
                                    ),
                                    width="100%",
                                    align_items="center",
                                    padding="4px 8px",
                                    background="var(--gray-a2)",
                                    border_radius="4px",
                                ),
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        rx.text("Nog niet aan scopes gekoppeld.", size="1", color="gray", font_style="italic"),
                    ),

                    # Add to scope
                    rx.hstack(
                        rx.select.root(
                            rx.select.trigger(placeholder="Selecteer scope..."),
                            rx.select.content(
                                rx.foreach(
                                    RiskState.all_scopes,
                                    lambda s: rx.select.item(s["name"], value=s["id"].to_string()),
                                ),
                            ),
                            value=RiskState.selected_scope_id_to_link,
                            on_change=RiskState.set_selected_scope_id_to_link,
                            width="100%",
                        ),
                        rx.button(
                            "Toevoegen aan scope",
                            on_click=RiskState.link_scope,
                            disabled=~RiskState.selected_scope_id_to_link,
                        ),
                        width="100%",
                        spacing="2",
                        margin_top="8px",
                    ),

                    spacing="3",
                    width="100%",
                    align_items="start",
                ),

                spacing="4",
                width="100%",
            ),

            # Action buttons
            rx.hstack(
                rx.dialog.close(
                    rx.button(
                        "Annuleren",
                        variant="soft",
                        color_scheme="gray",
                        on_click=RiskState.close_form_dialog,
                    ),
                ),
                rx.button(
                    rx.cond(
                        RiskState.is_editing,
                        "Opslaan",
                        "Toevoegen",
                    ),
                    on_click=RiskState.save_risk,
                ),
                spacing="3",
                justify="end",
                margin_top="16px",
            ),

            max_width=rx.breakpoints(initial="95vw", md="700px"),
        ),
        open=RiskState.show_form_dialog,
    )


def delete_confirm_dialog() -> rx.Component:
    """Dialog for confirming risk deletion."""
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Risico Verwijderen"),
            rx.alert_dialog.description(
                rx.vstack(
                    rx.text("Weet u zeker dat u dit risico wilt verwijderen?"),
                    rx.text(
                        RiskState.deleting_risk_title,
                        weight="bold",
                        color="red",
                    ),
                    rx.text(
                        "Deze actie kan niet ongedaan worden gemaakt.",
                        size="2",
                        color="gray",
                    ),
                    spacing="2",
                    align_items="start",
                ),
            ),
            rx.hstack(
                rx.alert_dialog.cancel(
                    rx.button(
                        "Annuleren",
                        variant="soft",
                        color_scheme="gray",
                        on_click=RiskState.close_delete_dialog,
                    ),
                ),
                rx.alert_dialog.action(
                    rx.button(
                        "Verwijderen",
                        color_scheme="red",
                        on_click=RiskState.confirm_delete,
                    ),
                ),
                spacing="3",
                justify="end",
                margin_top="16px",
            ),
        ),
        open=RiskState.show_delete_dialog,
    )


def risk_row(risk: dict) -> rx.Component:
    """Single row in risks table."""
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
                # Match on Dutch enum values returned by API
                ("Mitigeren", rx.badge(
                    rx.hstack(rx.icon("shield-alert", size=12), rx.text("Mitigeren"), spacing="1"),
                    color_scheme="red", variant="soft"
                )),
                ("Zekerheid verkrijgen", rx.badge(
                    rx.hstack(rx.icon("shield-check", size=12), rx.text("Zekerheid"), spacing="1"),
                    color_scheme="blue", variant="soft"
                )),
                ("Meten & monitoren", rx.badge(
                    rx.hstack(rx.icon("eye", size=12), rx.text("Monitoren"), spacing="1"),
                    color_scheme="yellow", variant="soft"
                )),
                ("Accepteren", rx.badge(
                    rx.hstack(rx.icon("circle-check", size=12), rx.text("Accepteren"), spacing="1"),
                    color_scheme="green", variant="soft"
                )),
                rx.badge("Niet ingedeeld", color_scheme="gray", variant="outline"),
            ),
        ),
        rx.table.cell(
            rx.match(
                risk["inherent_impact"],
                # Match on enum values returned by API (capitalized)
                ("Low", rx.badge("Laag", color_scheme="green", variant="soft")),
                ("Medium", rx.badge("Gemiddeld", color_scheme="yellow", variant="soft")),
                ("High", rx.badge("Hoog", color_scheme="orange", variant="soft")),
                ("Critical", rx.badge("Kritiek", color_scheme="red", variant="soft")),
                rx.badge("N/A", color_scheme="gray", variant="soft"),
            ),
        ),
        rx.table.cell(
            rx.text(risk["inherent_risk_score"], size="2"),
        ),

        rx.table.cell(
            rx.hstack(
                rx.cond(
                    AuthState.can_edit,
                    rx.icon_button(
                        rx.icon("pencil", size=14),
                        variant="ghost",
                        size="1",
                        on_click=lambda: RiskState.open_edit_dialog(risk["id"]),
                    ),
                ),
                rx.cond(
                    AuthState.can_edit,
                    rx.icon_button(
                        rx.icon("trash-2", size=14),
                        variant="ghost",
                        size="1",
                        color_scheme="red",
                        on_click=lambda: RiskState.open_delete_dialog(risk["id"]),
                    ),
                ),
                spacing="1",
            ),
        ),
        _hover={"background": "var(--gray-a3)"},
    )


def risk_mobile_card(risk: dict) -> rx.Component:
    """Mobile card view for a single risk."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text(risk["title"], weight="medium", size="2", flex="1"),
                rx.hstack(
                    rx.icon_button(
                        rx.icon("pencil", size=14),
                        variant="ghost",
                        size="1",
                        on_click=lambda: RiskState.open_edit_dialog(risk["id"]),
                    ),
                    rx.icon_button(
                        rx.icon("trash-2", size=14),
                        variant="ghost",
                        size="1",
                        color_scheme="red",
                        on_click=lambda: RiskState.open_delete_dialog(risk["id"]),
                    ),
                    spacing="1",
                ),
                width="100%",
                align="center",
            ),
            rx.text(risk["description"], size="1", color="gray", no_of_lines=2),
            rx.hstack(
                rx.match(
                    risk["attention_quadrant"],
                    ("Mitigeren", rx.badge("Mitigeren", color_scheme="red", variant="soft", size="1")),
                    ("Zekerheid verkrijgen", rx.badge("Zekerheid", color_scheme="blue", variant="soft", size="1")),
                    ("Meten & monitoren", rx.badge("Monitoren", color_scheme="yellow", variant="soft", size="1")),
                    ("Accepteren", rx.badge("Accepteren", color_scheme="green", variant="soft", size="1")),
                    rx.badge("Niet ingedeeld", color_scheme="gray", variant="outline", size="1"),
                ),
                rx.match(
                    risk["inherent_impact"],
                    ("Low", rx.badge("Laag", color_scheme="green", variant="soft", size="1")),
                    ("Medium", rx.badge("Gemiddeld", color_scheme="yellow", variant="soft", size="1")),
                    ("High", rx.badge("Hoog", color_scheme="orange", variant="soft", size="1")),
                    ("Critical", rx.badge("Kritiek", color_scheme="red", variant="soft", size="1")),
                    rx.badge("N/A", color_scheme="gray", variant="soft", size="1"),
                ),
                rx.badge(
                    rx.fragment("Score: ", risk["inherent_risk_score"]),
                    variant="outline",
                    size="1",
                ),
                spacing="2",
                wrap="wrap",
            ),
            spacing="2",
            width="100%",
        ),
        width="100%",
    )


def risks_table() -> rx.Component:
    """Risks data table."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("ID", width="60px"),
                rx.table.column_header_cell("Risico"),
                rx.table.column_header_cell("Behandeling", width="140px"),
                rx.table.column_header_cell("Impact", width="100px"),
                rx.table.column_header_cell("Score", width="80px"),

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
                                    rx.button(
                                        rx.icon("plus", size=14),
                                        "Voeg eerste risico toe",
                                        variant="soft",
                                        size="2",
                                        margin_top="8px",
                                        on_click=RiskState.open_create_dialog,
                                    ),
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
    return rx.flex(
        rx.select.root(
            rx.select.trigger(placeholder="Filter op behandeling"),
            rx.select.content(
                rx.select.item("Alle behandelingen", value="ALLE"),
                rx.select.item("Mitigeren", value="Mitigeren"),
                rx.select.item("Zekerheid verkrijgen", value="Zekerheid verkrijgen"),
                rx.select.item("Monitoren", value="Meten & monitoren"),
                rx.select.item("Accepteren", value="Accepteren"),
            ),
            value=RiskState.filter_quadrant,
            on_change=RiskState.set_filter_quadrant,
            size="2",
            default_value="ALLE",
            width=rx.breakpoints(initial="100%", md="auto"),
        ),
        rx.button(
            rx.icon("x", size=14),
            "Reset filters",
            variant="ghost",
            size="2",
            on_click=RiskState.clear_filters,
            width=rx.breakpoints(initial="100%", md="auto"),
        ),
        rx.spacer(display=rx.breakpoints(initial="none", md="block")),
        rx.cond(
            AuthState.can_edit,
            rx.button(
                rx.icon("plus", size=14),
                "Nieuw Risico",
                size="2",
                on_click=RiskState.open_create_dialog,
                width=rx.breakpoints(initial="100%", md="auto"),
            ),
        ),
        wrap="wrap",
        gap="2",
        width="100%",
    )


def risks_content() -> rx.Component:
    """Risks page content."""
    return rx.vstack(
        # Success message
        rx.cond(
            RiskState.success_message != "",
            rx.callout(
                RiskState.success_message,
                icon="circle-check",
                color="green",
                margin_bottom="16px",
            ),
        ),

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

        # Journey hint
        next_step_hint("risks"),

        # Filter bar
        filter_bar(),

        # Table (desktop)
        rx.box(
            rx.card(
                risks_table(),
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
                    RiskState.is_loading,
                    rx.center(rx.spinner(size="2"), padding="40px"),
                    rx.cond(
                        RiskState.risks.length() > 0,
                        rx.foreach(RiskState.risks, risk_mobile_card),
                        rx.center(rx.text("Geen risico's gevonden", color="gray"), padding="40px"),
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
        risk_form_dialog(),
        delete_confirm_dialog(),

        width="100%",
        on_mount=[RiskState.load_risks, JourneyState.load_journey_data],
    )


def risks_page() -> rx.Component:
    """Risks page with layout."""
    return layout(
        risks_content(),
        title="Risico's",
        subtitle="Beheer en monitor uw risico's",
    )
