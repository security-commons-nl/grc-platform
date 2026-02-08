"""
Assessment Detail Page
Route: /assessments/[id]
Stepper + 5 tabs: Overzicht | Vragenlijst | Bevindingen | Evidence | Acties
"""
import reflex as rx
from ims.state.assessment import AssessmentState, ASSESSMENT_PHASES
from ims.pages.assessments import wizard_dialog
from ims.components.layout import layout


# =============================================================================
# PHASE STEPPER
# =============================================================================

def phase_step(phase_name: str, index: int) -> rx.Component:
    """Single step in the phase stepper."""
    return rx.hstack(
        rx.cond(
            AssessmentState.detail_phase_index > index,
            # Completed
            rx.box(
                rx.icon("check", size=14, color="white"),
                width="28px",
                height="28px",
                border_radius="50%",
                background="var(--green-9)",
                display="flex",
                align_items="center",
                justify_content="center",
            ),
            rx.cond(
                AssessmentState.detail_phase_index == index,
                # Current
                rx.box(
                    rx.text(str(index + 1), size="1", color="white", weight="bold"),
                    width="28px",
                    height="28px",
                    border_radius="50%",
                    background="var(--indigo-9)",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                ),
                # Future
                rx.box(
                    rx.text(str(index + 1), size="1", color="gray"),
                    width="28px",
                    height="28px",
                    border_radius="50%",
                    border="2px solid var(--gray-6)",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                ),
            ),
        ),
        rx.text(
            phase_name,
            size="1",
            weight=rx.cond(
                AssessmentState.detail_phase_index == index,
                "bold",
                "regular",
            ),
            color=rx.cond(
                AssessmentState.detail_phase_index >= index,
                "var(--gray-12)",
                "var(--gray-8)",
            ),
        ),
        spacing="2",
        align_items="center",
        cursor="pointer",
        on_click=AssessmentState.advance_phase(phase_name),
    )


def phase_stepper() -> rx.Component:
    """Visual phase stepper for the assessment."""
    return rx.card(
        rx.vstack(
            rx.text("Workflow Fase", size="2", weight="bold", color="gray"),
            rx.flex(
                phase_step("Aangevraagd", 0),
                rx.box(width="20px", height="2px", background="var(--gray-6)", align_self="center"),
                phase_step("Planning", 1),
                rx.box(width="20px", height="2px", background="var(--gray-6)", align_self="center"),
                phase_step("Voorbereiding", 2),
                rx.box(width="20px", height="2px", background="var(--gray-6)", align_self="center"),
                phase_step("In uitvoering", 3),
                rx.box(width="20px", height="2px", background="var(--gray-6)", align_self="center"),
                phase_step("Review", 4),
                rx.box(width="20px", height="2px", background="var(--gray-6)", align_self="center"),
                phase_step("Rapportage", 5),
                rx.box(width="20px", height="2px", background="var(--gray-6)", align_self="center"),
                phase_step("Afgerond", 6),
                wrap="wrap",
                gap="2",
                align_items="center",
            ),
            spacing="3",
            width="100%",
        ),
        width="100%",
    )


# =============================================================================
# TAB: OVERZICHT
# =============================================================================

def bia_result_card() -> rx.Component:
    """BIA result display card (only for BIA assessments with results)."""
    return rx.cond(
        AssessmentState.detail_has_bia_result,
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.icon("shield-check", size=20, color="var(--indigo-9)"),
                    rx.text("BIA Resultaat", size="3", weight="bold"),
                    spacing="2",
                ),
                rx.separator(),
                rx.grid(
                    rx.vstack(
                        rx.text("CIA Classificatie", size="1", color="gray"),
                        rx.text(
                            AssessmentState.detail_assessment["bia_cia_label"],
                            size="4",
                            weight="bold",
                            color="var(--indigo-9)",
                        ),
                        spacing="0",
                    ),
                    rx.vstack(
                        rx.text("RTO", size="1", color="gray"),
                        rx.text(
                            rx.cond(
                                AssessmentState.detail_assessment["bia_rto_hours"].to(int) > 0,
                                AssessmentState.detail_assessment["bia_rto_hours"].to(str) + " uur",
                                "< 15 min",
                            ),
                            size="3",
                            weight="bold",
                        ),
                        spacing="0",
                    ),
                    rx.vstack(
                        rx.text("RPO", size="1", color="gray"),
                        rx.text(
                            rx.cond(
                                AssessmentState.detail_assessment["bia_rpo_hours"].to(int) > 0,
                                AssessmentState.detail_assessment["bia_rpo_hours"].to(str) + " uur",
                                "0 (geen verlies)",
                            ),
                            size="3",
                            weight="bold",
                        ),
                        spacing="0",
                    ),
                    rx.vstack(
                        rx.text("MTPD", size="1", color="gray"),
                        rx.text(
                            rx.cond(
                                AssessmentState.detail_assessment["bia_mtpd_hours"].to(int) > 0,
                                AssessmentState.detail_assessment["bia_mtpd_hours"].to(str) + " uur",
                                "4 uur",
                            ),
                            size="3",
                            weight="bold",
                        ),
                        spacing="0",
                    ),
                    rx.vstack(
                        rx.text("BCP Vereist", size="1", color="gray"),
                        rx.cond(
                            AssessmentState.detail_assessment["bia_bcp_required"],
                            rx.badge("Ja", color_scheme="red", variant="soft"),
                            rx.badge("Nee", color_scheme="green", variant="soft"),
                        ),
                        spacing="1",
                    ),
                    columns=rx.breakpoints(initial="2", md="5"),
                    spacing="4",
                    width="100%",
                ),
                spacing="3",
                width="100%",
            ),
            width="100%",
        ),
        rx.fragment(),
    )


def overview_tab() -> rx.Component:
    """Overview tab content."""
    return rx.vstack(
        bia_result_card(),
        rx.grid(
            rx.card(
                rx.vstack(
                    rx.text("Type", size="1", color="gray"),
                    rx.text(AssessmentState.detail_assessment["type"], size="2", weight="medium"),
                    spacing="1",
                ),
            ),
            rx.card(
                rx.vstack(
                    rx.text("Status", size="1", color="gray"),
                    rx.text(AssessmentState.detail_assessment["status"], size="2", weight="medium"),
                    spacing="1",
                ),
            ),
            rx.card(
                rx.vstack(
                    rx.text("Fase", size="1", color="gray"),
                    rx.text(AssessmentState.detail_phase, size="2", weight="medium"),
                    spacing="1",
                ),
            ),
            rx.card(
                rx.vstack(
                    rx.text("Bevindingen", size="1", color="gray"),
                    rx.text(AssessmentState.detail_findings_count, size="2", weight="medium"),
                    spacing="1",
                ),
            ),
            columns=rx.breakpoints(initial="2", md="4"),
            spacing="3",
            width="100%",
        ),
        rx.card(
            rx.vstack(
                rx.text("Beschrijving", size="2", weight="bold"),
                rx.text(
                    rx.cond(
                        AssessmentState.detail_assessment["description"],
                        AssessmentState.detail_assessment["description"],
                        "Geen beschrijving",
                    ),
                    size="2",
                    color="gray",
                ),
                spacing="2",
                width="100%",
            ),
            width="100%",
        ),
        spacing="4",
        width="100%",
    )


# =============================================================================
# TAB: VRAGENLIJST (BIA)
# =============================================================================

def score_button(question_id: str, score: int, label: str, color: str) -> rx.Component:
    """Single score button for BIA question."""
    qid = question_id
    score_str = str(score)
    return rx.button(
        f"{score}",
        title=label,
        variant="outline",
        color_scheme=color,
        size="1",
        on_click=AssessmentState.set_bia_response(qid, score_str),
    )


def bia_question_card(question: dict) -> rx.Component:
    """Single BIA question with 1-4 score selector."""
    qid = question["id"].to(str)
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.badge(question["code"], variant="outline", size="1"),
                rx.text(question["question_text"], size="2", weight="medium"),
                spacing="2",
                align_items="start",
                width="100%",
            ),
            rx.cond(
                question["guidance"],
                rx.text(question["guidance"], size="1", color="gray"),
                rx.fragment(),
            ),
            rx.hstack(
                rx.text("Score:", size="2", weight="medium"),
                score_button(qid, 1, "Laag", "green"),
                rx.text("Laag", size="1", color="gray"),
                score_button(qid, 2, "Midden", "yellow"),
                rx.text("Midden", size="1", color="gray"),
                score_button(qid, 3, "Hoog", "orange"),
                rx.text("Hoog", size="1", color="gray"),
                score_button(qid, 4, "Kritiek", "red"),
                rx.text("Kritiek", size="1", color="gray"),
                spacing="2",
                align_items="center",
                wrap="wrap",
            ),
            spacing="2",
            width="100%",
        ),
        width="100%",
    )


def questionnaire_tab() -> rx.Component:
    """BIA questionnaire tab."""
    return rx.cond(
        AssessmentState.detail_is_bia,
        rx.vstack(
            # Progress bar
            rx.card(
                rx.vstack(
                    rx.hstack(
                        rx.text("Voortgang", size="2", weight="bold"),
                        rx.spacer(),
                        rx.text(
                            AssessmentState.bia_progress_answered.to(str)
                            + " / "
                            + AssessmentState.bia_progress_total.to(str)
                            + " vragen beantwoord",
                            size="1",
                            color="gray",
                        ),
                        width="100%",
                    ),
                    rx.progress(
                        value=AssessmentState.bia_progress_pct,
                        width="100%",
                    ),
                    spacing="2",
                    width="100%",
                ),
                width="100%",
            ),
            # Questions
            rx.foreach(AssessmentState.bia_questions, bia_question_card),
            # Calculate button
            rx.card(
                rx.hstack(
                    rx.button(
                        rx.cond(
                            AssessmentState.bia_calculating,
                            rx.spinner(size="1"),
                            rx.icon("calculator", size=14),
                        ),
                        "Bereken BIA Score",
                        on_click=AssessmentState.calculate_bia,
                        disabled=AssessmentState.bia_calculating,
                        size="3",
                    ),
                    rx.cond(
                        AssessmentState.bia_has_all_answers,
                        rx.badge("Alle vragen beantwoord", color_scheme="green", variant="soft"),
                        rx.badge(
                            "Nog niet alle vragen beantwoord",
                            color_scheme="orange",
                            variant="soft",
                        ),
                    ),
                    spacing="3",
                    align_items="center",
                    wrap="wrap",
                ),
                width="100%",
            ),
            spacing="3",
            width="100%",
            on_mount=AssessmentState.load_bia_questions,
        ),
        rx.center(
            rx.vstack(
                rx.icon("clipboard-list", size=32, color="gray"),
                rx.text("De vragenlijst is beschikbaar voor BIA assessments", color="gray"),
                spacing="2",
                align_items="center",
            ),
            padding="60px",
        ),
    )


# =============================================================================
# TAB: BEVINDINGEN
# =============================================================================

def finding_row(finding: dict) -> rx.Component:
    """Single finding card."""
    return rx.card(
        rx.hstack(
            rx.vstack(
                rx.text(finding["title"], size="2", weight="medium"),
                rx.text(finding["description"], size="1", color="gray", no_of_lines=2),
                spacing="1",
                flex="1",
            ),
            rx.vstack(
                rx.match(
                    finding["severity"],
                    ("Critical", rx.badge("Kritiek", color_scheme="red", variant="soft")),
                    ("High", rx.badge("Hoog", color_scheme="orange", variant="soft")),
                    ("Medium", rx.badge("Midden", color_scheme="yellow", variant="soft")),
                    ("Low", rx.badge("Laag", color_scheme="green", variant="soft")),
                    rx.badge(finding["severity"], variant="outline"),
                ),
                rx.match(
                    finding["status"],
                    ("Active", rx.badge("Open", color_scheme="blue", variant="soft")),
                    ("Closed", rx.badge("Gesloten", color_scheme="green", variant="soft")),
                    rx.badge(finding["status"], variant="outline"),
                ),
                spacing="1",
                align_items="end",
            ),
            width="100%",
            align_items="start",
        ),
        width="100%",
    )


def finding_dialog() -> rx.Component:
    """Create finding dialog."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Nieuwe Bevinding"),
            rx.vstack(
                rx.text("Titel *", size="2", weight="medium"),
                rx.input(
                    placeholder="Titel van de bevinding",
                    value=AssessmentState.finding_title,
                    on_change=AssessmentState.set_finding_title,
                    width="100%",
                ),
                rx.text("Beschrijving", size="2", weight="medium"),
                rx.text_area(
                    placeholder="Details",
                    value=AssessmentState.finding_description,
                    on_change=AssessmentState.set_finding_description,
                    width="100%",
                    rows="3",
                ),
                rx.text("Ernst", size="2", weight="medium"),
                rx.select.root(
                    rx.select.trigger(placeholder="Ernst"),
                    rx.select.content(
                        rx.select.item("Kritiek", value="Critical"),
                        rx.select.item("Hoog", value="High"),
                        rx.select.item("Midden", value="Medium"),
                        rx.select.item("Laag", value="Low"),
                    ),
                    value=AssessmentState.finding_severity,
                    on_change=AssessmentState.set_finding_severity,
                    width="100%",
                ),
                spacing="2",
                width="100%",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button("Annuleren", variant="soft", color_scheme="gray"),
                ),
                rx.button("Toevoegen", on_click=AssessmentState.create_finding),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
            max_width="450px",
        ),
        open=AssessmentState.show_finding_dialog,
    )


def findings_tab() -> rx.Component:
    """Findings tab content."""
    return rx.vstack(
        rx.hstack(
            rx.text("Bevindingen", size="3", weight="bold"),
            rx.spacer(),
            rx.button(
                rx.icon("plus", size=14),
                "Nieuwe Bevinding",
                size="2",
                on_click=AssessmentState.open_finding_dialog,
            ),
            width="100%",
        ),
        rx.cond(
            AssessmentState.detail_findings.length() > 0,
            rx.vstack(
                rx.foreach(AssessmentState.detail_findings, finding_row),
                spacing="2",
                width="100%",
            ),
            rx.center(
                rx.vstack(
                    rx.icon("search", size=32, color="gray"),
                    rx.text("Geen bevindingen", color="gray"),
                    spacing="2",
                    align_items="center",
                ),
                padding="40px",
            ),
        ),
        finding_dialog(),
        spacing="3",
        width="100%",
    )


# =============================================================================
# TAB: EVIDENCE
# =============================================================================

def evidence_row(evidence: dict) -> rx.Component:
    """Single evidence card."""
    return rx.card(
        rx.hstack(
            rx.icon("file-text", size=16, color="var(--indigo-9)"),
            rx.vstack(
                rx.text(evidence["title"], size="2", weight="medium"),
                rx.text(evidence["description"], size="1", color="gray", no_of_lines=1),
                spacing="0",
            ),
            rx.spacer(),
            rx.cond(
                evidence["evidence_type"],
                rx.badge(evidence["evidence_type"], variant="outline", size="1"),
                rx.fragment(),
            ),
            spacing="3",
            width="100%",
            align_items="center",
        ),
        width="100%",
    )


def evidence_dialog() -> rx.Component:
    """Create evidence dialog."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Nieuw Bewijs"),
            rx.vstack(
                rx.text("Titel *", size="2", weight="medium"),
                rx.input(
                    placeholder="Titel van het bewijs",
                    value=AssessmentState.evidence_title,
                    on_change=AssessmentState.set_evidence_title,
                    width="100%",
                ),
                rx.text("Beschrijving", size="2", weight="medium"),
                rx.text_area(
                    placeholder="Beschrijving",
                    value=AssessmentState.evidence_description,
                    on_change=AssessmentState.set_evidence_description,
                    width="100%",
                    rows="2",
                ),
                rx.text("Type", size="2", weight="medium"),
                rx.select.root(
                    rx.select.trigger(placeholder="Type bewijs"),
                    rx.select.content(
                        rx.select.item("Screenshot", value="Screenshot"),
                        rx.select.item("Log", value="Log"),
                        rx.select.item("Rapport", value="Report"),
                        rx.select.item("Configuratie", value="Config"),
                        rx.select.item("Document", value="Document"),
                    ),
                    value=AssessmentState.evidence_type,
                    on_change=AssessmentState.set_evidence_type,
                    width="100%",
                ),
                rx.text("URL", size="2", weight="medium"),
                rx.input(
                    placeholder="Link naar bewijs (optioneel)",
                    value=AssessmentState.evidence_url,
                    on_change=AssessmentState.set_evidence_url,
                    width="100%",
                ),
                spacing="2",
                width="100%",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button("Annuleren", variant="soft", color_scheme="gray"),
                ),
                rx.button("Toevoegen", on_click=AssessmentState.create_evidence),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
            max_width="450px",
        ),
        open=AssessmentState.show_evidence_dialog,
    )


def evidence_tab() -> rx.Component:
    """Evidence tab content."""
    return rx.vstack(
        rx.hstack(
            rx.text("Bewijsmateriaal", size="3", weight="bold"),
            rx.spacer(),
            rx.button(
                rx.icon("plus", size=14),
                "Nieuw Bewijs",
                size="2",
                on_click=AssessmentState.open_evidence_dialog,
            ),
            width="100%",
        ),
        rx.cond(
            AssessmentState.detail_evidence.length() > 0,
            rx.vstack(
                rx.foreach(AssessmentState.detail_evidence, evidence_row),
                spacing="2",
                width="100%",
            ),
            rx.center(
                rx.vstack(
                    rx.icon("folder-open", size=32, color="gray"),
                    rx.text("Geen bewijsmateriaal", color="gray"),
                    spacing="2",
                    align_items="center",
                ),
                padding="40px",
            ),
        ),
        evidence_dialog(),
        spacing="3",
        width="100%",
    )


# =============================================================================
# TAB: ACTIES
# =============================================================================

def actions_tab() -> rx.Component:
    """Corrective actions tab — lists actions per finding."""
    return rx.vstack(
        rx.text("Corrigerende Maatregelen", size="3", weight="bold"),
        rx.text(
            "Acties worden beheerd per bevinding. Ga naar de Bevindingen-tab om acties toe te voegen.",
            size="2",
            color="gray",
        ),
        spacing="3",
        width="100%",
    )


# =============================================================================
# MAIN DETAIL PAGE
# =============================================================================

def tab_button(label: str, value: str, icon_name: str) -> rx.Component:
    """Tab button."""
    return rx.button(
        rx.icon(icon_name, size=14),
        label,
        variant=rx.cond(
            AssessmentState.detail_tab == value,
            "solid",
            "ghost",
        ),
        size="2",
        on_click=AssessmentState.set_detail_tab(value),
    )


def assessment_detail_content() -> rx.Component:
    """Detail page content."""
    return rx.vstack(
        # Error/success messages
        rx.cond(
            AssessmentState.error != "",
            rx.callout(
                AssessmentState.error,
                icon="circle-alert",
                color_scheme="red",
            ),
        ),
        rx.cond(
            AssessmentState.success_message != "",
            rx.callout(
                AssessmentState.success_message,
                icon="circle-check",
                color_scheme="green",
            ),
        ),
        # Loading
        rx.cond(
            AssessmentState.detail_loading,
            rx.center(rx.spinner(size="3"), padding="60px"),
            rx.vstack(
                # Back button + title
                rx.hstack(
                    rx.button(
                        rx.icon("arrow-left", size=14),
                        "Terug",
                        variant="ghost",
                        size="2",
                        on_click=rx.redirect("/assessments"),
                    ),
                    rx.spacer(),
                    rx.button(
                        rx.icon("pencil", size=14),
                        "Bewerken",
                        variant="outline",
                        size="2",
                        on_click=AssessmentState.open_edit_dialog(
                            AssessmentState.detail_assessment,
                        ),
                    ),
                    width="100%",
                ),
                # Title
                rx.heading(
                    AssessmentState.detail_assessment["title"],
                    size="5",
                ),
                # Phase stepper
                phase_stepper(),
                # Tab navigation
                rx.flex(
                    tab_button("Overzicht", "overzicht", "layout-dashboard"),
                    tab_button("Vragenlijst", "vragenlijst", "clipboard-list"),
                    tab_button("Bevindingen", "bevindingen", "search"),
                    tab_button("Evidence", "evidence", "file-text"),
                    tab_button("Acties", "acties", "list-checks"),
                    gap="2",
                    wrap="wrap",
                ),
                # Tab content
                rx.match(
                    AssessmentState.detail_tab,
                    ("overzicht", overview_tab()),
                    ("vragenlijst", questionnaire_tab()),
                    ("bevindingen", findings_tab()),
                    ("evidence", evidence_tab()),
                    ("acties", actions_tab()),
                    overview_tab(),
                ),
                spacing="4",
                width="100%",
            ),
        ),
        wizard_dialog(),
        width="100%",
        spacing="4",
    )


def assessment_detail_page() -> rx.Component:
    """Assessment detail page with layout."""
    return layout(
        assessment_detail_content(),
        title="Assessment Detail",
        subtitle="",
    )
