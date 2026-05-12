"""Pydantic schemas voor organisatie-eenheden (RFC 0002)."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class OrganizationalUnitCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    code: Optional[str] = Field(None, max_length=32)
    unit_type: str = Field(
        ...,
        max_length=32,
        description=(
            "Vrije aanduiding (bv. directie, cluster, team, afdeling). "
            "Tenant kiest zelf de set; geen DB-enum."
        ),
    )
    parent_id: Optional[UUID] = None
    is_active: bool = True


class OrganizationalUnitUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    code: Optional[str] = Field(None, max_length=32)
    unit_type: Optional[str] = Field(None, max_length=32)
    parent_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class OrganizationalUnitResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    name: str
    code: Optional[str]
    unit_type: str
    parent_id: Optional[UUID]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OrganizationalUnitTreeNode(OrganizationalUnitResponse):
    """Boom-representatie — children genest in response."""

    children: list["OrganizationalUnitTreeNode"] = Field(default_factory=list)


OrganizationalUnitTreeNode.model_rebuild()
