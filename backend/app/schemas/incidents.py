from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional


class IncidentCreate(BaseModel):
    title: str
    incident_type: str
    severity: str
    status: str = "open"
    reported_at: datetime
    resolved_at: Optional[datetime] = None
    external_ticket_id: Optional[str] = None
    corrective_action_id: Optional[UUID] = None


class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    incident_type: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    resolved_at: Optional[datetime] = None
    external_ticket_id: Optional[str] = None
    corrective_action_id: Optional[UUID] = None


class IncidentResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    title: str
    incident_type: str
    severity: str
    status: str
    reported_at: datetime
    resolved_at: Optional[datetime]
    external_ticket_id: Optional[str]
    corrective_action_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
