"""
Policies Page - Policy management with workflow states
"""
import reflex as rx
from ims.state.policy import PolicyState
from ims.state.auth import AuthState
from ims.components.layout import layout


def state_badge(state: str) -> rx.Component:
    """Badge for policy state."""
    return rx.match(
        state,
        ("Draft", rx.badge("Concept", color_scheme="gray", variant="soft")),
        ("Review", rx.badge("In Review", color_scheme="yellow", variant="soft")),
        ("Approved", rx.badge("Goedgekeurd", color_scheme="blue", variant="soft")),
        ("Published", rx.badge("Gepubliceerd", color_scheme="green", variant="soft")),
        ("Archived", rx.badge("Gearchiveerd", color_scheme="orange", variant="soft")),
        rx.badge(state, color_scheme="gray", variant="outline"),
    )


def policy_row(policy: dict) -> rx.Component:
    """Single row in policies table."""
    return rx.table.row(
        rx.table.cell(
            rx.text(policy["id"], size="2", color="gray"),
        ),
        rx.table.cell(
            rx.vstack(
                rx.text(policy["title"], weight="medium", size="2"),
                rx.text(
                    policy["content"],
                    size="1",
                    color="gray",
                    no_of_lines=1,
                ),
                align_items="start",
                spacing="0",
            ),
        ),
        rx.table.cell(state_badge(policy["state"])),
        rx.table.cell(
            rx.text(policy["version"], size="2"),
        ),
        rx.table.cell(
            rx.hstack(
                rx.icon_button(
                    rx.icon("pencil", size=14),
                    variant="ghost",
                    size="1",
                    on_click=lambda: PolicyState.open_edit_dialog(policy["id"]),
                ),
                rx.icon_button(
                    rx.icon("trash-2", size=14),
                    variant="ghost",
                    size="1",
                    color_scheme="red",
                    on_click=lambda: PolicyState.open_delete_dialog(policy["id"]),
                ),
                spacing="1",
            ),
        ),
        _hover={"background": "var(--gray-a3)"},
    )


def policy_mobile_card(policy: dict) -> rx.Component:
    """Mobile card view for a single policy."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text(policy["title"], weight="medium", size="2", flex="1"),
                rx.hstack(
                    rx.icon_button(
                        rx.icon("pencil", size=14),
                        variant="ghost",
                        size="1",
                        on_click=lambda: PolicyState.open_edit_dialog(policy["id"]),
                    ),
                    rx.icon_button(
                        rx.icon("trash-2", size=14),
                        variant="ghost",
                        size="1",
                        color_scheme="red",
                        on_click=lambda: PolicyState.open_delete_dialog(policy["id"]),
                    ),
                    spacing="1",
                ),
                width="100%",
                align="center",
            ),
            rx.text(policy["content"], size="1", color="gray", no_of_lines=2),
            rx.hstack(
                state_badge(policy["state"]),
                rx.badge(
                    rx.fragment("v", policy["version"]),
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


def policies_table() -> rx.Component:
    """Policies data table."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("ID", width="60px"),
                rx.table.column_header_cell("Beleid"),
                rx.table.column_header_cell("Status", width="120px"),
                rx.table.column_header_cell("Versie", width="80px"),
                rx.table.column_header_cell("Acties", width="100px"),
            ),
        ),
        rx.table.body(
            rx.cond(
                PolicyState.is_loading,
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
                    PolicyState.policies.length() > 0,
                    rx.foreach(PolicyState.policies, policy_row),
                    rx.table.row(
                        rx.table.cell(
                            rx.center(
                                rx.vstack(
                                    rx.icon("file-text", size=32, color="gray"),
                                    rx.text("Geen beleidsdocumenten gevonden", color="gray"),
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
    """Filter bar for policies."""
    return rx.flex(
        rx.select.root(
            rx.select.trigger(placeholder="Filter op status"),
            rx.select.content(
                rx.select.item("Alle statussen", value="ALLE"),
                rx.select.item("Concept", value="Draft"),
                rx.select.item("In Review", value="Review"),
                rx.select.item("Goedgekeurd", value="Approved"),
                rx.select.item("Gepubliceerd", value="Published"),
                rx.select.item("Gearchiveerd", value="Archived"),
            ),
            value=PolicyState.filter_state,
            on_change=PolicyState.set_filter_state,
            size="2",
            default_value="ALLE",
            width=rx.breakpoints(initial="100%", md="auto"),
        ),
        rx.button(
            rx.icon("x", size=14),
            "Reset filters",
            variant="ghost",
            size="2",
            on_click=PolicyState.clear_filters,
            width=rx.breakpoints(initial="100%", md="auto"),
        ),
        rx.spacer(display=rx.breakpoints(initial="none", md="block")),
        rx.button(
            rx.icon("plus", size=14),
            "Nieuw Beleid",
            size="2",
            on_click=PolicyState.open_create_dialog,
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
                rx.icon("file-pen", size=20, color="var(--gray-9)"),
                rx.vstack(
                    rx.text("Concept", size="1", color="gray"),
                    rx.text(PolicyState.draft_count, size="4", weight="bold"),
                    spacing="0",
                    align_items="start",
                ),
                spacing="3",
            ),
            padding="12px",
        ),
        rx.card(
            rx.hstack(
                rx.icon("clock", size=20, color="var(--yellow-9)"),
                rx.vstack(
                    rx.text("In Review", size="1", color="gray"),
                    rx.text(PolicyState.review_count, size="4", weight="bold"),
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
                    rx.text("Gepubliceerd", size="1", color="gray"),
                    rx.text(PolicyState.published_count, size="4", weight="bold"),
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


def policy_form_dialog() -> rx.Component:
    """Dialog for creating/editing a policy."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(
                    PolicyState.is_editing,
                    "Beleid Bewerken",
                    "Nieuw Beleid",
                ),
            ),
            rx.dialog.description(
                "Beheer beleidsdocumenten en workflows.",
                size="2",
                margin_bottom="16px",
            ),

            rx.cond(
                PolicyState.error != "",
                rx.callout(
                    PolicyState.error,
                    icon="circle-alert",
                    color="red",
                    margin_bottom="16px",
                ),
            ),

            rx.vstack(
                # Basic info
                rx.text("Beleid Details", weight="bold", size="3"),

                rx.vstack(
                    rx.text("Titel *", size="2", weight="medium"),
                    rx.input(
                        placeholder="Bijv. Wachtwoordbeleid",
                        value=PolicyState.form_title,
                        on_change=PolicyState.set_form_title,
                        width="100%",
                    ),
                    align_items="start",
                    width="100%",
                ),

                rx.vstack(
                    rx.text("Inhoud *", size="2", weight="medium"),
                    rx.text_area(
                        placeholder="De tekst van het beleid...",
                        value=PolicyState.form_content,
                        on_change=PolicyState.set_form_content,
                        width="100%",
                        rows="6",
                    ),
                    align_items="start",
                    width="100%",
                ),

                rx.flex(
                    rx.vstack(
                        rx.text("Versie", size="2", weight="medium"),
                        rx.input(
                            placeholder="1.0",
                            value=PolicyState.form_version,
                            on_change=PolicyState.set_form_version,
                            width="100%",
                        ),
                        align_items="start",
                        flex="1",
                        min_width="200px",
                    ),
                    rx.vstack(
                        rx.text("Status", size="2", weight="medium"),
                        rx.select.root(
                            rx.select.trigger(placeholder="Status"),
                            rx.select.content(
                                rx.select.item("Concept", value="Draft"),
                                rx.select.item("In Review", value="Review"),
                                rx.select.item("Goedgekeurd", value="Approved"),
                                rx.select.item("Gepubliceerd", value="Published"),
                                rx.select.item("Gearchiveerd", value="Archived"),
                            ),
                            value=PolicyState.form_state,
                            on_change=PolicyState.set_form_state,
                        ),
                        align_items="start",
                        flex="1",
                        min_width="200px",
                    ),
                    wrap="wrap",
                    gap="3",
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
                        on_click=PolicyState.close_form_dialog,
                    ),
                ),
                rx.button(
                    rx.cond(PolicyState.is_editing, "Opslaan", "Toevoegen"),
                    on_click=PolicyState.save_policy,
                ),
                spacing="3",
                justify="end",
                margin_top="16px",
            ),

            max_width=rx.breakpoints(initial="95vw", md="600px"),
        ),
        open=PolicyState.show_form_dialog,
    )


def delete_confirm_dialog() -> rx.Component:
    """Dialog for confirming policy deletion."""
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Beleid Verwijderen"),
            rx.alert_dialog.description(
                rx.vstack(
                    rx.text("Weet u zeker dat u dit beleid wilt verwijderen?"),
                    rx.text(PolicyState.deleting_policy_title, weight="bold", color="red"),
                    rx.text("Deze actie kan niet ongedaan worden gemaakt.", size="2", color="gray"),
                    spacing="2",
                    align_items="start",
                ),
            ),
            rx.hstack(
                rx.alert_dialog.cancel(
                    rx.button("Annuleren", variant="soft", color_scheme="gray", on_click=PolicyState.close_delete_dialog),
                ),
                rx.alert_dialog.action(
                    rx.button("Verwijderen", color_scheme="red", on_click=PolicyState.confirm_delete),
                ),
                spacing="3",
                justify="end",
                margin_top="16px",
            ),
        ),
        open=PolicyState.show_delete_dialog,
    )


def policies_content() -> rx.Component:
    """Policies page content."""
    return rx.vstack(
        rx.cond(
            PolicyState.success_message != "",
            rx.callout(
                PolicyState.success_message,
                icon="circle-check",
                color="green",
                margin_bottom="16px",
            ),
        ),
        rx.cond(
            PolicyState.error != "",
            rx.callout(
                PolicyState.error,
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
                policies_table(),
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
                    PolicyState.is_loading,
                    rx.center(rx.spinner(size="2"), padding="40px"),
                    rx.cond(
                        PolicyState.policies.length() > 0,
                        rx.foreach(PolicyState.policies, policy_mobile_card),
                        rx.center(rx.text("Geen beleidsdocumenten gevonden", color="gray"), padding="40px"),
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
        policy_form_dialog(),
        delete_confirm_dialog(),

        width="100%",
        spacing="4",
        on_mount=PolicyState.load_policies,
    )


def policies_page() -> rx.Component:
    """Policies page with layout."""
    return layout(
        rx.cond(
            AuthState.can_configure,
            policies_content(),
            rx.callout(
                "Je hebt onvoldoende rechten om deze pagina te bekijken.",
                icon="shield-alert",
                color_scheme="red",
                size="3",
            ),
        ),
        title="Beleid",
        subtitle="Beheer beleidsdocumenten en workflows",
    )
