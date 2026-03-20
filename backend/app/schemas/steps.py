from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional


# ── IMSStep ─────────────────────────────────────────────────────────────────


class StepCreate(BaseModel):
    number: str
    phase: int
    name: str
    waarom_nu: str
    required_gremium: str
    is_optional: bool = False
    domain: Optional[str] = None


class StepUpdate(BaseModel):
    number: Optional[str] = None
    phase: Optional[int] = None
    name: Optional[str] = None
    waarom_nu: Optional[str] = None
    required_gremium: Optional[str] = None
    is_optional: Optional[bool] = None
    domain: Optional[str] = None


class StepResponse(BaseModel):
    id: UUID
    number: str
    phase: int
    name: str
    waarom_nu: str
    required_gremium: str
    is_optional: bool
    domain: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── IMSStepDependency ──────────────────────────────────────────────────────


class StepDependencyCreate(BaseModel):
    step_id: UUID
    depends_on_step_id: UUID
    dependency_type: str


class StepDependencyResponse(BaseModel):
    id: UUID
    step_id: UUID
    depends_on_step_id: UUID
    dependency_type: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── IMSStepExecution ────────────────────────────────────────────────────────


class StepExecutionCreate(BaseModel):
    step_id: UUID
    cyclus_id: Optional[int] = None
    status: str = "niet_gestart"
    skipped: bool = False
    skip_reason: Optional[str] = None
    skip_logged_by: Optional[str] = None


class StepExecutionUpdate(BaseModel):
    status: Optional[str] = None
    skipped: Optional[bool] = None
    skip_reason: Optional[str] = None
    skip_logged_by: Optional[str] = None


class StepExecutionResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    step_id: UUID
    cyclus_id: Optional[int]
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    skipped: bool
    skip_reason: Optional[str]
    skip_logged_by: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
