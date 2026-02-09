"""
Risicokader (Risk Framework) Page — Hiaat 3
"""
import reflex as rx
from ims.state.risk_framework import RiskFrameworkState
from ims.components.layout import layout
from ims.state.auth import AuthState


def framework_card(fw: dict) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(fw["name"], weight="bold", size="3"),
                    rx.text(rx.fragment("Versie ", fw["version"]), size="1", color="gray"),
                    spacing="0", align_items="start",
                ),
                rx.spacer(),
                rx.match(
                    fw["status"],
                    ("Actief", rx.badge("Actief", color_scheme="green", variant="soft")),
                    ("Concept", rx.badge("Concept", color_scheme="yellow", variant="soft")),
                    ("Gearchiveerd", rx.badge("Gearchiveerd", color_scheme="gray", variant="soft")),
                    rx.badge(fw["status"], variant="outline"),
                ),
                width="100%", align="center",
            ),
            rx.divider(),
            rx.hstack(
                rx.icon_button(rx.icon("pencil", size=14), variant="ghost", size="1",
                    on_click=lambda: RiskFrameworkState.open_edit_dialog(fw["id"])),
                rx.icon_button(rx.icon("trash-2", size=14), variant="ghost", size="1", color_scheme="red",
                    on_click=lambda: RiskFrameworkState.open_delete_dialog(fw["id"])),
                spacing="1",
            ),
            spacing="3", width="100%",
        ),
        width="100%",
    )


def framework_form_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(RiskFrameworkState.is_editing, "Risicokader Bewerken", "Nieuw Risicokader"),
            ),
            rx.cond(
                RiskFrameworkState.error != "",
                rx.callout(RiskFrameworkState.error, icon="circle-alert", color="red", margin_bottom="16px"),
            ),
            rx.vstack(
                rx.vstack(
                    rx.text("Naam *", size="2", weight="medium"),
                    rx.input(
                        placeholder="Bijv. IMS Risicokader 2025",
                        value=RiskFrameworkState.form_name,
                        on_change=RiskFrameworkState.set_form_name,
                        width="100%",
                    ),
                    align_items="start", width="100%",
                ),
                rx.vstack(
                    rx.text("Impactdefinities (JSON)", size="2", weight="medium"),
                    rx.text_area(
                        placeholder='{"LOW": {"description": "..."}, ...}',
                        value=RiskFrameworkState.form_impact_definitions,
                        on_change=RiskFrameworkState.set_form_impact_definitions,
                        width="100%", rows="4",
                    ),
                    align_items="start", width="100%",
                ),
                rx.vstack(
                    rx.text("Kansdefinities (JSON)", size="2", weight="medium"),
                    rx.text_area(
                        placeholder='{"LOW": {"description": "..."}, ...}',
                        value=RiskFrameworkState.form_likelihood_definitions,
                        on_change=RiskFrameworkState.set_form_likelihood_definitions,
                        width="100%", rows="4",
                    ),
                    align_items="start", width="100%",
                ),
                rx.vstack(
                    rx.text("Risicotolerantie (JSON)", size="2", weight="medium"),
                    rx.text_area(
                        placeholder='{"threshold": "HIGH", "description": "..."}',
                        value=RiskFrameworkState.form_risk_tolerance,
                        on_change=RiskFrameworkState.set_form_risk_tolerance,
                        width="100%", rows="3",
                    ),
                    align_items="start", width="100%",
                ),
                rx.vstack(
                    rx.text("Beslisregels (JSON)", size="2", weight="medium"),
                    rx.text_area(
                        placeholder='{"dt_decision_required_above": 9}',
                        value=RiskFrameworkState.form_decision_rules,
                        on_change=RiskFrameworkState.set_form_decision_rules,
                        width="100%", rows="2",
                    ),
                    align_items="start", width="100%",
                ),
                spacing="4", width="100%",
            ),
            rx.hstack(
                rx.dialog.close(
                    rx.button("Annuleren", variant="soft", color_scheme="gray", on_click=RiskFrameworkState.close_form_dialog),
                ),
                rx.button(
                    rx.cond(RiskFrameworkState.is_editing, "Opslaan", "Aanmaken"),
                    on_click=RiskFrameworkState.save_framework,
                ),
                spacing="3", justify="end", margin_top="16px",
            ),
            max_width=rx.breakpoints(initial="95vw", md="700px"),
        ),
        open=RiskFrameworkState.show_form_dialog,
    )


def delete_confirm_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Risicokader verwijderen"),
            rx.text("Weet je zeker dat je dit risicokader wilt verwijderen? Dit kan niet ongedaan worden gemaakt.", size="2"),
            rx.hstack(
                rx.dialog.close(
                    rx.button("Annuleren", variant="soft", color_scheme="gray", on_click=RiskFrameworkState.close_delete_dialog),
                ),
                rx.button("Verwijderen", color_scheme="red", on_click=RiskFrameworkState.confirm_delete),
                spacing="3", justify="end", margin_top="16px",
            ),
        ),
        open=RiskFrameworkState.show_delete_dialog,
    )


def risk_framework_content() -> rx.Component:
    return rx.vstack(
        rx.cond(
            RiskFrameworkState.success_message != "",
            rx.callout(RiskFrameworkState.success_message, icon="circle-check", color="green", margin_bottom="16px"),
        ),
        rx.cond(
            RiskFrameworkState.error != "",
            rx.callout(RiskFrameworkState.error, icon="circle-alert", color="red", margin_bottom="16px"),
        ),
        rx.flex(
            rx.spacer(display=rx.breakpoints(initial="none", md="block")),
            rx.button(
                rx.icon("plus", size=14), "Nieuw Risicokader", size="2",
                on_click=RiskFrameworkState.open_create_dialog,
                width=rx.breakpoints(initial="100%", md="auto"),
            ),
            wrap="wrap", gap="2", width="100%",
        ),
        rx.cond(
            RiskFrameworkState.is_loading,
            rx.center(rx.spinner(size="2"), padding="40px"),
            rx.cond(
                RiskFrameworkState.frameworks.length() > 0,
                rx.vstack(
                    rx.foreach(RiskFrameworkState.frameworks, framework_card),
                    spacing="3", width="100%", margin_top="16px",
                ),
                rx.center(
                    rx.vstack(
                        rx.icon("shield", size=32, color="gray"),
                        rx.text("Geen risicokaders gevonden", color="gray"),
                        spacing="2",
                    ),
                    padding="40px",
                ),
            ),
        ),
        framework_form_dialog(),
        delete_confirm_dialog(),
        width="100%",
        on_mount=RiskFrameworkState.load_frameworks,
    )


def _no_access() -> rx.Component:
    return rx.center(
        rx.callout("Je hebt onvoldoende rechten om deze pagina te bekijken.", icon="shield-alert", color_scheme="red"),
        padding="48px",
    )


def risk_framework_page() -> rx.Component:
    return layout(
        rx.cond(AuthState.can_discover, risk_framework_content(), _no_access()),
        title="Risicokader",
        subtitle="Impact- en kansdefinities, risicotolerantie en beslisregels",
    )
