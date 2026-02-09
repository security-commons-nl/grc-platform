"""
Beleidsuitgangspunten (Policy Principles) Page — Hiaat 6
Traceability: Policy → Principle → Risk → Control
"""
import reflex as rx
from ims.state.policy_principle import PolicyPrincipleState
from ims.components.layout import layout
from ims.state.auth import AuthState


def principle_card(principle: dict) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.hstack(
                        rx.badge(principle["code"], variant="solid", size="1"),
                        rx.text(principle["title"], weight="bold", size="3"),
                        spacing="2", align="center",
                    ),
                    rx.cond(
                        principle["description"],
                        rx.text(principle["description"], size="1", color="gray", no_of_lines=2),
                        rx.fragment(),
                    ),
                    spacing="1", align_items="start",
                ),
                rx.spacer(),
                rx.hstack(
                    rx.icon_button(rx.icon("pencil", size=14), variant="ghost", size="1",
                        on_click=lambda: PolicyPrincipleState.open_edit_dialog(principle["id"])),
                    rx.icon_button(rx.icon("trash-2", size=14), variant="ghost", size="1", color_scheme="red",
                        on_click=lambda: PolicyPrincipleState.open_delete_dialog(principle["id"])),
                    spacing="1",
                ),
                width="100%", align="center",
            ),
            spacing="2", width="100%",
        ),
        width="100%",
    )


def principle_form_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(PolicyPrincipleState.is_editing, "Uitgangspunt Bewerken", "Nieuw Uitgangspunt"),
            ),
            rx.cond(
                PolicyPrincipleState.error != "",
                rx.callout(PolicyPrincipleState.error, icon="circle-alert", color="red", margin_bottom="16px"),
            ),
            rx.vstack(
                rx.vstack(
                    rx.text("Code *", size="2", weight="medium"),
                    rx.input(
                        placeholder="Bijv. ISB-01",
                        value=PolicyPrincipleState.form_code,
                        on_change=PolicyPrincipleState.set_form_code,
                        width="100%",
                    ),
                    align_items="start", width="100%",
                ),
                rx.vstack(
                    rx.text("Titel *", size="2", weight="medium"),
                    rx.input(
                        placeholder="Bijv. Gegevensclassificatie is verplicht",
                        value=PolicyPrincipleState.form_title,
                        on_change=PolicyPrincipleState.set_form_title,
                        width="100%",
                    ),
                    align_items="start", width="100%",
                ),
                rx.vstack(
                    rx.text("Beleid *", size="2", weight="medium"),
                    rx.select.root(
                        rx.select.trigger(placeholder="Selecteer beleid"),
                        rx.select.content(
                            rx.foreach(
                                PolicyPrincipleState.policies,
                                lambda p: rx.select.item(p["title"], value=p["id"].to(str)),
                            ),
                        ),
                        value=PolicyPrincipleState.form_policy_id,
                        on_change=PolicyPrincipleState.set_form_policy_id,
                    ),
                    align_items="start", width="100%",
                ),
                rx.vstack(
                    rx.text("Omschrijving", size="2", weight="medium"),
                    rx.text_area(
                        placeholder="Nadere toelichting op dit uitgangspunt...",
                        value=PolicyPrincipleState.form_description,
                        on_change=PolicyPrincipleState.set_form_description,
                        width="100%", rows="3",
                    ),
                    align_items="start", width="100%",
                ),
                spacing="4", width="100%",
            ),
            rx.hstack(
                rx.dialog.close(
                    rx.button("Annuleren", variant="soft", color_scheme="gray", on_click=PolicyPrincipleState.close_form_dialog),
                ),
                rx.button(
                    rx.cond(PolicyPrincipleState.is_editing, "Opslaan", "Aanmaken"),
                    on_click=PolicyPrincipleState.save_principle,
                ),
                spacing="3", justify="end", margin_top="16px",
            ),
            max_width=rx.breakpoints(initial="95vw", md="600px"),
        ),
        open=PolicyPrincipleState.show_form_dialog,
    )


def delete_confirm_dialog() -> rx.Component:
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Uitgangspunt Verwijderen"),
            rx.alert_dialog.description(
                rx.vstack(
                    rx.text("Weet u zeker dat u dit uitgangspunt wilt verwijderen?"),
                    rx.text(PolicyPrincipleState.deleting_title, weight="bold", color="red"),
                    spacing="2", align_items="start",
                ),
            ),
            rx.hstack(
                rx.alert_dialog.cancel(
                    rx.button("Annuleren", variant="soft", color_scheme="gray", on_click=PolicyPrincipleState.close_delete_dialog),
                ),
                rx.alert_dialog.action(
                    rx.button("Verwijderen", color_scheme="red", on_click=PolicyPrincipleState.confirm_delete),
                ),
                spacing="3", justify="end", margin_top="16px",
            ),
        ),
        open=PolicyPrincipleState.show_delete_dialog,
    )


def policy_principles_content() -> rx.Component:
    return rx.vstack(
        rx.cond(
            PolicyPrincipleState.success_message != "",
            rx.callout(PolicyPrincipleState.success_message, icon="circle-check", color="green", margin_bottom="16px"),
        ),
        rx.cond(
            PolicyPrincipleState.error != "",
            rx.callout(PolicyPrincipleState.error, icon="circle-alert", color="red", margin_bottom="16px"),
        ),
        rx.flex(
            rx.spacer(display=rx.breakpoints(initial="none", md="block")),
            rx.button(
                rx.icon("plus", size=14), "Nieuw Uitgangspunt", size="2",
                on_click=PolicyPrincipleState.open_create_dialog,
                width=rx.breakpoints(initial="100%", md="auto"),
            ),
            wrap="wrap", gap="2", width="100%",
        ),
        rx.cond(
            PolicyPrincipleState.is_loading,
            rx.center(rx.spinner(size="2"), padding="40px"),
            rx.cond(
                PolicyPrincipleState.principles.length() > 0,
                rx.vstack(
                    rx.foreach(PolicyPrincipleState.principles, principle_card),
                    spacing="3", width="100%", margin_top="16px",
                ),
                rx.center(
                    rx.vstack(
                        rx.icon("link-2", size=32, color="gray"),
                        rx.text("Geen uitgangspunten gevonden", color="gray"),
                        spacing="2",
                    ),
                    padding="40px",
                ),
            ),
        ),
        principle_form_dialog(),
        delete_confirm_dialog(),
        width="100%",
        on_mount=PolicyPrincipleState.load_principles,
    )


def _no_access() -> rx.Component:
    return rx.center(
        rx.callout("Je hebt onvoldoende rechten om deze pagina te bekijken.", icon="shield-alert", color_scheme="red"),
        padding="48px",
    )


def policy_principles_page() -> rx.Component:
    return layout(
        rx.cond(AuthState.can_discover, policy_principles_content(), _no_access()),
        title="Beleidsuitgangspunten",
        subtitle="Traceerbaarheid: Beleid \u2192 Uitgangspunt \u2192 Risico \u2192 Control",
    )
