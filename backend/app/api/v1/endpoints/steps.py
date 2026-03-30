from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.core.auth import CurrentUser, get_current_user, require_role
from app.core.db import get_db
from app.models.core_models import (
    IMSStep,
    IMSStepDependency,
    IMSStepExecution,
    IMSStepOutput,
    IMSStepOutputFulfillment,
)
from app.schemas.steps import (
    StepCreate, StepUpdate, StepResponse,
    StepDependencyCreate, StepDependencyResponse,
    StepExecutionCreate, StepExecutionUpdate, StepExecutionResponse,
    StepOutputResponse,
    StepOutputFulfillmentCreate, StepOutputFulfillmentResponse,
    OutputReadinessItem, StepReadiness,
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
    query = select(IMSStep).options(selectinload(IMSStep.outputs))
    if phase is not None:
        query = query.where(IMSStep.phase == phase)
    if domain:
        query = query.where(IMSStep.domain == domain)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().unique().all()


@router.get("/{step_id}", response_model=StepResponse)
async def get_step(
    step_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(IMSStep)
        .options(selectinload(IMSStep.outputs))
        .where(IMSStep.id == step_id)
    )
    step = result.scalar_one_or_none()
    if not step:
        raise HTTPException(status_code=404, detail="Stap niet gevonden")
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
        raise HTTPException(status_code=404, detail="Stap niet gevonden")
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
        raise HTTPException(status_code=404, detail="Stap niet gevonden")
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
        raise HTTPException(status_code=404, detail="Stapafhankelijkheid niet gevonden")
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
        raise HTTPException(status_code=404, detail="Stapuitvoering niet gevonden")
    return execution


@router.post("/executions/", response_model=StepExecutionResponse, status_code=201)
async def create_step_execution(
    data: StepExecutionCreate,
    current_user: CurrentUser = Depends(require_role("tactisch_lid")),
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
    current_user: CurrentUser = Depends(require_role("tactisch_lid")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(IMSStepExecution).where(IMSStepExecution.id == execution_id))
    execution = result.scalar_one_or_none()
    if not execution:
        raise HTTPException(status_code=404, detail="Stapuitvoering niet gevonden")

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

        # Check blocking dependencies when starting a step
        if new_status == "in_uitvoering":
            await _check_blocking_dependencies(db, execution, current_user.tenant_id)

        # Check required outputs before advancing to in_review or vastgesteld
        if new_status in ("in_review", "vastgesteld"):
            await _check_required_outputs(db, execution, new_status)

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
        raise HTTPException(status_code=404, detail="Stapuitvoering niet gevonden")
    await db.delete(execution)
    await db.flush()


# ── Readiness ──────────────────────────────────────────────────────────────


@router.get("/executions/{execution_id}/readiness", response_model=StepReadiness)
async def get_step_readiness(
    execution_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Load execution
    result = await db.execute(
        select(IMSStepExecution).where(IMSStepExecution.id == execution_id)
    )
    execution = result.scalar_one_or_none()
    if not execution:
        raise HTTPException(status_code=404, detail="Stapuitvoering niet gevonden")

    # Load step with outputs
    result = await db.execute(
        select(IMSStep)
        .options(selectinload(IMSStep.outputs))
        .where(IMSStep.id == execution.step_id)
    )
    step = result.scalar_one()

    # Load fulfillments for this execution
    result = await db.execute(
        select(IMSStepOutputFulfillment).where(
            IMSStepOutputFulfillment.step_execution_id == execution_id
        )
    )
    fulfillments = result.scalars().all()
    fulfillment_by_output = {f.step_output_id: f for f in fulfillments}

    # Build output readiness items
    output_items = []
    recommended_unfulfilled = []
    required_total = 0
    required_fulfilled = 0
    for output in sorted(step.outputs, key=lambda o: o.sort_order):
        f = fulfillment_by_output.get(output.id)
        fulfilled = f is not None
        item = OutputReadinessItem(output=output, fulfilled=fulfilled, fulfillment=f)

        if output.requirement == "V":
            required_total += 1
            if fulfilled:
                required_fulfilled += 1
        elif output.requirement == "A" and not fulfilled:
            recommended_unfulfilled.append(item)

        output_items.append(item)

    all_required_met = required_fulfilled == required_total

    # Check blocking dependencies
    blocking_deps = await _get_blocking_dependency_ids(
        db, execution.step_id, current_user.tenant_id
    )
    dependencies_met = len(blocking_deps) == 0

    # Compute allowed transitions (only V-outputs block, A-outputs warn but don't block)
    base_transitions = VALID_TRANSITIONS.get(execution.status, [])
    allowed_transitions = []
    for t in base_transitions:
        if t == "in_uitvoering" and not dependencies_met:
            continue
        if t in ("in_review", "vastgesteld") and not all_required_met:
            continue
        allowed_transitions.append(t)

    can_advance = len(allowed_transitions) > 0

    return StepReadiness(
        step_id=step.id,
        execution_id=execution.id,
        current_status=execution.status,
        outputs=output_items,
        required_fulfilled=required_fulfilled,
        required_total=required_total,
        all_required_met=all_required_met,
        recommended_unfulfilled=recommended_unfulfilled,
        dependencies_met=dependencies_met,
        blocking_dependencies=blocking_deps,
        allowed_transitions=allowed_transitions,
        can_advance=can_advance,
    )


# ── Fulfillments ───────────────────────────────────────────────────────────


@router.get(
    "/executions/{execution_id}/fulfillments",
    response_model=list[StepOutputFulfillmentResponse],
)
async def list_fulfillments(
    execution_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(IMSStepOutputFulfillment).where(
            IMSStepOutputFulfillment.step_execution_id == execution_id
        )
    )
    return result.scalars().all()


@router.post(
    "/executions/{execution_id}/fulfillments",
    response_model=StepOutputFulfillmentResponse,
    status_code=201,
)
async def create_fulfillment(
    execution_id: UUID,
    data: StepOutputFulfillmentCreate,
    current_user: CurrentUser = Depends(require_role("tactisch_lid")),
    db: AsyncSession = Depends(get_db),
):
    # Verify execution exists
    result = await db.execute(
        select(IMSStepExecution).where(IMSStepExecution.id == execution_id)
    )
    execution = result.scalar_one_or_none()
    if not execution:
        raise HTTPException(status_code=404, detail="Stapuitvoering niet gevonden")

    # Verify exactly one link is provided
    has_decision = data.decision_id is not None
    has_document = data.document_id is not None
    if has_decision == has_document:
        raise HTTPException(
            status_code=422,
            detail="Precies een van decision_id of document_id moet worden opgegeven",
        )

    # Verify the output belongs to this step
    result = await db.execute(
        select(IMSStepOutput).where(IMSStepOutput.id == data.step_output_id)
    )
    step_output = result.scalar_one_or_none()
    if not step_output:
        raise HTTPException(status_code=404, detail="Stap-output niet gevonden")
    if step_output.step_id != execution.step_id:
        raise HTTPException(
            status_code=422,
            detail="Output behoort niet bij deze stap",
        )

    # Check for duplicate
    result = await db.execute(
        select(IMSStepOutputFulfillment).where(
            IMSStepOutputFulfillment.step_output_id == data.step_output_id,
            IMSStepOutputFulfillment.step_execution_id == execution_id,
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail="Deze output is al ingevuld voor deze uitvoering",
        )

    fulfillment = IMSStepOutputFulfillment(
        tenant_id=current_user.tenant_id,
        step_execution_id=execution_id,
        **data.model_dump(),
    )
    db.add(fulfillment)
    await db.flush()
    await db.refresh(fulfillment)
    return fulfillment


@router.delete("/fulfillments/{fulfillment_id}", status_code=204)
async def delete_fulfillment(
    fulfillment_id: UUID,
    current_user: CurrentUser = Depends(require_role("tactisch_lid")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(IMSStepOutputFulfillment).where(
            IMSStepOutputFulfillment.id == fulfillment_id
        )
    )
    fulfillment = result.scalar_one_or_none()
    if not fulfillment:
        raise HTTPException(status_code=404, detail="Fulfillment niet gevonden")
    await db.delete(fulfillment)
    await db.flush()


# ── Internal helpers ───────────────────────────────────────────────────────


async def _get_blocking_dependency_ids(
    db: AsyncSession, step_id: UUID, tenant_id: UUID
) -> list[UUID]:
    """Return step IDs of unsatisfied blocking dependencies."""
    result = await db.execute(
        select(IMSStepDependency).where(
            IMSStepDependency.step_id == step_id,
            IMSStepDependency.dependency_type == "B",
        )
    )
    blocking_deps = result.scalars().all()

    unmet = []
    for dep in blocking_deps:
        result = await db.execute(
            select(IMSStepExecution).where(
                IMSStepExecution.step_id == dep.depends_on_step_id,
                IMSStepExecution.tenant_id == tenant_id,
            )
        )
        dep_exec = result.scalar_one_or_none()
        if not dep_exec or dep_exec.status != "vastgesteld":
            unmet.append(dep.depends_on_step_id)
    return unmet


async def _check_blocking_dependencies(
    db: AsyncSession, execution: IMSStepExecution, tenant_id: UUID
) -> None:
    """Raise 422 if blocking dependencies are not satisfied."""
    unmet = await _get_blocking_dependency_ids(db, execution.step_id, tenant_id)
    if unmet:
        raise HTTPException(
            status_code=422,
            detail="Blokkerende afhankelijkheden zijn niet voldaan",
        )


async def _check_required_outputs(
    db: AsyncSession, execution: IMSStepExecution, new_status: str
) -> None:
    """Raise 422 if required outputs are not fulfilled."""
    # Load step with outputs
    result = await db.execute(
        select(IMSStep)
        .options(selectinload(IMSStep.outputs))
        .where(IMSStep.id == execution.step_id)
    )
    step = result.scalar_one()

    required_outputs = [o for o in step.outputs if o.requirement == "V"]
    if not required_outputs:
        return

    # Load fulfillments
    result = await db.execute(
        select(IMSStepOutputFulfillment).where(
            IMSStepOutputFulfillment.step_execution_id == execution.id
        )
    )
    fulfilled_ids = {f.step_output_id for f in result.scalars().all()}

    missing = [o for o in required_outputs if o.id not in fulfilled_ids]
    if missing:
        missing_names = ", ".join(o.name for o in missing)
        action = "indienen voor review" if new_status == "in_review" else "vaststellen"
        raise HTTPException(
            status_code=422,
            detail=f"Kan niet {action}: verplichte outputs ontbreken: {missing_names}",
        )
