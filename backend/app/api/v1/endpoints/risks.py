"""
Risk Management Endpoints
Handles Risks and their linkage to Controls.
Implements the "In Control" risk management model.
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.db import get_session
from app.core.crud import CRUDBase
from app.models.core_models import (
    Risk,
    Control,
    ControlRiskLink,
    RiskLevel,
    Status,
    AttentionQuadrant,
    MitigationApproach,
)
from app.services.knowledge_service import knowledge_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
crud_risk = CRUDBase(Risk)
crud_control = CRUDBase(Control)


# =============================================================================
# RISK CRUD
# =============================================================================

@router.get("/", response_model=List[Risk])
async def list_risks(
    skip: int = 0,
    limit: int = 100,
    tenant_id: Optional[int] = Query(None, description="Filter by tenant"),
    scope_id: Optional[int] = Query(None, description="Filter by scope"),
    quadrant: Optional[AttentionQuadrant] = Query(None, description="Filter by attention quadrant"),
    risk_accepted: Optional[bool] = Query(None, description="Filter by acceptance status"),
    session: AsyncSession = Depends(get_session),
):
    """List risks with optional filters."""
    filters = {}
    if tenant_id:
        filters["tenant_id"] = tenant_id
    if scope_id:
        filters["scope_id"] = scope_id
    if quadrant:
        filters["attention_quadrant"] = quadrant
    if risk_accepted is not None:
        filters["risk_accepted"] = risk_accepted

    return await crud_risk.get_multi(session, skip=skip, limit=limit, filters=filters)


@router.post("/", response_model=Risk)
async def create_risk(
    risk: Risk,
    session: AsyncSession = Depends(get_session),
):
    """Create a new risk. Also indexes in knowledge base for AI RAG."""
    # Calculate inherent risk score
    level_to_score = {RiskLevel.LOW: 1, RiskLevel.MEDIUM: 2, RiskLevel.HIGH: 3, RiskLevel.CRITICAL: 4}
    risk.inherent_risk_score = (
        level_to_score.get(risk.inherent_likelihood, 1) *
        level_to_score.get(risk.inherent_impact, 1)
    )

    # Initialize residual = inherent if not provided
    if risk.residual_likelihood is None:
        risk.residual_likelihood = risk.inherent_likelihood
    if risk.residual_impact is None:
        risk.residual_impact = risk.inherent_impact

    risk.residual_risk_score = (
        level_to_score.get(risk.residual_likelihood, 1) *
        level_to_score.get(risk.residual_impact, 1)
    )

    created_risk = await crud_risk.create(session, obj_in=risk)

    # Index in knowledge base for AI RAG
    try:
        content = f"Risico: {created_risk.title}\n\nBeschrijving: {created_risk.description or ''}\n\nOorzaak: {created_risk.cause or ''}\n\nGevolg: {created_risk.consequence or ''}"
        await knowledge_service.add_knowledge(
            session=session,
            key=f"risk_{created_risk.id}",
            title=created_risk.title or f"Risk {created_risk.id}",
            content=content,
            category="risk"
        )
    except Exception as e:
        logger.warning(f"Failed to index risk {created_risk.id} in knowledge base: {e}")

    return created_risk


# =============================================================================
# HEATMAP & QUADRANT ROUTES (must be before /{risk_id} to avoid path conflicts)
# =============================================================================

@router.get("/heatmap", response_model=dict)
async def get_risk_heatmap(
    tenant_id: Optional[int] = None,
    scope_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
):
    """
    Get risk heatmap data for visualization.
    Returns risks grouped by quadrant with counts.
    """
    filters = {}
    if tenant_id:
        filters["tenant_id"] = tenant_id
    if scope_id:
        filters["scope_id"] = scope_id

    risks = await crud_risk.get_multi(session, filters=filters, limit=1000)

    heatmap = {
        "MITIGATE": [],
        "ASSURANCE": [],
        "MONITOR": [],
        "ACCEPT": [],
        "UNCLASSIFIED": [],
    }

    for risk in risks:
        # Use .name to get enum key (MITIGATE) not .value (Mitigeren)
        quadrant = risk.attention_quadrant.name if risk.attention_quadrant else "UNCLASSIFIED"
        heatmap[quadrant].append({
            "id": risk.id,
            "title": risk.title,
            "inherent_score": risk.inherent_risk_score,
            "residual_score": risk.residual_risk_score,
            "vulnerability_score": risk.vulnerability_score,
        })

    return {
        "heatmap": heatmap,
        "counts": {k: len(v) for k, v in heatmap.items()},
        "total": len(risks),
    }


@router.get("/by-quadrant/{quadrant}", response_model=List[Risk])
async def get_risks_by_quadrant(
    quadrant: AttentionQuadrant,
    tenant_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
):
    """Get all risks in a specific attention quadrant."""
    filters = {"attention_quadrant": quadrant}
    if tenant_id:
        filters["tenant_id"] = tenant_id
    return await crud_risk.get_multi(session, filters=filters, limit=500)


# =============================================================================
# RISK CRUD - Individual operations
# =============================================================================

@router.get("/{risk_id}", response_model=Risk)
async def get_risk(
    risk_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get a risk by ID."""
    return await crud_risk.get_or_404(session, risk_id)


@router.patch("/{risk_id}", response_model=Risk)
async def update_risk(
    risk_id: int,
    risk_update: dict,
    session: AsyncSession = Depends(get_session),
):
    """Update a risk."""
    db_risk = await crud_risk.get_or_404(session, risk_id)

    # Recalculate scores if likelihood/impact changed
    level_to_score = {RiskLevel.LOW: 1, RiskLevel.MEDIUM: 2, RiskLevel.HIGH: 3, RiskLevel.CRITICAL: 4}

    if "inherent_likelihood" in risk_update or "inherent_impact" in risk_update:
        likelihood = risk_update.get("inherent_likelihood", db_risk.inherent_likelihood)
        impact = risk_update.get("inherent_impact", db_risk.inherent_impact)
        risk_update["inherent_risk_score"] = level_to_score.get(likelihood, 1) * level_to_score.get(impact, 1)

    if "residual_likelihood" in risk_update or "residual_impact" in risk_update:
        likelihood = risk_update.get("residual_likelihood", db_risk.residual_likelihood)
        impact = risk_update.get("residual_impact", db_risk.residual_impact)
        risk_update["residual_risk_score"] = level_to_score.get(likelihood, 1) * level_to_score.get(impact, 1)

    risk_update["updated_at"] = datetime.utcnow()
    return await crud_risk.update(session, db_obj=db_risk, obj_in=risk_update)


@router.delete("/{risk_id}")
async def delete_risk(
    risk_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Delete a risk."""
    deleted = await crud_risk.delete(session, id=risk_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Risk not found")
    return {"message": "Risk deleted"}


# =============================================================================
# RISK ACCEPTANCE
# =============================================================================

@router.post("/{risk_id}/accept", response_model=Risk)
async def accept_risk(
    risk_id: int,
    accepted_by_id: int,
    justification: str,
    session: AsyncSession = Depends(get_session),
):
    """Accept a risk (formal risk acceptance)."""
    db_risk = await crud_risk.get_or_404(session, risk_id)

    return await crud_risk.update(session, db_obj=db_risk, obj_in={
        "risk_accepted": True,
        "accepted_by_id": accepted_by_id,
        "acceptance_date": datetime.utcnow(),
        "acceptance_justification": justification,
    })


@router.post("/{risk_id}/revoke-acceptance", response_model=Risk)
async def revoke_risk_acceptance(
    risk_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Revoke risk acceptance."""
    db_risk = await crud_risk.get_or_404(session, risk_id)

    return await crud_risk.update(session, db_obj=db_risk, obj_in={
        "risk_accepted": False,
        "accepted_by_id": None,
        "acceptance_date": None,
        "acceptance_justification": None,
    })


# =============================================================================
# ATTENTION QUADRANT (In Control Model)
# =============================================================================

@router.patch("/{risk_id}/quadrant", response_model=Risk)
async def set_risk_quadrant(
    risk_id: int,
    quadrant: AttentionQuadrant,
    mitigation_approach: Optional[MitigationApproach] = None,
    justification: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
):
    """
    Set the attention quadrant for a risk.

    Quadrants ("In Control" model):
    - MITIGATE: High impact, high vulnerability → reduce/transfer/avoid
    - ASSURANCE: High impact, low vulnerability → verify controls work
    - MONITOR: Low impact, high vulnerability → watch for changes
    - ACCEPT: Low impact, low vulnerability → accept residual risk
    """
    db_risk = await crud_risk.get_or_404(session, risk_id)

    updates = {
        "attention_quadrant": quadrant,
        "treatment_justification": justification,
    }

    # Mitigation approach only relevant for MITIGATE quadrant
    if quadrant == AttentionQuadrant.MITIGATE and mitigation_approach:
        updates["mitigation_approach"] = mitigation_approach
    elif quadrant != AttentionQuadrant.MITIGATE:
        updates["mitigation_approach"] = None

    return await crud_risk.update(session, db_obj=db_risk, obj_in=updates)


# =============================================================================
# RISK-CONTROL LINKAGE
# =============================================================================

@router.post("/{risk_id}/controls/{control_id}")
async def link_control_to_risk(
    risk_id: int,
    control_id: int,
    mitigation_percent: int = Query(50, ge=0, le=100, description="How much this control contributes to risk reduction"),
    session: AsyncSession = Depends(get_session),
):
    """Link a control to a risk."""
    # Verify both exist
    await crud_risk.get_or_404(session, risk_id)
    await crud_control.get_or_404(session, control_id)

    # Check if link already exists
    result = await session.execute(
        select(ControlRiskLink).where(
            ControlRiskLink.risk_id == risk_id,
            ControlRiskLink.control_id == control_id
        )
    )
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Link already exists")

    link = ControlRiskLink(
        risk_id=risk_id,
        control_id=control_id,
        mitigation_percent=mitigation_percent,
    )
    session.add(link)
    await session.commit()

    # Recalculate risk control effectiveness
    await _recalculate_control_effectiveness(session, risk_id)

    return {"message": "Control linked to risk"}


@router.delete("/{risk_id}/controls/{control_id}")
async def unlink_control_from_risk(
    risk_id: int,
    control_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Remove link between control and risk."""
    result = await session.execute(
        select(ControlRiskLink).where(
            ControlRiskLink.risk_id == risk_id,
            ControlRiskLink.control_id == control_id
        )
    )
    link = result.scalars().first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    await session.delete(link)
    await session.commit()

    # Recalculate risk control effectiveness
    await _recalculate_control_effectiveness(session, risk_id)

    return {"message": "Control unlinked from risk"}


@router.get("/{risk_id}/controls", response_model=List[Control])
async def get_risk_controls(
    risk_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get all controls linked to a risk."""
    await crud_risk.get_or_404(session, risk_id)

    result = await session.execute(
        select(Control).join(
            ControlRiskLink, Control.id == ControlRiskLink.control_id
        ).where(ControlRiskLink.risk_id == risk_id)
    )
    return result.scalars().all()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def _recalculate_control_effectiveness(session: AsyncSession, risk_id: int):
    """
    Recalculate the control effectiveness for a risk based on linked controls.
    Updates the risk's control_effectiveness_pct and vulnerability_score.
    """
    # Get all linked controls
    result = await session.execute(
        select(Control, ControlRiskLink.mitigation_percent)
        .join(ControlRiskLink, Control.id == ControlRiskLink.control_id)
        .where(ControlRiskLink.risk_id == risk_id)
    )
    linked_controls = result.all()

    if not linked_controls:
        # No controls linked, no control effectiveness
        effectiveness = 0
    else:
        # Calculate weighted average effectiveness
        total_weight = 0
        weighted_effectiveness = 0

        for control, contribution in linked_controls:
            if control.effectiveness_percentage is not None:
                weighted_effectiveness += (control.effectiveness_percentage * contribution)
                total_weight += contribution

        if total_weight > 0:
            effectiveness = weighted_effectiveness // total_weight
        else:
            effectiveness = 0

    # Update risk
    db_risk = await crud_risk.get(session, risk_id)
    if db_risk:
        # Vulnerability = 100 - control effectiveness (higher = more vulnerable)
        vulnerability = 100 - effectiveness

        db_risk.control_effectiveness_pct = effectiveness
        db_risk.vulnerability_score = vulnerability

        session.add(db_risk)
        await session.commit()
