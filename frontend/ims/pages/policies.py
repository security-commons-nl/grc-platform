"""
Policies Page - Policy management with workflow states
"""
import reflex as rx
from ims.state.policy import PolicyState
from ims.components.layout import layout


def state_badge(state: str) -> rx.Component:
    """Badge for policy state."""
    return rx.match(
        state,
        ("DRAFT", rx.badge("Concept", color_scheme="gray", variant="soft")),
        ("REVIEW", rx.badge("In Review", color_scheme="yellow", variant="soft")),
        ("APPROVED", rx.badge("Goedgekeurd", color_scheme="blue", variant="soft")),
        ("PUBLISHED", rx.badge("Gepubliceerd", color_scheme="green", variant="soft")),
        ("ARCHIVED", rx.badge("Gearchiveerd", color_scheme="orange", variant="soft")),
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
                    rx.icon("eye", size=14),
                    variant="ghost",
                    size="1",
                ),
                rx.icon_button(
                    rx.icon("pencil", size=14),
                    variant="ghost",
                    size="1",
                ),
                spacing="1",
            ),
        ),
        _hover={"background": "var(--gray-a3)"},
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
    return rx.hstack(
        rx.select.root(
            rx.select.trigger(placeholder="Filter op status"),
            rx.select.content(
                rx.select.item("Alle statussen", value="ALLE"),
                rx.select.item("Concept", value="DRAFT"),
                rx.select.item("In Review", value="REVIEW"),
                rx.select.item("Goedgekeurd", value="APPROVED"),
                rx.select.item("Gepubliceerd", value="PUBLISHED"),
                rx.select.item("Gearchiveerd", value="ARCHIVED"),
            ),
            value=PolicyState.filter_state,
            on_change=PolicyState.set_filter_state,
            size="2",
            default_value="ALLE",
        ),
        rx.button(
            rx.icon("x", size=14),
            "Reset filters",
            variant="ghost",
            size="2",
            on_click=PolicyState.clear_filters,
        ),
        rx.spacer(),
        rx.button(
            rx.icon("plus", size=14),
            "Nieuw Beleid",
            size="2",
        ),
        width="100%",
        spacing="2",
    )


def stat_cards() -> rx.Component:
    """Statistics cards."""
    return rx.hstack(
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
        spacing="3",
        width="100%",
    )


def policies_content() -> rx.Component:
    """Policies page content."""
    return rx.vstack(
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
        rx.box(
            rx.card(
                policies_table(),
                padding="0",
            ),
            width="100%",
            margin_top="16px",
        ),
        width="100%",
        spacing="4",
        on_mount=PolicyState.load_policies,
    )


def policies_page() -> rx.Component:
    """Policies page with layout."""
    return layout(
        policies_content(),
        title="Beleid",
        subtitle="Beheer beleidsdocumenten en workflows",
    )
