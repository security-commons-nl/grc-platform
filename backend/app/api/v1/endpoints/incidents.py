"""
Incident Management Endpoints
Handles Incidents, Exceptions (Waivers), and related Corrective Actions.
Implements the PDCA "Act" phase.
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
# Note: Python's Exception is shadowed, use full import
from app.models import core_models

from app.core.db import get_session
from app.core.crud import CRUDBase
from app.models.core_models import (
    Incident,
    CorrectiveAction,
    Status,
    RiskLevel,
    FindingSeverity,
)

router = APIRouter()
crud_incident = CRUDBase(Incident)
crud_exception = CRUDBase(core_models.Exception)
crud_corrective_action = CRUDBase(CorrectiveAction)


# =============================================================================
# INCIDENT CRUD
# =============================================================================

@router.get("/", response_model=List[Incident])
async def list_incidents(
    skip: int = 0,
    limit: int = 100,
    tenant_id: Optional[int] = Query(None),
    status: Optional[Status] = Query(None),
    scope_id: Optional[int] = Query(None),
    severity: Optional[FindingSeverity] = Query(None),
    is_data_breach: Optional[bool] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    """List incidents with optional filters."""
    filters = {}
    if tenant_id:
        filters["tenant_id"] = tenant_id
    if status:
        filters["status"] = status
    if scope_id:
        filters["scope_id"] = scope_id
    if severity:
        filters["severity"] = severity
    if is_data_breach is not None:
        filters["is_data_breach"] = is_data_breach

    return await crud_incident.get_multi(session, skip=skip, limit=limit, filters=filters)


@router.post("/", response_model=Incident)
async def create_incident(
    incident: Incident,
    session: AsyncSession = Depends(get_session),
):
    """Create a new incident."""
    # Set detection date if not provided
    if incident.date_detected is None:
        incident.date_detected = datetime.utcnow()

    # If data breach, calculate notification deadline (72 hours)
    if incident.is_data_breach and incident.authority_notification_deadline is None:
        incident.authority_notification_deadline = incident.date_detected + timedelta(hours=72)

    return await crud_incident.create(session, obj_in=incident)


@router.get("/{incident_id}", response_model=Incident)
async def get_incident(
    incident_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get an incident by ID."""
    return await crud_incident.get_or_404(session, incident_id)


@router.patch("/{incident_id}", response_model=Incident)
async def update_incident(
    incident_id: int,
    incident_update: dict,
    session: AsyncSession = Depends(get_session),
):
    """Update an incident."""
    db_incident = await crud_incident.get_or_404(session, incident_id)
    return await crud_incident.update(session, db_obj=db_incident, obj_in=incident_update)


@router.delete("/{incident_id}")
async def delete_incident(
    incident_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Delete an incident."""
    deleted = await crud_incident.delete(session, id=incident_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Incident not found")
    return {"message": "Incident deleted"}


# =============================================================================
# INCIDENT LIFECYCLE
# =============================================================================

@router.post("/{incident_id}/resolve", response_model=Incident)
async def resolve_incident(
    incident_id: int,
    root_cause: Optional[str] = None,
    resolution_notes: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
):
    """Resolve an incident."""
    db_incident = await crud_incident.get_or_404(session, incident_id)

    return await crud_incident.update(session, db_obj=db_incident, obj_in={
        "status": Status.CLOSED,
        "date_resolved": datetime.utcnow(),
        "root_cause": root_cause,
    })


@router.post("/{incident_id}/reopen", response_model=Incident)
async def reopen_incident(
    incident_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Reopen a closed incident."""
    db_incident = await crud_incident.get_or_404(session, incident_id)

    if db_incident.status != Status.CLOSED:
        raise HTTPException(status_code=400, detail="Only closed incidents can be reopened")

    return await crud_incident.update(session, db_obj=db_incident, obj_in={
        "status": Status.ACTIVE,
        "date_resolved": None,
    })


# =============================================================================
# DATA BREACH (AVG Art. 33/34)
# =============================================================================

@router.post("/{incident_id}/mark-data-breach", response_model=Incident)
async def mark_as_data_breach(
    incident_id: int,
    data_subjects_affected: Optional[int] = None,
    personal_data_categories: Optional[str] = None,
    special_categories_involved: bool = False,
    session: AsyncSession = Depends(get_session),
):
    """
    Mark an incident as a data breach (AVG).
    Sets the 72-hour notification deadline.
    """
    db_incident = await crud_incident.get_or_404(session, incident_id)

    detection_time = db_incident.date_detected or datetime.utcnow()
    notification_deadline = detection_time + timedelta(hours=72)

    return await crud_incident.update(session, db_obj=db_incident, obj_in={
        "is_data_breach": True,
        "data_subjects_affected": data_subjects_affected,
        "personal_data_categories": personal_data_categories,
        "special_categories_involved": special_categories_involved,
        "authority_notification_deadline": notification_deadline,
    })


@router.post("/{incident_id}/notify-authority", response_model=Incident)
async def notify_authority(
    incident_id: int,
    authority_reference: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
):
    """Record that the authority (AP) has been notified about a data breach."""
    db_incident = await crud_incident.get_or_404(session, incident_id)

    if not db_incident.is_data_breach:
        raise HTTPException(status_code=400, detail="Incident is not marked as a data breach")

    return await crud_incident.update(session, db_obj=db_incident, obj_in={
        "notified_to_authority": True,
        "authority_notification_date": datetime.utcnow(),
        "authority_reference": authority_reference,
    })


@router.post("/{incident_id}/notify-subjects", response_model=Incident)
async def notify_data_subjects(
    incident_id: int,
    notification_method: str,
    session: AsyncSession = Depends(get_session),
):
    """Record that data subjects have been notified about a data breach."""
    db_incident = await crud_incident.get_or_404(session, incident_id)

    if not db_incident.is_data_breach:
        raise HTTPException(status_code=400, detail="Incident is not marked as a data breach")

    return await crud_incident.update(session, db_obj=db_incident, obj_in={
        "notified_to_subjects": True,
        "subject_notification_date": datetime.utcnow(),
        "subject_notification_method": notification_method,
    })


@router.get("/data-breaches/overdue", response_model=List[Incident])
async def get_overdue_breach_notifications(
    tenant_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
):
    """Get data breaches that have exceeded the 72-hour notification deadline."""
    query = select(Incident).where(
        Incident.is_data_breach == True,
        Incident.notified_to_authority == False,
        Incident.authority_notification_deadline < datetime.utcnow(),
    )
    if tenant_id:
        query = query.where(Incident.tenant_id == tenant_id)

    result = await session.execute(query)
    return result.scalars().all()


# =============================================================================
# INCIDENT CORRECTIVE ACTIONS
# =============================================================================

@router.get("/{incident_id}/corrective-actions", response_model=List[CorrectiveAction])
async def list_incident_corrective_actions(
    incident_id: int,
    session: AsyncSession = Depends(get_session),
):
    """List corrective actions for an incident."""
    await crud_incident.get_or_404(session, incident_id)
    return await crud_corrective_action.get_multi_by_field(session, "incident_id", incident_id)


@router.post("/{incident_id}/corrective-actions", response_model=CorrectiveAction)
async def create_incident_corrective_action(
    incident_id: int,
    corrective_action: CorrectiveAction,
    session: AsyncSession = Depends(get_session),
):
    """Create a corrective action for an incident."""
    await crud_incident.get_or_404(session, incident_id)

    corrective_action.incident_id = incident_id
    return await crud_corrective_action.create(session, obj_in=corrective_action)


# =============================================================================
# EXCEPTIONS (WAIVERS)
# =============================================================================

@router.get("/exceptions/", response_model=List[core_models.Exception])
async def list_exceptions(
    skip: int = 0,
    limit: int = 100,
    tenant_id: Optional[int] = Query(None),
    status: Optional[Status] = Query(None),
    scope_id: Optional[int] = Query(None),
    include_expired: bool = Query(False, description="Include expired exceptions"),
    session: AsyncSession = Depends(get_session),
):
    """List exceptions (waivers) with optional filters."""
    query = select(core_models.Exception)

    if tenant_id:
        query = query.where(core_models.Exception.tenant_id == tenant_id)
    if status:
        query = query.where(core_models.Exception.status == status)
    if scope_id:
        query = query.where(core_models.Exception.scope_id == scope_id)
    if not include_expired:
        query = query.where(core_models.Exception.expiration_date > datetime.utcnow())

    query = query.offset(skip).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()


@router.post("/exceptions/", response_model=core_models.Exception)
async def create_exception(
    exception: core_models.Exception,
    session: AsyncSession = Depends(get_session),
):
    """Create a new exception (waiver) request."""
    return await crud_exception.create(session, obj_in=exception)


@router.get("/exceptions/{exception_id}", response_model=core_models.Exception)
async def get_exception(
    exception_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get an exception by ID."""
    return await crud_exception.get_or_404(session, exception_id)


@router.patch("/exceptions/{exception_id}", response_model=core_models.Exception)
async def update_exception(
    exception_id: int,
    exception_update: dict,
    session: AsyncSession = Depends(get_session),
):
    """Update an exception."""
    db_exception = await crud_exception.get_or_404(session, exception_id)
    return await crud_exception.update(session, db_obj=db_exception, obj_in=exception_update)


@router.post("/exceptions/{exception_id}/approve", response_model=core_models.Exception)
async def approve_exception(
    exception_id: int,
    approved_by_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Approve an exception request."""
    db_exception = await crud_exception.get_or_404(session, exception_id)

    if db_exception.status != Status.DRAFT:
        raise HTTPException(status_code=400, detail="Only draft exceptions can be approved")

    return await crud_exception.update(session, db_obj=db_exception, obj_in={
        "status": Status.ACTIVE,
        "approval_date": datetime.utcnow(),
        "approved_by_id": approved_by_id,
    })


@router.post("/exceptions/{exception_id}/reject", response_model=core_models.Exception)
async def reject_exception(
    exception_id: int,
    rejection_reason: str,
    session: AsyncSession = Depends(get_session),
):
    """Reject an exception request."""
    db_exception = await crud_exception.get_or_404(session, exception_id)

    if db_exception.status != Status.DRAFT:
        raise HTTPException(status_code=400, detail="Only draft exceptions can be rejected")

    return await crud_exception.update(session, db_obj=db_exception, obj_in={
        "status": Status.CLOSED,
    })


@router.post("/exceptions/{exception_id}/extend", response_model=core_models.Exception)
async def extend_exception(
    exception_id: int,
    new_expiration_date: datetime,
    extension_justification: str,
    approved_by_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Extend an exception's expiration date."""
    db_exception = await crud_exception.get_or_404(session, exception_id)

    if new_expiration_date <= db_exception.expiration_date:
        raise HTTPException(
            status_code=400,
            detail="New expiration date must be after current expiration"
        )

    return await crud_exception.update(session, db_obj=db_exception, obj_in={
        "expiration_date": new_expiration_date,
    })


@router.get("/exceptions/expiring-soon", response_model=List[core_models.Exception])
async def get_expiring_exceptions(
    days: int = Query(30, ge=1, le=365, description="Number of days to look ahead"),
    tenant_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
):
    """Get exceptions expiring within the specified number of days."""
    now = datetime.utcnow()
    deadline = now + timedelta(days=days)

    query = select(core_models.Exception).where(
        core_models.Exception.status == Status.ACTIVE,
        core_models.Exception.expiration_date >= now,
        core_models.Exception.expiration_date <= deadline,
    )
    if tenant_id:
        query = query.where(core_models.Exception.tenant_id == tenant_id)

    result = await session.execute(query)
    return result.scalars().all()
