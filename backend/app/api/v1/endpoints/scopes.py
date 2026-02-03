"""
Scope Management Endpoints
Handles Organization, Cluster, Department, Process, Asset, Supplier hierarchies.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.db import get_session
from app.core.crud import CRUDBase
from app.models.core_models import (
    Scope,
    ScopeType,
    ScopeDependency,
    ClassificationLevel,
    AssetType,
)

router = APIRouter()
crud_scope = CRUDBase(Scope)


# --- Scope CRUD ---

@router.get("/", response_model=List[Scope])
async def list_scopes(
    skip: int = 0,
    limit: int = 100,
    tenant_id: Optional[int] = Query(None, description="Filter by tenant"),
    scope_type: Optional[ScopeType] = Query(None, description="Filter by type"),
    parent_id: Optional[int] = Query(None, description="Filter by parent scope"),
    is_active: bool = Query(True, description="Filter by active status"),
    session: AsyncSession = Depends(get_session),
):
    """List scopes with optional filters."""
    filters = {"is_active": is_active}
    if tenant_id:
        filters["tenant_id"] = tenant_id
    if scope_type:
        filters["type"] = scope_type
    if parent_id:
        filters["parent_id"] = parent_id

    return await crud_scope.get_multi(session, skip=skip, limit=limit, filters=filters)


@router.post("/", response_model=Scope)
async def create_scope(
    scope: Scope,
    session: AsyncSession = Depends(get_session),
):
    """Create a new scope."""
    # Validate parent exists if specified
    if scope.parent_id:
        parent = await crud_scope.get(session, scope.parent_id)
        if not parent:
            raise HTTPException(status_code=400, detail="Parent scope not found")
        # Validate hierarchy (parent must be higher level)
        hierarchy = [ScopeType.ORGANIZATION, ScopeType.CLUSTER, ScopeType.DEPARTMENT,
                     ScopeType.PROCESS, ScopeType.ASSET]
        if scope.type in hierarchy and parent.type in hierarchy:
            if hierarchy.index(scope.type) <= hierarchy.index(parent.type):
                raise HTTPException(
                    status_code=400,
                    detail=f"Scope type {scope.type} cannot be child of {parent.type}"
                )

    return await crud_scope.create(session, obj_in=scope)


@router.get("/{scope_id}", response_model=Scope)
async def get_scope(
    scope_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get a scope by ID."""
    return await crud_scope.get_or_404(session, scope_id)


@router.patch("/{scope_id}", response_model=Scope)
async def update_scope(
    scope_id: int,
    scope_update: dict,
    session: AsyncSession = Depends(get_session),
):
    """Update a scope."""
    db_scope = await crud_scope.get_or_404(session, scope_id)
    return await crud_scope.update(session, db_obj=db_scope, obj_in=scope_update)


@router.delete("/{scope_id}")
async def delete_scope(
    scope_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Delete a scope (soft delete - sets is_active=False)."""
    db_scope = await crud_scope.get_or_404(session, scope_id)
    await crud_scope.update(session, db_obj=db_scope, obj_in={"is_active": False})
    return {"message": "Scope deactivated"}


# --- Hierarchy Operations ---

@router.get("/{scope_id}/children", response_model=List[Scope])
async def get_scope_children(
    scope_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get direct children of a scope."""
    await crud_scope.get_or_404(session, scope_id)  # Verify parent exists
    return await crud_scope.get_multi_by_field(session, "parent_id", scope_id)


@router.get("/{scope_id}/tree", response_model=dict)
async def get_scope_tree(
    scope_id: int,
    max_depth: int = Query(5, ge=1, le=10),
    session: AsyncSession = Depends(get_session),
):
    """Get scope with full subtree."""
    scope = await crud_scope.get_or_404(session, scope_id)

    async def build_tree(s: Scope, depth: int) -> dict:
        if depth <= 0:
            return {"scope": s, "children": []}

        children = await crud_scope.get_multi_by_field(session, "parent_id", s.id)
        return {
            "scope": s,
            "children": [await build_tree(c, depth - 1) for c in children]
        }

    return await build_tree(scope, max_depth)


# --- BIA (Business Impact Analysis) ---

@router.patch("/{scope_id}/bia", response_model=Scope)
async def update_scope_bia(
    scope_id: int,
    availability_rating: Optional[ClassificationLevel] = None,
    integrity_rating: Optional[ClassificationLevel] = None,
    confidentiality_rating: Optional[ClassificationLevel] = None,
    rto_hours: Optional[int] = None,
    rpo_hours: Optional[int] = None,
    mtpd_hours: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
):
    """Update BIA (Business Impact Analysis) ratings for a scope."""
    db_scope = await crud_scope.get_or_404(session, scope_id)

    updates = {}
    if availability_rating is not None:
        updates["availability_rating"] = availability_rating
    if integrity_rating is not None:
        updates["integrity_rating"] = integrity_rating
    if confidentiality_rating is not None:
        updates["confidentiality_rating"] = confidentiality_rating
    if rto_hours is not None:
        updates["rto_hours"] = rto_hours
    if rpo_hours is not None:
        updates["rpo_hours"] = rpo_hours
    if mtpd_hours is not None:
        updates["mtpd_hours"] = mtpd_hours

    return await crud_scope.update(session, db_obj=db_scope, obj_in=updates)


# --- Scope Dependencies ---

@router.post("/{scope_id}/dependencies/{provider_id}")
async def add_scope_dependency(
    scope_id: int,
    provider_id: int,
    dependency_type: str = "operational",
    criticality: str = "medium",
    session: AsyncSession = Depends(get_session),
):
    """
    Add a dependency between scopes.
    scope_id depends on provider_id.
    """
    # Verify both scopes exist
    depender = await crud_scope.get_or_404(session, scope_id)
    provider = await crud_scope.get_or_404(session, provider_id)

    if scope_id == provider_id:
        raise HTTPException(status_code=400, detail="Scope cannot depend on itself")

    # Check if dependency already exists
    result = await session.execute(
        select(ScopeDependency).where(
            ScopeDependency.depender_id == scope_id,
            ScopeDependency.provider_id == provider_id
        )
    )
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Dependency already exists")

    dependency = ScopeDependency(
        depender_id=scope_id,
        provider_id=provider_id,
        dependency_type=dependency_type,
        criticality=criticality,
    )
    session.add(dependency)
    await session.commit()
    await session.refresh(dependency)

    return {"message": "Dependency created", "dependency": dependency}


@router.delete("/{scope_id}/dependencies/{provider_id}")
async def remove_scope_dependency(
    scope_id: int,
    provider_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Remove a dependency between scopes."""
    result = await session.execute(
        select(ScopeDependency).where(
            ScopeDependency.depender_id == scope_id,
            ScopeDependency.provider_id == provider_id
        )
    )
    dependency = result.scalars().first()
    if not dependency:
        raise HTTPException(status_code=404, detail="Dependency not found")

    await session.delete(dependency)
    await session.commit()

    return {"message": "Dependency removed"}


@router.get("/{scope_id}/dependencies", response_model=List[Scope])
async def get_scope_dependencies(
    scope_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get all scopes that this scope depends on."""
    await crud_scope.get_or_404(session, scope_id)

    result = await session.execute(
        select(Scope).join(
            ScopeDependency, Scope.id == ScopeDependency.provider_id
        ).where(ScopeDependency.depender_id == scope_id)
    )
    return result.scalars().all()


@router.get("/{scope_id}/dependents", response_model=List[Scope])
async def get_scope_dependents(
    scope_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get all scopes that depend on this scope."""
    await crud_scope.get_or_404(session, scope_id)

    result = await session.execute(
        select(Scope).join(
            ScopeDependency, Scope.id == ScopeDependency.depender_id
        ).where(ScopeDependency.provider_id == scope_id)
    )
    return result.scalars().all()
