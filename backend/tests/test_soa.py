import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.models.core_models import (
    ApplicabilityStatement,
    Standard,
    Requirement,
    Scope,
    Tenant,
    FrameworkType,
    ScopeType,
    ClassificationLevel
)


class TestSoAInitialization:
    @pytest.mark.asyncio
    async def test_initialize_soa_from_standard(self, client: AsyncClient, db_session: AsyncSession):
        # 1. Setup Data
        tenant = Tenant(name="Test Tenant SoA", slug="test-soa", is_active=True)
        db_session.add(tenant)
        await db_session.flush()

        standard = Standard(
            name="BIO",
            version="1.04",
            type=FrameworkType.BIO,
            tenant_id=tenant.id
        )
        db_session.add(standard)
        await db_session.flush()

        # Create 5 requirements
        reqs = []
        for i in range(5):
            req = Requirement(
                standard_id=standard.id,
                code=f"REQ-{i}",
                title=f"Requirement {i}",
                description="Test requirement"
            )
            reqs.append(req)
        db_session.add_all(reqs)

        scope = Scope(
            tenant_id=tenant.id,
            name="Test Scope SoA",
            type=ScopeType.PROCESS,
            owner="Test Owner",
            availability_rating=ClassificationLevel.INTERNAL,
            integrity_rating=ClassificationLevel.INTERNAL,
            confidentiality_rating=ClassificationLevel.INTERNAL
        )
        db_session.add(scope)
        await db_session.commit()

        # Reload IDs
        scope_id = scope.id
        standard_id = standard.id
        tenant_id = tenant.id

        # 2. Call API to initialize
        response = await client.post(
            f"/api/v1/soa/scope/{scope_id}/initialize-from-standard/{standard_id}?tenant_id={tenant_id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["created"] == 5
        assert data["skipped"] == 0

        # Verify DB
        result = await db_session.execute(
            select(ApplicabilityStatement)
            .where(ApplicabilityStatement.scope_id == scope_id)
            .where(ApplicabilityStatement.tenant_id == tenant_id)
        )
        soas = result.scalars().all()
        assert len(soas) == 5

        # 3. Call again (should skip all)
        response = await client.post(
            f"/api/v1/soa/scope/{scope_id}/initialize-from-standard/{standard_id}?tenant_id={tenant_id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["created"] == 0
        assert data["skipped"] == 5

        # 4. Add new requirement and call again
        new_req = Requirement(
            standard_id=standard.id,
            code="REQ-NEW",
            title="New Requirement",
            description="Test requirement"
        )
        db_session.add(new_req)
        await db_session.commit()

        response = await client.post(
            f"/api/v1/soa/scope/{scope_id}/initialize-from-standard/{standard_id}?tenant_id={tenant_id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["created"] == 1
        assert data["skipped"] == 5

