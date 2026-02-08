"""
Relationship Graph Components
Reflex-native interactive network diagram with SVG edges and positioned nodes.
"""
import reflex as rx
from ims.state.relationship import RelationshipState


# Node color mapping
NODE_COLORS = {
    "risk": "#f97316",
    "control": "#3b82f6",
    "scope": "#6b7280",
    "measure": "#7c3aed",
    "decision": "#d97706",
    "assessment": "#06b6d4",
}

NODE_ICONS = {
    "risk": "triangle-alert",
    "control": "shield-check",
    "scope": "git-branch",
    "measure": "book-open",
    "decision": "gavel",
    "assessment": "clipboard-check",
}


def _render_edge(edge: dict) -> rx.Component:
    """Render a single SVG line for an edge."""
    # Find source and target positions from nodes
    # We use rx.foreach on nodes so we need a simpler approach:
    # Pre-compute edge coordinates in state. For now, draw with data attributes.
    return rx.el.line(
        x1=edge["source_x"].to(str),
        y1=edge["source_y"].to(str),
        x2=edge["target_x"].to(str),
        y2=edge["target_y"].to(str),
        stroke="var(--gray-a6)",
        stroke_width="1.5",
        stroke_dasharray=rx.cond(
            edge["type"] == "belongs_to",
            "4,4",
            "0",
        ),
    )


def _render_node(node: dict) -> rx.Component:
    """Render a single node as an absolutely positioned box."""
    return rx.box(
        rx.tooltip(
            rx.center(
                rx.icon(
                    node["icon"].to(str),
                    size=18,
                    color="white",
                ),
                width="36px",
                height="36px",
                border_radius="50%",
                background=node["color"],
                border=rx.cond(
                    node["has_gap"],
                    "2.5px solid #ef4444",
                    "2px solid transparent",
                ),
                box_shadow=rx.cond(
                    node["has_gap"],
                    "0 0 8px rgba(239, 68, 68, 0.5)",
                    "0 1px 3px rgba(0,0,0,0.1)",
                ),
                _hover={
                    "transform": "scale(1.15)",
                    "box_shadow": "0 2px 8px rgba(0,0,0,0.2)",
                },
                transition="all 0.15s ease",
            ),
            content=node["label"],
        ),
        position="absolute",
        cursor="pointer",
        on_click=RelationshipState.select_node(node["id"]),
        left=(node["x"].to(int) - 18).to(str) + "px",
        top=(node["y"].to(int) - 18).to(str) + "px",
    )


def relationship_graph() -> rx.Component:
    """Main graph canvas with SVG edges and positioned nodes."""
    return rx.box(
        # Empty state
        rx.cond(
            RelationshipState.total_nodes.to(int) == 0,
            rx.center(
                rx.vstack(
                    rx.icon("network", size=48, color="var(--gray-8)"),
                    rx.text("Geen relaties gevonden", size="3", color="gray"),
                    rx.text(
                        "Voeg risico's, controls en scopes toe om het relatieweb te zien.",
                        size="2",
                        color="gray",
                    ),
                    align="center",
                    spacing="2",
                ),
                height="100%",
                min_height="400px",
            ),
            # Graph container
            rx.box(
                # SVG layer for edges
                rx.el.svg(
                    rx.foreach(
                        RelationshipState.computed_edges,
                        _render_edge,
                    ),
                    width="100%",
                    height="100%",
                    position="absolute",
                    top="0",
                    left="0",
                    pointer_events="none",
                ),
                # Node layer
                rx.foreach(
                    RelationshipState.computed_nodes,
                    _render_node,
                ),
                position="relative",
                width="100%",
                height="600px",
                background="var(--gray-a2)",
                border_radius="var(--radius-3)",
                border="1px solid var(--gray-a5)",
                overflow="hidden",
            ),
        ),
    )


def _render_gap_item(gap: dict) -> rx.Component:
    """Render a single gap item in the panel."""
    return rx.hstack(
        rx.icon("alert-triangle", size=16, color="#ef4444"),
        rx.text(gap["label"], size="2"),
        width="100%",
        padding="6px 8px",
        border_radius="md",
        _hover={"background": "var(--gray-a3)"},
    )


def gap_panel() -> rx.Component:
    """Panel showing detected gaps in the relationship graph."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("alert-triangle", size=18, color="#ef4444"),
                rx.text("Gap-analyse", size="3", weight="bold"),
                align="center",
            ),
            rx.separator(),
            # Summary badges
            rx.hstack(
                rx.cond(
                    RelationshipState.gap_risks_without_controls.to(int) > 0,
                    rx.badge(
                        RelationshipState.gap_risks_without_controls.to(str) + " ongedekte risico's",
                        color_scheme="red",
                        size="1",
                    ),
                ),
                rx.cond(
                    RelationshipState.gap_orphan_controls.to(int) > 0,
                    rx.badge(
                        RelationshipState.gap_orphan_controls.to(str) + " wees-controls",
                        color_scheme="blue",
                        size="1",
                    ),
                ),
                rx.cond(
                    RelationshipState.gap_scopes_without_risks.to(int) > 0,
                    rx.badge(
                        RelationshipState.gap_scopes_without_risks.to(str) + " scopes zonder risico's",
                        color_scheme="gray",
                        size="1",
                    ),
                ),
                wrap="wrap",
                spacing="2",
            ),
            # Gap list
            rx.cond(
                RelationshipState.total_gaps.to(int) > 0,
                rx.vstack(
                    rx.foreach(RelationshipState.gaps, _render_gap_item),
                    spacing="1",
                    width="100%",
                    max_height="200px",
                    overflow_y="auto",
                ),
                rx.text("Geen gaps gedetecteerd", size="2", color="green"),
            ),
            spacing="3",
            width="100%",
        ),
        width="100%",
    )


def _render_connected_edge(edge: dict) -> rx.Component:
    """Render a connected edge in the detail panel."""
    return rx.hstack(
        rx.text(edge["type"], size="1", color="gray"),
        rx.icon("arrow-right", size=12, color="gray"),
        rx.text(
            rx.cond(edge["source"] == RelationshipState.selected_node["id"], edge["target"], edge["source"]),
            size="2",
        ),
        rx.cond(
            edge["label"] != "",
            rx.badge(edge["label"], size="1", variant="outline"),
        ),
        spacing="2",
        align="center",
    )


def detail_panel() -> rx.Component:
    """Panel showing details of the selected node."""
    return rx.cond(
        RelationshipState.has_selection,
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.icon("info", size=18, color="var(--accent-9)"),
                    rx.text("Details", size="3", weight="bold"),
                    rx.spacer(),
                    rx.icon_button(
                        rx.icon("x", size=14),
                        variant="ghost",
                        size="1",
                        on_click=RelationshipState.clear_selection,
                    ),
                    align="center",
                    width="100%",
                ),
                rx.separator(),
                rx.vstack(
                    rx.hstack(
                        rx.badge(
                            RelationshipState.selected_node_type,
                            size="1",
                        ),
                        spacing="2",
                    ),
                    rx.text(
                        RelationshipState.selected_node_label,
                        size="3",
                        weight="medium",
                    ),
                    spacing="1",
                ),
                # Connected edges
                rx.cond(
                    RelationshipState.selected_node_edges.length() > 0,
                    rx.vstack(
                        rx.text("Verbindingen", size="2", weight="medium", color="gray"),
                        rx.foreach(
                            RelationshipState.selected_node_edges,
                            _render_connected_edge,
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    rx.text("Geen verbindingen", size="2", color="gray"),
                ),
                # Link to detail page
                rx.link(
                    rx.button(
                        rx.icon("external-link", size=14),
                        "Bekijk detail",
                        variant="outline",
                        size="2",
                    ),
                    href=RelationshipState.selected_node_link,
                ),
                spacing="3",
                width="100%",
            ),
            width="100%",
        ),
    )
