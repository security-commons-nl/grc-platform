from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional


class DecisionCreate(BaseModel):
    number: str
    step_execution_id: Optional[UUID] = None
    decision_type: str
    content: str
    grondslag: str
    gremium: str
    decided_by_name: str
    decided_by_role: str
    decided_at: datetime
    valid_until: Optional[str] = None
    motivation: Optional[str] = None
    alternatives: Optional[str] = None
    iso_clause: Optional[str] = None
    supersedes_id: Optional[UUID] = None


class DecisionResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    number: str
    step_execution_id: Optional[UUID]
    decision_type: str
    content: str
    grondslag: str
    gremium: str
    decided_by_name: str
    decided_by_role: str
    decided_at: datetime
    valid_until: Optional[str]
    motivation: Optional[str]
    alternatives: Optional[str]
    iso_clause: Optional[str]
    supersedes_id: Optional[UUID]
    created_at: datetime

    model_config = {"from_attributes": True}
