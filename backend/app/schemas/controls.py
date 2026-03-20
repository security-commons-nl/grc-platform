from pydantic import BaseModel
from datetime import date, datetime
from uuid import UUID
from typing import Optional


class ControlCreate(BaseModel):
    requirement_id: Optional[UUID] = None
    title: str
    description: str
    domain: str
    owner_user_id: Optional[UUID] = None
    implementation_status: str = "niet_gestart"
    implementation_date: Optional[date] = None


class ControlUpdate(BaseModel):
    requirement_id: Optional[UUID] = None
    title: Optional[str] = None
    description: Optional[str] = None
    domain: Optional[str] = None
    owner_user_id: Optional[UUID] = None
    implementation_status: Optional[str] = None
    implementation_date: Optional[date] = None


class ControlResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    requirement_id: Optional[UUID]
    title: str
    description: str
    domain: str
    owner_user_id: Optional[UUID]
    implementation_status: str
    implementation_date: Optional[date]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
