from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional
from decimal import Decimal


# ── IMSRisk ─────────────────────────────────────────────────────────────────


class RiskCreate(BaseModel):
    scope_id: UUID
    domain: str
    title: str
    description: str
    likelihood: int
    impact: int
    status: str = "open"
    owner_user_id: Optional[UUID] = None
    cyclus_id: Optional[int] = None
    financial_impact_eur: Optional[Decimal] = None
    treatment_decision_id: Optional[UUID] = None


class RiskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    likelihood: Optional[int] = None
    impact: Optional[int] = None
    status: Optional[str] = None
    owner_user_id: Optional[UUID] = None
    cyclus_id: Optional[int] = None
    financial_impact_eur: Optional[Decimal] = None
    treatment_decision_id: Optional[UUID] = None


class RiskResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    scope_id: UUID
    domain: str
    title: str
    description: str
    likelihood: int
    impact: int
    risk_score: int
    financial_impact_eur: Optional[Decimal]
    risk_level: str
    status: str
    owner_user_id: Optional[UUID]
    cyclus_id: Optional[int]
    treatment_decision_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── IMSRiskControlLink ─────────────────────────────────────────────────────


class RiskControlLinkCreate(BaseModel):
    risk_id: UUID
    control_id: UUID


class RiskControlLinkResponse(BaseModel):
    risk_id: UUID
    control_id: UUID

    model_config = {"from_attributes": True}
