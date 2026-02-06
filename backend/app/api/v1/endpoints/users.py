"""
User Management and RBAC Endpoints
Handles Users, UserScopeRoles, and basic authentication utilities.
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.db import get_session
from app.core.crud import CRUDBase
from app.models.core_models import (
    User,
    UserRead,
    UserScopeRole,
    TenantUser,
    Role,
    TenantRole,
    Scope,
)

router = APIRouter()
crud_user = CRUDBase(User)
crud_user_scope_role = CRUDBase(UserScopeRole)


# =============================================================================
# USER CRUD
# =============================================================================

@router.get("/", response_model=List[UserRead])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    is_active: bool = Query(True, description="Filter by active status"),
    session: AsyncSession = Depends(get_session),
):
    """List users with optional filters."""
    filters = {"is_active": is_active}
    return await crud_user.get_multi(session, skip=skip, limit=limit, filters=filters)


@router.post("/", response_model=UserRead)
async def create_user(
    user: User,
    session: AsyncSession = Depends(get_session),
):
    """Create a new user."""
    # Check if username or email already exists
    existing = await crud_user.get_by_field(session, "username", user.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")

    existing = await crud_user.get_by_field(session, "email", user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    return await crud_user.create(session, obj_in=user)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get a user by ID."""
    return await crud_user.get_or_404(session, user_id)


@router.get("/by-username/{username}", response_model=UserRead)
async def get_user_by_username(
    username: str,
    session: AsyncSession = Depends(get_session),
):
    """Get a user by username."""
    user = await crud_user.get_by_field(session, "username", username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/by-email/{email}", response_model=UserRead)
async def get_user_by_email(
    email: str,
    session: AsyncSession = Depends(get_session),
):
    """Get a user by email."""
    user = await crud_user.get_by_field(session, "email", email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user_update: dict,
    session: AsyncSession = Depends(get_session),
):
    """Update a user."""
    db_user = await crud_user.get_or_404(session, user_id)

    # Prevent changing username/email to existing values
    if "username" in user_update and user_update["username"] != db_user.username:
        existing = await crud_user.get_by_field(session, "username", user_update["username"])
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")

    if "email" in user_update and user_update["email"] != db_user.email:
        existing = await crud_user.get_by_field(session, "email", user_update["email"])
        if existing:
            raise HTTPException(status_code=400, detail="Email already taken")

    return await crud_user.update(session, db_obj=db_user, obj_in=user_update)


@router.delete("/{user_id}")
async def deactivate_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Deactivate a user (soft delete)."""
    db_user = await crud_user.get_or_404(session, user_id)
    await crud_user.update(session, db_obj=db_user, obj_in={"is_active": False})
    return {"message": "User deactivated"}


@router.post("/{user_id}/login")
async def record_login(
    user_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Record a user login (updates last_login timestamp)."""
    db_user = await crud_user.get_or_404(session, user_id)
    await crud_user.update(session, db_obj=db_user, obj_in={"last_login": datetime.utcnow()})
    return {"message": "Login recorded"}


# =============================================================================
# USER SCOPE ROLES (RBAC)
# =============================================================================

@router.post("/{user_id}/scopes/{scope_id}/roles/{role}")
async def assign_scope_role(
    user_id: int,
    scope_id: int,
    role: Role,
    tenant_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Assign a role to a user for a specific scope.

    Roles:
    - ADMIN: Full access to scope
    - PROCESS_OWNER: Owns the process, can approve risks
    - SYSTEM_OWNER: Technical owner of assets
    - RISK_OWNER: Can accept risks
    - EDITOR: Can modify data
    - VIEWER: Read-only access
    """
    # Verify user and scope exist
    await crud_user.get_or_404(session, user_id)

    scope_crud = CRUDBase(Scope)
    await scope_crud.get_or_404(session, scope_id)

    # Check if role already exists
    result = await session.execute(
        select(UserScopeRole).where(
            UserScopeRole.user_id == user_id,
            UserScopeRole.scope_id == scope_id,
            UserScopeRole.role == role,
        )
    )
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Role already assigned")

    user_scope_role = UserScopeRole(
        tenant_id=tenant_id,
        user_id=user_id,
        scope_id=scope_id,
        role=role,
    )
    session.add(user_scope_role)
    await session.commit()
    await session.refresh(user_scope_role)

    return {"message": "Role assigned", "user_scope_role": user_scope_role}


@router.delete("/{user_id}/scopes/{scope_id}/roles/{role}")
async def remove_scope_role(
    user_id: int,
    scope_id: int,
    role: Role,
    session: AsyncSession = Depends(get_session),
):
    """Remove a role from a user for a specific scope."""
    result = await session.execute(
        select(UserScopeRole).where(
            UserScopeRole.user_id == user_id,
            UserScopeRole.scope_id == scope_id,
            UserScopeRole.role == role,
        )
    )
    user_scope_role = result.scalars().first()
    if not user_scope_role:
        raise HTTPException(status_code=404, detail="Role assignment not found")

    await session.delete(user_scope_role)
    await session.commit()

    return {"message": "Role removed"}


@router.get("/{user_id}/scopes", response_model=List[dict])
async def get_user_scopes(
    user_id: int,
    tenant_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
):
    """Get all scopes a user has access to with their roles."""
    await crud_user.get_or_404(session, user_id)

    query = select(UserScopeRole, Scope).join(
        Scope, UserScopeRole.scope_id == Scope.id
    ).where(UserScopeRole.user_id == user_id)

    if tenant_id:
        query = query.where(UserScopeRole.tenant_id == tenant_id)

    result = await session.execute(query)
    rows = result.all()

    # Group by scope
    scope_roles = {}
    for user_scope_role, scope in rows:
        if scope.id not in scope_roles:
            scope_roles[scope.id] = {
                "scope": scope,
                "roles": []
            }
        scope_roles[scope.id]["roles"].append(user_scope_role.role)

    return list(scope_roles.values())


@router.get("/{user_id}/permissions/{scope_id}")
async def check_user_permissions(
    user_id: int,
    scope_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Check what permissions a user has for a specific scope.
    Returns roles and derived permissions.
    """
    await crud_user.get_or_404(session, user_id)

    result = await session.execute(
        select(UserScopeRole).where(
            UserScopeRole.user_id == user_id,
            UserScopeRole.scope_id == scope_id,
        )
    )
    roles = [usr.role for usr in result.scalars().all()]

    # Derive permissions from roles
    permissions = {
        "can_view": len(roles) > 0,
        "can_edit": any(r in [Role.ADMIN, Role.PROCESS_OWNER, Role.SYSTEM_OWNER, Role.EDITOR] for r in roles),
        "can_accept_risks": any(r in [Role.ADMIN, Role.PROCESS_OWNER, Role.RISK_OWNER] for r in roles),
        "can_manage_users": Role.ADMIN in roles,
        "is_owner": any(r in [Role.PROCESS_OWNER, Role.SYSTEM_OWNER] for r in roles),
    }

    return {
        "user_id": user_id,
        "scope_id": scope_id,
        "roles": roles,
        "permissions": permissions,
    }


# =============================================================================
# TENANT MEMBERSHIP
# =============================================================================

@router.get("/{user_id}/tenants", response_model=List[dict])
async def get_user_tenants(
    user_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get all tenants a user belongs to."""
    await crud_user.get_or_404(session, user_id)

    result = await session.execute(
        select(TenantUser).where(TenantUser.user_id == user_id)
    )
    memberships = result.scalars().all()

    return [
        {
            "tenant_id": m.tenant_id,
            "role": m.role,
            "is_default": m.is_default,
            "joined_at": m.joined_at,
        }
        for m in memberships
    ]


@router.post("/{user_id}/tenants/{tenant_id}")
async def add_user_to_tenant(
    user_id: int,
    tenant_id: int,
    role: TenantRole = TenantRole.MEMBER,
    is_default: bool = False,
    session: AsyncSession = Depends(get_session),
):
    """Add a user to a tenant."""
    await crud_user.get_or_404(session, user_id)

    # Check if already member
    result = await session.execute(
        select(TenantUser).where(
            TenantUser.user_id == user_id,
            TenantUser.tenant_id == tenant_id,
        )
    )
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="User already member of tenant")

    # If setting as default, unset other defaults
    if is_default:
        result = await session.execute(
            select(TenantUser).where(
                TenantUser.user_id == user_id,
                TenantUser.is_default == True,
            )
        )
        for tu in result.scalars().all():
            tu.is_default = False
            session.add(tu)

    tenant_user = TenantUser(
        user_id=user_id,
        tenant_id=tenant_id,
        role=role,
        is_default=is_default,
    )
    session.add(tenant_user)
    await session.commit()

    return {"message": "User added to tenant"}


@router.delete("/{user_id}/tenants/{tenant_id}")
async def remove_user_from_tenant(
    user_id: int,
    tenant_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Remove a user from a tenant."""
    result = await session.execute(
        select(TenantUser).where(
            TenantUser.user_id == user_id,
            TenantUser.tenant_id == tenant_id,
        )
    )
    tenant_user = result.scalars().first()
    if not tenant_user:
        raise HTTPException(status_code=404, detail="User not member of tenant")

    await session.delete(tenant_user)
    await session.commit()

    return {"message": "User removed from tenant"}
