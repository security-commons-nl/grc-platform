"""Human-In-The-Loop checkpoints endpoints (M4 AI Governance).

Append-only audit-trail van menselijke beslissingen op AI-output.
Onmisbaar voor EU AI Act art. 14 (menselijk toezicht).
"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, get_current_user, require_role
from app.core.db import get_db
from app.models.core_models import AIHITLCheckpoint, AIAuditLog
from app.schemas.ai_hitl import HITLCheckpointCreate, HITLCheckpointResponse

router = APIRouter()


class AIAuditLogWithReview(BaseModel):
    """AI-audit-log uitgebreid met telling van bijbehorende HITL-reviews."""

    id: UUID
    tenant_id: UUID
    user_id: UUID | None
    agent_name: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    feedback: str | None
    review_count: int
    last_decision: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[HITLCheckpointResponse])
async def list_hitl_checkpoints(
    audit_log_id: UUID | None = None,
    decision: str | None = None,
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(AIHITLCheckpoint).where(
        AIHITLCheckpoint.tenant_id == current_user.tenant_id
    )
    if audit_log_id:
        query = query.where(AIHITLCheckpoint.audit_log_id == audit_log_id)
    if decision:
        query = query.where(AIHITLCheckpoint.decision == decision)
    query = query.order_by(AIHITLCheckpoint.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/audit-logs", response_model=list[AIAuditLogWithReview])
async def list_audit_logs_with_review(
    only_unreviewed: bool = Query(
        False, description="Toon alleen audit-logs zonder enige HITL-review."
    ),
    agent_name: str | None = Query(None, description="Filter op naam van de AI-agent."),
    skip: int = 0,
    limit: int = Query(50, ge=1, le=200),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """AI-agent-activiteit met review-status — voedt de HITL-review-UI.

    Per audit-log levert dit endpoint het aantal HITL-checkpoints en het
    laatste oordeel. Voor M4-UI zodat reviewers een werklijst hebben van
    "wat heeft de agent gedaan en is er al naar gekeken".
    """
    # Subquery: aantal HITL-checkpoints + laatste decision per audit-log
    count_subq = (
        select(
            AIHITLCheckpoint.audit_log_id.label("audit_log_id"),
            func.count(AIHITLCheckpoint.id).label("review_count"),
        )
        .where(AIHITLCheckpoint.tenant_id == current_user.tenant_id)
        .group_by(AIHITLCheckpoint.audit_log_id)
        .subquery()
    )

    query = (
        select(
            AIAuditLog,
            func.coalesce(count_subq.c.review_count, 0).label("review_count"),
        )
        .outerjoin(count_subq, count_subq.c.audit_log_id == AIAuditLog.id)
        .where(AIAuditLog.tenant_id == current_user.tenant_id)
    )

    if only_unreviewed:
        query = query.where(count_subq.c.review_count.is_(None))

    if agent_name:
        query = query.where(AIAuditLog.agent_name == agent_name)

    query = query.order_by(AIAuditLog.created_at.desc()).offset(skip).limit(limit)
    rows = (await db.execute(query)).all()

    # Laatste decision per audit_log_id ophalen — kleine N+1 maar limit is begrensd
    audit_log_ids = [r[0].id for r in rows]
    last_decisions: dict[UUID, str] = {}
    if audit_log_ids:
        latest_q = (
            select(
                AIHITLCheckpoint.audit_log_id,
                AIHITLCheckpoint.decision,
                AIHITLCheckpoint.created_at,
            )
            .where(
                AIHITLCheckpoint.tenant_id == current_user.tenant_id,
                AIHITLCheckpoint.audit_log_id.in_(audit_log_ids),
            )
            .order_by(
                AIHITLCheckpoint.audit_log_id,
                AIHITLCheckpoint.created_at.desc(),
            )
        )
        for row in (await db.execute(latest_q)).all():
            aid = row[0]
            if aid not in last_decisions:
                last_decisions[aid] = row[1]

    return [
        AIAuditLogWithReview(
            id=log.id,
            tenant_id=log.tenant_id,
            user_id=log.user_id,
            agent_name=log.agent_name,
            model=log.model,
            prompt_tokens=log.prompt_tokens,
            completion_tokens=log.completion_tokens,
            feedback=log.feedback,
            review_count=int(count),
            last_decision=last_decisions.get(log.id),
            created_at=log.created_at,
        )
        for (log, count) in rows
    ]


@router.post("/", response_model=HITLCheckpointResponse, status_code=201)
async def create_hitl_checkpoint(
    data: HITLCheckpointCreate,
    current_user: CurrentUser = Depends(require_role("discipline_eigenaar")),
    db: AsyncSession = Depends(get_db),
):
    """Leg een menselijke review-beslissing vast op een AI-uitvoer.

    De review wordt geattribueerd aan de geauthenticeerde user — niet aan
    een vrije UUID in het payload — zodat de audit-trail consistent is met
    de identiteit die de actie uitvoerde.
    """
    # Verifieer dat de audit-log bestaat in dezelfde tenant
    audit_check = await db.execute(
        select(AIAuditLog).where(
            AIAuditLog.id == data.audit_log_id,
            AIAuditLog.tenant_id == current_user.tenant_id,
        )
    )
    if audit_check.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=404,
            detail="audit_log_id not found in this tenant",
        )

    checkpoint = AIHITLCheckpoint(
        tenant_id=current_user.tenant_id,
        audit_log_id=data.audit_log_id,
        reviewer_user_id=current_user.id,
        decision=data.decision,
        reason=data.reason,
    )
    db.add(checkpoint)
    await db.flush()
    await db.refresh(checkpoint)
    return checkpoint
