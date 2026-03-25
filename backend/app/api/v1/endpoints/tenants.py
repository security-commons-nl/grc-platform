from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.auth import CurrentUser, get_current_user, require_role
from app.core.db import get_db
from app.models.core_models import Tenant, Region, User, UserTenantRole, UserRegionRole
from app.schemas.tenants import (
    TenantCreate, TenantUpdate, TenantResponse,
    RegionCreate, RegionUpdate, RegionResponse,
    UserCreate, UserUpdate, UserResponse,
    UserTenantRoleCreate, UserTenantRoleResponse,
    UserRegionRoleCreate, UserRegionRoleResponse,
)

router = APIRouter()


# ── Tenants ─────────────────────────────────────────────────────────────────


@router.get("/", response_model=list[TenantResponse])
async def list_tenants(
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Tenant).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@router.post("/", response_model=TenantResponse, status_code=201)
async def create_tenant(
    data: TenantCreate,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    tenant = Tenant(**data.model_dump())
    db.add(tenant)
    await db.flush()
    await db.refresh(tenant)
    return tenant


@router.patch("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: UUID,
    data: TenantUpdate,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(tenant, field, value)
    await db.flush()
    await db.refresh(tenant)
    return tenant


@router.delete("/{tenant_id}", status_code=204)
async def delete_tenant(
    tenant_id: UUID,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    await db.delete(tenant)
    await db.flush()


# ── Regions ─────────────────────────────────────────────────────────────────


@router.get("/regions/", response_model=list[RegionResponse])
async def list_regions(
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Region).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/regions/{region_id}", response_model=RegionResponse)
async def get_region(
    region_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Region).where(Region.id == region_id))
    region = result.scalar_one_or_none()
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    return region


@router.post("/regions/", response_model=RegionResponse, status_code=201)
async def create_region(
    data: RegionCreate,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    region = Region(**data.model_dump())
    db.add(region)
    await db.flush()
    await db.refresh(region)
    return region


@router.patch("/regions/{region_id}", response_model=RegionResponse)
async def update_region(
    region_id: UUID,
    data: RegionUpdate,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Region).where(Region.id == region_id))
    region = result.scalar_one_or_none()
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(region, field, value)
    await db.flush()
    await db.refresh(region)
    return region


@router.delete("/regions/{region_id}", status_code=204)
async def delete_region(
    region_id: UUID,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Region).where(Region.id == region_id))
    region = result.scalar_one_or_none()
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    await db.delete(region)
    await db.flush()


# ── Users ───────────────────────────────────────────────────────────────────


@router.get("/users/", response_model=list[UserResponse])
async def list_users(
    tenant_id: UUID = Query(...),
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(User).where(User.tenant_id == tenant_id).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/users/", response_model=UserResponse, status_code=201)
async def create_user(
    data: UserCreate,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    user = User(**data.model_dump())
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    await db.flush()
    await db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: UUID,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(user)
    await db.flush()


# ── User Tenant Roles ──────────────────────────────────────────────────────


@router.get("/user-tenant-roles/", response_model=list[UserTenantRoleResponse])
async def list_user_tenant_roles(
    tenant_id: UUID = Query(...),
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(UserTenantRole).where(UserTenantRole.tenant_id == tenant_id).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/user-tenant-roles/", response_model=UserTenantRoleResponse, status_code=201)
async def create_user_tenant_role(
    data: UserTenantRoleCreate,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    role = UserTenantRole(**data.model_dump())
    db.add(role)
    await db.flush()
    await db.refresh(role)
    return role


@router.delete("/user-tenant-roles/{role_id}", status_code=204)
async def delete_user_tenant_role(
    role_id: UUID,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(UserTenantRole).where(UserTenantRole.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="UserTenantRole not found")
    await db.delete(role)
    await db.flush()


# ── User Region Roles ──────────────────────────────────────────────────────


@router.get("/user-region-roles/", response_model=list[UserRegionRoleResponse])
async def list_user_region_roles(
    region_id: UUID = Query(...),
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(UserRegionRole).where(UserRegionRole.region_id == region_id).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/user-region-roles/", response_model=UserRegionRoleResponse, status_code=201)
async def create_user_region_role(
    data: UserRegionRoleCreate,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    role = UserRegionRole(**data.model_dump())
    db.add(role)
    await db.flush()
    await db.refresh(role)
    return role


@router.delete("/user-region-roles/{role_id}", status_code=204)
async def delete_user_region_role(
    role_id: UUID,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(UserRegionRole).where(UserRegionRole.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="UserRegionRole not found")
    await db.delete(role)
    await db.flush()
