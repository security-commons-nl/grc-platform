"""Tests that verify reference data is correctly loaded and accessible via API."""
import pytest
from httpx import AsyncClient
from tests.conftest import make_token


@pytest.mark.asyncio
async def test_steps_are_seeded(client: AsyncClient):
    """After seed migration, GET /steps/ should return all 22 steps."""
    token = make_token(role="admin")
    response = await client.get(
        "/api/v1/steps/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    steps = response.json()
    assert len(steps) >= 24  # At least 24 seed steps (other tests may add more)

    # Check all seed step numbers are present
    numbers = {s["number"] for s in steps}
    expected = {"1", "2a", "2b", "3a", "3b", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22"}
    assert expected.issubset(numbers), f"Missing steps: {expected - numbers}"


@pytest.mark.asyncio
async def test_steps_have_correct_phases(client: AsyncClient):
    """Steps should be assigned to correct phases."""
    token = make_token(role="admin")
    response = await client.get(
        "/api/v1/steps/",
        headers={"Authorization": f"Bearer {token}"},
    )
    steps = {s["number"]: s for s in response.json()}

    # Fase 0: stap 1, 2a, 2b, 3a, 3b, 4, 5, 6 (8 stappen)
    for num in ["1", "2a", "2b", "3a", "3b", "4", "5", "6"]:
        assert steps[num]["phase"] == 0, f"Step {num} should be phase 0"

    # Fase 1: stap 7, 8, 9, 10, 11, 12 (6 stappen)
    for num in ["7", "8", "9", "10", "11", "12"]:
        assert steps[num]["phase"] == 1, f"Step {num} should be phase 1"

    # Fase 2: stap 13, 14, 15, 16, 17 (5 stappen)
    for num in ["13", "14", "15", "16", "17"]:
        assert steps[num]["phase"] == 2, f"Step {num} should be phase 2"

    # Fase 3: stap 18, 19, 20, 21, 22 (5 stappen)
    for num in ["18", "19", "20", "21", "22"]:
        assert steps[num]["phase"] == 3, f"Step {num} should be phase 3"


@pytest.mark.asyncio
async def test_fase3_steps_are_optional(client: AsyncClient):
    """Fase 3 steps should be marked as optional."""
    token = make_token(role="admin")
    response = await client.get(
        "/api/v1/steps/",
        headers={"Authorization": f"Bearer {token}"},
    )
    steps = {s["number"]: s for s in response.json()}

    for num in ["18", "19", "20", "21", "22"]:
        assert steps[num]["is_optional"] is True, f"Step {num} should be optional"

    for num in ["1", "6", "9", "13", "17"]:
        assert steps[num]["is_optional"] is False, f"Step {num} should not be optional"


@pytest.mark.asyncio
async def test_step_dependencies_exist(client: AsyncClient):
    """Dependencies should be loaded."""
    token = make_token(role="admin")
    response = await client.get(
        "/api/v1/steps/dependencies/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    deps = response.json()
    assert len(deps) >= 25  # We defined 26 dependencies


@pytest.mark.asyncio
async def test_standards_are_seeded(client: AsyncClient):
    """Base standards should be loaded."""
    token = make_token(role="admin")
    response = await client.get(
        "/api/v1/standards/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    standards = response.json()
    assert len(standards) >= 5  # At least 5 seed standards

    names = {s["name"] for s in standards}
    assert "BIO" in names
    assert "ISO 27001" in names
    assert "ISO 27701" in names
    assert "ISO 22301" in names
    assert "AVG" in names


@pytest.mark.asyncio
async def test_step_1_details(client: AsyncClient):
    """Step 1 should have correct content."""
    token = make_token(role="admin")
    response = await client.get(
        "/api/v1/steps/",
        headers={"Authorization": f"Bearer {token}"},
    )
    steps = {s["number"]: s for s in response.json()}
    step1 = steps["1"]

    assert step1["name"] == "Bestuurlijk commitment"
    assert step1["phase"] == 0
    assert step1["required_gremium"] == "sims"
    assert "mandaat" in step1["waarom_nu"].lower()
