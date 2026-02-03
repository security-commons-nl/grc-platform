"""
Assessment (Verification) Endpoints
Handles Assessments, Findings, Evidence, and Corrective Actions.
Implements the PDCA "Check" phase.
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.db import get_session
from app.core.crud import CRUDBase
from app.models.core_models import (
    Assessment,
    AssessmentType,
    Finding,
    FindingSeverity,
    Evidence,
    CorrectiveAction,
    Status,
    AuditResult,
)

router = APIRouter()
crud_assessment = CRUDBase(Assessment)
crud_finding = CRUDBase(Finding)
crud_evidence = CRUDBase(Evidence)
crud_corrective_action = CRUDBase(CorrectiveAction)


# =============================================================================
# ASSESSMENT CRUD
# =============================================================================

@router.get("/", response_model=List[Assessment])
async def list_assessments(
    skip: int = 0,
    limit: int = 100,
    tenant_id: Optional[int] = Query(None),
    assessment_type: Optional[AssessmentType] = Query(None),
    status: Optional[Status] = Query(None),
    scope_id: Optional[int] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    """List assessments with optional filters."""
    filters = {}
    if tenant_id:
        filters["tenant_id"] = tenant_id
    if assessment_type:
        filters["type"] = assessment_type
    if status:
        filters["status"] = status
    if scope_id:
        filters["scope_id"] = scope_id

    return await crud_assessment.get_multi(session, skip=skip, limit=limit, filters=filters)


@router.post("/", response_model=Assessment)
async def create_assessment(
    assessment: Assessment,
    session: AsyncSession = Depends(get_session),
):
    """Create a new assessment."""
    return await crud_assessment.create(session, obj_in=assessment)


@router.get("/{assessment_id}", response_model=Assessment)
async def get_assessment(
    assessment_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get an assessment by ID."""
    return await crud_assessment.get_or_404(session, assessment_id)


@router.patch("/{assessment_id}", response_model=Assessment)
async def update_assessment(
    assessment_id: int,
    assessment_update: dict,
    session: AsyncSession = Depends(get_session),
):
    """Update an assessment."""
    db_assessment = await crud_assessment.get_or_404(session, assessment_id)
    return await crud_assessment.update(session, db_obj=db_assessment, obj_in=assessment_update)


@router.delete("/{assessment_id}")
async def delete_assessment(
    assessment_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Delete an assessment."""
    deleted = await crud_assessment.delete(session, id=assessment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return {"message": "Assessment deleted"}


# =============================================================================
# ASSESSMENT LIFECYCLE
# =============================================================================

@router.post("/{assessment_id}/start", response_model=Assessment)
async def start_assessment(
    assessment_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Start an assessment (set status to Active)."""
    db_assessment = await crud_assessment.get_or_404(session, assessment_id)

    if db_assessment.status != Status.DRAFT:
        raise HTTPException(status_code=400, detail="Assessment must be in Draft status to start")

    return await crud_assessment.update(session, db_obj=db_assessment, obj_in={
        "status": Status.ACTIVE,
        "start_date": datetime.utcnow(),
    })


@router.post("/{assessment_id}/complete", response_model=Assessment)
async def complete_assessment(
    assessment_id: int,
    overall_result: AuditResult,
    executive_summary: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
):
    """Complete an assessment with results."""
    db_assessment = await crud_assessment.get_or_404(session, assessment_id)

    if db_assessment.status != Status.ACTIVE:
        raise HTTPException(status_code=400, detail="Assessment must be Active to complete")

    return await crud_assessment.update(session, db_obj=db_assessment, obj_in={
        "status": Status.CLOSED,
        "completed_date": datetime.utcnow(),
        "overall_result": overall_result,
        "executive_summary": executive_summary,
    })


@router.get("/{assessment_id}/summary", response_model=dict)
async def get_assessment_summary(
    assessment_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get summary statistics for an assessment."""
    assessment = await crud_assessment.get_or_404(session, assessment_id)

    # Get findings
    findings = await crud_finding.get_multi_by_field(session, "assessment_id", assessment_id, limit=500)

    # Count by severity
    severity_counts = {s.value: 0 for s in FindingSeverity}
    for finding in findings:
        severity_counts[finding.severity.value] += 1

    # Count by status
    status_counts = {s.value: 0 for s in Status}
    for finding in findings:
        status_counts[finding.status.value] += 1

    return {
        "assessment_id": assessment_id,
        "title": assessment.title,
        "type": assessment.type,
        "status": assessment.status,
        "overall_result": assessment.overall_result,
        "total_findings": len(findings),
        "findings_by_severity": severity_counts,
        "findings_by_status": status_counts,
        "start_date": assessment.start_date,
        "completed_date": assessment.completed_date,
    }


# =============================================================================
# FINDINGS
# =============================================================================

@router.get("/{assessment_id}/findings", response_model=List[Finding])
async def list_assessment_findings(
    assessment_id: int,
    severity: Optional[FindingSeverity] = Query(None),
    status: Optional[Status] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    """List findings for an assessment."""
    await crud_assessment.get_or_404(session, assessment_id)

    query = select(Finding).where(Finding.assessment_id == assessment_id)
    if severity:
        query = query.where(Finding.severity == severity)
    if status:
        query = query.where(Finding.status == status)

    result = await session.execute(query)
    return result.scalars().all()


@router.post("/{assessment_id}/findings", response_model=Finding)
async def create_finding(
    assessment_id: int,
    finding: Finding,
    session: AsyncSession = Depends(get_session),
):
    """Create a finding for an assessment."""
    await crud_assessment.get_or_404(session, assessment_id)

    finding.assessment_id = assessment_id
    return await crud_finding.create(session, obj_in=finding)


@router.get("/findings/{finding_id}", response_model=Finding)
async def get_finding(
    finding_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get a finding by ID."""
    return await crud_finding.get_or_404(session, finding_id)


@router.patch("/findings/{finding_id}", response_model=Finding)
async def update_finding(
    finding_id: int,
    finding_update: dict,
    session: AsyncSession = Depends(get_session),
):
    """Update a finding."""
    db_finding = await crud_finding.get_or_404(session, finding_id)
    return await crud_finding.update(session, db_obj=db_finding, obj_in=finding_update)


@router.post("/findings/{finding_id}/close", response_model=Finding)
async def close_finding(
    finding_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Close a finding."""
    db_finding = await crud_finding.get_or_404(session, finding_id)
    return await crud_finding.update(session, db_obj=db_finding, obj_in={"status": Status.CLOSED})


# =============================================================================
# EVIDENCE
# =============================================================================

@router.get("/evidence/", response_model=List[Evidence])
async def list_evidence(
    skip: int = 0,
    limit: int = 100,
    measure_id: Optional[int] = Query(None),
    assessment_id: Optional[int] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    """List evidence with optional filters."""
    filters = {}
    if measure_id:
        filters["measure_id"] = measure_id
    if assessment_id:
        filters["assessment_id"] = assessment_id

    return await crud_evidence.get_multi(session, skip=skip, limit=limit, filters=filters)


@router.post("/evidence/", response_model=Evidence)
async def create_evidence(
    evidence: Evidence,
    session: AsyncSession = Depends(get_session),
):
    """Create new evidence."""
    return await crud_evidence.create(session, obj_in=evidence)


@router.get("/evidence/{evidence_id}", response_model=Evidence)
async def get_evidence(
    evidence_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get evidence by ID."""
    return await crud_evidence.get_or_404(session, evidence_id)


@router.delete("/evidence/{evidence_id}")
async def delete_evidence(
    evidence_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Delete evidence."""
    deleted = await crud_evidence.delete(session, id=evidence_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return {"message": "Evidence deleted"}


# =============================================================================
# CORRECTIVE ACTIONS
# =============================================================================

@router.get("/findings/{finding_id}/corrective-actions", response_model=List[CorrectiveAction])
async def list_finding_corrective_actions(
    finding_id: int,
    session: AsyncSession = Depends(get_session),
):
    """List corrective actions for a finding."""
    await crud_finding.get_or_404(session, finding_id)
    return await crud_corrective_action.get_multi_by_field(session, "finding_id", finding_id)


@router.post("/findings/{finding_id}/corrective-actions", response_model=CorrectiveAction)
async def create_corrective_action(
    finding_id: int,
    corrective_action: CorrectiveAction,
    session: AsyncSession = Depends(get_session),
):
    """Create a corrective action for a finding."""
    await crud_finding.get_or_404(session, finding_id)

    corrective_action.finding_id = finding_id
    return await crud_corrective_action.create(session, obj_in=corrective_action)


@router.get("/corrective-actions/{action_id}", response_model=CorrectiveAction)
async def get_corrective_action(
    action_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get a corrective action by ID."""
    return await crud_corrective_action.get_or_404(session, action_id)


@router.patch("/corrective-actions/{action_id}", response_model=CorrectiveAction)
async def update_corrective_action(
    action_id: int,
    action_update: dict,
    session: AsyncSession = Depends(get_session),
):
    """Update a corrective action."""
    db_action = await crud_corrective_action.get_or_404(session, action_id)
    return await crud_corrective_action.update(session, db_obj=db_action, obj_in=action_update)


@router.post("/corrective-actions/{action_id}/complete", response_model=CorrectiveAction)
async def complete_corrective_action(
    action_id: int,
    completed_by_id: int,
    completion_notes: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
):
    """Mark a corrective action as completed."""
    db_action = await crud_corrective_action.get_or_404(session, action_id)

    return await crud_corrective_action.update(session, db_obj=db_action, obj_in={
        "status": Status.CLOSED,
        "completed_date": datetime.utcnow(),
        "completed_by_id": completed_by_id,
        "completion_notes": completion_notes,
    })
