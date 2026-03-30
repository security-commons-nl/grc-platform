from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Any, Optional, List


# ── IMSStep ─────────────────────────────────────────────────────────────────


class StepCreate(BaseModel):
    number: str
    phase: int
    name: str
    waarom_nu: str
    uitleg: Optional[str] = None
    voorbeeld_content: Optional[Any] = None
    required_gremium: str
    is_optional: bool = False
    domain: Optional[str] = None


class StepUpdate(BaseModel):
    number: Optional[str] = None
    phase: Optional[int] = None
    name: Optional[str] = None
    waarom_nu: Optional[str] = None
    uitleg: Optional[str] = None
    voorbeeld_content: Optional[Any] = None
    required_gremium: Optional[str] = None
    is_optional: Optional[bool] = None
    domain: Optional[str] = None


class StepResponse(BaseModel):
    id: UUID
    number: str
    phase: int
    name: str
    waarom_nu: str
    uitleg: Optional[str] = None
    voorbeeld_content: Optional[Any] = None
    required_gremium: str
    is_optional: bool
    domain: Optional[str]
    outputs: List["StepOutputResponse"] = []
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


# ── IMSStepOutput ────────────────────────────────────────────────────────


class StepOutputResponse(BaseModel):
    id: UUID
    step_id: UUID
    name: str
    output_type: str
    requirement: str
    sort_order: int
    skip_warning: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── IMSStepOutputFulfillment ────────────────────────────────────────────


class StepOutputFulfillmentCreate(BaseModel):
    step_output_id: UUID
    decision_id: Optional[UUID] = None
    document_id: Optional[UUID] = None


class StepOutputFulfillmentResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    step_output_id: UUID
    step_execution_id: UUID
    decision_id: Optional[UUID]
    document_id: Optional[UUID]
    fulfilled_at: datetime
    fulfilled_by: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── StepReadiness (computed) ────────────────────────────────────────────


class OutputReadinessItem(BaseModel):
    output: StepOutputResponse
    fulfilled: bool
    fulfillment: Optional[StepOutputFulfillmentResponse] = None


class StepReadiness(BaseModel):
    step_id: UUID
    execution_id: Optional[UUID]
    current_status: str
    outputs: List[OutputReadinessItem]
    required_fulfilled: int
    required_total: int
    all_required_met: bool
    recommended_unfulfilled: List[OutputReadinessItem]
    dependencies_met: bool
    blocking_dependencies: List[UUID]
    allowed_transitions: List[str]
    can_advance: bool
