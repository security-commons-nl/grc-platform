"""
Relationship Graph State
Manages graph data, layout positions, filtering, and selection.
"""
import math
import reflex as rx
from typing import List, Dict, Any, Optional
from ims.api.client import api_client


# Layout constants
GRAPH_W = 800
GRAPH_H = 600
CENTER_X = GRAPH_W / 2
CENTER_Y = GRAPH_H / 2

# Colors per entity type
TYPE_COLORS = {
    "risk": "#f97316",
    "control": "#3b82f6",
    "scope": "#6b7280",
    "measure": "#7c3aed",
    "decision": "#d97706",
    "assessment": "#06b6d4",
}

TYPE_ICONS = {
    "risk": "triangle-alert",
    "control": "shield-check",
    "scope": "git-branch",
    "measure": "book-open",
    "decision": "gavel",
    "assessment": "clipboard-check",
}


def _circular_layout(nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Arrange nodes in concentric circles grouped by type."""
    if not nodes:
        return nodes

    # Group by type
    groups: Dict[str, List[int]] = {}
    for i, node in enumerate(nodes):
        t = node.get("type", "other")
        groups.setdefault(t, []).append(i)

    # Assign positions — each type on its own ring
    type_list = list(groups.keys())
    num_rings = len(type_list)

    for ring_idx, entity_type in enumerate(type_list):
        indices = groups[entity_type]
        count = len(indices)
        # Radius grows with ring index
        radius = 100 + ring_idx * 90
        if radius > min(CENTER_X, CENTER_Y) - 40:
            radius = min(CENTER_X, CENTER_Y) - 40

        for j, node_idx in enumerate(indices):
            angle = (2 * math.pi * j / max(count, 1)) - math.pi / 2
            x = CENTER_X + radius * math.cos(angle)
            y = CENTER_Y + radius * math.sin(angle)
            nodes[node_idx]["x"] = round(x)
            nodes[node_idx]["y"] = round(y)

    return nodes


class RelationshipState(rx.State):
    """State for the interactive relationship graph page."""

    # Graph data
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []
    gaps: List[Dict[str, Any]] = []

    # Selection
    selected_node: Dict[str, Any] = {}
    selected_node_edges: List[Dict[str, Any]] = []

    # Filters
    active_preset: str = "all"
    filter_types: List[str] = ["risk", "control", "scope", "measure", "decision", "assessment"]
    prompt_text: str = ""

    # Loading
    is_loading: bool = False
    error: str = ""

    @rx.var
    def total_nodes(self) -> int:
        return len(self.nodes)

    @rx.var
    def total_edges(self) -> int:
        return len(self.edges)

    @rx.var
    def total_gaps(self) -> int:
        return len(self.gaps)

    @rx.var
    def gap_risks_without_controls(self) -> int:
        return len([g for g in self.gaps if g.get("type") == "risk_without_control"])

    @rx.var
    def gap_orphan_controls(self) -> int:
        return len([g for g in self.gaps if g.get("type") == "orphan_control"])

    @rx.var
    def gap_scopes_without_risks(self) -> int:
        return len([g for g in self.gaps if g.get("type") == "scope_without_risks"])

    @rx.var
    def has_selection(self) -> bool:
        return bool(self.selected_node)

    @rx.var
    def selected_node_label(self) -> str:
        return self.selected_node.get("label", "")

    @rx.var
    def selected_node_type(self) -> str:
        return self.selected_node.get("type", "")

    @rx.var
    def selected_node_entity_id(self) -> int:
        return self.selected_node.get("entity_id", 0)

    @rx.var
    def selected_node_link(self) -> str:
        t = self.selected_node.get("type", "")
        eid = self.selected_node.get("entity_id", 0)
        routes = {
            "risk": "/risks",
            "control": "/controls",
            "scope": "/scopes",
            "measure": "/measures",
            "decision": "/decisions",
            "assessment": "/assessments",
        }
        return routes.get(t, "/")

    @rx.var
    def computed_nodes(self) -> List[Dict[str, Any]]:
        """Nodes enriched with color, icon, and short_label for rendering."""
        result = []
        for node in self.nodes:
            t = node.get("type", "other")
            label = node.get("label", "")
            short = label[:20] + "..." if len(label) > 20 else label
            result.append({
                **node,
                "color": TYPE_COLORS.get(t, "#6b7280"),
                "icon": TYPE_ICONS.get(t, "circle"),
                "short_label": short,
            })
        return result

    @rx.var
    def computed_edges(self) -> List[Dict[str, Any]]:
        """Edges enriched with source/target coordinates and color for SVG rendering."""
        edge_colors = {
            "mitigates": "#3b82f6",
            "implements": "#7c3aed",
            "decides": "#d97706",
            "depends_on": "#06b6d4",
            "belongs_to": "#9ca3af",
            "child_of": "#6b7280",
        }
        # Build a position lookup from nodes
        pos = {}
        for node in self.nodes:
            pos[node.get("id", "")] = (node.get("x", 0), node.get("y", 0))

        result = []
        for edge in self.edges:
            src = edge.get("source", "")
            tgt = edge.get("target", "")
            if src in pos and tgt in pos:
                sx, sy = pos[src]
                tx, ty = pos[tgt]
                etype = edge.get("type", "belongs_to")
                result.append({
                    **edge,
                    "source_x": sx,
                    "source_y": sy,
                    "target_x": tx,
                    "target_y": ty,
                    "color": edge_colors.get(etype, "#9ca3af"),
                })
        return result

    # --- Actions ---

    async def load_graph(self):
        """Load graph data from API."""
        self.is_loading = True
        self.error = ""
        try:
            entity_types = ",".join(self.filter_types)
            data = await api_client.get_graph_relationships(
                entity_types=entity_types,
            )
            raw_nodes = data.get("nodes", [])
            self.edges = data.get("edges", [])
            all_gaps = data.get("gaps", [])

            # Apply preset filter on gaps
            if self.active_preset == "uncovered_risks":
                gap_entity_ids = {
                    f"risk-{g['entity_id']}"
                    for g in all_gaps
                    if g.get("type") == "risk_without_control"
                }
                raw_nodes = [n for n in raw_nodes if n["id"] in gap_entity_ids or n["type"] != "risk"]
                # Also keep controls connected to those risks (none in this case, but keep for context)
            elif self.active_preset == "orphan_controls":
                gap_entity_ids = {
                    f"control-{g['entity_id']}"
                    for g in all_gaps
                    if g.get("type") == "orphan_control"
                }
                raw_nodes = [n for n in raw_nodes if n["id"] in gap_entity_ids or n["type"] != "control"]
            elif self.active_preset == "scope_coverage":
                gap_entity_ids = {
                    f"scope-{g['entity_id']}"
                    for g in all_gaps
                    if g.get("type") == "scope_without_risks"
                }
                raw_nodes = [n for n in raw_nodes if n["id"] in gap_entity_ids or n["type"] != "scope"]

            # Filter edges to match remaining nodes
            filtered_node_ids = {n["id"] for n in raw_nodes}
            self.edges = [
                e for e in self.edges
                if e["source"] in filtered_node_ids and e["target"] in filtered_node_ids
            ]

            # Calculate layout positions
            self.nodes = _circular_layout(raw_nodes)
            self.gaps = all_gaps
        except Exception as e:
            self.error = str(e)
            self.nodes = []
            self.edges = []
            self.gaps = []
        finally:
            self.is_loading = False

    def select_node(self, node_id: str):
        """Select a node and compute connected edges."""
        for node in self.nodes:
            if node.get("id") == node_id:
                self.selected_node = node
                # Find connected edges
                self.selected_node_edges = [
                    e for e in self.edges
                    if e.get("source") == node_id or e.get("target") == node_id
                ]
                return
        self.selected_node = {}
        self.selected_node_edges = []

    def clear_selection(self):
        self.selected_node = {}
        self.selected_node_edges = []

    def set_preset(self, preset: str):
        self.active_preset = preset
        self.clear_selection()
        return RelationshipState.load_graph

    def toggle_filter_type(self, entity_type: str):
        if entity_type in self.filter_types:
            self.filter_types = [t for t in self.filter_types if t != entity_type]
        else:
            self.filter_types = self.filter_types + [entity_type]
        self.clear_selection()
        return RelationshipState.load_graph

    def set_prompt_text(self, value: str):
        self.prompt_text = value

    async def handle_prompt_key(self, key: str):
        """Handle keydown in prompt input — trigger search on Enter."""
        if key == "Enter":
            return RelationshipState.apply_prompt

    async def apply_prompt(self):
        """Smart keyword filter — matches prompt text to presets or node labels.

        Loads graph data inline (no event chaining) for reliable execution.
        """
        if not self.prompt_text.strip():
            return
        query = self.prompt_text.strip().lower()

        # Match known preset patterns (Dutch + English)
        if any(kw in query for kw in ["zonder control", "ongedekt", "unmitigated", "no control"]):
            self.active_preset = "uncovered_risks"
        elif any(kw in query for kw in ["wees", "orphan", "losse control"]):
            self.active_preset = "orphan_controls"
        elif any(kw in query for kw in ["scope zonder", "scope coverage", "lege scope"]):
            self.active_preset = "scope_coverage"
        elif query in ("alles", "all", "reset", "toon alles"):
            self.active_preset = "all"
            self.filter_types = ["risk", "control", "scope", "measure", "decision", "assessment"]
        else:
            # Fallback: will filter by label substring below
            self.active_preset = "all"

        self.clear_selection()
        self.is_loading = True
        self.error = ""
        try:
            entity_types = ",".join(self.filter_types)
            data = await api_client.get_graph_relationships(entity_types=entity_types)
            raw_nodes = data.get("nodes", [])
            all_edges = data.get("edges", [])
            all_gaps = data.get("gaps", [])

            # Apply preset filter on gaps
            if self.active_preset == "uncovered_risks":
                gap_ids = {f"risk-{g['entity_id']}" for g in all_gaps if g.get("type") == "risk_without_control"}
                raw_nodes = [n for n in raw_nodes if n["id"] in gap_ids or n["type"] != "risk"]
            elif self.active_preset == "orphan_controls":
                gap_ids = {f"control-{g['entity_id']}" for g in all_gaps if g.get("type") == "orphan_control"}
                raw_nodes = [n for n in raw_nodes if n["id"] in gap_ids or n["type"] != "control"]
            elif self.active_preset == "scope_coverage":
                gap_ids = {f"scope-{g['entity_id']}" for g in all_gaps if g.get("type") == "scope_without_risks"}
                raw_nodes = [n for n in raw_nodes if n["id"] in gap_ids or n["type"] != "scope"]
            elif self.active_preset == "all" and query not in ("alles", "all", "reset", "toon alles"):
                # Label substring filter (fallback)
                matched = [n for n in raw_nodes if query in n.get("label", "").lower()]
                if matched:
                    # Also include nodes connected via edges
                    matched_ids = {n["id"] for n in matched}
                    for edge in all_edges:
                        if edge["source"] in matched_ids:
                            matched_ids.add(edge["target"])
                        elif edge["target"] in matched_ids:
                            matched_ids.add(edge["source"])
                    raw_nodes = [n for n in raw_nodes if n["id"] in matched_ids]

            # Filter edges to match remaining nodes
            filtered_ids = {n["id"] for n in raw_nodes}
            self.edges = [e for e in all_edges if e["source"] in filtered_ids and e["target"] in filtered_ids]
            self.nodes = _circular_layout(raw_nodes)
            self.gaps = all_gaps
        except Exception as e:
            self.error = str(e)
            self.nodes = []
            self.edges = []
            self.gaps = []
        finally:
            self.is_loading = False
