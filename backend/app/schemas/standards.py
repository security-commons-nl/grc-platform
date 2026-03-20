from pydantic import BaseModel
from datetime import date, datetime
from uuid import UUID
from typing import Any, Optional
from decimal import Decimal


# ── IMSStandard ─────────────────────────────────────────────────────────────


class StandardCreate(BaseModel):
    name: str
    version: str
    published_at: Optional[date] = None
    status: str
    superseded_by_id: Optional[UUID] = None
    domain: str


class StandardUpdate(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    published_at: Optional[date] = None
    status: Optional[str] = None
    superseded_by_id: Optional[UUID] = None
    domain: Optional[str] = None


class StandardResponse(BaseModel):
    id: UUID
    name: str
    version: str
    published_at: Optional[date]
    status: str
    superseded_by_id: Optional[UUID]
    domain: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── IMSRequirement ──────────────────────────────────────────────────────────


class RequirementCreate(BaseModel):
    standard_id: UUID
    code: str
    title: str
    description: str
    domain: str
    is_mandatory: bool = True


class RequirementUpdate(BaseModel):
    code: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    domain: Optional[str] = None
    is_mandatory: Optional[bool] = None


class RequirementResponse(BaseModel):
    id: UUID
    standard_id: UUID
    code: str
    title: str
    description: str
    domain: str
    is_mandatory: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── IMSRequirementMapping ──────────────────────────────────────────────────


class RequirementMappingCreate(BaseModel):
    source_requirement_id: UUID
    target_requirement_id: UUID
    norm_version_source: str
    confidence_score: Decimal
    created_by: str
    verified: bool = False
    orphaned: bool = False


class RequirementMappingUpdate(BaseModel):
    confidence_score: Optional[Decimal] = None
    verified: Optional[bool] = None
    orphaned: Optional[bool] = None


class RequirementMappingResponse(BaseModel):
    id: UUID
    source_requirement_id: UUID
    target_requirement_id: UUID
    norm_version_source: str
    confidence_score: Decimal
    created_by: str
    verified: bool
    orphaned: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── IMSTenantNormenkader ────────────────────────────────────────────────────


class TenantNormenkaderCreate(BaseModel):
    standard_id: UUID
    adopted_at: date
    is_active: bool = True
    decision_id: Optional[UUID] = None


class TenantNormenkaderUpdate(BaseModel):
    is_active: Optional[bool] = None
    decision_id: Optional[UUID] = None


class TenantNormenkaderResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    standard_id: UUID
    adopted_at: date
    is_active: bool
    decision_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── IMSStandardIngestion ───────────────────────────────────────────────────


class StandardIngestionCreate(BaseModel):
    uploaded_by_user_id: UUID
    source_type: str
    source_path: str
    detected_standard_id: Optional[UUID] = None
    detected_version: Optional[str] = None
    status: str = "parsing"
    parsed_requirements_json: Optional[Any] = None


class StandardIngestionUpdate(BaseModel):
    detected_standard_id: Optional[UUID] = None
    detected_version: Optional[str] = None
    status: Optional[str] = None
    parsed_requirements_json: Optional[Any] = None
    reviewed_at: Optional[datetime] = None
    reviewed_by_user_id: Optional[UUID] = None


class StandardIngestionResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    uploaded_by_user_id: UUID
    source_type: str
    source_path: str
    detected_standard_id: Optional[UUID]
    detected_version: Optional[str]
    status: str
    parsed_requirements_json: Optional[Any]
    reviewed_at: Optional[datetime]
    reviewed_by_user_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
