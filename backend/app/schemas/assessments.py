from pydantic import BaseModel
from datetime import date, datetime
from uuid import UUID
from typing import Optional


# ── IMSAssessment ───────────────────────────────────────────────────────────


class AssessmentCreate(BaseModel):
    assessment_type: str
    scope_id: Optional[UUID] = None
    domain: Optional[str] = None
    planned_at: date
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = "gepland"
    cyclus_id: Optional[int] = None
    document_id: Optional[UUID] = None


class AssessmentUpdate(BaseModel):
    assessment_type: Optional[str] = None
    scope_id: Optional[UUID] = None
    domain: Optional[str] = None
    planned_at: Optional[date] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: Optional[str] = None
    cyclus_id: Optional[int] = None
    document_id: Optional[UUID] = None


class AssessmentResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    assessment_type: str
    scope_id: Optional[UUID]
    domain: Optional[str]
    planned_at: date
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    status: str
    cyclus_id: Optional[int]
    document_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── IMSFinding ──────────────────────────────────────────────────────────────


class FindingCreate(BaseModel):
    assessment_id: UUID
    title: str
    description: str
    severity: str
    status: str = "open"
    requirement_id: Optional[UUID] = None


class FindingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    requirement_id: Optional[UUID] = None


class FindingResponse(BaseModel):
    id: UUID
    assessment_id: UUID
    tenant_id: UUID
    title: str
    description: str
    severity: str
    status: str
    requirement_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── IMSCorrectiveAction ────────────────────────────────────────────────────


class CorrectiveActionCreate(BaseModel):
    finding_id: Optional[UUID] = None
    risk_id: Optional[UUID] = None
    title: str
    description: str
    owner_user_id: Optional[UUID] = None
    due_date: date
    status: str = "open"


class CorrectiveActionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    owner_user_id: Optional[UUID] = None
    due_date: Optional[date] = None
    status: Optional[str] = None
    completed_at: Optional[datetime] = None


class CorrectiveActionResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    finding_id: Optional[UUID]
    risk_id: Optional[UUID]
    title: str
    description: str
    owner_user_id: Optional[UUID]
    due_date: date
    status: str
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
