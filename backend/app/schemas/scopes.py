from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional


class ScopeCreate(BaseModel):
    type: str
    name: str
    parent_id: Optional[UUID] = None
    domain: Optional[str] = None
    is_critical: bool = False
    verwerkt_pii: bool = False
    ext_verwerking_ref: Optional[str] = None


class ScopeUpdate(BaseModel):
    type: Optional[str] = None
    name: Optional[str] = None
    parent_id: Optional[UUID] = None
    domain: Optional[str] = None
    is_critical: Optional[bool] = None
    verwerkt_pii: Optional[bool] = None
    ext_verwerking_ref: Optional[str] = None


class ScopeResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    type: str
    name: str
    parent_id: Optional[UUID]
    domain: Optional[str]
    is_critical: bool
    verwerkt_pii: bool
    ext_verwerking_ref: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
