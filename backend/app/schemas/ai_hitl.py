"""Pydantic schemas voor AI HITL-checkpoints (M4 AI Governance)."""

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel


HITLDecision = Literal["approved", "rejected", "modified", "pending"]


class HITLCheckpointCreate(BaseModel):
    audit_log_id: UUID
    decision: HITLDecision
    reason: Optional[str] = None


class HITLCheckpointResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    audit_log_id: UUID
    reviewer_user_id: UUID
    decision: HITLDecision
    reason: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
