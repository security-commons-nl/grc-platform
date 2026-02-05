"""
Risks List Page with CRUD functionality
"""
import reflex as rx
from ims.state.risk import RiskState
from ims.components.layout import layout


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


def linked_control_row(control: dict) -> rx.Component:
    """Row for a linked control in the risk dialog."""
    return rx.hstack(
        rx.vstack(
            rx.text(control.get("title", "-"), weight="medium", size="2"),
            rx.text(
                control.get("description", "") or "Geen beschrijving",
                size="1",
                color="gray",
                no_of_lines=1,
            ),
            spacing="0",
            align_items="start",
        ),
        rx.button(
            "Ontkoppelen",
            size="2",
            variant="soft",
            color_scheme="red",
            on_click=lambda: RiskState.unlink_control(control.get("id")),
        ),
        justify="between",
        align="center",
        width="100%",
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

                # Risk Matrix and Selection Display (Side-by-side)
                rx.hstack(
                    rx.box(
                        risk_matrix(),
                        flex="1",
                    ),
                    rx.box(
                        selected_risk_display(),
                        width="auto", 
                    ),
                    spacing="4",
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

                rx.cond(
                    RiskState.is_editing,
                    rx.vstack(
                        rx.divider(),
                        rx.text("Gekoppelde controls", size="2", weight="medium"),
                        rx.cond(
                            RiskState.linked_controls.length() > 0,
                            rx.vstack(
                                rx.foreach(RiskState.linked_controls, linked_control_row),
                                spacing="2",
                                width="100%",
                            ),
                            rx.callout(
                                "Nog geen controls gekoppeld.",
                                icon="info",
                                color="gray",
                                size="2",
                            ),
                        ),
                        rx.hstack(
                            rx.select.root(
                                rx.select.trigger(placeholder="Selecteer control"),
                                rx.select.content(
                                    rx.select.item("Kies een control", value="0"),
                                    rx.foreach(
                                        RiskState.linkable_controls,
                                        lambda control: rx.select.item(
                                            f'{control.get("title", "Control")} (#{control.get("id")})',
                                            value=str(control.get("id")),
                                        ),
                                    ),
                                ),
                                value=RiskState.selected_control_id,
                                on_change=RiskState.set_selected_control_id,
                            ),
                            rx.button(
                                "Koppelen",
                                size="2",
                                on_click=RiskState.link_selected_control,
                                disabled=RiskState.selected_control_id == "0",
                            ),
                            width="100%",
                            align="center",
                            spacing="2",
                        ),
                        spacing="3",
                        width="100%",
                        align_items="start",
                    ),
                    rx.box(),
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

            max_width="700px",  # Increased width more for side-by-side
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
            rx.cond(
                risk["risk_accepted"],
                rx.badge("Geaccepteerd", color_scheme="green", variant="soft"),
                rx.badge("Open", color_scheme="gray", variant="outline"),
            ),
        ),
        rx.table.cell(
            rx.hstack(
                rx.icon_button(
                    rx.icon("pencil", size=14),
                    variant="ghost",
                    size="1",
                    on_click=lambda: [
                        RiskState.open_edit_dialog(risk["id"]),
                        RiskState.load_controls_for_risk(risk["id"]),
                    ],
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
                rx.table.column_header_cell("Behandeling", width="140px"),
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
    return rx.hstack(
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
            on_click=RiskState.open_create_dialog,
        ),
        width="100%",
        spacing="2",
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

        # Dialogs
        risk_form_dialog(),
        delete_confirm_dialog(),

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
