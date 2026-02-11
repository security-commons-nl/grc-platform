"""
Workflow Management Endpoints
Generic workflow engine for policies, risks, exceptions, incidents, etc.
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.db import get_session
from app.core.crud import TenantCRUDBase, CRUDBase
from app.core.rbac import get_tenant_id, require_editor
from app.models.core_models import (
    WorkflowDefinition,
    WorkflowState,
    WorkflowTransition,
    WorkflowInstance,
    WorkflowStepHistory,
    WorkflowStatus,
    User,
    AuditAction,
)
from app.services.audit_service import record_audit

router = APIRouter()
crud_definition = TenantCRUDBase(WorkflowDefinition)
crud_state = CRUDBase(WorkflowState)
crud_transition = CRUDBase(WorkflowTransition)
crud_instance = TenantCRUDBase(WorkflowInstance)
crud_history = CRUDBase(WorkflowStepHistory)


# =============================================================================
# WORKFLOW DEFINITIONS
# =============================================================================

@router.get("/definitions/", response_model=List[WorkflowDefinition])
async def list_workflow_definitions(
    skip: int = 0,
    limit: int = 100,
    tenant_id: int = Depends(get_tenant_id),
    entity_type: Optional[str] = Query(None, description="Filter by applicable entity type"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    session: AsyncSession = Depends(get_session),
):
    """List workflow definitions with optional filters."""
    filters = {"is_active": is_active}

    definitions = await crud_definition.get_multi(session, tenant_id, skip=skip, limit=limit, filters=filters)

    # Filter by entity type if specified (stored as JSON array)
    if entity_type:
        import json
        definitions = [
            d for d in definitions
            if entity_type in json.loads(d.applicable_entity_types or "[]")
        ]

    return definitions


@router.post("/definitions/", response_model=WorkflowDefinition)
async def create_workflow_definition(
    definition: WorkflowDefinition,
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """Create a new workflow definition."""
    return await crud_definition.create(session, obj_in=definition, tenant_id=tenant_id)


@router.get("/definitions/{definition_id}", response_model=WorkflowDefinition)
async def get_workflow_definition(
    definition_id: int,
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """Get a workflow definition by ID with its states and transitions."""
    definition = await crud_definition.get_or_404(session, definition_id, tenant_id)

    # Load states and transitions
    states_result = await session.execute(
        select(WorkflowState)
        .where(WorkflowState.workflow_id == definition_id)
        .order_by(WorkflowState.sequence)
    )
    definition.states = states_result.scalars().all()

    transitions_result = await session.execute(
        select(WorkflowTransition)
        .where(WorkflowTransition.workflow_id == definition_id)
    )
    definition.transitions = transitions_result.scalars().all()

    return definition


@router.patch("/definitions/{definition_id}", response_model=WorkflowDefinition)
async def update_workflow_definition(
    definition_id: int,
    definition_update: dict,
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """Update a workflow definition."""
    db_definition = await crud_definition.get_or_404(session, definition_id, tenant_id)
    definition_update["updated_at"] = datetime.utcnow()
    return await crud_definition.update(session, db_obj=db_definition, obj_in=definition_update, tenant_id=tenant_id)


@router.delete("/definitions/{definition_id}")
async def delete_workflow_definition(
    definition_id: int,
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """Delete a workflow definition (soft delete by setting is_active=False)."""
    db_definition = await crud_definition.get_or_404(session, definition_id, tenant_id)

    # Check if there are active instances
    active_count = await crud_instance.count(
        session,
        tenant_id,
        filters={"workflow_id": definition_id, "status": WorkflowStatus.IN_PROGRESS}
    )
    if active_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete workflow with {active_count} active instances"
        )

    # Soft delete
    return await crud_definition.update(
        session,
        db_obj=db_definition,
        obj_in={"is_active": False, "updated_at": datetime.utcnow()},
        tenant_id=tenant_id,
    )


# =============================================================================
# WORKFLOW STATES
# =============================================================================

@router.get("/definitions/{definition_id}/states/", response_model=List[WorkflowState])
async def list_workflow_states(
    definition_id: int,
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """List all states in a workflow definition."""
    await crud_definition.get_or_404(session, definition_id, tenant_id)

    result = await session.execute(
        select(WorkflowState)
        .where(WorkflowState.workflow_id == definition_id)
        .order_by(WorkflowState.sequence)
    )
    return result.scalars().all()


@router.post("/definitions/{definition_id}/states/", response_model=WorkflowState)
async def create_workflow_state(
    definition_id: int,
    state: WorkflowState,
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """Add a state to a workflow definition."""
    await crud_definition.get_or_404(session, definition_id, tenant_id)
    state.workflow_id = definition_id
    return await crud_state.create(session, obj_in=state)


@router.patch("/states/{state_id}", response_model=WorkflowState)
async def update_workflow_state(
    state_id: int,
    state_update: dict,
    session: AsyncSession = Depends(get_session),
):
    """Update a workflow state."""
    db_state = await crud_state.get_or_404(session, state_id)
    return await crud_state.update(session, db_obj=db_state, obj_in=state_update)


@router.delete("/states/{state_id}")
async def delete_workflow_state(
    state_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Delete a workflow state."""
    deleted = await crud_state.delete(session, id=state_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="State not found")
    return {"message": "State deleted"}


# =============================================================================
# WORKFLOW TRANSITIONS
# =============================================================================

@router.get("/definitions/{definition_id}/transitions/", response_model=List[WorkflowTransition])
async def list_workflow_transitions(
    definition_id: int,
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """List all transitions in a workflow definition."""
    await crud_definition.get_or_404(session, definition_id, tenant_id)

    result = await session.execute(
        select(WorkflowTransition)
        .where(WorkflowTransition.workflow_id == definition_id)
    )
    return result.scalars().all()


@router.post("/definitions/{definition_id}/transitions/", response_model=WorkflowTransition)
async def create_workflow_transition(
    definition_id: int,
    transition: WorkflowTransition,
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """Add a transition to a workflow definition."""
    await crud_definition.get_or_404(session, definition_id, tenant_id)

    # Verify states exist
    await crud_state.get_or_404(session, transition.from_state_id)
    await crud_state.get_or_404(session, transition.to_state_id)

    transition.workflow_id = definition_id
    return await crud_transition.create(session, obj_in=transition)


@router.patch("/transitions/{transition_id}", response_model=WorkflowTransition)
async def update_workflow_transition(
    transition_id: int,
    transition_update: dict,
    session: AsyncSession = Depends(get_session),
):
    """Update a workflow transition."""
    db_transition = await crud_transition.get_or_404(session, transition_id)
    return await crud_transition.update(session, db_obj=db_transition, obj_in=transition_update)


@router.delete("/transitions/{transition_id}")
async def delete_workflow_transition(
    transition_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Delete a workflow transition."""
    deleted = await crud_transition.delete(session, id=transition_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Transition not found")
    return {"message": "Transition deleted"}


# =============================================================================
# WORKFLOW INSTANCES
# =============================================================================

@router.get("/instances/", response_model=List[WorkflowInstance])
async def list_workflow_instances(
    skip: int = 0,
    limit: int = 100,
    tenant_id: int = Depends(get_tenant_id),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[int] = Query(None),
    status: Optional[WorkflowStatus] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    """List workflow instances with optional filters."""
    filters = {}
    if entity_type:
        filters["entity_type"] = entity_type
    if entity_id:
        filters["entity_id"] = entity_id
    if status:
        filters["status"] = status

    return await crud_instance.get_multi(session, tenant_id, skip=skip, limit=limit, filters=filters)


@router.post("/instances/", response_model=WorkflowInstance)
async def create_workflow_instance(
    instance: WorkflowInstance,
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """
    Start a workflow for an entity.
    Automatically sets the initial state and creates first history entry.
    """
    # Validate workflow exists and get initial state
    definition = await crud_definition.get_or_404(session, instance.workflow_id, tenant_id)

    result = await session.execute(
        select(WorkflowState)
        .where(WorkflowState.workflow_id == instance.workflow_id)
        .where(WorkflowState.is_initial == True)
    )
    initial_state = result.scalars().first()

    if not initial_state:
        raise HTTPException(
            status_code=400,
            detail="Workflow has no initial state defined"
        )

    # Set initial state
    instance.current_state_id = initial_state.id
    instance.status = WorkflowStatus.IN_PROGRESS
    instance.entered_current_state_at = datetime.utcnow()

    # Calculate remaining steps
    all_states_result = await session.execute(
        select(WorkflowState)
        .where(WorkflowState.workflow_id == instance.workflow_id)
        .where(WorkflowState.is_final == False)
    )
    instance.total_steps_remaining = len(all_states_result.scalars().all())

    created_instance = await crud_instance.create(session, obj_in=instance, tenant_id=tenant_id)

    # Create initial history entry
    history = WorkflowStepHistory(
        workflow_instance_id=created_instance.id,
        state_id=initial_state.id,
        state_name=initial_state.name,
        step_number=1,
        entered_at=datetime.utcnow(),
    )
    session.add(history)
    await session.commit()

    return created_instance


@router.get("/instances/{instance_id}", response_model=WorkflowInstance)
async def get_workflow_instance(
    instance_id: int,
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """Get a workflow instance with its history."""
    instance = await crud_instance.get_or_404(session, instance_id, tenant_id)

    # Load history
    history_result = await session.execute(
        select(WorkflowStepHistory)
        .where(WorkflowStepHistory.workflow_instance_id == instance_id)
        .order_by(WorkflowStepHistory.step_number)
    )
    instance.history = history_result.scalars().all()

    return instance


@router.get("/instances/{instance_id}/available-transitions", response_model=List[WorkflowTransition])
async def get_available_transitions(
    instance_id: int,
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """Get available transitions from the current state."""
    instance = await crud_instance.get_or_404(session, instance_id, tenant_id)

    result = await session.execute(
        select(WorkflowTransition)
        .where(WorkflowTransition.workflow_id == instance.workflow_id)
        .where(WorkflowTransition.from_state_id == instance.current_state_id)
    )
    return result.scalars().all()


@router.post("/instances/{instance_id}/execute-transition/{transition_id}", response_model=WorkflowInstance)
async def execute_transition(
    instance_id: int,
    transition_id: int,
    comment: Optional[str] = Query(None, description="Comment for this transition"),
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_editor),
):
    """
    Execute a transition to move the workflow to the next state.
    """
    instance = await crud_instance.get_or_404(session, instance_id, tenant_id)
    transition = await crud_transition.get_or_404(session, transition_id)

    # Validate transition is valid from current state
    if transition.from_state_id != instance.current_state_id:
        raise HTTPException(
            status_code=400,
            detail="Transition not valid from current state"
        )

    if transition.workflow_id != instance.workflow_id:
        raise HTTPException(
            status_code=400,
            detail="Transition does not belong to this workflow"
        )

    # Check if comment is required
    if transition.requires_comment and not comment:
        raise HTTPException(
            status_code=400,
            detail="Comment is required for this transition"
        )

    # Get target state
    target_state = await crud_state.get_or_404(session, transition.to_state_id)

    # Close current history entry
    history_result = await session.execute(
        select(WorkflowStepHistory)
        .where(WorkflowStepHistory.workflow_instance_id == instance_id)
        .where(WorkflowStepHistory.exited_at == None)
        .order_by(WorkflowStepHistory.step_number.desc())
    )
    current_history = history_result.scalars().first()

    if current_history:
        current_history.exited_at = datetime.utcnow()
        current_history.transition_id = transition_id
        current_history.transition_name = transition.name
        current_history.transitioned_by_id = current_user.id
        current_history.comment = comment

        # Calculate duration
        if current_history.entered_at:
            duration = (current_history.exited_at - current_history.entered_at).total_seconds() / 3600
            current_history.duration_hours = round(duration, 2)

        session.add(current_history)

    # Update instance
    now = datetime.utcnow()
    instance.current_state_id = target_state.id
    instance.entered_current_state_at = now
    instance.total_steps_completed += 1
    instance.total_steps_remaining = max(0, instance.total_steps_remaining - 1)
    instance.updated_at = now

    # Check if final state
    if target_state.is_final:
        instance.status = WorkflowStatus.COMPLETED
        instance.completed_at = now
    elif target_state.is_rejection:
        instance.status = WorkflowStatus.REJECTED

    # Handle approval status
    if transition.requires_approval:
        instance.status = WorkflowStatus.WAITING_APPROVAL
        instance.current_approver_id = None  # Will be set when assigned

    session.add(instance)

    # Create new history entry
    new_history = WorkflowStepHistory(
        workflow_instance_id=instance_id,
        state_id=target_state.id,
        state_name=target_state.name,
        step_number=(current_history.step_number + 1) if current_history else 1,
        entered_at=now,
    )
    session.add(new_history)

    await session.commit()
    await session.refresh(instance)

    await record_audit(
        session, tenant_id=tenant_id,
        entity_type="WorkflowInstance", entity_id=instance_id,
        action=AuditAction.STATUS_CHANGE, changed_by_id=current_user.id,
        field_name="current_state_id",
        old_value=str(transition.from_state_id),
        new_value=str(target_state.id),
        reason=comment,
    )

    return instance


@router.post("/instances/{instance_id}/cancel", response_model=WorkflowInstance)
async def cancel_workflow_instance(
    instance_id: int,
    reason: Optional[str] = Query(None, description="Cancellation reason"),
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_editor),
):
    """Cancel a workflow instance."""
    instance = await crud_instance.get_or_404(session, instance_id, tenant_id)

    if instance.status in [WorkflowStatus.COMPLETED, WorkflowStatus.CANCELLED]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel workflow in {instance.status.value} status"
        )

    old_status = instance.status.value
    instance.status = WorkflowStatus.CANCELLED
    instance.completed_at = datetime.utcnow()
    instance.updated_at = datetime.utcnow()

    session.add(instance)
    await session.commit()
    await session.refresh(instance)

    await record_audit(
        session, tenant_id=tenant_id,
        entity_type="WorkflowInstance", entity_id=instance_id,
        action=AuditAction.STATUS_CHANGE, changed_by_id=current_user.id,
        field_name="status", old_value=old_status, new_value="CANCELLED",
        reason=reason,
    )

    return instance


# =============================================================================
# WORKFLOW HISTORY
# =============================================================================

@router.get("/instances/{instance_id}/history", response_model=List[WorkflowStepHistory])
async def get_workflow_history(
    instance_id: int,
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """Get complete history for a workflow instance."""
    await crud_instance.get_or_404(session, instance_id, tenant_id)

    result = await session.execute(
        select(WorkflowStepHistory)
        .where(WorkflowStepHistory.workflow_instance_id == instance_id)
        .order_by(WorkflowStepHistory.step_number)
    )
    return result.scalars().all()


# =============================================================================
# HELPER ENDPOINTS
# =============================================================================

@router.get("/entity/{entity_type}/{entity_id}/instance", response_model=Optional[WorkflowInstance])
async def get_entity_workflow_instance(
    entity_type: str,
    entity_id: int,
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """Get the active workflow instance for a specific entity."""
    result = await session.execute(
        select(WorkflowInstance)
        .where(WorkflowInstance.tenant_id == tenant_id)
        .where(WorkflowInstance.entity_type == entity_type)
        .where(WorkflowInstance.entity_id == entity_id)
        .where(WorkflowInstance.status.in_([
            WorkflowStatus.IN_PROGRESS,
            WorkflowStatus.WAITING_APPROVAL
        ]))
    )
    return result.scalars().first()


@router.get("/stats/", response_model=dict)
async def get_workflow_stats(
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
):
    """Get workflow statistics."""
    total = await crud_instance.count(session, tenant_id)

    in_progress = await crud_instance.count(session, tenant_id, filters={"status": WorkflowStatus.IN_PROGRESS})
    completed = await crud_instance.count(session, tenant_id, filters={"status": WorkflowStatus.COMPLETED})
    waiting = await crud_instance.count(session, tenant_id, filters={"status": WorkflowStatus.WAITING_APPROVAL})

    return {
        "total": total,
        "in_progress": in_progress,
        "completed": completed,
        "waiting_approval": waiting,
        "completion_rate": round(completed / total * 100, 1) if total > 0 else 0,
    }
