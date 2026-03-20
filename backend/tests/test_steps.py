import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_step(client: AsyncClient):
    response = await client.post(
        "/api/v1/steps/",
        json={
            "number": "1.1",
            "phase": 1,
            "name": "Scope bepalen",
            "waarom_nu": "Basis voor verdere inrichting",
            "required_gremium": "sims",
            "is_optional": False,
            "domain": "ISMS",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["number"] == "1.1"
    assert data["phase"] == 1
    assert data["name"] == "Scope bepalen"


@pytest.mark.asyncio
async def test_list_steps(client: AsyncClient):
    # Create a step first
    await client.post(
        "/api/v1/steps/",
        json={
            "number": "2.1",
            "phase": 2,
            "name": "Risico-inventarisatie",
            "waarom_nu": "Risico's in kaart brengen",
            "required_gremium": "tims",
        },
    )
    response = await client.get("/api/v1/steps/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_list_steps_filter_phase(client: AsyncClient):
    await client.post(
        "/api/v1/steps/",
        json={
            "number": "3.1",
            "phase": 3,
            "name": "Implementatie",
            "waarom_nu": "Maatregelen invoeren",
            "required_gremium": "lijnmanagement",
        },
    )
    response = await client.get("/api/v1/steps/", params={"phase": 3})
    assert response.status_code == 200
    for step in response.json():
        assert step["phase"] == 3


@pytest.mark.asyncio
async def test_create_step_execution(client: AsyncClient, test_tenant):
    # Create step first
    step_resp = await client.post(
        "/api/v1/steps/",
        json={
            "number": "E.1",
            "phase": 1,
            "name": "Exec Test Step",
            "waarom_nu": "Test",
            "required_gremium": "sims",
        },
    )
    step = step_resp.json()

    response = await client.post(
        "/api/v1/steps/executions/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "step_id": step["id"],
            "status": "niet_gestart",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "niet_gestart"
    assert data["tenant_id"] == test_tenant["id"]


@pytest.mark.asyncio
async def test_step_execution_valid_transition(client: AsyncClient, test_tenant):
    step_resp = await client.post(
        "/api/v1/steps/",
        json={
            "number": "T.1",
            "phase": 1,
            "name": "Transition Test",
            "waarom_nu": "Test",
            "required_gremium": "sims",
        },
    )
    step = step_resp.json()

    exec_resp = await client.post(
        "/api/v1/steps/executions/",
        params={"tenant_id": test_tenant["id"]},
        json={"step_id": step["id"], "status": "niet_gestart"},
    )
    exec_id = exec_resp.json()["id"]

    # niet_gestart -> in_uitvoering (valid)
    response = await client.patch(
        f"/api/v1/steps/executions/{exec_id}",
        json={"status": "in_uitvoering"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "in_uitvoering"
    assert response.json()["started_at"] is not None

    # in_uitvoering -> concept (valid)
    response = await client.patch(
        f"/api/v1/steps/executions/{exec_id}",
        json={"status": "concept"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "concept"


@pytest.mark.asyncio
async def test_step_execution_invalid_transition(client: AsyncClient, test_tenant):
    step_resp = await client.post(
        "/api/v1/steps/",
        json={
            "number": "T.2",
            "phase": 1,
            "name": "Invalid Transition Test",
            "waarom_nu": "Test",
            "required_gremium": "sims",
        },
    )
    step = step_resp.json()

    exec_resp = await client.post(
        "/api/v1/steps/executions/",
        params={"tenant_id": test_tenant["id"]},
        json={"step_id": step["id"], "status": "niet_gestart"},
    )
    exec_id = exec_resp.json()["id"]

    # niet_gestart -> vastgesteld (invalid — skipping steps)
    response = await client.patch(
        f"/api/v1/steps/executions/{exec_id}",
        json={"status": "vastgesteld"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_step_execution_skip(client: AsyncClient, test_tenant):
    step_resp = await client.post(
        "/api/v1/steps/",
        json={
            "number": "S.1",
            "phase": 1,
            "name": "Skip Test",
            "waarom_nu": "Test",
            "required_gremium": "sims",
            "is_optional": True,
        },
    )
    step = step_resp.json()

    exec_resp = await client.post(
        "/api/v1/steps/executions/",
        params={"tenant_id": test_tenant["id"]},
        json={
            "step_id": step["id"],
            "status": "niet_gestart",
            "skipped": True,
            "skip_reason": "Niet van toepassing",
            "skip_logged_by": "Test User",
        },
    )
    assert exec_resp.status_code == 201
    data = exec_resp.json()
    assert data["skipped"] is True
    assert data["skip_reason"] == "Niet van toepassing"


@pytest.mark.asyncio
async def test_create_step_dependency(client: AsyncClient):
    step1_resp = await client.post(
        "/api/v1/steps/",
        json={
            "number": "D.1",
            "phase": 1,
            "name": "Dep Step 1",
            "waarom_nu": "Test",
            "required_gremium": "sims",
        },
    )
    step2_resp = await client.post(
        "/api/v1/steps/",
        json={
            "number": "D.2",
            "phase": 2,
            "name": "Dep Step 2",
            "waarom_nu": "Test",
            "required_gremium": "sims",
        },
    )
    step1 = step1_resp.json()
    step2 = step2_resp.json()

    response = await client.post(
        "/api/v1/steps/dependencies/",
        json={
            "step_id": step2["id"],
            "depends_on_step_id": step1["id"],
            "dependency_type": "B",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["dependency_type"] == "B"
