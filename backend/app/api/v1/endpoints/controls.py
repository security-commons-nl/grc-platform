"""
Control Management Endpoints
Handles security/compliance controls (context-specific implementations) with effectiveness tracking.

Controls are testable implementations of Measures (catalog/library items).
"""
from typing import List, Optional
from datetime import datetime
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.db import get_session
from app.core.crud import CRUDBase
from app.models.core_models import (
    Control,
    ControlRiskLink,
    ControlRequirementLink,
    ControlMeasureLink,
    Measure,
    Risk,
    Requirement,
    Status,
)
from app.services.knowledge_service import knowledge_service

router = APIRouter()
crud_control = CRUDBase(Control)
logger = logging.getLogger(__name__)


# =============================================================================
# CONTROL CRUD
# =============================================================================

@router.get("/", response_model=List[Control])
async def list_controls(
    skip: int = 0,
    limit: int = 100,
    tenant_id: Optional[int] = Query(None, description="Filter by tenant"),
    scope_id: Optional[int] = Query(None, description="Filter by scope"),
    status: Optional[Status] = Query(None, description="Filter by status"),
    owner_id: Optional[int] = Query(None, description="Filter by owner"),
    session: AsyncSession = Depends(get_session),
):
    """List controls with optional filters."""
    filters = {}
    if tenant_id:
        filters["tenant_id"] = tenant_id
    if scope_id:
        filters["scope_id"] = scope_id
    if status:
        filters["status"] = status
    if owner_id:
        filters["owner_id"] = owner_id

    return await crud_control.get_multi(session, skip=skip, limit=limit, filters=filters)


@router.post("/", response_model=Control)
async def create_control(
    control: Control,
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new control (context-specific implementation).

    Also indexes in knowledge base for AI RAG.
    """
    control.status = control.status or Status.DRAFT
    created_control = await crud_control.create(session, obj_in=control)

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
    session: AsyncSession = Depends(get_session),
):
    """Get a control by ID."""
    return await crud_control.get_or_404(session, control_id)


@router.patch("/{control_id}", response_model=Control)
async def update_control(
    control_id: int,
    control_update: dict,
    session: AsyncSession = Depends(get_session),
):
    """Update a control."""
    db_control = await crud_control.get_or_404(session, control_id)
    control_update["updated_at"] = datetime.utcnow()
    return await crud_control.update(session, db_obj=db_control, obj_in=control_update)


@router.delete("/{control_id}")
async def delete_control(
    control_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Delete a control."""
    deleted = await crud_control.delete(session, id=control_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Control not found")
    return {"message": "Control deleted"}


# =============================================================================
# CONTROL STATUS TRANSITIONS
# =============================================================================

@router.post("/{control_id}/activate", response_model=Control)
async def activate_control(
    control_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Activate a draft control."""
    db_control = await crud_control.get_or_404(session, control_id)

    if db_control.status != Status.DRAFT:
        raise HTTPException(
            status_code=400,
            detail=f"Only draft controls can be activated. Current status: {db_control.status}"
        )

    return await crud_control.update(session, db_obj=db_control, obj_in={
        "status": Status.ACTIVE,
        "updated_at": datetime.utcnow(),
    })


@router.post("/{control_id}/deactivate", response_model=Control)
async def deactivate_control(
    control_id: int,
    reason: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    """Deactivate an active control."""
    db_control = await crud_control.get_or_404(session, control_id)

    if db_control.status != Status.ACTIVE:
        raise HTTPException(
            status_code=400,
            detail=f"Only active controls can be deactivated. Current status: {db_control.status}"
        )

    return await crud_control.update(session, db_obj=db_control, obj_in={
        "status": Status.DEPRECATED,
        "updated_at": datetime.utcnow(),
    })


# =============================================================================
# EFFECTIVENESS TRACKING
# =============================================================================

@router.patch("/{control_id}/effectiveness", response_model=Control)
async def update_effectiveness(
    control_id: int,
    effectiveness_percentage: int = Query(..., ge=0, le=100, description="Effectiveness percentage (0-100)"),
    last_tested: Optional[datetime] = None,
    session: AsyncSession = Depends(get_session),
):
    """
    Update the effectiveness score of a control.

    Effectiveness is typically assessed through:
    - Testing results
    - Audit findings
    - Incident analysis
    """
    db_control = await crud_control.get_or_404(session, control_id)

    update_data = {
        "effectiveness_percentage": effectiveness_percentage,
        "updated_at": datetime.utcnow(),
    }
    if last_tested:
        update_data["last_tested"] = last_tested

    return await crud_control.update(session, db_obj=db_control, obj_in=update_data)


# =============================================================================
# CONTROL-RISK LINKAGE
# =============================================================================

@router.get("/{control_id}/risks", response_model=List[Risk])
async def get_linked_risks(
    control_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get all risks that this control addresses."""
    await crud_control.get_or_404(session, control_id)

    result = await session.execute(
        select(Risk)
        .join(ControlRiskLink, ControlRiskLink.risk_id == Risk.id)
        .where(ControlRiskLink.control_id == control_id)
    )
    return result.scalars().all()


@router.post("/{control_id}/risks/{risk_id}")
async def link_to_risk(
    control_id: int,
    risk_id: int,
    mitigation_percent: int = Query(50, ge=0, le=100),
    session: AsyncSession = Depends(get_session),
):
    """Link this control to a risk."""
    await crud_control.get_or_404(session, control_id)

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


@router.delete("/{control_id}/risks/{risk_id}")
async def unlink_from_risk(
    control_id: int,
    risk_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Remove link between this control and a risk."""
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


# =============================================================================
# CONTROL-REQUIREMENT LINKAGE
# =============================================================================

@router.get("/{control_id}/requirements", response_model=List[Requirement])
async def get_linked_requirements(
    control_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get all requirements that this control implements."""
    await crud_control.get_or_404(session, control_id)

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
    session: AsyncSession = Depends(get_session),
):
    """
    Link this control to a requirement (from a standard).

    This creates the mapping for Statement of Applicability (SoA).
    """
    await crud_control.get_or_404(session, control_id)

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
    session: AsyncSession = Depends(get_session),
):
    """Remove link between this control and a requirement."""
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
    session: AsyncSession = Depends(get_session),
):
    """Get all measures (from catalog) that this control implements."""
    await crud_control.get_or_404(session, control_id)

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
    session: AsyncSession = Depends(get_session),
):
    """
    Link this control to a measure from the catalog.

    This establishes that this control implements the given measure
    in a specific context (scope).
    """
    await crud_control.get_or_404(session, control_id)

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
    session: AsyncSession = Depends(get_session),
):
    """Remove link between this control and a measure."""
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
    tenant_id: Optional[int] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    """Get control counts grouped by status."""
    from sqlalchemy import func

    query = select(
        Control.status,
        func.count(Control.id).label("count")
    ).group_by(Control.status)

    if tenant_id:
        query = query.where(Control.tenant_id == tenant_id)

    result = await session.execute(query)
    return {row.status: row.count for row in result}


@router.get("/stats/effectiveness")
async def get_effectiveness_stats(
    tenant_id: Optional[int] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    """Get effectiveness statistics for controls."""
    from sqlalchemy import func

    query = select(
        func.avg(Control.effectiveness_percentage).label("average"),
        func.min(Control.effectiveness_percentage).label("minimum"),
        func.max(Control.effectiveness_percentage).label("maximum"),
        func.count(Control.id).label("total")
    ).where(Control.effectiveness_percentage.isnot(None))

    if tenant_id:
        query = query.where(Control.tenant_id == tenant_id)

    result = await session.execute(query)
    row = result.first()

    return {
        "average_effectiveness": round(row.average, 1) if row.average else 0,
        "min_effectiveness": row.minimum or 0,
        "max_effectiveness": row.maximum or 0,
        "controls_with_score": row.total or 0
    }
