"""Human-In-The-Loop checkpoints endpoints (M4 AI Governance).

Append-only audit-trail van menselijke beslissingen op AI-output.
Onmisbaar voor EU AI Act art. 14 (menselijk toezicht).
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, get_current_user, require_role
from app.core.db import get_db
from app.models.core_models import AIHITLCheckpoint, AIAuditLog
from app.schemas.ai_hitl import HITLCheckpointCreate, HITLCheckpointResponse

router = APIRouter()


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
