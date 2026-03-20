from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.db import get_db
from app.models.core_models import IMSAssessment, IMSFinding, IMSCorrectiveAction
from app.schemas.assessments import (
    AssessmentCreate, AssessmentUpdate, AssessmentResponse,
    FindingCreate, FindingUpdate, FindingResponse,
    CorrectiveActionCreate, CorrectiveActionUpdate, CorrectiveActionResponse,
)

router = APIRouter()


# ── Assessments ────────────────────────────────────────────────────────────


@router.get("/", response_model=list[AssessmentResponse])
async def list_assessments(
    tenant_id: UUID = Query(...),
    assessment_type: str | None = None,
    status: str | None = None,
    domain: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    query = select(IMSAssessment).where(IMSAssessment.tenant_id == tenant_id)
    if assessment_type:
        query = query.where(IMSAssessment.assessment_type == assessment_type)
    if status:
        query = query.where(IMSAssessment.status == status)
    if domain:
        query = query.where(IMSAssessment.domain == domain)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment(assessment_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IMSAssessment).where(IMSAssessment.id == assessment_id))
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment


@router.post("/", response_model=AssessmentResponse, status_code=201)
async def create_assessment(
    data: AssessmentCreate,
    tenant_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    assessment = IMSAssessment(tenant_id=tenant_id, **data.model_dump())
    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)
    return assessment


@router.patch("/{assessment_id}", response_model=AssessmentResponse)
async def update_assessment(assessment_id: UUID, data: AssessmentUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IMSAssessment).where(IMSAssessment.id == assessment_id))
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(assessment, field, value)
    await db.commit()
    await db.refresh(assessment)
    return assessment


@router.delete("/{assessment_id}", status_code=204)
async def delete_assessment(assessment_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IMSAssessment).where(IMSAssessment.id == assessment_id))
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    await db.delete(assessment)
    await db.commit()


# ── Findings ───────────────────────────────────────────────────────────────


@router.get("/findings/", response_model=list[FindingResponse])
async def list_findings(
    tenant_id: UUID = Query(...),
    assessment_id: UUID | None = None,
    severity: str | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    query = select(IMSFinding).where(IMSFinding.tenant_id == tenant_id)
    if assessment_id:
        query = query.where(IMSFinding.assessment_id == assessment_id)
    if severity:
        query = query.where(IMSFinding.severity == severity)
    if status:
        query = query.where(IMSFinding.status == status)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/findings/{finding_id}", response_model=FindingResponse)
async def get_finding(finding_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IMSFinding).where(IMSFinding.id == finding_id))
    finding = result.scalar_one_or_none()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    return finding


@router.post("/findings/", response_model=FindingResponse, status_code=201)
async def create_finding(
    data: FindingCreate,
    tenant_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    finding = IMSFinding(tenant_id=tenant_id, **data.model_dump())
    db.add(finding)
    await db.commit()
    await db.refresh(finding)
    return finding


@router.patch("/findings/{finding_id}", response_model=FindingResponse)
async def update_finding(finding_id: UUID, data: FindingUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IMSFinding).where(IMSFinding.id == finding_id))
    finding = result.scalar_one_or_none()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(finding, field, value)
    await db.commit()
    await db.refresh(finding)
    return finding


@router.delete("/findings/{finding_id}", status_code=204)
async def delete_finding(finding_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IMSFinding).where(IMSFinding.id == finding_id))
    finding = result.scalar_one_or_none()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    await db.delete(finding)
    await db.commit()


# ── Corrective Actions ─────────────────────────────────────────────────────


@router.get("/corrective-actions/", response_model=list[CorrectiveActionResponse])
async def list_corrective_actions(
    tenant_id: UUID = Query(...),
    finding_id: UUID | None = None,
    risk_id: UUID | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    query = select(IMSCorrectiveAction).where(IMSCorrectiveAction.tenant_id == tenant_id)
    if finding_id:
        query = query.where(IMSCorrectiveAction.finding_id == finding_id)
    if risk_id:
        query = query.where(IMSCorrectiveAction.risk_id == risk_id)
    if status:
        query = query.where(IMSCorrectiveAction.status == status)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/corrective-actions/{action_id}", response_model=CorrectiveActionResponse)
async def get_corrective_action(action_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(IMSCorrectiveAction).where(IMSCorrectiveAction.id == action_id)
    )
    action = result.scalar_one_or_none()
    if not action:
        raise HTTPException(status_code=404, detail="CorrectiveAction not found")
    return action


@router.post("/corrective-actions/", response_model=CorrectiveActionResponse, status_code=201)
async def create_corrective_action(
    data: CorrectiveActionCreate,
    tenant_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    action = IMSCorrectiveAction(tenant_id=tenant_id, **data.model_dump())
    db.add(action)
    await db.commit()
    await db.refresh(action)
    return action


@router.patch("/corrective-actions/{action_id}", response_model=CorrectiveActionResponse)
async def update_corrective_action(
    action_id: UUID, data: CorrectiveActionUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(IMSCorrectiveAction).where(IMSCorrectiveAction.id == action_id)
    )
    action = result.scalar_one_or_none()
    if not action:
        raise HTTPException(status_code=404, detail="CorrectiveAction not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(action, field, value)
    await db.commit()
    await db.refresh(action)
    return action


@router.delete("/corrective-actions/{action_id}", status_code=204)
async def delete_corrective_action(action_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(IMSCorrectiveAction).where(IMSCorrectiveAction.id == action_id)
    )
    action = result.scalar_one_or_none()
    if not action:
        raise HTTPException(status_code=404, detail="CorrectiveAction not found")
    await db.delete(action)
    await db.commit()
