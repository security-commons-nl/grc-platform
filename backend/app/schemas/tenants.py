from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional


# ── Tenant ──────────────────────────────────────────────────────────────────


class TenantCreate(BaseModel):
    name: str
    type: str
    region_id: Optional[UUID] = None
    is_active: bool = True


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    region_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class TenantResponse(BaseModel):
    id: UUID
    name: str
    type: str
    region_id: Optional[UUID]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Region ──────────────────────────────────────────────────────────────────


class RegionCreate(BaseModel):
    name: str
    centrum_tenant_id: Optional[UUID] = None


class RegionUpdate(BaseModel):
    name: Optional[str] = None
    centrum_tenant_id: Optional[UUID] = None


class RegionResponse(BaseModel):
    id: UUID
    name: str
    centrum_tenant_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── User ────────────────────────────────────────────────────────────────────


class UserCreate(BaseModel):
    tenant_id: UUID
    external_id: str
    name: str
    email: str
    is_active: bool = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    external_id: str
    name: str
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── UserTenantRole ──────────────────────────────────────────────────────────


class UserTenantRoleCreate(BaseModel):
    user_id: UUID
    tenant_id: UUID
    role: str
    domain: Optional[str] = None


class UserTenantRoleResponse(BaseModel):
    id: UUID
    user_id: UUID
    tenant_id: UUID
    role: str
    domain: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── UserRegionRole ──────────────────────────────────────────────────────────


class UserRegionRoleCreate(BaseModel):
    user_id: UUID
    region_id: UUID
    role: str


class UserRegionRoleResponse(BaseModel):
    id: UUID
    user_id: UUID
    region_id: UUID
    role: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
