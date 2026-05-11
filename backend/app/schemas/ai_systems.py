"""Pydantic schemas voor het AI-systemenregister (M4 AI Governance)."""

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel


SystemType = Literal[
    "chatbot",
    "decision_support",
    "content_generation",
    "classification",
    "monitoring",
    "automation",
    "other",
]

# EU AI Act risicocategorieën (verordening 2024/1689 art. 5-7)
EUAIActRisk = Literal[
    "unacceptable",     # Verboden praktijken (art. 5)
    "high",             # Hoog-risico (bijlage III)
    "limited",          # Transparantie-eisen (art. 50)
    "minimal",          # Beperkte verplichtingen
    "not_classified",   # Nog niet beoordeeld
]

# NIST AI RMF kernfuncties — Govern, Map, Measure, Manage
NistAIRMFStatus = Literal["govern", "map", "measure", "manage", "not_started"]

DeploymentStatus = Literal["planned", "building", "deployed", "retired"]


class AISystemBase(BaseModel):
    name: str
    description: Optional[str] = None
    vendor: Optional[str] = None
    system_type: SystemType = "other"
    eu_ai_act_risk: EUAIActRisk = "not_classified"
    nist_ai_rmf_status: NistAIRMFStatus = "not_started"
    deployment_status: DeploymentStatus = "planned"
    responsible_user_id: Optional[UUID] = None
    deployed_at: Optional[datetime] = None


class AISystemCreate(AISystemBase):
    pass


class AISystemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    vendor: Optional[str] = None
    system_type: Optional[SystemType] = None
    eu_ai_act_risk: Optional[EUAIActRisk] = None
    nist_ai_rmf_status: Optional[NistAIRMFStatus] = None
    deployment_status: Optional[DeploymentStatus] = None
    responsible_user_id: Optional[UUID] = None
    deployed_at: Optional[datetime] = None


class AISystemResponse(AISystemBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
