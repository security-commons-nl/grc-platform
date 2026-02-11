"""
Tests for Policy Management API endpoints.
Tests the full workflow: Draft -> Review -> Approved -> Published -> Archived
"""
import pytest
from httpx import AsyncClient


class TestPolicyCRUD:
    """Test basic CRUD operations for policies."""

    @pytest.mark.asyncio
    async def test_create_policy(self, client: AsyncClient, sample_policy_data: dict):
        """Test creating a new policy."""
        response = await client.post("/api/v1/policies/", json=sample_policy_data)
        assert response.status_code == 200

        data = response.json()
        assert data["title"] == sample_policy_data["title"]
        assert data["content"] == sample_policy_data["content"]
        assert data["id"] is not None
        assert data["state"] == "Draft"  # Always starts as Draft
        assert data["version"] == 1

    @pytest.mark.asyncio
    async def test_list_policies(self, client: AsyncClient, sample_policy_data: dict):
        """Test listing policies."""
        await client.post("/api/v1/policies/", json=sample_policy_data)

        response = await client.get("/api/v1/policies/")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_get_policy(self, client: AsyncClient, sample_policy_data: dict):
        """Test getting a single policy."""
        create_response = await client.post("/api/v1/policies/", json=sample_policy_data)
        policy_id = create_response.json()["id"]

        response = await client.get(f"/api/v1/policies/{policy_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == policy_id

    @pytest.mark.asyncio
    async def test_update_draft_policy(self, client: AsyncClient, sample_policy_data: dict):
        """Test updating a draft policy."""
        create_response = await client.post("/api/v1/policies/", json=sample_policy_data)
        policy_id = create_response.json()["id"]

        update_data = {"title": "Updated Policy Title"}
        response = await client.patch(f"/api/v1/policies/{policy_id}", json=update_data)
        assert response.status_code == 200

        data = response.json()
        assert data["title"] == "Updated Policy Title"

    @pytest.mark.asyncio
    async def test_delete_draft_policy(self, client: AsyncClient, sample_policy_data: dict):
        """Test deleting a draft policy."""
        create_response = await client.post("/api/v1/policies/", json=sample_policy_data)
        policy_id = create_response.json()["id"]

        response = await client.delete(f"/api/v1/policies/{policy_id}")
        assert response.status_code == 200


class TestPolicyWorkflow:
    """Test the full policy workflow: Draft -> Review -> Approved -> Published."""

    @pytest.mark.asyncio
    async def test_full_workflow(self, client: AsyncClient, sample_policy_data: dict):
        """Test the complete policy lifecycle."""
        # 1. Create (Draft)
        create_response = await client.post("/api/v1/policies/", json=sample_policy_data)
        assert create_response.status_code == 200
        policy_id = create_response.json()["id"]
        assert create_response.json()["state"] == "Draft"

        # 2. Submit for review
        review_response = await client.post(f"/api/v1/policies/{policy_id}/submit-for-review")
        assert review_response.status_code == 200
        assert review_response.json()["state"] == "Review"

        # 3. Approve
        approve_response = await client.post(
            f"/api/v1/policies/{policy_id}/approve",

        )
        assert approve_response.status_code == 200
        assert approve_response.json()["state"] == "Approved"

        # 4. Publish
        publish_response = await client.post(f"/api/v1/policies/{policy_id}/publish")
        assert publish_response.status_code == 200
        assert publish_response.json()["state"] == "Published"

        # 5. Archive
        archive_response = await client.post(f"/api/v1/policies/{policy_id}/archive")
        assert archive_response.status_code == 200
        assert archive_response.json()["state"] == "Archived"

    @pytest.mark.asyncio
    async def test_cannot_skip_workflow_steps(self, client: AsyncClient, sample_policy_data: dict):
        """Test that workflow steps cannot be skipped."""
        # Create a policy
        create_response = await client.post("/api/v1/policies/", json=sample_policy_data)
        policy_id = create_response.json()["id"]

        # Try to approve without submitting for review first
        approve_response = await client.post(
            f"/api/v1/policies/{policy_id}/approve",

        )
        assert approve_response.status_code == 400

        # Try to publish without approval
        publish_response = await client.post(f"/api/v1/policies/{policy_id}/publish")
        assert publish_response.status_code == 400

    @pytest.mark.asyncio
    async def test_reject_policy(self, client: AsyncClient, sample_policy_data: dict):
        """Test rejecting a policy in review."""
        # Create and submit for review
        create_response = await client.post("/api/v1/policies/", json=sample_policy_data)
        policy_id = create_response.json()["id"]
        await client.post(f"/api/v1/policies/{policy_id}/submit-for-review")

        # Reject
        reject_response = await client.post(
            f"/api/v1/policies/{policy_id}/reject",
            params={"rejection_reason": "Needs more detail"}
        )
        assert reject_response.status_code == 200
        assert reject_response.json()["state"] == "Draft"  # Returns to Draft


class TestPolicyVersioning:
    """Test policy versioning functionality."""

    @pytest.mark.asyncio
    async def test_create_new_version(self, client: AsyncClient, sample_policy_data: dict):
        """Test creating a new version of a published policy."""
        # Create, review, approve, publish
        create_response = await client.post("/api/v1/policies/", json=sample_policy_data)
        policy_id = create_response.json()["id"]
        await client.post(f"/api/v1/policies/{policy_id}/submit-for-review")
        await client.post(f"/api/v1/policies/{policy_id}/approve", params={"approved_by_id": 1})
        await client.post(f"/api/v1/policies/{policy_id}/publish")

        # Create new version
        new_version_response = await client.post(f"/api/v1/policies/{policy_id}/new-version")
        assert new_version_response.status_code == 200

        new_version = new_version_response.json()
        assert new_version["version"] == 2
        assert new_version["state"] == "Draft"
        assert new_version["id"] != policy_id  # New ID


class TestPolicyRestrictions:
    """Test policy editing restrictions based on state."""

    @pytest.mark.asyncio
    async def test_cannot_update_content_when_not_draft(self, client: AsyncClient, sample_policy_data: dict):
        """Test that content cannot be updated when policy is not in Draft state."""
        # Create and submit for review
        create_response = await client.post("/api/v1/policies/", json=sample_policy_data)
        policy_id = create_response.json()["id"]
        await client.post(f"/api/v1/policies/{policy_id}/submit-for-review")

        # Try to update content
        update_response = await client.patch(
            f"/api/v1/policies/{policy_id}",
            json={"title": "New Title"}
        )
        assert update_response.status_code == 400

    @pytest.mark.asyncio
    async def test_cannot_delete_published_policy(self, client: AsyncClient, sample_policy_data: dict):
        """Test that published policies cannot be deleted."""
        # Create full workflow to Published
        create_response = await client.post("/api/v1/policies/", json=sample_policy_data)
        policy_id = create_response.json()["id"]
        await client.post(f"/api/v1/policies/{policy_id}/submit-for-review")
        await client.post(f"/api/v1/policies/{policy_id}/approve", params={"approved_by_id": 1})
        await client.post(f"/api/v1/policies/{policy_id}/publish")

        # Try to delete
        delete_response = await client.delete(f"/api/v1/policies/{policy_id}")
        assert delete_response.status_code == 400
