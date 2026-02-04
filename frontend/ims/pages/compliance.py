"""
Compliance Page - Statement of Applicability (SoA) Management
"""
import reflex as rx
from ims.state.compliance import ComplianceState
from ims.components.layout import layout


def compliance_stat_card(title: str, value: rx.Var, icon: str, color: str) -> rx.Component:
    """Statistics card for compliance dashboard."""
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


def compliance_progress_bar() -> rx.Component:
    """Compliance progress bar."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text("Compliance Voortgang", weight="medium"),
                rx.spacer(),
                rx.text(
                    rx.fragment(ComplianceState.compliance_percentage_display, "%"),
                    weight="bold",
                    color="green",
                ),
                width="100%",
            ),
            rx.progress(
                value=ComplianceState.compliance_percentage,
                width="100%",
                color_scheme="green",
            ),
            rx.hstack(
                rx.badge(
                    rx.fragment(ComplianceState.implemented_count, " Geimplementeerd"),
                    color_scheme="green",
                    variant="soft",
                ),
                rx.badge(
                    rx.fragment(ComplianceState.in_progress_count, " In uitvoering"),
                    color_scheme="yellow",
                    variant="soft",
                ),
                rx.badge(
                    rx.fragment(ComplianceState.gaps_count, " Gaps"),
                    color_scheme="red",
                    variant="soft",
                ),
                spacing="2",
            ),
            spacing="3",
            align_items="start",
            width="100%",
        ),
        padding="16px",
    )


def scope_selector() -> rx.Component:
    """Scope selection dropdown."""
    return rx.vstack(
        rx.text("Scope", size="2", weight="medium"),
        rx.select.root(
            rx.select.trigger(placeholder="Selecteer scope..."),
            rx.select.content(
                rx.select.item("Alle scopes", value="NONE"),
                rx.foreach(
                    ComplianceState.scopes,
                    lambda scope: rx.select.item(
                        scope["name"],
                        value=scope["id"].to_string(),
                    ),
                ),
            ),
            on_change=ComplianceState.set_selected_scope,
            size="2",
        ),
        align_items="start",
        min_width="200px",
    )


def standard_selector() -> rx.Component:
    """Standard selection dropdown."""
    return rx.vstack(
        rx.text("Standaard", size="2", weight="medium"),
        rx.select.root(
            rx.select.trigger(placeholder="Selecteer standaard..."),
            rx.select.content(
                rx.select.item("Alle standaarden", value="NONE"),
                rx.foreach(
                    ComplianceState.standards,
                    lambda std: rx.select.item(
                        rx.fragment(std["name"], " ", std["version"]),
                        value=std["id"].to_string(),
                    ),
                ),
            ),
            on_change=ComplianceState.set_selected_standard,
            size="2",
        ),
        align_items="start",
        min_width="200px",
    )


def filter_bar() -> rx.Component:
    """Filter bar for SoA entries."""
    return rx.hstack(
        scope_selector(),
        standard_selector(),
        rx.vstack(
            rx.text("Dekking", size="2", weight="medium"),
            rx.select.root(
                rx.select.trigger(placeholder="Filter dekking"),
                rx.select.content(
                    rx.select.item("Alle", value="ALL"),
                    rx.select.item("Lokaal", value="Local"),
                    rx.select.item("Gedeeld", value="Shared"),
                    rx.select.item("Gecombineerd", value="Combined"),
                    rx.select.item("Niet gedekt", value="Not Covered"),
                    rx.select.item("N.v.t.", value="Not Applicable"),
                ),
                value=ComplianceState.filter_coverage,
                on_change=ComplianceState.set_filter_coverage,
                size="2",
            ),
            align_items="start",
        ),
        rx.vstack(
            rx.text("Status", size="2", weight="medium"),
            rx.select.root(
                rx.select.trigger(placeholder="Filter status"),
                rx.select.content(
                    rx.select.item("Alle", value="ALL"),
                    rx.select.item("Niet gestart", value="Not Started"),
                    rx.select.item("In uitvoering", value="In Progress"),
                    rx.select.item("Geimplementeerd", value="Implemented"),
                    rx.select.item("N.v.t.", value="Not Applicable"),
                ),
                value=ComplianceState.filter_status,
                on_change=ComplianceState.set_filter_status,
                size="2",
            ),
            align_items="start",
        ),
        rx.spacer(),
        rx.button(
            rx.icon("plus", size=14),
            "Initialiseer SoA",
            variant="soft",
            size="2",
            on_click=ComplianceState.open_init_dialog,
        ),
        spacing="4",
        width="100%",
        align_items="end",
    )


def coverage_badge(coverage_type: str) -> rx.Component:
    """Badge for coverage type."""
    return rx.match(
        coverage_type,
        ("Local", rx.badge("Lokaal", color_scheme="blue", variant="soft")),
        ("Shared", rx.badge("Gedeeld", color_scheme="purple", variant="soft")),
        ("Combined", rx.badge("Gecombineerd", color_scheme="cyan", variant="soft")),
        ("Not Covered", rx.badge("Niet gedekt", color_scheme="red", variant="soft")),
        ("Not Applicable", rx.badge("N.v.t.", color_scheme="gray", variant="soft")),
        rx.badge("Onbekend", color_scheme="gray", variant="outline"),
    )


def status_badge(status: str) -> rx.Component:
    """Badge for implementation status."""
    return rx.match(
        status,
        ("Not Started", rx.badge("Niet gestart", color_scheme="gray", variant="soft")),
        ("In Progress", rx.badge("In uitvoering", color_scheme="yellow", variant="soft")),
        ("Implemented", rx.badge("Geimplementeerd", color_scheme="green", variant="soft")),
        ("Not Applicable", rx.badge("N.v.t.", color_scheme="gray", variant="soft")),
        rx.badge("Onbekend", color_scheme="gray", variant="outline"),
    )


def soa_row(entry: dict) -> rx.Component:
    """Single row in SoA table."""
    return rx.table.row(
        rx.table.cell(
            rx.text(entry["id"], size="2", color="gray"),
        ),
        rx.table.cell(
            rx.vstack(
                rx.text(entry.get("requirement_id", ""), weight="medium", size="2"),
                rx.text(
                    entry.get("justification", ""),
                    size="1",
                    color="gray",
                    no_of_lines=1,
                ),
                align_items="start",
                spacing="0",
            ),
        ),
        rx.table.cell(
            rx.cond(
                entry["is_applicable"],
                rx.badge("Ja", color_scheme="green", variant="soft"),
                rx.badge("Nee", color_scheme="gray", variant="soft"),
            ),
        ),
        rx.table.cell(
            coverage_badge(entry.get("coverage_type", "")),
        ),
        rx.table.cell(
            status_badge(entry.get("implementation_status", "")),
        ),
        rx.table.cell(
            rx.icon_button(
                rx.icon("pencil", size=14),
                variant="ghost",
                size="1",
                on_click=lambda: ComplianceState.open_edit_dialog(entry["id"]),
            ),
        ),
        _hover={"background": "var(--gray-a3)"},
    )


def soa_table() -> rx.Component:
    """SoA entries table."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("ID", width="60px"),
                rx.table.column_header_cell("Requirement"),
                rx.table.column_header_cell("Toepasbaar", width="100px"),
                rx.table.column_header_cell("Dekking", width="120px"),
                rx.table.column_header_cell("Status", width="140px"),
                rx.table.column_header_cell("Acties", width="80px"),
            ),
        ),
        rx.table.body(
            rx.cond(
                ComplianceState.is_loading,
                rx.table.row(
                    rx.table.cell(
                        rx.center(
                            rx.spinner(size="2"),
                            width="100%",
                            padding="40px",
                        ),
                        col_span=6,
                    ),
                ),
                rx.cond(
                    ComplianceState.filtered_entries.length() > 0,
                    rx.foreach(ComplianceState.filtered_entries, soa_row),
                    rx.table.row(
                        rx.table.cell(
                            rx.center(
                                rx.vstack(
                                    rx.icon("file-question", size=32, color="gray"),
                                    rx.text("Geen SoA entries gevonden", color="gray"),
                                    rx.text(
                                        "Selecteer een scope en initialiseer de SoA",
                                        size="2",
                                        color="gray",
                                    ),
                                    spacing="2",
                                ),
                                width="100%",
                                padding="40px",
                            ),
                            col_span=6,
                        ),
                    ),
                ),
            ),
        ),
        width="100%",
    )


def edit_dialog() -> rx.Component:
    """Dialog for editing SoA entry."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("SoA Entry Bewerken"),
            rx.dialog.description(
                "Pas de applicability en implementatiestatus aan.",
                size="2",
                margin_bottom="16px",
            ),

            rx.vstack(
                # Is Applicable
                rx.hstack(
                    rx.text("Toepasbaar:", size="2", weight="medium"),
                    rx.switch(
                        checked=ComplianceState.editing_entry.get("is_applicable", True),
                        on_change=ComplianceState.set_edit_is_applicable,
                    ),
                    spacing="2",
                    align="center",
                ),

                # Implementation Status
                rx.vstack(
                    rx.text("Implementatie Status", size="2", weight="medium"),
                    rx.select.root(
                        rx.select.trigger(placeholder="Selecteer status"),
                        rx.select.content(
                            rx.select.item("Niet gestart", value="Not Started"),
                            rx.select.item("In uitvoering", value="In Progress"),
                            rx.select.item("Geimplementeerd", value="Implemented"),
                            rx.select.item("N.v.t.", value="Not Applicable"),
                        ),
                        value=ComplianceState.editing_entry.get("implementation_status", ""),
                        on_change=ComplianceState.set_edit_implementation_status,
                    ),
                    align_items="start",
                    width="100%",
                ),

                # Justification
                rx.vstack(
                    rx.text("Onderbouwing", size="2", weight="medium"),
                    rx.text_area(
                        placeholder="Waarom is dit wel/niet toepasbaar?",
                        value=ComplianceState.editing_entry.get("justification", ""),
                        on_change=ComplianceState.set_edit_justification,
                        width="100%",
                        rows="2",
                    ),
                    align_items="start",
                    width="100%",
                ),

                # Implementation Notes
                rx.vstack(
                    rx.text("Implementatie Notities", size="2", weight="medium"),
                    rx.text_area(
                        placeholder="Notities over de implementatie...",
                        value=ComplianceState.editing_entry.get("implementation_notes", ""),
                        on_change=ComplianceState.set_edit_implementation_notes,
                        width="100%",
                        rows="3",
                    ),
                    align_items="start",
                    width="100%",
                ),

                spacing="4",
                width="100%",
            ),

            rx.hstack(
                rx.dialog.close(
                    rx.button(
                        "Annuleren",
                        variant="soft",
                        color_scheme="gray",
                        on_click=ComplianceState.close_edit_dialog,
                    ),
                ),
                rx.button(
                    "Opslaan",
                    on_click=ComplianceState.save_entry,
                ),
                spacing="3",
                justify="end",
                margin_top="16px",
            ),

            max_width="500px",
        ),
        open=ComplianceState.show_edit_dialog,
    )


def init_dialog() -> rx.Component:
    """Dialog for initializing SoA from standard."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("SoA Initialiseren"),
            rx.dialog.description(
                "Maak SoA entries aan voor alle requirements uit een standaard.",
                size="2",
                margin_bottom="16px",
            ),

            rx.vstack(
                rx.callout(
                    "Dit maakt voor elke requirement in de geselecteerde standaard een SoA entry aan voor de gekozen scope.",
                    icon="info",
                    color="blue",
                ),

                rx.text(
                    "Selecteer eerst een scope en standaard in de filterbalk hierboven.",
                    size="2",
                    color="gray",
                ),

                spacing="4",
                width="100%",
            ),

            rx.hstack(
                rx.dialog.close(
                    rx.button(
                        "Annuleren",
                        variant="soft",
                        color_scheme="gray",
                        on_click=ComplianceState.close_init_dialog,
                    ),
                ),
                rx.button(
                    "Initialiseren",
                    color_scheme="blue",
                    disabled=~(ComplianceState.selected_scope_id.bool() & ComplianceState.selected_standard_id.bool()),
                    on_click=lambda: ComplianceState.initialize_soa(
                        ComplianceState.selected_scope_id,
                        ComplianceState.selected_standard_id,
                    ),
                ),
                spacing="3",
                justify="end",
                margin_top="16px",
            ),

            max_width="500px",
        ),
        open=ComplianceState.show_init_dialog,
    )


def gaps_section() -> rx.Component:
    """Section showing compliance gaps."""
    return rx.cond(
        ComplianceState.gaps.length() > 0,
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.icon("triangle-alert", size=20, color="var(--red-9)"),
                    rx.heading("Compliance Gaps", size="4"),
                    spacing="2",
                    align="center",
                ),
                rx.text(
                    "Requirements die nog niet gedekt zijn",
                    size="2",
                    color="gray",
                ),
                rx.divider(),
                rx.foreach(
                    ComplianceState.gaps,
                    lambda gap: rx.hstack(
                        rx.badge(gap["requirement_code"], color_scheme="red", variant="outline"),
                        rx.text(gap["requirement_title"], size="2"),
                        spacing="2",
                        padding="8px",
                        _hover={"background": "var(--gray-a2)"},
                        border_radius="md",
                    ),
                ),
                spacing="3",
                align_items="start",
            ),
            padding="16px",
        ),
    )


def compliance_content() -> rx.Component:
    """Compliance page content."""
    return rx.vstack(
        # Success message
        rx.cond(
            ComplianceState.success_message != "",
            rx.callout(
                ComplianceState.success_message,
                icon="circle-check",
                color="green",
                margin_bottom="16px",
            ),
        ),

        # Error message
        rx.cond(
            ComplianceState.error != "",
            rx.callout(
                ComplianceState.error,
                icon="circle-alert",
                color="red",
                margin_bottom="16px",
            ),
        ),

        # Stats row
        rx.cond(
            ComplianceState.selected_scope_id.bool(),
            rx.grid(
                compliance_stat_card(
                    "Totaal Requirements",
                    ComplianceState.total_requirements,
                    "file-text",
                    "blue",
                ),
                compliance_stat_card(
                    "Geimplementeerd",
                    ComplianceState.implemented_count,
                    "circle-check",
                    "green",
                ),
                compliance_stat_card(
                    "In Uitvoering",
                    ComplianceState.in_progress_count,
                    "clock",
                    "yellow",
                ),
                compliance_stat_card(
                    "Gaps",
                    ComplianceState.gaps_count,
                    "triangle-alert",
                    "red",
                ),
                columns="4",
                spacing="4",
                width="100%",
            ),
        ),

        # Progress bar (only if scope selected)
        rx.cond(
            ComplianceState.selected_scope_id.bool(),
            compliance_progress_bar(),
        ),

        # Filter bar
        rx.box(
            rx.card(
                filter_bar(),
                padding="16px",
            ),
            width="100%",
            margin_top="16px",
        ),

        # Main table
        rx.box(
            rx.card(
                soa_table(),
                padding="0",
            ),
            width="100%",
            margin_top="16px",
        ),

        # Gaps section
        rx.cond(
            ComplianceState.selected_scope_id.bool(),
            rx.box(
                gaps_section(),
                width="100%",
                margin_top="16px",
            ),
        ),

        # Dialogs
        edit_dialog(),
        init_dialog(),

        width="100%",
        on_mount=ComplianceState.load_data,
    )


def compliance_page() -> rx.Component:
    """Compliance page with layout."""
    return layout(
        compliance_content(),
        title="Compliance",
        subtitle="Statement of Applicability (SoA) beheer",
    )
