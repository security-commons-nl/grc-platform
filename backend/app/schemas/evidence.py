from pydantic import BaseModel
from datetime import date, datetime
from uuid import UUID
from typing import Optional


class EvidenceCreate(BaseModel):
    control_id: UUID
    title: str
    evidence_type: str
    storage_path: str
    collected_at: date
    valid_until: Optional[date] = None
    collected_by_user_id: Optional[UUID] = None


class EvidenceUpdate(BaseModel):
    title: Optional[str] = None
    evidence_type: Optional[str] = None
    storage_path: Optional[str] = None
    collected_at: Optional[date] = None
    valid_until: Optional[date] = None
    collected_by_user_id: Optional[UUID] = None


class EvidenceResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    control_id: UUID
    title: str
    evidence_type: str
    storage_path: str
    collected_at: date
    valid_until: Optional[date]
    collected_by_user_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
