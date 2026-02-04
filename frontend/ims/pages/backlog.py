"""
Backlog Page - Track improvement requests and ideas
"""
import reflex as rx
from ims.components.layout import layout
from ims.state.backlog import BacklogState


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


def backlog_item_card(item: dict) -> rx.Component:
    """Card component for a single backlog item."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.hstack(
                        rx.text(item["title"], weight="bold", size="4"),
                        priority_badge(item["priority"]),
                        width="100%",
                        align_items="center",
                        spacing="2",
                    ),
                    rx.hstack(
                        type_badge(item["item_type"]),
                        rx.text(f"ID: {item['id']}", size="1", color="gray"),
                        rx.spacer(),
                        status_badge(item["status"]),
                        width="100%",
                    ),
                    width="100%",
                    align_items="start",
                    spacing="1",
                ),
                width="100%",
            ),
            rx.divider(),
            rx.text(item["description"], size="2", color="gray"),
            rx.divider(),
            rx.hstack(
                rx.text(
                    rx.cond(
                        item.get("submitter_name"),
                        f"Ingediend door: {item['submitter_name']}",
                        "Ingediend door: Onbekend"
                    ),
                    size="1", 
                    color="gray"
                ),
                rx.spacer(),
                rx.button(
                    rx.icon("pencil", size=16),
                    "Bewerken",
                    size="1",
                    variant="soft",
                    on_click=lambda: BacklogState.open_edit_dialog(item["id"]),
                ),
                rx.button(
                    rx.icon("trash-2", size=16),
                    size="1",
                    variant="soft",
                    color_scheme="red",
                    on_click=lambda: BacklogState.open_delete_dialog(item["id"]),
                    display=rx.cond(BacklogState.is_admin, "flex", "none"),
                ),
                width="100%",
            ),
            width="100%",
            spacing="3",
        ),
        width="100%",
    )


def form_dialog() -> rx.Component:
    """Dialog for creating/editing backlog items."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(BacklogState.is_editing, "Item Bewerken", "Nieuw Item")
            ),
            rx.dialog.description(
                "Beschrijf de wens of het probleem."
            ),
            rx.vstack(
                rx.text("Titel", size="2", weight="bold"),
                rx.input(
                    placeholder="Korte titel...",
                    value=BacklogState.form_title,
                    on_change=BacklogState.set_form_title,
                ),
                rx.text("Type", size="2", weight="bold"),
                rx.select(
                    ["Technisch", "Functioneel", "Proces", "Tooling", "Artificial Intelligence", "Overig"],
                    value=BacklogState.form_type,
                    on_change=BacklogState.set_form_type,
                ),
                rx.text("Omschrijving", size="2", weight="bold"),
                rx.text_area(
                    placeholder="Gedetailleerde omschrijving...",
                    value=BacklogState.form_description,
                    on_change=BacklogState.set_form_description,
                ),
                
                # Admin controls
                rx.cond(
                    BacklogState.is_admin,
                    rx.vstack(
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
                    ),
                    # Non-admins just see status/priority as read-only or hidden?
                    # For now hidden to keep it simple, or maybe just read-only text if editing
                    rx.cond(
                        BacklogState.is_editing,
                        rx.hstack(
                           rx.text("Status:", weight="bold", size="1"),
                           rx.text(BacklogState.form_status, size="1"),
                           rx.spacer(),
                           rx.text("Prioriteit:", weight="bold", size="1"),
                           rx.text(BacklogState.form_priority, size="1"),
                           width="100%",
                           padding="4px",
                           background="var(--gray-a3)",
                           border_radius="md",
                        ),
                    ),
                ),
                
                rx.cond(
                    BacklogState.error != "",
                    rx.callout(
                        BacklogState.error,
                        icon="alert_triangle",
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
    """Main backlog page."""
    return layout(
        rx.vstack(
            rx.hstack(
                rx.input(
                    placeholder="Zoeken...",
                    icon="search",
                    width="250px",
                ),
                rx.spacer(),
                rx.select(
                    ["ALLE", "Technisch", "Functioneel", "Proces", "Tooling", "Artificial Intelligence", "Overig"],
                    value=BacklogState.filter_type,
                    on_change=BacklogState.set_filter_type,
                    placeholder="Type",
                ),
                rx.select(
                    ["ALLE", "Nieuw", "In Review", "Goedgekeurd", "In Uitvoering", "Gereed", "Afgewezen"],
                    value=BacklogState.filter_status,
                    on_change=BacklogState.set_filter_status,
                    placeholder="Status",
                ),
                rx.select(
                    ["ALLE", "Laag", "Middel", "Hoog", "Kritiek"],
                    value=BacklogState.filter_priority,
                    on_change=BacklogState.set_filter_priority,
                    placeholder="Prioriteit",
                ),
                rx.button(
                    rx.icon("plus", size=16),
                    "Nieuw Item",
                    on_click=BacklogState.open_create_dialog,
                ),
                width="100%",
                spacing="3",
            ),
            
            rx.divider(),
            
            rx.cond(
                BacklogState.is_loading,
                rx.center(rx.spinner(), padding="20px", width="100%"),
                rx.cond(
                    BacklogState.items,
                    rx.grid(
                        rx.foreach(BacklogState.items, backlog_item_card),
                        columns="2",
                        spacing="4",
                        width="100%",
                    ),
                    rx.center(
                        rx.vstack(
                            rx.icon("clipboard-list", size=48, color="gray"),
                            rx.text("Geen backlog items gevonden", color="gray"),
                        ),
                        width="100%",
                        padding="40px",
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
