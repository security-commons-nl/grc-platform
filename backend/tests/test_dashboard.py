import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.core_models import (
    Tenant, User, CorrectiveAction, ReviewSchedule,
    WorkflowInstance, WorkflowDefinition, WorkflowState, WorkflowStatus,
    FindingSeverity
)
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_get_my_tasks(client: AsyncClient, db_session: AsyncSession):
    # 1. Setup Tenant and User
    tenant = Tenant(name="Test Tenant", slug="test-tenant")
    db_session.add(tenant)
    await db_session.commit()
    await db_session.refresh(tenant)

    user = User(username="testuser", email="test@example.com", is_active=True)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # 2. Corrective Action (Assigned, Open)
    action = CorrectiveAction(
        tenant_id=tenant.id,
        title="Fix Security Gap",
        assigned_to_id=user.id,
        completed=False,
        priority=FindingSeverity.HIGH,
        due_date=datetime.utcnow() + timedelta(days=2)
    )
    db_session.add(action)

    # 3. Review Schedule (Responsible, Due Soon)
    review = ReviewSchedule(
        tenant_id=tenant.id,
        entity_type="Policy",
        entity_id=1,
        title="Annual Policy Review",
        responsible_id=user.id,
        next_review=datetime.utcnow() + timedelta(days=5),
        frequency_months=12
    )
    db_session.add(review)

    # 4. Workflow Instance (Assigned)
    # Need definition and state first
    wf_def = WorkflowDefinition(name="Test Workflow", applicable_entity_types='["Risk"]', tenant_id=tenant.id)
    db_session.add(wf_def)
    await db_session.commit()
    await db_session.refresh(wf_def)

    wf_state = WorkflowState(workflow_id=wf_def.id, name="Review", sequence=1)
    db_session.add(wf_state)
    await db_session.commit()
    await db_session.refresh(wf_state)

    wf_instance = WorkflowInstance(
        tenant_id=tenant.id,
        workflow_id=wf_def.id,
        entity_type="Risk",
        entity_id=1,
        current_state_id=wf_state.id,
        status=WorkflowStatus.IN_PROGRESS,
        current_assignee_id=user.id,
        entered_current_state_at=datetime.utcnow()
    )
    db_session.add(wf_instance)

    await db_session.commit()

    # 5. Call Endpoint
    response = await client.get(f"/api/v1/dashboard/my-tasks?user_id={user.id}&tenant_id={tenant.id}")

    # 6. Verify
    assert response.status_code == 200
    data = response.json()

    assert data["summary"]["total"] == 3
    # Action (2 days) + Review (5 days) = 2 due soon
    assert data["summary"]["due_soon"] == 2

    tasks = data["tasks"]
    assert len(tasks) == 3

    # Check types
    types = [t["type"] for t in tasks]
    assert "Corrective Action" in types
    assert "Review" in types
    assert "Workflow Task" in types
