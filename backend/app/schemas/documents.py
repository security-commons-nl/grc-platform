from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Any, Optional


# ── IMSDocument ─────────────────────────────────────────────────────────────


class DocumentCreate(BaseModel):
    step_execution_id: Optional[UUID] = None
    document_type: str
    title: str
    domain: Optional[str] = None
    visibility: str


class DocumentUpdate(BaseModel):
    document_type: Optional[str] = None
    title: Optional[str] = None
    domain: Optional[str] = None
    visibility: Optional[str] = None
    withdrawn_at: Optional[datetime] = None


class DocumentResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    step_execution_id: Optional[UUID]
    document_type: str
    title: str
    domain: Optional[str]
    visibility: str
    withdrawn_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── IMSDocumentVersion (immutable) ──────────────────────────────────────────


class DocumentVersionCreate(BaseModel):
    document_id: UUID
    version_number: str
    content_json: Optional[Any] = None
    status: str
    generated_by_agent: Optional[str] = None
    created_by_user_id: Optional[UUID] = None
    vastgesteld_at: Optional[datetime] = None
    vastgesteld_by_name: Optional[str] = None
    vastgesteld_by_role: Optional[str] = None
    decision_id: Optional[UUID] = None


class DocumentVersionResponse(BaseModel):
    id: UUID
    document_id: UUID
    version_number: str
    content_json: Optional[Any]
    status: str
    generated_by_agent: Optional[str]
    created_by_user_id: Optional[UUID]
    vastgesteld_at: Optional[datetime]
    vastgesteld_by_name: Optional[str]
    vastgesteld_by_role: Optional[str]
    decision_id: Optional[UUID]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── IMSStepInputDocument ───────────────────────────────────────────────────


class StepInputDocumentCreate(BaseModel):
    step_execution_id: UUID
    source_type: str
    storage_path: str
    status: str
    uploaded_at: datetime
    uploaded_by_user_id: UUID


class StepInputDocumentUpdate(BaseModel):
    status: Optional[str] = None


class StepInputDocumentResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    step_execution_id: UUID
    source_type: str
    storage_path: str
    status: str
    uploaded_at: datetime
    uploaded_by_user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── IMSGapAnalysisResult ───────────────────────────────────────────────────


class GapAnalysisResultCreate(BaseModel):
    input_document_id: UUID
    field_reference: str
    ai_suggestion: str
    uncertainty: bool = False


class GapAnalysisResultValidate(BaseModel):
    validated: bool
    validated_by_user_id: Optional[UUID] = None


class GapAnalysisResultResponse(BaseModel):
    id: UUID
    input_document_id: UUID
    tenant_id: UUID
    field_reference: str
    ai_suggestion: str
    uncertainty: bool
    validated: bool
    validated_at: Optional[datetime]
    validated_by_user_id: Optional[UUID]
    created_at: datetime

    model_config = {"from_attributes": True}
