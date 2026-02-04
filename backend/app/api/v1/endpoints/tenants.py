"""
Tenant Management Endpoints
Handles multi-tenant configuration and relationships.
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.db import get_session
from app.core.crud import CRUDBase
from app.models.core_models import (
    Tenant,
    TenantUser,
    TenantRelationship,
    TenantRelationshipType,
    TenantRole,
)

router = APIRouter()
crud_tenant = CRUDBase(Tenant)


# =============================================================================
# TENANT CRUD
# =============================================================================

@router.get("/", response_model=List[Tenant])
async def list_tenants(
    skip: int = 0,
    limit: int = 100,
    is_active: bool = Query(True),
    session: AsyncSession = Depends(get_session),
):
    """List all tenants."""
    filters = {"is_active": is_active}
    return await crud_tenant.get_multi(session, skip=skip, limit=limit, filters=filters)


@router.post("/", response_model=Tenant)
async def create_tenant(
    tenant: Tenant,
    session: AsyncSession = Depends(get_session),
):
    """Create a new tenant."""
    # Check slug uniqueness
    existing = await crud_tenant.get_by_field(session, "slug", tenant.slug)
    if existing:
        raise HTTPException(status_code=400, detail="Tenant slug already exists")

    return await crud_tenant.create(session, obj_in=tenant)


@router.get("/{tenant_id}", response_model=Tenant)
async def get_tenant(
    tenant_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get a tenant by ID."""
    return await crud_tenant.get_or_404(session, tenant_id)


@router.get("/by-slug/{slug}", response_model=Tenant)
async def get_tenant_by_slug(
    slug: str,
    session: AsyncSession = Depends(get_session),
):
    """Get a tenant by slug."""
    tenant = await crud_tenant.get_by_field(session, "slug", slug)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@router.patch("/{tenant_id}", response_model=Tenant)
async def update_tenant(
    tenant_id: int,
    tenant_update: dict,
    session: AsyncSession = Depends(get_session),
):
    """Update a tenant."""
    db_tenant = await crud_tenant.get_or_404(session, tenant_id)

    # Check slug uniqueness if changing
    if "slug" in tenant_update and tenant_update["slug"] != db_tenant.slug:
        existing = await crud_tenant.get_by_field(session, "slug", tenant_update["slug"])
        if existing:
            raise HTTPException(status_code=400, detail="Tenant slug already exists")

    tenant_update["updated_at"] = datetime.utcnow()
    return await crud_tenant.update(session, db_obj=db_tenant, obj_in=tenant_update)


@router.delete("/{tenant_id}")
async def deactivate_tenant(
    tenant_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Deactivate a tenant (soft delete)."""
    db_tenant = await crud_tenant.get_or_404(session, tenant_id)
    await crud_tenant.update(session, db_obj=db_tenant, obj_in={"is_active": False})
    return {"message": "Tenant deactivated"}


# =============================================================================
# TENANT USERS
# =============================================================================

@router.get("/{tenant_id}/users", response_model=List[TenantUser])
async def get_tenant_users(
    tenant_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get all users in a tenant."""
    await crud_tenant.get_or_404(session, tenant_id)

    result = await session.execute(
        select(TenantUser).where(TenantUser.tenant_id == tenant_id)
    )
    return result.scalars().all()


@router.post("/{tenant_id}/users/{user_id}")
async def add_user_to_tenant(
    tenant_id: int,
    user_id: int,
    role: TenantRole = TenantRole.MEMBER,
    session: AsyncSession = Depends(get_session),
):
    """Add a user to a tenant."""
    await crud_tenant.get_or_404(session, tenant_id)

    # Check if already member
    result = await session.execute(
        select(TenantUser).where(
            TenantUser.tenant_id == tenant_id,
            TenantUser.user_id == user_id,
        )
    )
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="User already member of tenant")

    tenant_user = TenantUser(
        tenant_id=tenant_id,
        user_id=user_id,
        role=role,
    )
    session.add(tenant_user)
    await session.commit()

    return {"message": "User added to tenant"}


@router.patch("/{tenant_id}/users/{user_id}")
async def update_tenant_user_role(
    tenant_id: int,
    user_id: int,
    role: TenantRole,
    session: AsyncSession = Depends(get_session),
):
    """Update a user's role in a tenant."""
    result = await session.execute(
        select(TenantUser).where(
            TenantUser.tenant_id == tenant_id,
            TenantUser.user_id == user_id,
        )
    )
    tenant_user = result.scalars().first()
    if not tenant_user:
        raise HTTPException(status_code=404, detail="User not member of tenant")

    tenant_user.role = role
    session.add(tenant_user)
    await session.commit()

    return {"message": "User role updated"}


@router.delete("/{tenant_id}/users/{user_id}")
async def remove_user_from_tenant(
    tenant_id: int,
    user_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Remove a user from a tenant."""
    result = await session.execute(
        select(TenantUser).where(
            TenantUser.tenant_id == tenant_id,
            TenantUser.user_id == user_id,
        )
    )
    tenant_user = result.scalars().first()
    if not tenant_user:
        raise HTTPException(status_code=404, detail="User not member of tenant")

    await session.delete(tenant_user)
    await session.commit()

    return {"message": "User removed from tenant"}


# =============================================================================
# TENANT RELATIONSHIPS (SSC Model)
# =============================================================================

@router.get("/{tenant_id}/relationships", response_model=List[dict])
async def get_tenant_relationships(
    tenant_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get all relationships for a tenant (both as provider and consumer)."""
    await crud_tenant.get_or_404(session, tenant_id)

    # As provider
    provider_result = await session.execute(
        select(TenantRelationship).where(TenantRelationship.provider_tenant_id == tenant_id)
    )
    as_provider = provider_result.scalars().all()

    # As consumer
    consumer_result = await session.execute(
        select(TenantRelationship).where(TenantRelationship.consumer_tenant_id == tenant_id)
    )
    as_consumer = consumer_result.scalars().all()

    return {
        "as_provider": [{"id": r.id, "consumer_id": r.consumer_tenant_id, "type": r.relationship_type} for r in as_provider],
        "as_consumer": [{"id": r.id, "provider_id": r.provider_tenant_id, "type": r.relationship_type} for r in as_consumer],
    }


@router.post("/{provider_id}/relationships/{consumer_id}")
async def create_tenant_relationship(
    provider_id: int,
    consumer_id: int,
    relationship_type: TenantRelationshipType,
    session: AsyncSession = Depends(get_session),
):
    """Create a relationship between tenants (provider provides services to consumer)."""
    # Verify both tenants exist
    await crud_tenant.get_or_404(session, provider_id)
    await crud_tenant.get_or_404(session, consumer_id)

    if provider_id == consumer_id:
        raise HTTPException(status_code=400, detail="Tenant cannot have relationship with itself")

    # Check if relationship already exists
    result = await session.execute(
        select(TenantRelationship).where(
            TenantRelationship.provider_tenant_id == provider_id,
            TenantRelationship.consumer_tenant_id == consumer_id,
        )
    )
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Relationship already exists")

    relationship = TenantRelationship(
        provider_tenant_id=provider_id,
        consumer_tenant_id=consumer_id,
        relationship_type=relationship_type,
        is_active=True,
    )
    session.add(relationship)
    await session.commit()

    return {"message": "Tenant relationship created", "relationship_id": relationship.id}


@router.delete("/relationships/{relationship_id}")
async def delete_tenant_relationship(
    relationship_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Delete a tenant relationship."""
    result = await session.execute(
        select(TenantRelationship).where(TenantRelationship.id == relationship_id)
    )
    relationship = result.scalars().first()
    if not relationship:
        raise HTTPException(status_code=404, detail="Relationship not found")

    await session.delete(relationship)
    await session.commit()

    return {"message": "Relationship deleted"}

