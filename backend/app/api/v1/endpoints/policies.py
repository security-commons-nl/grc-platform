"""
Policy Management Endpoints
Handles Policies with workflow states (Draft -> Review -> Approved -> Published).
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.db import get_session
from app.core.crud import CRUDBase
from app.models.core_models import (
    Policy,
    PolicyState,
)

router = APIRouter()
crud_policy = CRUDBase(Policy)


# =============================================================================
# POLICY CRUD
# =============================================================================

@router.get("/", response_model=List[Policy])
async def list_policies(
    skip: int = 0,
    limit: int = 100,
    tenant_id: Optional[int] = Query(None),
    state: Optional[PolicyState] = Query(None),
    scope_id: Optional[int] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    """List policies with optional filters."""
    filters = {}
    if tenant_id:
        filters["tenant_id"] = tenant_id
    if state:
        filters["state"] = state
    if scope_id:
        filters["scope_id"] = scope_id

    return await crud_policy.get_multi(session, skip=skip, limit=limit, filters=filters)


@router.post("/", response_model=Policy)
async def create_policy(
    policy: Policy,
    session: AsyncSession = Depends(get_session),
):
    """Create a new policy (starts in Draft state)."""
    policy.state = PolicyState.DRAFT
    policy.version = 1
    return await crud_policy.create(session, obj_in=policy)


@router.get("/{policy_id}", response_model=Policy)
async def get_policy(
    policy_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get a policy by ID."""
    return await crud_policy.get_or_404(session, policy_id)


@router.patch("/{policy_id}", response_model=Policy)
async def update_policy(
    policy_id: int,
    policy_update: dict,
    session: AsyncSession = Depends(get_session),
):
    """
    Update a policy.
    Only allowed in Draft state. Other states require workflow transitions.
    """
    db_policy = await crud_policy.get_or_404(session, policy_id)

    # Content updates only allowed in Draft state
    if db_policy.state != PolicyState.DRAFT:
        # Only allow metadata updates, not content
        content_fields = ["title", "content"]
        for field in content_fields:
            if field in policy_update:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot update {field} when policy is in {db_policy.state} state. Create a new version instead."
                )

    policy_update["updated_at"] = datetime.utcnow()
    return await crud_policy.update(session, db_obj=db_policy, obj_in=policy_update)


@router.delete("/{policy_id}")
async def delete_policy(
    policy_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Delete a policy (only allowed for Draft policies)."""
    db_policy = await crud_policy.get_or_404(session, policy_id)

    if db_policy.state != PolicyState.DRAFT:
        raise HTTPException(
            status_code=400,
            detail="Only draft policies can be deleted. Archive published policies instead."
        )

    deleted = await crud_policy.delete(session, id=policy_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Policy not found")
    return {"message": "Policy deleted"}


# =============================================================================
# POLICY WORKFLOW (Draft -> Review -> Approved -> Published -> Archived)
# =============================================================================

@router.post("/{policy_id}/submit-for-review", response_model=Policy)
async def submit_for_review(
    policy_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Submit a draft policy for review."""
    db_policy = await crud_policy.get_or_404(session, policy_id)

    if db_policy.state != PolicyState.DRAFT:
        raise HTTPException(
            status_code=400,
            detail=f"Only draft policies can be submitted for review. Current state: {db_policy.state}"
        )

    return await crud_policy.update(session, db_obj=db_policy, obj_in={
        "state": PolicyState.REVIEW,
        "updated_at": datetime.utcnow(),
    })


@router.post("/{policy_id}/approve", response_model=Policy)
async def approve_policy(
    policy_id: int,
    approved_by_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Approve a policy that is in review."""
    db_policy = await crud_policy.get_or_404(session, policy_id)

    if db_policy.state != PolicyState.REVIEW:
        raise HTTPException(
            status_code=400,
            detail=f"Only policies in review can be approved. Current state: {db_policy.state}"
        )

    return await crud_policy.update(session, db_obj=db_policy, obj_in={
        "state": PolicyState.APPROVED,
        "approved_by_id": approved_by_id,
        "updated_at": datetime.utcnow(),
    })


@router.post("/{policy_id}/reject", response_model=Policy)
async def reject_policy(
    policy_id: int,
    rejection_reason: str,
    session: AsyncSession = Depends(get_session),
):
    """Reject a policy that is in review, returns it to draft state."""
    db_policy = await crud_policy.get_or_404(session, policy_id)

    if db_policy.state != PolicyState.REVIEW:
        raise HTTPException(
            status_code=400,
            detail=f"Only policies in review can be rejected. Current state: {db_policy.state}"
        )

    return await crud_policy.update(session, db_obj=db_policy, obj_in={
        "state": PolicyState.DRAFT,
        "updated_at": datetime.utcnow(),
    })


@router.post("/{policy_id}/publish", response_model=Policy)
async def publish_policy(
    policy_id: int,
    effective_date: Optional[datetime] = None,
    session: AsyncSession = Depends(get_session),
):
    """Publish an approved policy."""
    db_policy = await crud_policy.get_or_404(session, policy_id)

    if db_policy.state != PolicyState.APPROVED:
        raise HTTPException(
            status_code=400,
            detail=f"Only approved policies can be published. Current state: {db_policy.state}"
        )

    return await crud_policy.update(session, db_obj=db_policy, obj_in={
        "state": PolicyState.PUBLISHED,
        "effective_date": effective_date or datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    })


@router.post("/{policy_id}/archive", response_model=Policy)
async def archive_policy(
    policy_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Archive a published policy."""
    db_policy = await crud_policy.get_or_404(session, policy_id)

    if db_policy.state != PolicyState.PUBLISHED:
        raise HTTPException(
            status_code=400,
            detail=f"Only published policies can be archived. Current state: {db_policy.state}"
        )

    return await crud_policy.update(session, db_obj=db_policy, obj_in={
        "state": PolicyState.ARCHIVED,
        "expiration_date": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    })


# =============================================================================
# POLICY VERSIONING
# =============================================================================

@router.post("/{policy_id}/new-version", response_model=Policy)
async def create_new_version(
    policy_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new version of a published policy.
    Copies the current policy and creates a new draft with incremented version.
    """
    db_policy = await crud_policy.get_or_404(session, policy_id)

    if db_policy.state not in [PolicyState.PUBLISHED, PolicyState.APPROVED]:
        raise HTTPException(
            status_code=400,
            detail="Can only create new versions from published or approved policies"
        )

    # Create new version
    new_policy = Policy(
        tenant_id=db_policy.tenant_id,
        title=db_policy.title,
        content=db_policy.content,
        state=PolicyState.DRAFT,
        version=db_policy.version + 1,
        scope_id=db_policy.scope_id,
        requirement_id=db_policy.requirement_id,
        created_by_id=db_policy.created_by_id,
    )

    return await crud_policy.create(session, obj_in=new_policy)


@router.get("/{policy_id}/versions", response_model=List[Policy])
async def get_policy_versions(
    policy_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get all versions of a policy (by matching title and tenant)."""
    db_policy = await crud_policy.get_or_404(session, policy_id)

    result = await session.execute(
        select(Policy).where(
            Policy.tenant_id == db_policy.tenant_id,
            Policy.title == db_policy.title,
        ).order_by(Policy.version.desc())
    )
    return result.scalars().all()


# =============================================================================
# POLICY REVIEW REMINDERS
# =============================================================================

@router.get("/due-for-review", response_model=List[Policy])
async def get_policies_due_for_review(
    tenant_id: Optional[int] = None,
    days_ahead: int = Query(30, ge=1, le=365),
    session: AsyncSession = Depends(get_session),
):
    """Get published policies that are due for review within specified days."""
    from datetime import timedelta

    deadline = datetime.utcnow() + timedelta(days=days_ahead)

    query = select(Policy).where(
        Policy.state == PolicyState.PUBLISHED,
        Policy.review_date != None,
        Policy.review_date <= deadline,
    )

    if tenant_id:
        query = query.where(Policy.tenant_id == tenant_id)

    result = await session.execute(query)
    return result.scalars().all()


@router.patch("/{policy_id}/set-review-date", response_model=Policy)
async def set_review_date(
    policy_id: int,
    review_date: datetime,
    session: AsyncSession = Depends(get_session),
):
    """Set or update the review date for a policy."""
    db_policy = await crud_policy.get_or_404(session, policy_id)

    return await crud_policy.update(session, db_obj=db_policy, obj_in={
        "review_date": review_date,
        "updated_at": datetime.utcnow(),
    })
