"""
Assessments Page - Verification/Audit management
Full CRUD + wizard dialog + phase badges + clickable rows
"""
import reflex as rx
from ims.state.assessment import AssessmentState, ASSESSMENT_TYPES
from ims.components.layout import layout


def type_badge(assessment_type: str) -> rx.Component:
    """Badge for assessment type."""
    return rx.match(
        assessment_type,
        ("DPIA", rx.badge(
            rx.hstack(rx.icon("shield", size=12), rx.text("DPIA"), spacing="1"),
            color_scheme="purple", variant="soft"
        )),
        ("Pentest", rx.badge(
            rx.hstack(rx.icon("bug", size=12), rx.text("Pentest"), spacing="1"),
            color_scheme="red", variant="soft"
        )),
        ("Audit", rx.badge(
            rx.hstack(rx.icon("clipboard-check", size=12), rx.text("Audit"), spacing="1"),
            color_scheme="blue", variant="soft"
        )),
        ("Self-Assessment", rx.badge(
            rx.hstack(rx.icon("user-check", size=12), rx.text("Self-Assessment"), spacing="1"),
            color_scheme="green", variant="soft"
        )),
        ("BIA", rx.badge(
            rx.hstack(rx.icon("shield-check", size=12), rx.text("BIA"), spacing="1"),
            color_scheme="orange", variant="soft"
        )),
        ("Compliance Journey", rx.badge(
            rx.hstack(rx.icon("route", size=12), rx.text("Compliance"), spacing="1"),
            color_scheme="cyan", variant="soft"
        )),
        ("Supplier Assessment", rx.badge(
            rx.hstack(rx.icon("truck", size=12), rx.text("Supplier"), spacing="1"),
            color_scheme="amber", variant="soft"
        )),
        ("Maturity Assessment", rx.badge(
            rx.hstack(rx.icon("trending-up", size=12), rx.text("Maturity"), spacing="1"),
            color_scheme="teal", variant="soft"
        )),
        rx.badge(assessment_type, color_scheme="gray", variant="outline"),
    )


def phase_badge(phase: str) -> rx.Component:
    """Badge for assessment phase."""
    return rx.match(
        phase,
        ("Aangevraagd", rx.badge("Aangevraagd", color_scheme="gray", variant="soft")),
        ("Planning", rx.badge("Planning", color_scheme="blue", variant="soft")),
        ("Voorbereiding", rx.badge("Voorbereiding", color_scheme="cyan", variant="soft")),
        ("In uitvoering", rx.badge("In uitvoering", color_scheme="indigo", variant="soft")),
        ("Review", rx.badge("Review", color_scheme="orange", variant="soft")),
        ("Rapportage", rx.badge("Rapportage", color_scheme="amber", variant="soft")),
        ("Afgerond", rx.badge("Afgerond", color_scheme="green", variant="soft")),
        ("Geannuleerd", rx.badge("Geannuleerd", color_scheme="red", variant="soft")),
        rx.badge(phase, color_scheme="gray", variant="outline"),
    )


def assessment_row(assessment: dict) -> rx.Component:
    """Single clickable row in assessments table."""
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
        rx.table.cell(phase_badge(assessment["phase"])),
        rx.table.cell(
            rx.hstack(
                rx.icon_button(
                    rx.icon("eye", size=14),
                    variant="ghost",
                    size="1",
                    on_click=AssessmentState.go_to_detail(assessment),
                ),
                rx.icon_button(
                    rx.icon("pencil", size=14),
                    variant="ghost",
                    size="1",
                    on_click=AssessmentState.open_edit_dialog(assessment),
                ),
                rx.icon_button(
                    rx.icon("trash-2", size=14),
                    variant="ghost",
                    size="1",
                    color_scheme="red",
                    on_click=AssessmentState.confirm_delete(assessment),
                ),
                spacing="1",
            ),
        ),
        _hover={"background": "var(--gray-a3)", "cursor": "pointer"},
    )


def assessment_mobile_card(assessment: dict) -> rx.Component:
    """Mobile card view for a single assessment."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text(assessment["title"], weight="medium", size="2"),
                rx.spacer(),
                rx.icon_button(
                    rx.icon("pencil", size=12),
                    variant="ghost",
                    size="1",
                    on_click=AssessmentState.open_edit_dialog(assessment),
                ),
                width="100%",
            ),
            rx.text(assessment["description"], size="1", color="gray", no_of_lines=2),
            rx.hstack(
                type_badge(assessment["type"]),
                phase_badge(assessment["phase"]),
                spacing="2",
                wrap="wrap",
            ),
            spacing="2",
            width="100%",
        ),
        width="100%",
        cursor="pointer",
        on_click=AssessmentState.go_to_detail(assessment),
    )


def assessments_table() -> rx.Component:
    """Assessments data table."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("ID", width="60px"),
                rx.table.column_header_cell("Assessment"),
                rx.table.column_header_cell("Type", width="140px"),
                rx.table.column_header_cell("Fase", width="130px"),
                rx.table.column_header_cell("Acties", width="120px"),
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
                rx.select.item("Pentest", value="Pentest"),
                rx.select.item("Audit", value="Audit"),
                rx.select.item("Self-Assessment", value="Self-Assessment"),
                rx.select.item("BIA", value="BIA"),
                rx.select.item("Compliance Journey", value="Compliance Journey"),
                rx.select.item("Supplier Assessment", value="Supplier Assessment"),
                rx.select.item("Maturity Assessment", value="Maturity Assessment"),
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
                rx.select.item("Concept", value="Draft"),
                rx.select.item("Actief", value="Active"),
                rx.select.item("Afgerond", value="Closed"),
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
            on_click=AssessmentState.open_create_dialog,
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
                rx.icon("clipboard-list", size=20, color="var(--gray-9)"),
                rx.vstack(
                    rx.text("Totaal", size="1", color="gray"),
                    rx.text(AssessmentState.total_count, size="4", weight="bold"),
                    spacing="0",
                    align_items="start",
                ),
                spacing="3",
            ),
            padding="12px",
        ),
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
        columns=rx.breakpoints(initial="1", sm="3"),
        spacing="3",
        width="100%",
    )


def wizard_dialog() -> rx.Component:
    """Create/edit assessment wizard dialog."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(
                    AssessmentState.is_editing,
                    "Assessment bewerken",
                    "Nieuw Assessment",
                ),
            ),
            rx.dialog.description(
                "Vul de gegevens in voor het assessment.",
                size="2",
                margin_bottom="16px",
            ),
            rx.vstack(
                # Title
                rx.text("Titel *", size="2", weight="medium"),
                rx.input(
                    placeholder="Naam van het assessment",
                    value=AssessmentState.form_title,
                    on_change=AssessmentState.set_form_title,
                    width="100%",
                ),
                # Type
                rx.text("Type", size="2", weight="medium"),
                rx.select.root(
                    rx.select.trigger(placeholder="Kies type"),
                    rx.select.content(
                        *[rx.select.item(label, value=value) for label, value in ASSESSMENT_TYPES],
                    ),
                    value=AssessmentState.form_type,
                    on_change=AssessmentState.set_form_type,
                    width="100%",
                ),
                # Scope
                rx.text("Scope", size="2", weight="medium"),
                rx.select.root(
                    rx.select.trigger(placeholder="Kies scope (optioneel)"),
                    rx.select.content(
                        rx.select.item("Geen scope", value=""),
                        rx.foreach(
                            AssessmentState.available_scopes,
                            lambda s: rx.select.item(
                                s["name"],
                                value=s["id"].to(str),
                            ),
                        ),
                    ),
                    value=AssessmentState.form_scope_id,
                    on_change=AssessmentState.set_form_scope_id,
                    width="100%",
                ),
                # Description
                rx.text("Beschrijving", size="2", weight="medium"),
                rx.text_area(
                    placeholder="Beschrijving van het assessment",
                    value=AssessmentState.form_description,
                    on_change=AssessmentState.set_form_description,
                    width="100%",
                    rows=3,
                ),
                # Lead assessor
                rx.text("Lead Assessor", size="2", weight="medium"),
                rx.select.root(
                    rx.select.trigger(placeholder="Kies assessor (optioneel)"),
                    rx.select.content(
                        rx.select.item("Geen assessor", value=""),
                        rx.foreach(
                            AssessmentState.available_users,
                            lambda u: rx.select.item(
                                u["full_name"],
                                value=u["id"].to(str),
                            ),
                        ),
                    ),
                    value=AssessmentState.form_lead_assessor_id,
                    on_change=AssessmentState.set_form_lead_assessor_id,
                    width="100%",
                ),
                # External assessor
                rx.text("Externe Assessor", size="2", weight="medium"),
                rx.input(
                    placeholder="Naam externe assessor (optioneel)",
                    value=AssessmentState.form_external_assessor,
                    on_change=AssessmentState.set_form_external_assessor,
                    width="100%",
                ),
                # Methodology
                rx.text("Methodologie", size="2", weight="medium"),
                rx.input(
                    placeholder="bijv. ISO 27001, OWASP, BIO...",
                    value=AssessmentState.form_methodology,
                    on_change=AssessmentState.set_form_methodology,
                    width="100%",
                ),
                # Error
                rx.cond(
                    AssessmentState.error != "",
                    rx.callout(
                        AssessmentState.error,
                        icon="circle-alert",
                        color_scheme="red",
                        size="1",
                    ),
                ),
                spacing="2",
                width="100%",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button("Annuleren", variant="soft", color_scheme="gray"),
                ),
                rx.button(
                    rx.cond(AssessmentState.is_editing, "Opslaan", "Aanmaken"),
                    on_click=AssessmentState.save_assessment,
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
            max_width="500px",
        ),
        open=AssessmentState.show_form_dialog,
        on_open_change=AssessmentState.set_show_form_dialog,
    )


def delete_dialog() -> rx.Component:
    """Delete confirmation dialog."""
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Assessment verwijderen"),
            rx.alert_dialog.description(
                rx.text(
                    "Weet je zeker dat je ",
                    rx.text(AssessmentState.deleting_assessment_title, weight="bold"),
                    " wilt verwijderen? Dit kan niet ongedaan worden.",
                ),
            ),
            rx.flex(
                rx.alert_dialog.cancel(
                    rx.button("Annuleren", variant="soft", color_scheme="gray"),
                ),
                rx.alert_dialog.action(
                    rx.button("Verwijderen", color_scheme="red", on_click=AssessmentState.delete_assessment),
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
        ),
        open=AssessmentState.show_delete_dialog,
        on_open_change=AssessmentState.set_show_delete_dialog,
    )


def assessments_content() -> rx.Component:
    """Assessments page content."""
    return rx.vstack(
        rx.cond(
            AssessmentState.error != "",
            rx.callout(
                AssessmentState.error,
                icon="circle-alert",
                color_scheme="red",
                margin_bottom="16px",
            ),
        ),
        rx.cond(
            AssessmentState.success_message != "",
            rx.callout(
                AssessmentState.success_message,
                icon="circle-check",
                color_scheme="green",
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
        wizard_dialog(),
        delete_dialog(),
        width="100%",
        spacing="4",
        on_mount=AssessmentState.load_assessments,
    )


def assessments_page() -> rx.Component:
    """Assessments page with layout."""
    return layout(
        assessments_content(),
        title="Assessments",
        subtitle="DPIA's, Pentests, Audits, BIA's en Self-Assessments",
    )
