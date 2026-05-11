from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.auth import CurrentUser, get_current_user, require_role
from app.core.db import get_db
from app.models.core_models import IMSAssessment, IMSFinding, IMSCorrectiveAction, IMSAISystem
from app.schemas.assessments import (
    AssessmentCreate, AssessmentUpdate, AssessmentResponse,
    FindingCreate, FindingUpdate, FindingResponse,
    CorrectiveActionCreate, CorrectiveActionUpdate, CorrectiveActionResponse,
)


async def _ensure_ai_system_in_tenant(
    db: AsyncSession, ai_system_id: UUID, tenant_id: UUID
) -> None:
    """Verifieer dat een ai_system_id in dezelfde tenant zit. Voorkomt
    cross-tenant koppelingen via vrije UUID-input."""
    result = await db.execute(
        select(IMSAISystem).where(
            IMSAISystem.id == ai_system_id,
            IMSAISystem.tenant_id == tenant_id,
        )
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=404, detail="ai_system_id not found in this tenant"
        )

router = APIRouter()


# ── Assessments ────────────────────────────────────────────────────────────


@router.get("/", response_model=list[AssessmentResponse])
async def list_assessments(
    assessment_type: str | None = None,
    status: str | None = None,
    domain: str | None = None,
    ai_system_id: UUID | None = None,
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(IMSAssessment).where(IMSAssessment.tenant_id == current_user.tenant_id)
    if assessment_type:
        query = query.where(IMSAssessment.assessment_type == assessment_type)
    if status:
        query = query.where(IMSAssessment.status == status)
    if domain:
        query = query.where(IMSAssessment.domain == domain)
    if ai_system_id:
        query = query.where(IMSAssessment.ai_system_id == ai_system_id)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment(
    assessment_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(IMSAssessment).where(IMSAssessment.id == assessment_id))
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment niet gevonden")
    return assessment


@router.post("/", response_model=AssessmentResponse, status_code=201)
async def create_assessment(
    data: AssessmentCreate,
    current_user: CurrentUser = Depends(require_role("discipline_eigenaar")),
    db: AsyncSession = Depends(get_db),
):
    if data.ai_system_id is not None:
        await _ensure_ai_system_in_tenant(db, data.ai_system_id, current_user.tenant_id)

    # ai_conformity assessments moeten gekoppeld zijn aan een AI-systeem —
    # anders ontbreekt de scope (welk systeem wordt beoordeeld?)
    if data.assessment_type == "ai_conformity" and data.ai_system_id is None:
        raise HTTPException(
            status_code=400,
            detail="ai_conformity assessment requires ai_system_id",
        )

    assessment = IMSAssessment(tenant_id=current_user.tenant_id, **data.model_dump())
    db.add(assessment)
    await db.flush()
    await db.refresh(assessment)
    return assessment


@router.patch("/{assessment_id}", response_model=AssessmentResponse)
async def update_assessment(
    assessment_id: UUID,
    data: AssessmentUpdate,
    current_user: CurrentUser = Depends(require_role("discipline_eigenaar")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(IMSAssessment).where(IMSAssessment.id == assessment_id))
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment niet gevonden")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(assessment, field, value)
    await db.flush()
    await db.refresh(assessment)
    return assessment


@router.delete("/{assessment_id}", status_code=204)
async def delete_assessment(
    assessment_id: UUID,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(IMSAssessment).where(IMSAssessment.id == assessment_id))
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment niet gevonden")
    await db.delete(assessment)
    await db.flush()


# ── Findings ───────────────────────────────────────────────────────────────


@router.get("/findings/", response_model=list[FindingResponse])
async def list_findings(
    assessment_id: UUID | None = None,
    severity: str | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(IMSFinding).where(IMSFinding.tenant_id == current_user.tenant_id)
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
async def get_finding(
    finding_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(IMSFinding).where(IMSFinding.id == finding_id))
    finding = result.scalar_one_or_none()
    if not finding:
        raise HTTPException(status_code=404, detail="Bevinding niet gevonden")
    return finding


@router.post("/findings/", response_model=FindingResponse, status_code=201)
async def create_finding(
    data: FindingCreate,
    current_user: CurrentUser = Depends(require_role("discipline_eigenaar")),
    db: AsyncSession = Depends(get_db),
):
    finding = IMSFinding(tenant_id=current_user.tenant_id, **data.model_dump())
    db.add(finding)
    await db.flush()
    await db.refresh(finding)
    return finding


@router.patch("/findings/{finding_id}", response_model=FindingResponse)
async def update_finding(
    finding_id: UUID,
    data: FindingUpdate,
    current_user: CurrentUser = Depends(require_role("discipline_eigenaar")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(IMSFinding).where(IMSFinding.id == finding_id))
    finding = result.scalar_one_or_none()
    if not finding:
        raise HTTPException(status_code=404, detail="Bevinding niet gevonden")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(finding, field, value)
    await db.flush()
    await db.refresh(finding)
    return finding


@router.delete("/findings/{finding_id}", status_code=204)
async def delete_finding(
    finding_id: UUID,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(IMSFinding).where(IMSFinding.id == finding_id))
    finding = result.scalar_one_or_none()
    if not finding:
        raise HTTPException(status_code=404, detail="Bevinding niet gevonden")
    await db.delete(finding)
    await db.flush()


# ── Corrective Actions ─────────────────────────────────────────────────────


@router.get("/corrective-actions/", response_model=list[CorrectiveActionResponse])
async def list_corrective_actions(
    finding_id: UUID | None = None,
    risk_id: UUID | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(IMSCorrectiveAction).where(IMSCorrectiveAction.tenant_id == current_user.tenant_id)
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
async def get_corrective_action(
    action_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(IMSCorrectiveAction).where(IMSCorrectiveAction.id == action_id)
    )
    action = result.scalar_one_or_none()
    if not action:
        raise HTTPException(status_code=404, detail="Corrigerende maatregel niet gevonden")
    return action


@router.post("/corrective-actions/", response_model=CorrectiveActionResponse, status_code=201)
async def create_corrective_action(
    data: CorrectiveActionCreate,
    current_user: CurrentUser = Depends(require_role("lijnmanager")),
    db: AsyncSession = Depends(get_db),
):
    action = IMSCorrectiveAction(tenant_id=current_user.tenant_id, **data.model_dump())
    db.add(action)
    await db.flush()
    await db.refresh(action)
    return action


@router.patch("/corrective-actions/{action_id}", response_model=CorrectiveActionResponse)
async def update_corrective_action(
    action_id: UUID,
    data: CorrectiveActionUpdate,
    current_user: CurrentUser = Depends(require_role("lijnmanager")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(IMSCorrectiveAction).where(IMSCorrectiveAction.id == action_id)
    )
    action = result.scalar_one_or_none()
    if not action:
        raise HTTPException(status_code=404, detail="Corrigerende maatregel niet gevonden")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(action, field, value)
    await db.flush()
    await db.refresh(action)
    return action


@router.delete("/corrective-actions/{action_id}", status_code=204)
async def delete_corrective_action(
    action_id: UUID,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(IMSCorrectiveAction).where(IMSCorrectiveAction.id == action_id)
    )
    action = result.scalar_one_or_none()
    if not action:
        raise HTTPException(status_code=404, detail="Corrigerende maatregel niet gevonden")
    await db.delete(action)
    await db.flush()
