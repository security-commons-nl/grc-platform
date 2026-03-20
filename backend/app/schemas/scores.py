from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Any, Optional
from decimal import Decimal


# ── IMSMaturityProfile ──────────────────────────────────────────────────────


class MaturityProfileCreate(BaseModel):
    domain: str
    existing_registers: str
    existing_analyses: str
    coordination_capacity: str
    linemanagement_structure: str
    recommended_option: Optional[str] = None


class MaturityProfileUpdate(BaseModel):
    domain: Optional[str] = None
    existing_registers: Optional[str] = None
    existing_analyses: Optional[str] = None
    coordination_capacity: Optional[str] = None
    linemanagement_structure: Optional[str] = None
    recommended_option: Optional[str] = None


class MaturityProfileResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    domain: str
    existing_registers: str
    existing_analyses: str
    coordination_capacity: str
    linemanagement_structure: str
    recommended_option: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── IMSSetupScore ──────────────────────────────────────────────────────────


class SetupScoreCreate(BaseModel):
    domain: str
    cyclus_year: int
    score_pct: Decimal
    steps_completed: int
    steps_total: int
    confirmed_at: Optional[datetime] = None
    calculated_at: datetime


class SetupScoreUpdate(BaseModel):
    score_pct: Optional[Decimal] = None
    steps_completed: Optional[int] = None
    steps_total: Optional[int] = None
    confirmed_at: Optional[datetime] = None


class SetupScoreResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    domain: str
    cyclus_year: int
    score_pct: Decimal
    steps_completed: int
    steps_total: int
    confirmed_at: Optional[datetime]
    calculated_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── IMSGRCScore ─────────────────────────────────────────────────────────────


class GRCScoreCreate(BaseModel):
    domain: str
    cyclus_year: int
    score_pct: Decimal
    components_json: Any
    calculated_at: datetime


class GRCScoreUpdate(BaseModel):
    score_pct: Optional[Decimal] = None
    components_json: Optional[Any] = None


class GRCScoreResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    domain: str
    cyclus_year: int
    score_pct: Decimal
    components_json: Any
    calculated_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
