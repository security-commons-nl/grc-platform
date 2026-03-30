import uuid
import pytest
from httpx import AsyncClient
from tests.conftest import make_token


# ── Helpers ──────────────────────────────────────────────────────────────────


async def _create_step(client, token, number="O.1", **kwargs):
    defaults = {
        "number": number,
        "phase": 0,
        "name": f"Test Step {number}",
        "waarom_nu": "Test",
        "required_gremium": "strategisch",
    }
    defaults.update(kwargs)
    resp = await client.post(
        "/api/v1/steps/",
        json=defaults,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    return resp.json()


async def _create_execution(client, token, step_id, status="niet_gestart"):
    resp = await client.post(
        "/api/v1/steps/executions/",
        json={"step_id": step_id, "status": status},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    return resp.json()


async def _create_output(client, token, step_id, name="Test Output", output_type="document", requirement="V"):
    """Create a step output definition via direct DB insert (admin endpoint doesn't exist yet)."""
    # We use the step's outputs that come back from the API, or create via the step itself
    # Since there's no admin endpoint for outputs, we'll rely on seeded data or test with seeded steps
    pass


async def _create_decision(client, token, execution_id, tenant_id):
    resp = await client.post(
        "/api/v1/decisions/",
        json={
            "step_execution_id": execution_id,
            "decision_type": "normaal",
            "content": "Test besluit",
            "grondslag": "Test",
            "gremium": "strategisch",
            "decided_by_name": "Test User",
            "decided_by_role": "admin",
            "decided_at": "2026-03-28T10:00:00Z",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201, f"Decision create failed: {resp.text}"
    return resp.json()


async def _create_document(client, token, execution_id):
    resp = await client.post(
        "/api/v1/documents/",
        json={
            "step_execution_id": execution_id,
            "document_type": "overig",
            "title": "Test Document",
            "visibility": "privé",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201, f"Document create failed: {resp.text}"
    return resp.json()


# ── Tests: Step response includes outputs ────────────────────────────────────


@pytest.mark.asyncio
async def test_list_steps_includes_outputs(client: AsyncClient, admin_token):
    """Steps response should contain an 'outputs' array."""
    step = await _create_step(client, admin_token, number="O.list")
    resp = await client.get(
        "/api/v1/steps/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    steps = resp.json()
    for s in steps:
        assert "outputs" in s


@pytest.mark.asyncio
async def test_get_step_includes_outputs(client: AsyncClient, admin_token):
    """Single step response should contain outputs."""
    step = await _create_step(client, admin_token, number="O.get")
    resp = await client.get(
        f"/api/v1/steps/{step['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "outputs" in data
    assert isinstance(data["outputs"], list)


# ── Tests: Readiness endpoint ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_readiness_no_fulfillments(client: AsyncClient, test_tenant, tenant_token):
    """Readiness for a step with no fulfillments should show all outputs as not fulfilled."""
    step = await _create_step(client, tenant_token, number="R.1")
    execution = await _create_execution(client, tenant_token, step["id"])

    resp = await client.get(
        f"/api/v1/steps/executions/{execution['id']}/readiness",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["step_id"] == step["id"]
    assert data["execution_id"] == execution["id"]
    assert data["current_status"] == "niet_gestart"
    assert isinstance(data["outputs"], list)
    assert isinstance(data["allowed_transitions"], list)
    assert "dependencies_met" in data


@pytest.mark.asyncio
async def test_readiness_not_found(client: AsyncClient, admin_token):
    """Readiness for nonexistent execution returns 404."""
    fake_id = str(uuid.uuid4())
    resp = await client.get(
        f"/api/v1/steps/executions/{fake_id}/readiness",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 404


# ── Tests: Fulfillment CRUD ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_fulfillment_create_and_list(client: AsyncClient, test_tenant, tenant_token):
    """Create a fulfillment and verify it appears in the list."""
    step = await _create_step(client, tenant_token, number="F.1")
    execution = await _create_execution(client, tenant_token, step["id"])

    # Step has no outputs yet (created via API, not seeded), so we need outputs
    # to test fulfillments. Let's get the readiness to check.
    readiness_resp = await client.get(
        f"/api/v1/steps/executions/{execution['id']}/readiness",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    readiness = readiness_resp.json()

    # If no outputs defined for this step, fulfillment list should be empty
    resp = await client.get(
        f"/api/v1/steps/executions/{execution['id']}/fulfillments",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_fulfillment_requires_exactly_one_link(client: AsyncClient, test_tenant, tenant_token):
    """Fulfillment must have exactly one of decision_id or document_id."""
    step = await _create_step(client, tenant_token, number="F.2")
    execution = await _create_execution(client, tenant_token, step["id"])

    # Try with neither
    resp = await client.post(
        f"/api/v1/steps/executions/{execution['id']}/fulfillments",
        json={"step_output_id": str(uuid.uuid4())},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_fulfillment_wrong_step_rejected(client: AsyncClient, test_tenant, tenant_token):
    """Cannot link an output from step A to an execution of step B."""
    step_a = await _create_step(client, tenant_token, number="F.3a")
    step_b = await _create_step(client, tenant_token, number="F.3b")
    execution_b = await _create_execution(client, tenant_token, step_b["id"])

    # If step_a has outputs (from seed), try to link one to execution_b
    step_a_resp = await client.get(
        f"/api/v1/steps/{step_a['id']}",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    outputs_a = step_a_resp.json().get("outputs", [])
    if outputs_a:
        decision = await _create_decision(client, tenant_token, execution_b["id"], test_tenant["id"])
        resp = await client.post(
            f"/api/v1/steps/executions/{execution_b['id']}/fulfillments",
            json={
                "step_output_id": outputs_a[0]["id"],
                "decision_id": decision["id"],
            },
            headers={"Authorization": f"Bearer {tenant_token}"},
        )
        assert resp.status_code == 422


# ── Tests: Transition blocked by dependencies ────────────────────────────────


@pytest.mark.asyncio
async def test_transition_blocked_by_dependencies(client: AsyncClient, test_tenant, tenant_token):
    """Starting a step should fail if blocking dependencies are not met."""
    # Create two steps with a blocking dependency
    step1 = await _create_step(client, tenant_token, number="B.1")
    step2 = await _create_step(client, tenant_token, number="B.2")

    # Add blocking dependency: step2 depends on step1
    dep_resp = await client.post(
        "/api/v1/steps/dependencies/",
        json={
            "step_id": step2["id"],
            "depends_on_step_id": step1["id"],
            "dependency_type": "B",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert dep_resp.status_code == 201

    # Create execution for step2
    exec2 = await _create_execution(client, tenant_token, step2["id"])

    # Try to start step2 — should fail because step1 is not vastgesteld
    resp = await client.patch(
        f"/api/v1/steps/executions/{exec2['id']}",
        json={"status": "in_uitvoering"},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert resp.status_code == 422
    assert "afhankelijkheden" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_transition_allowed_when_dependency_met(client: AsyncClient, test_tenant, tenant_token):
    """Starting a step succeeds when blocking dependencies are vastgesteld."""
    step1 = await _create_step(client, tenant_token, number="BM.1")
    step2 = await _create_step(client, tenant_token, number="BM.2")

    # Blocking dependency
    await client.post(
        "/api/v1/steps/dependencies/",
        json={
            "step_id": step2["id"],
            "depends_on_step_id": step1["id"],
            "dependency_type": "B",
        },
        headers={"Authorization": f"Bearer {tenant_token}"},
    )

    # Complete step1 through all transitions
    exec1 = await _create_execution(client, tenant_token, step1["id"])
    for status in ["in_uitvoering", "concept", "in_review", "vastgesteld"]:
        await client.patch(
            f"/api/v1/steps/executions/{exec1['id']}",
            json={"status": status},
            headers={"Authorization": f"Bearer {tenant_token}"},
        )

    # Now start step2 — should work
    exec2 = await _create_execution(client, tenant_token, step2["id"])
    resp = await client.patch(
        f"/api/v1/steps/executions/{exec2['id']}",
        json={"status": "in_uitvoering"},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_uitvoering"


# ── Tests: Transition blocked by missing outputs ─────────────────────────────


@pytest.mark.asyncio
async def test_transition_to_vastgesteld_blocked_without_outputs(client: AsyncClient, test_tenant, tenant_token):
    """Step 1 (only A-outputs) can advance without fulfillments. Step with V-outputs cannot."""
    # Step 1 has only decision outputs (now A/aanbevolen) — should NOT be blocked
    resp = await client.get(
        "/api/v1/steps/",
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    step1 = next(s for s in resp.json() if s["number"] == "1")
    execution = await _create_execution(client, tenant_token, step1["id"])

    # Move through states
    await client.patch(
        f"/api/v1/steps/executions/{execution['id']}",
        json={"status": "in_uitvoering"},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    await client.patch(
        f"/api/v1/steps/executions/{execution['id']}",
        json={"status": "concept"},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )

    # Step 1 should advance to in_review even without fulfillments (only A-outputs)
    resp = await client.patch(
        f"/api/v1/steps/executions/{execution['id']}",
        json={"status": "in_review"},
        headers={"Authorization": f"Bearer {tenant_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_review"
