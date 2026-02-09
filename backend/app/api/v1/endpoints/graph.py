"""
Relationship Graph Endpoint
Returns nodes + edges for the interactive relationship web visualization.

Filters:
- Risk/Control/Assessment: status != CLOSED
- Measure: is_active == True
- Scope: is_active == True
- Decision: status == ACTIVE
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.db import get_session
from app.models.core_models import (
    Risk,
    Control,
    Measure,
    Scope,
    Decision,
    Assessment,
    DecisionStatus,
    Status,
    ControlRiskLink,
    ControlMeasureLink,
    DecisionRiskLink,
    ScopeDependency,
)

router = APIRouter()


@router.get("/relationships")
async def get_relationships(
    entity_types: str = Query("risk,control,scope,measure,decision,assessment"),
    scope_id: Optional[int] = Query(None),
    tenant_id: int = Query(1),
    session: AsyncSession = Depends(get_session),
):
    """Build a relationship graph of nodes and edges for visualization.

    Only includes active/non-closed entities. Deleted or closed items are excluded.
    """
    types = [t.strip() for t in entity_types.split(",") if t.strip()]
    nodes = []
    edges = []
    node_ids = set()
    # Cache scope_id per node to avoid re-querying for edges
    node_scope_map = {}  # node_id -> scope_id
    node_parent_map = {}  # scope node_id -> parent_id

    # --- Load entities as nodes (filtered on status/is_active) ---
    if "risk" in types:
        stmt = select(Risk).where(
            Risk.tenant_id == tenant_id,
            Risk.status != Status.CLOSED,
        )
        if scope_id:
            stmt = stmt.where(Risk.scope_id == scope_id)
        result = await session.execute(stmt)
        for r in result.scalars().all():
            nid = f"risk-{r.id}"
            nodes.append({"id": nid, "type": "risk", "label": r.title, "entity_id": r.id, "has_gap": False})
            node_ids.add(nid)
            if r.scope_id:
                node_scope_map[nid] = r.scope_id

    if "control" in types:
        stmt = select(Control).where(
            Control.tenant_id == tenant_id,
            Control.status != Status.CLOSED,
        )
        if scope_id:
            stmt = stmt.where(Control.scope_id == scope_id)
        result = await session.execute(stmt)
        for c in result.scalars().all():
            nid = f"control-{c.id}"
            nodes.append({"id": nid, "type": "control", "label": c.title, "entity_id": c.id, "has_gap": False})
            node_ids.add(nid)
            if c.scope_id:
                node_scope_map[nid] = c.scope_id

    if "measure" in types:
        stmt = select(Measure).where(
            Measure.tenant_id == tenant_id,
            Measure.is_active == True,
        )
        result = await session.execute(stmt)
        for m in result.scalars().all():
            nid = f"measure-{m.id}"
            nodes.append({"id": nid, "type": "measure", "label": m.name, "entity_id": m.id, "has_gap": False})
            node_ids.add(nid)

    if "scope" in types:
        stmt = select(Scope).where(
            Scope.tenant_id == tenant_id,
            Scope.is_active == True,
        )
        if scope_id:
            stmt = stmt.where(Scope.id == scope_id)
        result = await session.execute(stmt)
        for s in result.scalars().all():
            nid = f"scope-{s.id}"
            nodes.append({"id": nid, "type": "scope", "label": s.name, "entity_id": s.id, "has_gap": False})
            node_ids.add(nid)
            if s.parent_id:
                node_parent_map[nid] = s.parent_id

    if "decision" in types:
        stmt = select(Decision).where(
            Decision.tenant_id == tenant_id,
            Decision.status == DecisionStatus.ACTIVE,
        )
        if scope_id:
            stmt = stmt.where(Decision.scope_id == scope_id)
        result = await session.execute(stmt)
        for d in result.scalars().all():
            nid = f"decision-{d.id}"
            nodes.append({"id": nid, "type": "decision", "label": d.decision_text[:50], "entity_id": d.id, "has_gap": False})
            node_ids.add(nid)
            if d.scope_id:
                node_scope_map[nid] = d.scope_id

    if "assessment" in types:
        stmt = select(Assessment).where(
            Assessment.tenant_id == tenant_id,
            Assessment.status != Status.CLOSED,
        )
        if scope_id:
            stmt = stmt.where(Assessment.scope_id == scope_id)
        result = await session.execute(stmt)
        for a in result.scalars().all():
            nid = f"assessment-{a.id}"
            nodes.append({"id": nid, "type": "assessment", "label": a.title, "entity_id": a.id, "has_gap": False})
            node_ids.add(nid)
            if a.scope_id:
                node_scope_map[nid] = a.scope_id

    # --- Load edges ---
    # Control <-> Risk
    result = await session.execute(select(ControlRiskLink))
    for link in result.scalars().all():
        src = f"risk-{link.risk_id}"
        tgt = f"control-{link.control_id}"
        if src in node_ids and tgt in node_ids:
            label = f"{link.mitigation_percent}%" if link.mitigation_percent else ""
            edges.append({"source": src, "target": tgt, "type": "mitigates", "label": label})

    # Control <-> Measure
    result = await session.execute(select(ControlMeasureLink))
    for link in result.scalars().all():
        src = f"control-{link.control_id}"
        tgt = f"measure-{link.measure_id}"
        if src in node_ids and tgt in node_ids:
            edges.append({"source": src, "target": tgt, "type": "implements", "label": ""})

    # Decision <-> Risk
    result = await session.execute(select(DecisionRiskLink))
    for link in result.scalars().all():
        src = f"decision-{link.decision_id}"
        tgt = f"risk-{link.risk_id}"
        if src in node_ids and tgt in node_ids:
            edges.append({"source": src, "target": tgt, "type": "decides", "label": ""})

    # Scope dependencies
    result = await session.execute(select(ScopeDependency))
    for dep in result.scalars().all():
        src = f"scope-{dep.depender_id}"
        tgt = f"scope-{dep.provider_id}"
        if src in node_ids and tgt in node_ids:
            edges.append({"source": src, "target": tgt, "type": "depends_on", "label": dep.dependency_type or ""})

    # Entity <-> Scope (from cached scope_id, no re-query needed)
    for nid, sid in node_scope_map.items():
        scope_nid = f"scope-{sid}"
        if scope_nid in node_ids:
            edges.append({"source": nid, "target": scope_nid, "type": "belongs_to", "label": ""})

    # Scope parent → child hierarchy (from cached parent_id)
    for nid, pid in node_parent_map.items():
        parent_nid = f"scope-{pid}"
        if parent_nid in node_ids:
            edges.append({"source": nid, "target": parent_nid, "type": "child_of", "label": ""})

    # --- Gap detection ---
    gaps = []

    # Track connected nodes per type
    risk_ids_with_controls = set()
    control_ids_with_risks = set()
    control_ids_with_measures = set()
    scope_ids_with_risks = set()

    for edge in edges:
        if edge["type"] == "mitigates":
            risk_ids_with_controls.add(edge["source"])
            control_ids_with_risks.add(edge["target"])
        elif edge["type"] == "implements":
            control_ids_with_measures.add(edge["source"])
        elif edge["type"] == "belongs_to" and edge["source"].startswith("risk-"):
            scope_ids_with_risks.add(edge["target"])

    for node in nodes:
        if node["type"] == "risk" and node["id"] not in risk_ids_with_controls:
            node["has_gap"] = True
            gaps.append({
                "type": "risk_without_control",
                "entity_id": node["entity_id"],
                "label": f"Risico '{node['label']}' heeft geen controls",
            })
        elif node["type"] == "control" and node["id"] not in control_ids_with_risks:
            node["has_gap"] = True
            gaps.append({
                "type": "orphan_control",
                "entity_id": node["entity_id"],
                "label": f"Control '{node['label']}' heeft geen risico's",
            })
        elif node["type"] == "scope" and node["id"] not in scope_ids_with_risks:
            node["has_gap"] = True
            gaps.append({
                "type": "scope_without_risks",
                "entity_id": node["entity_id"],
                "label": f"Scope '{node['label']}' heeft geen risico's",
            })

    return {"nodes": nodes, "edges": edges, "gaps": gaps}
