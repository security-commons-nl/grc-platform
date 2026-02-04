"""
Backlog Page - Track improvement requests and ideas
Features Kanban board view with User Story format submissions
"""
import reflex as rx
from ims.components.layout import layout
from ims.state.backlog import BacklogState
from ims.state.auth import AuthState


def status_badge(status: str) -> rx.Component:
    """Return a badge for the status."""
    color_map = {
        "Nieuw": "blue",
        "In Review": "orange",
        "Goedgekeurd": "purple",
        "In Uitvoering": "plum",
        "Gereed": "green",
        "Afgewezen": "red",
    }
    return rx.badge(status, color_scheme=color_map.get(status, "gray"))


def priority_badge(priority: str) -> rx.Component:
    """Return a badge for the priority."""
    color_map = {
        "Laag": "gray",
        "Middel": "blue",
        "Hoog": "orange",
        "Kritiek": "red",
    }
    return rx.badge(priority, color_scheme=color_map.get(priority, "gray"), variant="solid")


def type_badge(item_type: str) -> rx.Component:
    """Return a badge for the item type."""
    icon_map = {
        "Technisch": "code",
        "Functioneel": "layout-list",
        "Proces": "workflow",
        "Tooling": "wrench",
        "Artificial Intelligence": "brain-circuit",
        "Overig": "help-circle",
    }
    return rx.hstack(
        rx.icon(icon_map.get(item_type, "circle"), size=14),
        rx.text(item_type, size="1"),
        spacing="1",
        align_items="center",
        padding="2px 6px",
        background="var(--gray-a3)",
        border_radius="full",
    )


# =============================================================================
# KANBAN COMPONENTS
# =============================================================================

def kanban_card(item: dict) -> rx.Component:
    """Compact card for Kanban board."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                type_badge(item["item_type"]),
                rx.spacer(),
                priority_badge(item["priority"]),
                width="100%",
            ),
            rx.text(
                item["title"],
                weight="medium",
                size="2",
                style={"lineHeight": "1.3"},
            ),
            rx.cond(
                item.get("user_role"),
                rx.text(
                    f"Als {item.get('user_role', '')}...",
                    size="1",
                    color="gray",
                    style={"fontStyle": "italic"},
                ),
            ),
            rx.hstack(
                rx.text(
                    item.get("submitter_name", "Onbekend"),
                    size="1",
                    color="gray",
                ),
                rx.spacer(),
                rx.text(
                    f"#{item['id']}",
                    size="1",
                    color="gray",
                ),
                width="100%",
            ),
            spacing="2",
            width="100%",
            align_items="start",
        ),
        padding="12px",
        background="var(--gray-1)",
        border_radius="8px",
        border="1px solid var(--gray-a5)",
        width="100%",
        cursor="pointer",
        _hover={"background": "var(--gray-2)", "border_color": "var(--accent-8)"},
        on_click=lambda: BacklogState.open_edit_dialog(item["id"]),
    )


def kanban_column(title: str, color: str, items: list) -> rx.Component:
    """Single column in Kanban board."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(
                    width="8px",
                    height="8px",
                    background=f"var(--{color}-9)",
                    border_radius="full",
                ),
                rx.text(title, weight="bold", size="2"),
                rx.badge(
                    rx.cond(items, items.length(), 0),
                    color_scheme=color,
                    variant="soft",
                    size="1",
                ),
                spacing="2",
                align_items="center",
            ),
            rx.divider(),
            rx.vstack(
                rx.foreach(items, kanban_card),
                spacing="2",
                width="100%",
                min_height="200px",
            ),
            spacing="3",
            width="100%",
            align_items="start",
        ),
        padding="12px",
        background="var(--gray-a2)",
        border_radius="12px",
        flex="1",
        min_width="200px",
    )


def kanban_board() -> rx.Component:
    """Full Kanban board with all status columns."""
    return rx.hstack(
        kanban_column("Nieuw", "blue", BacklogState.items_nieuw),
        kanban_column("In Review", "orange", BacklogState.items_review),
        kanban_column("Goedgekeurd", "purple", BacklogState.items_approved),
        kanban_column("In Uitvoering", "plum", BacklogState.items_in_progress),
        kanban_column("Gereed", "green", BacklogState.items_done),
        spacing="4",
        width="100%",
        overflow_x="auto",
        align_items="start",
    )


# =============================================================================
# USER STORY FORM
# =============================================================================

def user_story_form() -> rx.Component:
    """User Story format form for normal users."""
    return rx.vstack(
        rx.text("Vanuit mijn rol als...", size="2", weight="bold", color="gray"),
        rx.select(
            ["Process Owner", "Editor", "Viewer", "Risk Owner", "Admin", "Auditor"],
            value=BacklogState.form_user_role,
            on_change=BacklogState.set_form_user_role,
            placeholder="Selecteer je rol",
        ),
        
        rx.text("...wil ik...", size="2", weight="bold", color="gray"),
        rx.text_area(
            placeholder="Beschrijf wat je wilt kunnen doen...",
            value=BacklogState.form_user_want,
            on_change=BacklogState.set_form_user_want,
            rows=2,
        ),
        
        rx.text("...zodat ik...", size="2", weight="bold", color="gray"),
        rx.text_area(
            placeholder="Beschrijf het doel of de waarde...",
            value=BacklogState.form_user_so_that,
            on_change=BacklogState.set_form_user_so_that,
            rows=2,
        ),
        
        rx.text("Type", size="2", weight="bold"),
        rx.select(
            ["Technisch", "Functioneel", "Proces", "Tooling", "Artificial Intelligence", "Overig"],
            value=BacklogState.form_type,
            on_change=BacklogState.set_form_type,
        ),
        
        spacing="3",
        width="100%",
    )


def admin_form_extras() -> rx.Component:
    """Additional form fields for admin users."""
    return rx.vstack(
        rx.divider(),
        rx.text("Admin Instellingen", size="2", weight="bold", color="tomato"),
        rx.hstack(
            rx.vstack(
                rx.text("Prioriteit", size="1"),
                rx.select(
                    ["Laag", "Middel", "Hoog", "Kritiek"],
                    value=BacklogState.form_priority,
                    on_change=BacklogState.set_form_priority,
                ),
                width="50%",
            ),
            rx.vstack(
                rx.text("Status", size="1"),
                rx.select(
                    ["Nieuw", "In Review", "Goedgekeurd", "In Uitvoering", "Gereed", "Afgewezen"],
                    value=BacklogState.form_status,
                    on_change=BacklogState.set_form_status,
                ),
                width="50%",
            ),
            width="100%",
        ),
        width="100%",
        spacing="2",
        padding_top="10px",
    )


def form_dialog() -> rx.Component:
    """Dialog for creating/editing backlog items."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(BacklogState.is_editing, "Item Bekijken", "Nieuw Verzoek")
            ),
            rx.dialog.description(
                rx.cond(
                    BacklogState.is_editing,
                    "Details van dit backlog item.",
                    "Beschrijf je wens in User Story formaat."
                )
            ),
            rx.vstack(
                user_story_form(),
                
                # Admin controls (alleen voor superuser)
                rx.cond(
                    AuthState.is_admin,
                    admin_form_extras(),
                ),
                
                rx.cond(
                    BacklogState.error != "",
                    rx.callout(
                        BacklogState.error,
                        icon="triangle-alert",
                        color_scheme="red",
                        role="alert",
                    ),
                ),
                
                spacing="3",
                margin_top="16px",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button("Annuleren", variant="soft", color_scheme="gray", on_click=BacklogState.close_form_dialog),
                ),
                rx.dialog.close(
                    rx.button("Opslaan", on_click=BacklogState.save_item),
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
        ),
        open=BacklogState.show_form_dialog,
        on_open_change=BacklogState.close_form_dialog,
    )


def delete_dialog() -> rx.Component:
    """Confirmation dialog for deletion."""
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Item verwijderen"),
            rx.alert_dialog.description(
                f"Weet je zeker dat je '{BacklogState.deleting_item_title}' wilt verwijderen?"
            ),
            rx.flex(
                rx.alert_dialog.cancel(
                    rx.button("Annuleren", variant="soft", color_scheme="gray", on_click=BacklogState.close_delete_dialog),
                ),
                rx.alert_dialog.action(
                    rx.button("Verwijderen", color_scheme="red", on_click=BacklogState.confirm_delete),
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
        ),
        open=BacklogState.show_delete_dialog,
    )


def backlog_page() -> rx.Component:
    """Main backlog page with Kanban board."""
    return layout(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text("Productbacklog", size="1", color="gray"),
                    rx.text(
                        "Bekijk de status van alle verzoeken en verbeteringen",
                        size="2",
                        color="gray",
                    ),
                    spacing="0",
                    align_items="start",
                ),
                rx.spacer(),
                rx.select(
                    ["ALLE", "Technisch", "Functioneel", "Proces", "Tooling", "Artificial Intelligence", "Overig"],
                    value=BacklogState.filter_type,
                    on_change=BacklogState.set_filter_type,
                    placeholder="Type",
                    size="2",
                ),
                rx.button(
                    rx.icon("plus", size=16),
                    "Nieuw Verzoek",
                    on_click=BacklogState.open_create_dialog,
                ),
                width="100%",
                spacing="3",
                align_items="center",
            ),
            
            rx.divider(),
            
            rx.cond(
                BacklogState.is_loading,
                rx.center(rx.spinner(), padding="40px", width="100%"),
                rx.cond(
                    BacklogState.items,
                    kanban_board(),
                    rx.center(
                        rx.vstack(
                            rx.icon("clipboard-list", size=48, color="gray"),
                            rx.text("Geen backlog items gevonden", color="gray"),
                            rx.text("Klik op 'Nieuw Verzoek' om er een toe te voegen.", size="1", color="gray"),
                        ),
                        width="100%",
                        padding="60px",
                    ),
                )
            ),
            
            form_dialog(),
            delete_dialog(),
            
            width="100%",
            spacing="4",
        ),
        title="Backlog",
        subtitle="Verzoeken, verbeteringen en ideeën voor het IMS"
    )
