"""
Control Management Endpoints
Handles security/compliance controls (context-specific implementations) with effectiveness tracking.

Controls are testable implementations of Measures (catalog/library items).
"""
from typing import List, Optional, Set
from datetime import datetime
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, delete

from app.core.db import get_session
from app.core.crud import ScopedTenantCRUDBase
from app.core.rbac import require_editor, get_tenant_id, get_scope_access
from app.models.core_models import (
    Control,
    ControlRiskLink,
    ControlRiskScopeLink,
    ControlRequirementLink,
    ControlMeasureLink,
    Measure,
    Risk,
    RiskScope,
    Requirement,
    Status,
    User,
)
from app.services.knowledge_service import knowledge_service

router = APIRouter()
crud_control = ScopedTenantCRUDBase(Control)
logger = logging.getLogger(__name__)


# =============================================================================
# CONTROL CRUD
# =============================================================================

@router.get("/", response_model=List[Control])
async def list_controls(
    skip: int = 0,
    limit: int = 100,
    scope_id: Optional[int] = Query(None, description="Filter by scope"),
    status: Optional[Status] = Query(None, description="Filter by status"),
    owner_id: Optional[int] = Query(None, description="Filter by owner"),
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
):
    """List controls with optional filters."""
    filters = {}
    if scope_id:
        filters["scope_id"] = scope_id
    if status:
        filters["status"] = status
    if owner_id:
        filters["owner_id"] = owner_id

    return await crud_control.get_multi_scoped(session, tenant_id, accessible_scopes, skip=skip, limit=limit, filters=filters)


@router.post("/", response_model=Control)
async def create_control(
    control: Control,
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_editor),
):
    """
    Create a new control (context-specific implementation).

    Also indexes in knowledge base for AI RAG.
    """
    control.status = control.status or Status.DRAFT
    created_control = await crud_control.create(session, obj_in=control, tenant_id=tenant_id)

    # Index in knowledge base for AI RAG
    try:
        content = f"Control: {created_control.title}\n\nBeschrijving: {created_control.description or ''}"
        await knowledge_service.add_knowledge(
            session=session,
            key=f"control_{created_control.id}",
            title=created_control.title or f"Control {created_control.id}",
            content=content,
            category="control"
        )
    except Exception as e:
        logger.warning(f"Failed to index control {created_control.id} in knowledge base: {e}")

    return created_control


@router.get("/{control_id}", response_model=Control)
async def get_control(
    control_id: int,
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
):
    """Get a control by ID."""
    return await crud_control.get_scoped_or_404(session, control_id, tenant_id, accessible_scopes)


@router.patch("/{control_id}", response_model=Control)
async def update_control(
    control_id: int,
    control_update: dict,
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_editor),
):
    """Update a control."""
    db_control = await crud_control.get_scoped_or_404(session, control_id, tenant_id, accessible_scopes)
    control_update["updated_at"] = datetime.utcnow()
    return await crud_control.update(session, db_obj=db_control, obj_in=control_update, tenant_id=tenant_id)


@router.delete("/{control_id}")
async def delete_control(
    control_id: int,
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_editor),
):
    """Delete a control and its risk/scope links."""
    await crud_control.get_scoped_or_404(session, control_id, tenant_id, accessible_scopes)

    # Remove linked rows that block cascade-less deletion
    await session.execute(
        delete(ControlRiskLink).where(ControlRiskLink.control_id == control_id)
    )
    await session.execute(
        delete(ControlRiskScopeLink).where(ControlRiskScopeLink.control_id == control_id)
    )

    deleted = await crud_control.delete(session, id=control_id, tenant_id=tenant_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Control not found")
    return {"message": "Control deleted"}


# =============================================================================
# CONTROL STATUS TRANSITIONS
# =============================================================================

@router.post("/{control_id}/activate", response_model=Control)
async def activate_control(
    control_id: int,
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_editor),
):
    """Activate a draft control."""
    db_control = await crud_control.get_scoped_or_404(session, control_id, tenant_id, accessible_scopes)

    if db_control.status != Status.DRAFT:
        raise HTTPException(
            status_code=400,
            detail=f"Only draft controls can be activated. Current status: {db_control.status}"
        )

    return await crud_control.update(session, db_obj=db_control, obj_in={
        "status": Status.ACTIVE,
        "updated_at": datetime.utcnow(),
    }, tenant_id=tenant_id)


@router.post("/{control_id}/deactivate", response_model=Control)
async def deactivate_control(
    control_id: int,
    reason: Optional[str] = Query(None),
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_editor),
):
    """Deactivate an active control."""
    db_control = await crud_control.get_scoped_or_404(session, control_id, tenant_id, accessible_scopes)

    if db_control.status != Status.ACTIVE:
        raise HTTPException(
            status_code=400,
            detail=f"Only active controls can be deactivated. Current status: {db_control.status}"
        )

    return await crud_control.update(session, db_obj=db_control, obj_in={
        "status": Status.DEPRECATED,
        "updated_at": datetime.utcnow(),
    }, tenant_id=tenant_id)


# =============================================================================
# EFFECTIVENESS TRACKING
# =============================================================================

@router.patch("/{control_id}/effectiveness", response_model=Control)
async def update_effectiveness(
    control_id: int,
    effectiveness_percentage: int = Query(..., ge=0, le=100, description="Effectiveness percentage (0-100)"),
    last_tested: Optional[datetime] = None,
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_editor),
):
    """
    Update the effectiveness score of a control.

    Effectiveness is typically assessed through:
    - Testing results
    - Audit findings
    - Incident analysis
    """
    db_control = await crud_control.get_scoped_or_404(session, control_id, tenant_id, accessible_scopes)

    update_data = {
        "effectiveness_percentage": effectiveness_percentage,
        "updated_at": datetime.utcnow(),
    }
    if last_tested:
        update_data["last_tested"] = last_tested

    return await crud_control.update(session, db_obj=db_control, obj_in=update_data, tenant_id=tenant_id)


# =============================================================================
# CONTROL-RISK LINKAGE
# =============================================================================

@router.get("/{control_id}/risks", response_model=List[Risk], deprecated=True)
async def get_linked_risks(
    control_id: int,
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
):
    """Get all risks that this control addresses. DEPRECATED: use GET /risk-scopes/?scope_id=X for scope-aware view."""
    await crud_control.get_scoped_or_404(session, control_id, tenant_id, accessible_scopes)

    result = await session.execute(
        select(Risk)
        .join(ControlRiskLink, ControlRiskLink.risk_id == Risk.id)
        .where(ControlRiskLink.control_id == control_id)
    )
    return result.scalars().all()


@router.post("/{control_id}/risks/{risk_id}", deprecated=True)
async def link_to_risk(
    control_id: int,
    risk_id: int,
    mitigation_percent: int = Query(50, ge=0, le=100),
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_editor),
):
    """Link this control to a risk. DEPRECATED: use POST /risk-scopes/{risk_scope_id}/controls/{control_id}."""
    await crud_control.get_scoped_or_404(session, control_id, tenant_id, accessible_scopes)

    # Check if link exists
    result = await session.execute(
        select(ControlRiskLink).where(
            ControlRiskLink.control_id == control_id,
            ControlRiskLink.risk_id == risk_id
        )
    )
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Link already exists")

    link = ControlRiskLink(
        control_id=control_id,
        risk_id=risk_id,
        mitigation_percent=mitigation_percent,
    )
    session.add(link)
    await session.commit()

    return {"message": "Control linked to risk"}


@router.delete("/{control_id}/risks/{risk_id}", deprecated=True)
async def unlink_from_risk(
    control_id: int,
    risk_id: int,
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_editor),
):
    """Remove link between this control and a risk. DEPRECATED: use DELETE /risk-scopes/{risk_scope_id}/controls/{control_id}."""
    await crud_control.get_scoped_or_404(session, control_id, tenant_id, accessible_scopes)
    result = await session.execute(
        select(ControlRiskLink).where(
            ControlRiskLink.control_id == control_id,
            ControlRiskLink.risk_id == risk_id
        )
    )
    link = result.scalars().first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    await session.delete(link)
    await session.commit()

    return {"message": "Link removed"}


@router.get("/{control_id}/risk-scopes", response_model=List[RiskScope])
async def get_linked_risk_scopes(
    control_id: int,
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
):
    """Get all scope-contextualized risks linked to this control."""
    await crud_control.get_scoped_or_404(session, control_id, tenant_id, accessible_scopes)

    query = (
        select(RiskScope)
        .join(ControlRiskScopeLink, ControlRiskScopeLink.risk_scope_id == RiskScope.id)
        .where(ControlRiskScopeLink.control_id == control_id)
    )
    if accessible_scopes is not None:
        query = query.where(RiskScope.scope_id.in_(accessible_scopes))

    result = await session.execute(query)
    return result.scalars().all()


# =============================================================================
# CONTROL-REQUIREMENT LINKAGE
# =============================================================================

@router.get("/{control_id}/requirements", response_model=List[Requirement])
async def get_linked_requirements(
    control_id: int,
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
):
    """Get all requirements that this control implements."""
    await crud_control.get_scoped_or_404(session, control_id, tenant_id, accessible_scopes)

    result = await session.execute(
        select(Requirement)
        .join(ControlRequirementLink, ControlRequirementLink.requirement_id == Requirement.id)
        .where(ControlRequirementLink.control_id == control_id)
    )
    return result.scalars().all()


@router.post("/{control_id}/requirements/{requirement_id}")
async def link_to_requirement(
    control_id: int,
    requirement_id: int,
    coverage_percentage: int = Query(100, ge=0, le=100),
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_editor),
):
    """
    Link this control to a requirement (from a standard).

    This creates the mapping for Statement of Applicability (SoA).
    """
    await crud_control.get_scoped_or_404(session, control_id, tenant_id, accessible_scopes)

    # Check if link exists
    result = await session.execute(
        select(ControlRequirementLink).where(
            ControlRequirementLink.control_id == control_id,
            ControlRequirementLink.requirement_id == requirement_id
        )
    )
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Link already exists")

    link = ControlRequirementLink(
        control_id=control_id,
        requirement_id=requirement_id,
        coverage_percentage=coverage_percentage,
    )
    session.add(link)
    await session.commit()

    return {"message": "Control linked to requirement"}


@router.delete("/{control_id}/requirements/{requirement_id}")
async def unlink_from_requirement(
    control_id: int,
    requirement_id: int,
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_editor),
):
    """Remove link between this control and a requirement."""
    await crud_control.get_scoped_or_404(session, control_id, tenant_id, accessible_scopes)
    result = await session.execute(
        select(ControlRequirementLink).where(
            ControlRequirementLink.control_id == control_id,
            ControlRequirementLink.requirement_id == requirement_id
        )
    )
    link = result.scalars().first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    await session.delete(link)
    await session.commit()

    return {"message": "Link removed"}


# =============================================================================
# CONTROL-MEASURE LINKAGE (Control implements Measures from catalog)
# =============================================================================

@router.get("/{control_id}/measures", response_model=List[Measure])
async def get_linked_measures(
    control_id: int,
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
):
    """Get all measures (from catalog) that this control implements."""
    await crud_control.get_scoped_or_404(session, control_id, tenant_id, accessible_scopes)

    result = await session.execute(
        select(Measure)
        .join(ControlMeasureLink, ControlMeasureLink.measure_id == Measure.id)
        .where(ControlMeasureLink.control_id == control_id)
    )
    return result.scalars().all()


@router.post("/{control_id}/measures/{measure_id}")
async def link_to_measure(
    control_id: int,
    measure_id: int,
    coverage_percentage: int = Query(100, ge=0, le=100),
    notes: Optional[str] = Query(None),
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_editor),
):
    """
    Link this control to a measure from the catalog.

    This establishes that this control implements the given measure
    in a specific context (scope).
    """
    await crud_control.get_scoped_or_404(session, control_id, tenant_id, accessible_scopes)

    # Check if link exists
    result = await session.execute(
        select(ControlMeasureLink).where(
            ControlMeasureLink.control_id == control_id,
            ControlMeasureLink.measure_id == measure_id
        )
    )
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Link already exists")

    link = ControlMeasureLink(
        control_id=control_id,
        measure_id=measure_id,
        coverage_percentage=coverage_percentage,
        notes=notes,
    )
    session.add(link)
    await session.commit()

    return {"message": "Control linked to measure"}


@router.delete("/{control_id}/measures/{measure_id}")
async def unlink_from_measure(
    control_id: int,
    measure_id: int,
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_editor),
):
    """Remove link between this control and a measure."""
    await crud_control.get_scoped_or_404(session, control_id, tenant_id, accessible_scopes)
    result = await session.execute(
        select(ControlMeasureLink).where(
            ControlMeasureLink.control_id == control_id,
            ControlMeasureLink.measure_id == measure_id
        )
    )
    link = result.scalars().first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    await session.delete(link)
    await session.commit()

    return {"message": "Link removed"}


# =============================================================================
# CONTROL STATISTICS
# =============================================================================

@router.get("/stats/by-status")
async def get_controls_by_status(
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """Get control counts grouped by status."""
    from sqlalchemy import func

    query = select(
        Control.status,
        func.count(Control.id).label("count")
    ).where(Control.tenant_id == tenant_id).group_by(Control.status)

    result = await session.execute(query)
    return {row.status: row.count for row in result}


@router.get("/stats/effectiveness")
async def get_effectiveness_stats(
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """Get effectiveness statistics for controls."""
    from sqlalchemy import func

    query = select(
        func.avg(Control.effectiveness_percentage).label("average"),
        func.min(Control.effectiveness_percentage).label("minimum"),
        func.max(Control.effectiveness_percentage).label("maximum"),
        func.count(Control.id).label("total")
    ).where(
        Control.effectiveness_percentage.isnot(None),
        Control.tenant_id == tenant_id,
    )

    result = await session.execute(query)
    row = result.first()

    return {
        "average_effectiveness": round(row.average, 1) if row.average else 0,
        "min_effectiveness": row.minimum or 0,
        "max_effectiveness": row.maximum or 0,
        "controls_with_score": row.total or 0
    }
