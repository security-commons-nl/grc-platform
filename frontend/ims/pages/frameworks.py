"""
Frameworks Page - Knowledge Base Frameworks and Mappings
"""
import reflex as rx
from ims.state.framework import FrameworkState
from ims.components.layout import layout
from ims.state.auth import AuthState


def framework_row(item: dict) -> rx.Component:
    """Single row in frameworks/mappings table."""
    return rx.table.row(
        rx.table.cell(
            rx.text(item["key"], size="2", font_family="monospace", color="gray"),
        ),
        rx.table.cell(
            rx.vstack(
                rx.text(item["title"], weight="medium", size="2"),
                rx.text(
                    item["content"],
                    size="1",
                    color="gray",
                    no_of_lines=2,
                ),
                align_items="start",
                spacing="0",
            ),
        ),
        rx.table.cell(
            rx.badge(
                rx.cond(item["subcategory"] != "", item["subcategory"], "General"), 
                color_scheme="blue", 
                variant="soft"
            ),
        ),
        _hover={"background": "var(--gray-a3)"},
    )


def data_table(data: list, empty_message: str) -> rx.Component:
    """Generic data table for knowledge items."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Key", width="150px"),
                rx.table.column_header_cell("Titel & Inhoud"),
                rx.table.column_header_cell("Categorie", width="120px"),
            ),
        ),
        rx.table.body(
            rx.cond(
                FrameworkState.is_loading,
                rx.table.row(
                    rx.table.cell(
                        rx.center(
                            rx.spinner(size="2"),
                            width="100%",
                            padding="40px",
                        ),
                        col_span=3,
                    ),
                ),
                rx.cond(
                    data.length() > 0,
                    rx.foreach(data, framework_row),
                    rx.table.row(
                        rx.table.cell(
                            rx.center(
                                rx.vstack(
                                    rx.icon("library", size=32, color="gray"),
                                    rx.text(empty_message, color="gray"),
                                    spacing="2",
                                ),
                                width="100%",
                                padding="40px",
                            ),
                            col_span=3,
                        ),
                    ),
                ),
            ),
        ),
        width="100%",
    )


def frameworks_content() -> rx.Component:
    """Frameworks page content."""
    return rx.vstack(
        rx.cond(
            FrameworkState.error != "",
            rx.callout(
                FrameworkState.error,
                icon="circle-alert",
                color="red",
                margin_bottom="16px",
            ),
        ),
        
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger("Frameworks", value="frameworks"),
                rx.tabs.trigger("Mappings (Tweede Lijn)", value="mappings"),
            ),
            rx.tabs.content(
                rx.card(
                    data_table(FrameworkState.frameworks, "Geen frameworks gevonden"),
                    padding="0",
                    margin_top="16px",
                ),
                value="frameworks",
            ),
            rx.tabs.content(
                rx.card(
                    data_table(FrameworkState.mappings, "Geen mappings gevonden"),
                    padding="0",
                    margin_top="16px",
                ),
                value="mappings",
            ),
            value=FrameworkState.current_tab,
            on_change=FrameworkState.set_tab,
            width="100%",
        ),

        width="100%",
        spacing="4",
        on_mount=FrameworkState.load_data,
    )


def _no_access() -> rx.Component:
    return rx.center(
        rx.callout("Je hebt onvoldoende rechten om deze pagina te bekijken.", icon="shield-alert", color_scheme="red"),
        padding="48px",
    )


def frameworks_page() -> rx.Component:
    """Frameworks page with layout."""
    return layout(
        rx.cond(AuthState.can_discover, frameworks_content(), _no_access()),
        title="Frameworks & Mappings",
        subtitle="Kennisbank frameworks en tweedelijns mappings",
    )
