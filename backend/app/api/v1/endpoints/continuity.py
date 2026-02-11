"""
Business Continuity Management System (BCMS) Endpoints
Handles Continuity Plans and Tests.
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_
from sqlmodel import select

from app.core.db import get_session
from app.core.crud import ScopedTenantCRUDBase, TenantCRUDBase
from app.core.rbac import get_tenant_id, get_scope_access, require_editor
from app.models.core_models import (
    ContinuityPlan,
    ContinuityTest,
    Status,
    AuditResult,
    User,
    AuditAction,
)
from app.services.audit_service import record_audit

router = APIRouter()
crud_plan = ScopedTenantCRUDBase(ContinuityPlan)
crud_test = TenantCRUDBase(ContinuityTest)


# =============================================================================
# CONTINUITY PLANS
# =============================================================================

@router.get("/plans/", response_model=List[ContinuityPlan])
async def list_continuity_plans(
    skip: int = 0,
    limit: int = 100,
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    scope_id: Optional[int] = Query(None),
    plan_type: Optional[str] = Query(None, description="BCP, DRP, IRP, etc."),
    status: Optional[Status] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    """List continuity plans."""
    filters = {}
    if scope_id:
        filters["scope_id"] = scope_id
    if plan_type:
        filters["plan_type"] = plan_type
    if status:
        filters["status"] = status

    return await crud_plan.get_multi_scoped(
        session, tenant_id, accessible_scopes,
        skip=skip, limit=limit, filters=filters,
    )


@router.post("/plans/", response_model=ContinuityPlan)
async def create_continuity_plan(
    plan: ContinuityPlan,
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """Create a new continuity plan."""
    plan.version = 1
    plan.status = Status.DRAFT
    return await crud_plan.create(session, obj_in=plan, tenant_id=tenant_id)


@router.get("/plans/{plan_id}", response_model=ContinuityPlan)
async def get_continuity_plan(
    plan_id: int,
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
):
    """Get a continuity plan by ID."""
    return await crud_plan.get_scoped_or_404(session, plan_id, tenant_id, accessible_scopes)


@router.patch("/plans/{plan_id}", response_model=ContinuityPlan)
async def update_continuity_plan(
    plan_id: int,
    plan_update: dict,
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
):
    """Update a continuity plan."""
    db_plan = await crud_plan.get_scoped_or_404(session, plan_id, tenant_id, accessible_scopes)
    plan_update["updated_at"] = datetime.utcnow()
    return await crud_plan.update(session, db_obj=db_plan, obj_in=plan_update, tenant_id=tenant_id)


@router.delete("/plans/{plan_id}")
async def delete_continuity_plan(
    plan_id: int,
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
):
    """Delete a continuity plan (only drafts) and all FK-dependent rows."""
    db_plan = await crud_plan.get_scoped_or_404(session, plan_id, tenant_id, accessible_scopes)

    if db_plan.status != Status.DRAFT:
        raise HTTPException(
            status_code=400,
            detail="Only draft plans can be deleted"
        )

    from sqlalchemy import text
    # Delete non-nullable FK rows
    await session.execute(
        text("DELETE FROM continuitytest WHERE plan_id = :pid"),
        {"pid": plan_id},
    )
    # Null out nullable FK columns
    await session.execute(
        text("UPDATE incident SET continuity_plan_id = NULL WHERE continuity_plan_id = :pid"),
        {"pid": plan_id},
    )
    # Delete the plan itself
    await session.execute(
        text("DELETE FROM continuityplan WHERE id = :pid AND tenant_id = :tid"),
        {"pid": plan_id, "tid": tenant_id},
    )
    await session.commit()
    return {"message": "Plan deleted"}


# =============================================================================
# PLAN LIFECYCLE
# =============================================================================

@router.post("/plans/{plan_id}/activate", response_model=ContinuityPlan)
async def activate_plan(
    plan_id: int,
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_editor),
):
    """Activate a continuity plan."""
    db_plan = await crud_plan.get_scoped_or_404(session, plan_id, tenant_id, accessible_scopes)

    if db_plan.status != Status.DRAFT:
        raise HTTPException(
            status_code=400,
            detail="Only draft plans can be activated"
        )

    result = await crud_plan.update(session, db_obj=db_plan, obj_in={
        "status": Status.ACTIVE,
        "approved_by_id": current_user.id,
        "approved_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }, tenant_id=tenant_id)

    await record_audit(
        session, tenant_id=tenant_id, entity_type="ContinuityPlan", entity_id=plan_id,
        action=AuditAction.APPROVE, changed_by_id=current_user.id,
        field_name="status", old_value="Draft", new_value="Active",
    )

    return result


@router.post("/plans/{plan_id}/archive", response_model=ContinuityPlan)
async def archive_plan(
    plan_id: int,
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
):
    """Archive a continuity plan."""
    db_plan = await crud_plan.get_scoped_or_404(session, plan_id, tenant_id, accessible_scopes)

    return await crud_plan.update(session, db_obj=db_plan, obj_in={
        "status": Status.DEPRECATED,
        "updated_at": datetime.utcnow(),
    }, tenant_id=tenant_id)


@router.post("/plans/{plan_id}/new-version", response_model=ContinuityPlan)
async def create_new_plan_version(
    plan_id: int,
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
):
    """Create a new version of a continuity plan."""
    db_plan = await crud_plan.get_scoped_or_404(session, plan_id, tenant_id, accessible_scopes)

    if db_plan.status != Status.ACTIVE:
        raise HTTPException(
            status_code=400,
            detail="Can only create new versions from active plans"
        )

    # Create new version
    new_plan = ContinuityPlan(
        tenant_id=tenant_id,
        scope_id=db_plan.scope_id,
        title=db_plan.title,
        plan_type=db_plan.plan_type,
        content=db_plan.content,
        rto_hours=db_plan.rto_hours,
        rpo_hours=db_plan.rpo_hours,
        mtpd_hours=db_plan.mtpd_hours,
        version=db_plan.version + 1,
        status=Status.DRAFT,
        owner_id=db_plan.owner_id,
    )

    return await crud_plan.create(session, obj_in=new_plan, tenant_id=tenant_id)


# =============================================================================
# PLAN REVIEW
# =============================================================================

@router.get("/plans/due-for-review", response_model=List[ContinuityPlan])
async def get_plans_due_for_review(
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    days_ahead: int = Query(30, ge=1, le=365),
    session: AsyncSession = Depends(get_session),
):
    """Get plans due for review within specified days."""
    deadline = datetime.utcnow() + timedelta(days=days_ahead)

    query = select(ContinuityPlan).where(
        ContinuityPlan.tenant_id == tenant_id,
        ContinuityPlan.status == Status.ACTIVE,
        ContinuityPlan.review_date != None,
        ContinuityPlan.review_date <= deadline,
    )

    # Apply scope filtering
    if accessible_scopes is not None:
        query = query.where(
            or_(
                ContinuityPlan.scope_id.in_(accessible_scopes),
                ContinuityPlan.scope_id.is_(None),
            )
        )

    result = await session.execute(query)
    return result.scalars().all()


@router.patch("/plans/{plan_id}/set-review-date", response_model=ContinuityPlan)
async def set_plan_review_date(
    plan_id: int,
    review_date: datetime,
    tenant_id: int = Depends(get_tenant_id),
    accessible_scopes: set[int] | None = Depends(get_scope_access),
    session: AsyncSession = Depends(get_session),
):
    """Set the review date for a plan."""
    db_plan = await crud_plan.get_scoped_or_404(session, plan_id, tenant_id, accessible_scopes)

    return await crud_plan.update(session, db_obj=db_plan, obj_in={
        "review_date": review_date,
        "updated_at": datetime.utcnow(),
    }, tenant_id=tenant_id)


# =============================================================================
# CONTINUITY TESTS
# =============================================================================

@router.get("/tests/", response_model=List[ContinuityTest])
async def list_continuity_tests(
    skip: int = 0,
    limit: int = 100,
    tenant_id: int = Depends(get_tenant_id),
    plan_id: Optional[int] = Query(None),
    test_type: Optional[str] = Query(None, description="Tabletop, Walkthrough, Full"),
    result: Optional[AuditResult] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    """List continuity tests."""
    query = select(ContinuityTest).where(ContinuityTest.tenant_id == tenant_id)

    if plan_id:
        query = query.where(ContinuityTest.plan_id == plan_id)
    if test_type:
        query = query.where(ContinuityTest.test_type == test_type)
    if result:
        query = query.where(ContinuityTest.result == result)

    query = query.order_by(ContinuityTest.scheduled_date.desc())
    query = query.offset(skip).limit(limit)
    result_set = await session.execute(query)
    return result_set.scalars().all()


@router.post("/tests/", response_model=ContinuityTest)
async def create_continuity_test(
    test: ContinuityTest,
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """Schedule a new continuity test."""
    # Verify plan exists
    await crud_plan.get_or_404(session, test.plan_id, tenant_id)

    test.status = Status.DRAFT
    return await crud_test.create(session, obj_in=test, tenant_id=tenant_id)


@router.get("/tests/{test_id}", response_model=ContinuityTest)
async def get_continuity_test(
    test_id: int,
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """Get a continuity test by ID."""
    return await crud_test.get_or_404(session, test_id, tenant_id)


@router.patch("/tests/{test_id}", response_model=ContinuityTest)
async def update_continuity_test(
    test_id: int,
    test_update: dict,
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """Update a continuity test."""
    db_test = await crud_test.get_or_404(session, test_id, tenant_id)
    test_update["updated_at"] = datetime.utcnow()
    return await crud_test.update(session, db_obj=db_test, obj_in=test_update, tenant_id=tenant_id)


@router.delete("/tests/{test_id}")
async def delete_continuity_test(
    test_id: int,
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """Delete a continuity test."""
    deleted = await crud_test.delete(session, id=test_id, tenant_id=tenant_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Test not found")
    return {"message": "Test deleted"}


# =============================================================================
# TEST LIFECYCLE
# =============================================================================

@router.post("/tests/{test_id}/start", response_model=ContinuityTest)
async def start_test(
    test_id: int,
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """Start a scheduled continuity test."""
    db_test = await crud_test.get_or_404(session, test_id, tenant_id)

    if db_test.status != Status.DRAFT:
        raise HTTPException(
            status_code=400,
            detail="Only draft tests can be started"
        )

    return await crud_test.update(session, db_obj=db_test, obj_in={
        "status": Status.ACTIVE,
        "actual_date": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }, tenant_id=tenant_id)


@router.post("/tests/{test_id}/complete", response_model=ContinuityTest)
async def complete_test(
    test_id: int,
    result: AuditResult,
    findings: Optional[str] = None,
    lessons_learned: Optional[str] = None,
    actual_rto_achieved: Optional[int] = None,
    actual_rpo_achieved: Optional[int] = None,
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """Complete a continuity test with results."""
    db_test = await crud_test.get_or_404(session, test_id, tenant_id)

    if db_test.status != Status.ACTIVE:
        raise HTTPException(
            status_code=400,
            detail="Only active tests can be completed"
        )

    update_data = {
        "status": Status.CLOSED,
        "result": result,
        "completed_date": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    if findings:
        update_data["findings"] = findings
    if lessons_learned:
        update_data["lessons_learned"] = lessons_learned
    if actual_rto_achieved is not None:
        update_data["actual_rto_achieved"] = actual_rto_achieved
    if actual_rpo_achieved is not None:
        update_data["actual_rpo_achieved"] = actual_rpo_achieved

    # Update plan's last tested date
    if db_test.plan_id:
        plan = await crud_plan.get(session, db_test.plan_id, tenant_id)
        if plan:
            await crud_plan.update(session, db_obj=plan, obj_in={
                "last_tested_date": datetime.utcnow(),
            }, tenant_id=tenant_id)

    return await crud_test.update(session, db_obj=db_test, obj_in=update_data, tenant_id=tenant_id)


# =============================================================================
# TEST SCHEDULE
# =============================================================================

@router.get("/tests/upcoming", response_model=List[ContinuityTest])
async def get_upcoming_tests(
    days: int = Query(30, ge=1, le=365),
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """Get tests scheduled within specified days."""
    now = datetime.utcnow()
    deadline = now + timedelta(days=days)

    query = select(ContinuityTest).where(
        ContinuityTest.tenant_id == tenant_id,
        ContinuityTest.status == Status.DRAFT,
        ContinuityTest.scheduled_date >= now,
        ContinuityTest.scheduled_date <= deadline,
    )

    query = query.order_by(ContinuityTest.scheduled_date.asc())
    result = await session.execute(query)
    return result.scalars().all()


@router.get("/tests/overdue", response_model=List[ContinuityTest])
async def get_overdue_tests(
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """Get tests that are past their scheduled date but not completed."""
    query = select(ContinuityTest).where(
        ContinuityTest.tenant_id == tenant_id,
        ContinuityTest.status == Status.DRAFT,
        ContinuityTest.scheduled_date < datetime.utcnow(),
    )

    result = await session.execute(query)
    return result.scalars().all()


# =============================================================================
# BCMS DASHBOARD
# =============================================================================

@router.get("/dashboard", response_model=dict)
async def get_bcms_dashboard(
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """Get BCMS dashboard summary."""
    # Plans
    plan_query = select(ContinuityPlan).where(ContinuityPlan.tenant_id == tenant_id)
    plan_result = await session.execute(plan_query)
    plans = plan_result.scalars().all()

    # Tests
    test_query = select(ContinuityTest).where(ContinuityTest.tenant_id == tenant_id)
    test_result = await session.execute(test_query)
    tests = test_result.scalars().all()

    # Calculate stats
    active_plans = [p for p in plans if p.status == Status.ACTIVE]
    completed_tests = [t for t in tests if t.status == Status.CLOSED]
    passed_tests = [t for t in completed_tests if t.result == AuditResult.PASS]

    # Plans due for review
    now = datetime.utcnow()
    review_deadline = now + timedelta(days=30)
    plans_due_review = sum(
        1 for p in active_plans
        if p.review_date and p.review_date <= review_deadline
    )

    return {
        "plans": {
            "total": len(plans),
            "active": len(active_plans),
            "draft": sum(1 for p in plans if p.status == Status.DRAFT),
            "due_for_review": plans_due_review,
        },
        "tests": {
            "total": len(tests),
            "completed": len(completed_tests),
            "passed": len(passed_tests),
            "pass_rate": round(len(passed_tests) / len(completed_tests) * 100, 1) if completed_tests else 0,
            "scheduled": sum(1 for t in tests if t.status == Status.DRAFT),
        },
        "generated_at": now.isoformat(),
    }
