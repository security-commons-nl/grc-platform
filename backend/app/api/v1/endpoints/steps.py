from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.auth import CurrentUser, get_current_user, require_role
from app.core.db import get_db
from app.models.core_models import IMSStep, IMSStepDependency, IMSStepExecution
from app.schemas.steps import (
    StepCreate, StepUpdate, StepResponse,
    StepDependencyCreate, StepDependencyResponse,
    StepExecutionCreate, StepExecutionUpdate, StepExecutionResponse,
)

router = APIRouter()

VALID_TRANSITIONS = {
    "niet_gestart": ["in_uitvoering"],
    "in_uitvoering": ["concept"],
    "concept": ["in_review"],
    "in_review": ["vastgesteld", "concept"],
    "vastgesteld": [],
}


# ── Steps (platform-wide) ──────────────────────────────────────────────────


@router.get("/", response_model=list[StepResponse])
async def list_steps(
    phase: int | None = None,
    domain: str | None = None,
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(IMSStep)
    if phase is not None:
        query = query.where(IMSStep.phase == phase)
    if domain:
        query = query.where(IMSStep.domain == domain)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{step_id}", response_model=StepResponse)
async def get_step(
    step_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(IMSStep).where(IMSStep.id == step_id))
    step = result.scalar_one_or_none()
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")
    return step


@router.post("/", response_model=StepResponse, status_code=201)
async def create_step(
    data: StepCreate,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    step = IMSStep(**data.model_dump())
    db.add(step)
    await db.flush()
    await db.refresh(step)
    return step


@router.patch("/{step_id}", response_model=StepResponse)
async def update_step(
    step_id: UUID,
    data: StepUpdate,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(IMSStep).where(IMSStep.id == step_id))
    step = result.scalar_one_or_none()
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(step, field, value)
    await db.flush()
    await db.refresh(step)
    return step


@router.delete("/{step_id}", status_code=204)
async def delete_step(
    step_id: UUID,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(IMSStep).where(IMSStep.id == step_id))
    step = result.scalar_one_or_none()
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")
    await db.delete(step)
    await db.flush()


# ── Step Dependencies ──────────────────────────────────────────────────────


@router.get("/dependencies/", response_model=list[StepDependencyResponse])
async def list_step_dependencies(
    step_id: UUID | None = None,
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(IMSStepDependency)
    if step_id:
        query = query.where(IMSStepDependency.step_id == step_id)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/dependencies/", response_model=StepDependencyResponse, status_code=201)
async def create_step_dependency(
    data: StepDependencyCreate,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    dep = IMSStepDependency(**data.model_dump())
    db.add(dep)
    await db.flush()
    await db.refresh(dep)
    return dep


@router.delete("/dependencies/{dep_id}", status_code=204)
async def delete_step_dependency(
    dep_id: UUID,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(IMSStepDependency).where(IMSStepDependency.id == dep_id))
    dep = result.scalar_one_or_none()
    if not dep:
        raise HTTPException(status_code=404, detail="StepDependency not found")
    await db.delete(dep)
    await db.flush()


# ── Step Executions ─────────────────────────────────────────────────────────


@router.get("/executions/", response_model=list[StepExecutionResponse])
async def list_step_executions(
    step_id: UUID | None = None,
    status_filter: str | None = Query(None, alias="status"),
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(IMSStepExecution).where(IMSStepExecution.tenant_id == current_user.tenant_id)
    if step_id:
        query = query.where(IMSStepExecution.step_id == step_id)
    if status_filter:
        query = query.where(IMSStepExecution.status == status_filter)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/executions/{execution_id}", response_model=StepExecutionResponse)
async def get_step_execution(
    execution_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(IMSStepExecution).where(IMSStepExecution.id == execution_id))
    execution = result.scalar_one_or_none()
    if not execution:
        raise HTTPException(status_code=404, detail="StepExecution not found")
    return execution


@router.post("/executions/", response_model=StepExecutionResponse, status_code=201)
async def create_step_execution(
    data: StepExecutionCreate,
    current_user: CurrentUser = Depends(require_role("tims_lid")),
    db: AsyncSession = Depends(get_db),
):
    execution = IMSStepExecution(tenant_id=current_user.tenant_id, **data.model_dump())
    db.add(execution)
    await db.flush()
    await db.refresh(execution)
    return execution


@router.patch("/executions/{execution_id}", response_model=StepExecutionResponse)
async def update_step_execution(
    execution_id: UUID,
    data: StepExecutionUpdate,
    current_user: CurrentUser = Depends(require_role("tims_lid")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(IMSStepExecution).where(IMSStepExecution.id == execution_id))
    execution = result.scalar_one_or_none()
    if not execution:
        raise HTTPException(status_code=404, detail="StepExecution not found")

    update_data = data.model_dump(exclude_unset=True)

    # Validate status transition
    if "status" in update_data:
        new_status = update_data["status"]
        current_status = execution.status
        allowed = VALID_TRANSITIONS.get(current_status, [])
        if new_status not in allowed:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid status transition: {current_status} -> {new_status}. "
                       f"Allowed: {allowed}",
            )
        # Set timestamps based on transition
        if new_status == "in_uitvoering" and not execution.started_at:
            execution.started_at = datetime.utcnow()
        if new_status == "vastgesteld":
            execution.completed_at = datetime.utcnow()

    for field, value in update_data.items():
        setattr(execution, field, value)

    await db.flush()
    await db.refresh(execution)
    return execution


@router.delete("/executions/{execution_id}", status_code=204)
async def delete_step_execution(
    execution_id: UUID,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(IMSStepExecution).where(IMSStepExecution.id == execution_id))
    execution = result.scalar_one_or_none()
    if not execution:
        raise HTTPException(status_code=404, detail="StepExecution not found")
    await db.delete(execution)
    await db.flush()
