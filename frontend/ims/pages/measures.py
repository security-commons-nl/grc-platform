"""
Measures Page - Control measures management
"""
import reflex as rx
from ims.state.measure import MeasureState
from ims.components.layout import layout


def control_type_badge(control_type: str) -> rx.Component:
    """Badge for control type."""
    return rx.match(
        control_type,
        ("Preventive", rx.badge("Preventief", color_scheme="blue", variant="soft")),
        ("Detective", rx.badge("Detectief", color_scheme="yellow", variant="soft")),
        ("Corrective", rx.badge("Correctief", color_scheme="orange", variant="soft")),
        rx.badge("-", color_scheme="gray", variant="outline"),
    )


def measure_row(measure: dict) -> rx.Component:
    """Single row in measures table."""
    return rx.table.row(
        rx.table.cell(
            rx.text(measure["id"], size="2", color="gray"),
        ),
        rx.table.cell(
            rx.vstack(
                rx.text(measure["name"], weight="medium", size="2"),
                rx.text(
                    measure["description"],
                    size="1",
                    color="gray",
                    no_of_lines=1,
                ),
                align_items="start",
                spacing="0",
            ),
        ),
        rx.table.cell(control_type_badge(measure["control_type"])),
        rx.table.cell(
            rx.cond(
                measure["typical_effectiveness"] != None,
                rx.hstack(
                    rx.text(measure["typical_effectiveness"], size="2"),
                    rx.text("%", size="2", color="gray"),
                    spacing="0",
                ),
                rx.text("-", size="2", color="gray"),
            ),
        ),
        rx.table.cell(
            rx.hstack(
                rx.icon_button(
                    rx.icon("pencil", size=14),
                    variant="ghost",
                    size="1",
                    on_click=lambda: MeasureState.open_edit_dialog(measure["id"]),
                ),
                rx.icon_button(
                    rx.icon("trash-2", size=14),
                    variant="ghost",
                    size="1",
                    color_scheme="red",
                    on_click=lambda: MeasureState.open_delete_dialog(measure["id"]),
                ),
                spacing="1",
            ),
        ),
        _hover={"background": "var(--gray-a3)"},
    )


def measure_mobile_card(measure: dict) -> rx.Component:
    """Mobile card view for a single measure."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text(measure["name"], weight="medium", size="2", flex="1"),
                rx.hstack(
                    rx.icon_button(
                        rx.icon("pencil", size=14),
                        variant="ghost",
                        size="1",
                        on_click=lambda: MeasureState.open_edit_dialog(measure["id"]),
                    ),
                    rx.icon_button(
                        rx.icon("trash-2", size=14),
                        variant="ghost",
                        size="1",
                        color_scheme="red",
                        on_click=lambda: MeasureState.open_delete_dialog(measure["id"]),
                    ),
                    spacing="1",
                ),
                width="100%",
                align="center",
            ),
            rx.text(measure["description"], size="1", color="gray", no_of_lines=2),
            rx.hstack(
                control_type_badge(measure["control_type"]),
                spacing="2",
                wrap="wrap",
            ),
            spacing="2",
            width="100%",
        ),
        width="100%",
    )


def measures_table() -> rx.Component:
    """Measures data table."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("ID", width="60px"),
                rx.table.column_header_cell("Maatregel"),
                rx.table.column_header_cell("Type", width="120px"),
                rx.table.column_header_cell("Effectiviteit", width="120px"),
                rx.table.column_header_cell("Acties", width="100px"),
            ),
        ),
        rx.table.body(
            rx.cond(
                MeasureState.is_loading,
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
                    MeasureState.measures.length() > 0,
                    rx.foreach(MeasureState.measures, measure_row),
                    rx.table.row(
                        rx.table.cell(
                            rx.center(
                                rx.vstack(
                                    rx.icon("shield", size=32, color="gray"),
                                    rx.text("Geen maatregelen gevonden", color="gray"),
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
    """Filter bar for measures."""
    return rx.flex(
        rx.input(
            placeholder="Zoek maatregel...",
            width=rx.breakpoints(initial="100%", md="auto"),
            style={"min_width": "200px"},
        ),
        rx.spacer(display=rx.breakpoints(initial="none", md="block")),
        rx.button(
            rx.icon("plus", size=14),
            "Nieuwe Maatregel",
            size="2",
            on_click=MeasureState.open_create_dialog,
            width=rx.breakpoints(initial="100%", md="auto"),
        ),
        wrap="wrap",
        gap="2",
        width="100%",
    )


def stat_cards() -> rx.Component:
    """Statistics cards."""
    return rx.hstack(
        rx.card(
            rx.hstack(
                rx.icon("shield", size=20, color="var(--blue-9)"),
                rx.vstack(
                    rx.text("Totaal Maatregelen", size="1", color="gray"),
                    rx.text(MeasureState.measures.length(), size="4", weight="bold"),
                    spacing="0",
                    align_items="start",
                ),
                spacing="3",
            ),
            padding="12px",
        ),
        spacing="3",
        width="100%",
    )


def measure_form_dialog() -> rx.Component:
    """Dialog for creating/editing a measure."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(
                    MeasureState.is_editing,
                    "Maatregel Bewerken",
                    "Nieuwe Maatregel",
                ),
            ),
            rx.dialog.description(
                "Beheer beveiligingsmaatregelen en controls.",
                size="2",
                margin_bottom="16px",
            ),

            rx.cond(
                MeasureState.error != "",
                rx.callout(
                    MeasureState.error,
                    icon="circle-alert",
                    color="red",
                    margin_bottom="16px",
                ),
            ),

            rx.vstack(
                # Basic info
                rx.text("Maatregel Details", weight="bold", size="3"),

                rx.vstack(
                    rx.text("Naam *", size="2", weight="medium"),
                    rx.input(
                        placeholder="Bijv. Multifactor authenticatie",
                        value=MeasureState.form_name,
                        on_change=MeasureState.set_form_name,
                        width="100%",
                    ),
                    align_items="start",
                    width="100%",
                ),

                rx.vstack(
                    rx.text("Beschrijving *", size="2", weight="medium"),
                    rx.text_area(
                        placeholder="Wat houdt deze maatregel in?",
                        value=MeasureState.form_description,
                        on_change=MeasureState.set_form_description,
                        width="100%",
                        rows="3",
                    ),
                    align_items="start",
                    width="100%",
                ),

                rx.vstack(
                    rx.text("Type Control", size="2", weight="medium"),
                    rx.select.root(
                        rx.select.trigger(placeholder="Type"),
                        rx.select.content(
                            rx.select.item("Preventief", value="Preventive"),
                            rx.select.item("Detectief", value="Detective"),
                            rx.select.item("Correctief", value="Corrective"),
                        ),
                        value=MeasureState.form_control_type,
                        on_change=MeasureState.set_form_control_type,
                    ),
                    align_items="start",
                    width="100%",
                ),

                spacing="3",
                width="100%",
            ),

            rx.hstack(
                rx.dialog.close(
                    rx.button(
                        "Annuleren",
                        variant="soft",
                        color_scheme="gray",
                        on_click=MeasureState.close_form_dialog,
                    ),
                ),
                rx.button(
                    rx.cond(MeasureState.is_editing, "Opslaan", "Toevoegen"),
                    on_click=MeasureState.save_measure,
                ),
                spacing="3",
                justify="end",
                margin_top="16px",
            ),

            max_width=rx.breakpoints(initial="95vw", md="550px"),
        ),
        open=MeasureState.show_form_dialog,
    )


def delete_confirm_dialog() -> rx.Component:
    """Dialog for confirming measure deletion."""
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Maatregel Verwijderen"),
            rx.alert_dialog.description(
                rx.vstack(
                    rx.text("Weet u zeker dat u deze maatregel wilt verwijderen?"),
                    rx.text(MeasureState.deleting_measure_name, weight="bold", color="red"),
                    rx.text("Deze actie kan niet ongedaan worden gemaakt.", size="2", color="gray"),
                    spacing="2",
                    align_items="start",
                ),
            ),
            rx.hstack(
                rx.alert_dialog.cancel(
                    rx.button("Annuleren", variant="soft", color_scheme="gray", on_click=MeasureState.close_delete_dialog),
                ),
                rx.alert_dialog.action(
                    rx.button("Verwijderen", color_scheme="red", on_click=MeasureState.confirm_delete),
                ),
                spacing="3",
                justify="end",
                margin_top="16px",
            ),
        ),
        open=MeasureState.show_delete_dialog,
    )


def measures_content() -> rx.Component:
    """Measures page content."""
    return rx.vstack(
        rx.cond(
            MeasureState.success_message != "",
            rx.callout(
                MeasureState.success_message,
                icon="circle-check",
                color="green",
                margin_bottom="16px",
            ),
        ),
        rx.cond(
            MeasureState.error != "",
            rx.callout(
                MeasureState.error,
                icon="circle-alert",
                color="red",
                margin_bottom="16px",
            ),
        ),
        stat_cards(),
        filter_bar(),
        # Table (desktop)
        rx.box(
            rx.card(
                measures_table(),
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
                    MeasureState.is_loading,
                    rx.center(rx.spinner(size="2"), padding="40px"),
                    rx.cond(
                        MeasureState.measures.length() > 0,
                        rx.foreach(MeasureState.measures, measure_mobile_card),
                        rx.center(rx.text("Geen maatregelen gevonden", color="gray"), padding="40px"),
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
        measure_form_dialog(),
        delete_confirm_dialog(),
        
        width="100%",
        spacing="4",
        on_mount=MeasureState.load_measures,
    )


def measures_page() -> rx.Component:
    """Measures page with layout."""
    return layout(
        measures_content(),
        title="Maatregelen",
        subtitle="Beheersmaatregelen en controles",
    )
