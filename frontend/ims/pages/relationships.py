"""
Relaties Page — Interactive Relationship Web
Shows how risks, controls, scopes, measures, decisions, and assessments relate.
"""
import reflex as rx
from ims.state.relationship import RelationshipState
from ims.components.layout import layout
from ims.state.auth import AuthState
from ims.components.relationship_graph import (
    relationship_graph,
    gap_panel,
    detail_panel,
)


PRESETS = [
    ("all", "Alles"),
    ("uncovered_risks", "Ongedekte risico's"),
    ("orphan_controls", "Wees-controls"),
    ("scope_coverage", "Scope-dekking"),
]

ENTITY_TYPES = [
    ("risk", "Risico's", "#f97316"),
    ("control", "Controls", "#3b82f6"),
    ("scope", "Scopes", "#6b7280"),
    ("measure", "Maatregelen", "#7c3aed"),
    ("decision", "Besluiten", "#d97706"),
    ("assessment", "Assessments", "#06b6d4"),
]


def _preset_button(key: str, label: str) -> rx.Component:
    return rx.button(
        label,
        variant=rx.cond(
            RelationshipState.active_preset == key,
            "solid",
            "outline",
        ),
        size="1",
        on_click=RelationshipState.set_preset(key),
    )


def _type_checkbox(key: str, label: str, color: str) -> rx.Component:
    return rx.hstack(
        rx.checkbox(
            checked=RelationshipState.filter_types.contains(key),
            on_change=lambda _: RelationshipState.toggle_filter_type(key),
            size="1",
        ),
        rx.box(width="10px", height="10px", border_radius="50%", background=color),
        rx.text(label, size="2"),
        spacing="2",
        align="center",
    )


def filter_sidebar() -> rx.Component:
    """Left sidebar with presets, type filters, and AI prompt."""
    return rx.vstack(
        # Presets
        rx.text("Presets", size="2", weight="bold", color="gray"),
        rx.vstack(
            *[_preset_button(key, label) for key, label in PRESETS],
            spacing="2",
            width="100%",
        ),
        rx.separator(),

        # Entity type filters
        rx.text("Entiteiten", size="2", weight="bold", color="gray"),
        rx.vstack(
            *[_type_checkbox(key, label, color) for key, label, color in ENTITY_TYPES],
            spacing="2",
            width="100%",
        ),
        rx.separator(),

        # AI Prompt
        rx.text("AI Prompt", size="2", weight="bold", color="gray"),
        rx.input(
            placeholder="bijv. 'risico's zonder controls'",
            value=RelationshipState.prompt_text,
            on_change=RelationshipState.set_prompt_text,
            on_key_down=RelationshipState.handle_prompt_key,
            size="2",
        ),
        rx.button(
            rx.icon("search", size=14),
            "Zoek",
            variant="outline",
            size="1",
            on_click=RelationshipState.apply_prompt,
            width="100%",
        ),

        # Stats
        rx.separator(),
        rx.vstack(
            rx.hstack(
                rx.text("Nodes:", size="1", color="gray"),
                rx.text(RelationshipState.total_nodes.to(str), size="1", weight="bold"),
            ),
            rx.hstack(
                rx.text("Edges:", size="1", color="gray"),
                rx.text(RelationshipState.total_edges.to(str), size="1", weight="bold"),
            ),
            rx.hstack(
                rx.text("Gaps:", size="1", color="gray"),
                rx.text(RelationshipState.total_gaps.to(str), size="1", weight="bold", color="red"),
            ),
            spacing="1",
        ),

        spacing="4",
        width="100%",
        padding="16px",
    )


def relationships_content() -> rx.Component:
    """Main content area for the relationships page."""
    return rx.vstack(
        rx.cond(
            RelationshipState.is_loading,
            rx.center(rx.spinner(size="3"), width="100%", padding="48px"),
            # Main layout: sidebar + graph + panels
            rx.flex(
                # Left: filters
                rx.box(
                    filter_sidebar(),
                    width=rx.breakpoints(initial="100%", md="220px"),
                    min_width=rx.breakpoints(initial="0", md="220px"),
                    border_right=rx.breakpoints(initial="none", md="1px solid var(--gray-a5)"),
                    border_bottom=rx.breakpoints(initial="1px solid var(--gray-a5)", md="none"),
                ),
                # Center: graph
                rx.box(
                    relationship_graph(),
                    flex="1",
                    min_width="0",
                    padding="8px",
                ),
                # Right: gap + detail panels
                rx.box(
                    rx.vstack(
                        gap_panel(),
                        detail_panel(),
                        spacing="3",
                        width="100%",
                        padding="12px",
                    ),
                    width=rx.breakpoints(initial="100%", md="280px"),
                    min_width=rx.breakpoints(initial="0", md="280px"),
                    border_left=rx.breakpoints(initial="none", md="1px solid var(--gray-a5)"),
                    border_top=rx.breakpoints(initial="1px solid var(--gray-a5)", md="none"),
                ),
                direction=rx.breakpoints(initial="column", md="row"),
                width="100%",
                min_height="600px",
            ),
        ),
        rx.cond(
            RelationshipState.error != "",
            rx.callout(
                RelationshipState.error,
                icon="alert-triangle",
                color_scheme="red",
                size="1",
            ),
        ),
        width="100%",
        on_mount=RelationshipState.load_graph,
    )


def _no_access() -> rx.Component:
    return rx.center(
        rx.callout("Je hebt onvoldoende rechten om deze pagina te bekijken.", icon="shield-alert", color_scheme="red"),
        padding="48px",
    )


def relationships_page() -> rx.Component:
    """Relaties page with layout wrapper."""
    return layout(
        rx.cond(AuthState.can_discover, relationships_content(), _no_access()),
        title="Relaties",
        subtitle="Interactief relatieweb van risico's, controls en scopes",
    )
