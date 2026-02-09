"""
Besluitlog (Decision Log) Page — Hiaat 1
"""
import reflex as rx
from ims.state.decision import DecisionState
from ims.state.auth import AuthState
from ims.components.layout import layout


def decision_form_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(DecisionState.is_editing, "Besluit Bewerken", "Nieuw Besluit"),
            ),
            rx.dialog.description(
                "Leg een formeel DT-besluit vast.", size="2", margin_bottom="16px",
            ),
            rx.cond(
                DecisionState.error != "",
                rx.callout(DecisionState.error, icon="circle-alert", color="red", margin_bottom="16px"),
            ),
            rx.vstack(
                # Type
                rx.vstack(
                    rx.text("Type besluit *", size="2", weight="medium"),
                    rx.select.root(
                        rx.select.trigger(placeholder="Selecteer type"),
                        rx.select.content(
                            rx.select.item("Restrisico-acceptatie", value="Restrisico-acceptatie"),
                            rx.select.item("Prioritering", value="Prioritering"),
                            rx.select.item("Afwijking", value="Afwijking"),
                            rx.select.item("Scopewijziging", value="Scopewijziging"),
                            rx.select.item("Beleidsgoedkeuring", value="Beleidsgoedkeuring"),
                        ),
                        value=DecisionState.form_decision_type,
                        on_change=DecisionState.set_form_decision_type,
                    ),
                    align_items="start", width="100%",
                ),
                # Decision text
                rx.vstack(
                    rx.text("Besluittekst *", size="2", weight="medium"),
                    rx.text_area(
                        placeholder="Beschrijf het besluit...",
                        value=DecisionState.form_decision_text,
                        on_change=DecisionState.set_form_decision_text,
                        width="100%", rows="4",
                    ),
                    align_items="start", width="100%",
                ),
                # Valid until
                rx.vstack(
                    rx.text("Geldig tot", size="2", weight="medium"),
                    rx.input(
                        type="date",
                        placeholder="Verloopdatum",
                        value=DecisionState.form_valid_until,
                        on_change=DecisionState.set_form_valid_until,
                        width="100%",
                    ),
                    align_items="start", width="100%",
                ),
                # Justification
                rx.vstack(
                    rx.text("Onderbouwing", size="2", weight="medium"),
                    rx.text_area(
                        placeholder="Waarom dit besluit?",
                        value=DecisionState.form_justification,
                        on_change=DecisionState.set_form_justification,
                        width="100%", rows="2",
                    ),
                    align_items="start", width="100%",
                ),
                spacing="4", width="100%",
            ),
            rx.hstack(
                rx.dialog.close(
                    rx.button("Annuleren", variant="soft", color_scheme="gray", on_click=DecisionState.close_form_dialog),
                ),
                rx.button(
                    rx.cond(DecisionState.is_editing, "Opslaan", "Vastleggen"),
                    on_click=DecisionState.save_decision,
                ),
                spacing="3", justify="end", margin_top="16px",
            ),
            max_width=rx.breakpoints(initial="95vw", md="600px"),
        ),
        open=DecisionState.show_form_dialog,
    )


def delete_confirm_dialog() -> rx.Component:
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Besluit Verwijderen"),
            rx.alert_dialog.description(
                rx.vstack(
                    rx.text("Weet u zeker dat u dit besluit wilt verwijderen?"),
                    rx.text(DecisionState.deleting_title, weight="bold", color="red"),
                    spacing="2", align_items="start",
                ),
            ),
            rx.hstack(
                rx.alert_dialog.cancel(
                    rx.button("Annuleren", variant="soft", color_scheme="gray", on_click=DecisionState.close_delete_dialog),
                ),
                rx.alert_dialog.action(
                    rx.button("Verwijderen", color_scheme="red", on_click=DecisionState.confirm_delete),
                ),
                spacing="3", justify="end", margin_top="16px",
            ),
        ),
        open=DecisionState.show_delete_dialog,
    )


def decision_row(decision: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(rx.text(decision["id"], size="2", color="gray")),
        rx.table.cell(
            rx.vstack(
                rx.text(decision["decision_text"], weight="medium", size="2", no_of_lines=2),
                spacing="0", align_items="start",
            ),
        ),
        rx.table.cell(
            rx.badge(decision["decision_type"], variant="soft", size="1"),
        ),
        rx.table.cell(
            rx.match(
                decision["status"],
                ("Actief", rx.badge("Actief", color_scheme="green", variant="soft")),
                ("Verlopen", rx.badge("Verlopen", color_scheme="orange", variant="soft")),
                ("Ingetrokken", rx.badge("Ingetrokken", color_scheme="red", variant="soft")),
                ("Vervangen", rx.badge("Vervangen", color_scheme="gray", variant="soft")),
                rx.badge(decision["status"], variant="outline"),
            ),
        ),
        rx.table.cell(
            rx.text(decision["decision_date"], size="1", color="gray"),
        ),
        rx.table.cell(
            rx.hstack(
                rx.cond(
                    AuthState.can_edit,
                    rx.icon_button(rx.icon("pencil", size=14), variant="ghost", size="1",
                        on_click=lambda: DecisionState.open_edit_dialog(decision["id"])),
                ),
                rx.cond(
                    AuthState.can_edit,
                    rx.icon_button(rx.icon("trash-2", size=14), variant="ghost", size="1", color_scheme="red",
                        on_click=lambda: DecisionState.open_delete_dialog(decision["id"])),
                ),
                spacing="1",
            ),
        ),
        _hover={"background": "var(--gray-a3)"},
    )


def decision_mobile_card(decision: dict) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text(decision["decision_text"], weight="medium", size="2", flex="1", no_of_lines=2),
                rx.hstack(
                    rx.icon_button(rx.icon("pencil", size=14), variant="ghost", size="1",
                        on_click=lambda: DecisionState.open_edit_dialog(decision["id"])),
                    rx.icon_button(rx.icon("trash-2", size=14), variant="ghost", size="1", color_scheme="red",
                        on_click=lambda: DecisionState.open_delete_dialog(decision["id"])),
                    spacing="1",
                ),
                width="100%", align="center",
            ),
            rx.hstack(
                rx.badge(decision["decision_type"], variant="soft", size="1"),
                rx.match(
                    decision["status"],
                    ("Actief", rx.badge("Actief", color_scheme="green", variant="soft", size="1")),
                    ("Verlopen", rx.badge("Verlopen", color_scheme="orange", variant="soft", size="1")),
                    rx.badge(decision["status"], variant="outline", size="1"),
                ),
                spacing="2", wrap="wrap",
            ),
            spacing="2", width="100%",
        ),
        width="100%",
    )


def decisions_content() -> rx.Component:
    return rx.vstack(
        rx.cond(
            DecisionState.success_message != "",
            rx.callout(DecisionState.success_message, icon="circle-check", color="green", margin_bottom="16px"),
        ),
        rx.cond(
            DecisionState.error != "",
            rx.callout(DecisionState.error, icon="circle-alert", color="red", margin_bottom="16px"),
        ),
        # Action bar
        rx.flex(
            rx.spacer(display=rx.breakpoints(initial="none", md="block")),
            rx.cond(
                AuthState.can_edit,
                rx.button(
                    rx.icon("plus", size=14), "Nieuw Besluit", size="2",
                    on_click=DecisionState.open_create_dialog,
                    width=rx.breakpoints(initial="100%", md="auto"),
                ),
            ),
            wrap="wrap", gap="2", width="100%",
        ),
        # Desktop table
        rx.box(
            rx.card(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("ID", width="60px"),
                            rx.table.column_header_cell("Besluit"),
                            rx.table.column_header_cell("Type", width="160px"),
                            rx.table.column_header_cell("Status", width="120px"),
                            rx.table.column_header_cell("Datum", width="120px"),
                            rx.table.column_header_cell("Acties", width="100px"),
                        ),
                    ),
                    rx.table.body(
                        rx.cond(
                            DecisionState.is_loading,
                            rx.table.row(rx.table.cell(rx.center(rx.spinner(size="2"), padding="40px"), col_span=6)),
                            rx.cond(
                                DecisionState.decisions.length() > 0,
                                rx.foreach(DecisionState.decisions, decision_row),
                                rx.table.row(rx.table.cell(
                                    rx.center(rx.vstack(
                                        rx.icon("inbox", size=32, color="gray"),
                                        rx.text("Geen besluiten gevonden", color="gray"),
                                        spacing="2",
                                    ), padding="40px"),
                                    col_span=6,
                                )),
                            ),
                        ),
                    ),
                    width="100%",
                ),
                padding="0",
            ),
            width="100%", margin_top="16px", display=rx.breakpoints(initial="none", md="block"),
        ),
        # Mobile cards
        rx.box(
            rx.vstack(
                rx.cond(
                    DecisionState.is_loading,
                    rx.center(rx.spinner(size="2"), padding="40px"),
                    rx.cond(
                        DecisionState.decisions.length() > 0,
                        rx.foreach(DecisionState.decisions, decision_mobile_card),
                        rx.center(rx.text("Geen besluiten gevonden", color="gray"), padding="40px"),
                    ),
                ),
                spacing="2", width="100%",
            ),
            width="100%", margin_top="16px", display=rx.breakpoints(initial="block", md="none"),
        ),
        decision_form_dialog(),
        delete_confirm_dialog(),
        width="100%",
        on_mount=DecisionState.load_decisions,
    )


def _no_access() -> rx.Component:
    return rx.center(
        rx.callout("Je hebt onvoldoende rechten om deze pagina te bekijken.", icon="shield-alert", color_scheme="red"),
        padding="48px",
    )


def decisions_page() -> rx.Component:
    return layout(
        rx.cond(AuthState.can_configure, decisions_content(), _no_access()),
        title="Besluitlog",
        subtitle="Formele DT-besluiten en risicoacceptaties",
    )
