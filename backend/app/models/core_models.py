import enum
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Enums — Domain 1: Platform-breed
# ---------------------------------------------------------------------------


class TenantType(str, enum.Enum):
    centrum = "centrum"
    deelgemeente = "deelgemeente"
    standalone = "standalone"


class TenantRoleEnum(str, enum.Enum):
    admin = "admin"
    process_owner = "process_owner"
    editor = "editor"
    viewer = "viewer"


class RegionRoleEnum(str, enum.Enum):
    region_admin = "region_admin"
    region_viewer = "region_viewer"


class DomainEnum(str, enum.Enum):
    ISMS = "ISMS"
    PIMS = "PIMS"
    BCMS = "BCMS"


class AIFeedbackEnum(str, enum.Enum):
    positive = "positive"
    negative = "negative"
    neutral = "neutral"


# ---------------------------------------------------------------------------
# Enums — Domain 2: Inrichtingsmodus
# ---------------------------------------------------------------------------


class GremiumEnum(str, enum.Enum):
    directie = "directie"
    mt = "mt"
    ciso = "ciso"
    po = "po"
    fg = "fg"
    bcm_coordinator = "bcm_coordinator"
    werkgroep = "werkgroep"
    audit = "audit"


class DependencyTypeEnum(str, enum.Enum):
    B = "B"  # Blokkerend
    W = "W"  # Wenselijk


class StepStatusEnum(str, enum.Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"
    skipped = "skipped"


class DecisionTypeEnum(str, enum.Enum):
    scope = "scope"
    normenkader = "normenkader"
    risicobereidheid = "risicobereidheid"
    behandelkeuze = "behandelkeuze"
    uitzondering = "uitzondering"
    escalatie = "escalatie"
    overig = "overig"


class DocumentTypeEnum(str, enum.Enum):
    beleid = "beleid"
    procedure = "procedure"
    instructie = "instructie"
    rapport = "rapport"
    plan = "plan"
    register = "register"
    overig = "overig"


class VisibilityEnum(str, enum.Enum):
    intern = "intern"
    beperkt = "beperkt"
    openbaar = "openbaar"


class DocumentVersionStatusEnum(str, enum.Enum):
    concept = "concept"
    review = "review"
    vastgesteld = "vastgesteld"
    ingetrokken = "ingetrokken"


class InputDocumentSourceTypeEnum(str, enum.Enum):
    upload = "upload"
    url = "url"
    api = "api"


class InputDocumentStatusEnum(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    processed = "processed"
    failed = "failed"


# ---------------------------------------------------------------------------
# Enums — Domain 3: Normen & mapping
# ---------------------------------------------------------------------------


class StandardStatusEnum(str, enum.Enum):
    draft = "draft"
    active = "active"
    superseded = "superseded"
    withdrawn = "withdrawn"


class MappingCreatedByEnum(str, enum.Enum):
    human = "human"
    ai = "ai"


class IngestionSourceTypeEnum(str, enum.Enum):
    pdf = "pdf"
    url = "url"


class IngestionStatusEnum(str, enum.Enum):
    parsing = "parsing"
    pending_review = "pending_review"
    approved = "approved"
    rejected = "rejected"


# ---------------------------------------------------------------------------
# Enums — Domain 4: GRC-kern
# ---------------------------------------------------------------------------


class ScopeTypeEnum(str, enum.Enum):
    organization = "organization"
    cluster = "cluster"
    process = "process"
    asset = "asset"
    supplier = "supplier"


class RiskStatusEnum(str, enum.Enum):
    identified = "identified"
    assessed = "assessed"
    treated = "treated"
    accepted = "accepted"
    closed = "closed"


class ImplementationStatusEnum(str, enum.Enum):
    not_started = "not_started"
    planned = "planned"
    in_progress = "in_progress"
    implemented = "implemented"
    not_applicable = "not_applicable"


class AssessmentTypeEnum(str, enum.Enum):
    dpia = "dpia"
    pentest = "pentest"
    audit = "audit"
    self_assessment = "self_assessment"
    gap_analysis = "gap_analysis"


class AssessmentStatusEnum(str, enum.Enum):
    planned = "planned"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class FindingSeverityEnum(str, enum.Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"
    informational = "informational"


class FindingStatusEnum(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    accepted = "accepted"
    false_positive = "false_positive"


class ActionStatusEnum(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class EvidenceTypeEnum(str, enum.Enum):
    document = "document"
    screenshot = "screenshot"
    log = "log"
    certificate = "certificate"
    report = "report"
    other = "other"


class IncidentTypeEnum(str, enum.Enum):
    data_breach = "data_breach"
    availability = "availability"
    integrity = "integrity"
    confidentiality = "confidentiality"
    physical = "physical"
    other = "other"


class IncidentSeverityEnum(str, enum.Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class IncidentStatusEnum(str, enum.Enum):
    reported = "reported"
    investigating = "investigating"
    contained = "contained"
    resolved = "resolved"
    closed = "closed"


# ---------------------------------------------------------------------------
# Enums — Domain 5: Scores
# ---------------------------------------------------------------------------


class ExistingRegistersEnum(str, enum.Enum):
    aanwezig = "aanwezig"
    gedeeltelijk = "gedeeltelijk"
    afwezig = "afwezig"


class CoordinationCapacityEnum(str, enum.Enum):
    hoog = "hoog"
    gemiddeld = "gemiddeld"
    laag = "laag"


class LineManagementStructureEnum(str, enum.Enum):
    formeel = "formeel"
    informeel = "informeel"


class RecommendedOptionEnum(str, enum.Enum):
    B = "B"
    C = "C"


class ScoreDomainEnum(str, enum.Enum):
    ISMS = "ISMS"
    PIMS = "PIMS"
    BCMS = "BCMS"
    totaal = "totaal"


# ---------------------------------------------------------------------------
# Enums — Domain 6: RAG-store
# ---------------------------------------------------------------------------


class KnowledgeLayerEnum(str, enum.Enum):
    normatief = "normatief"
    organisatie = "organisatie"


class KnowledgeSourceTypeEnum(str, enum.Enum):
    standard = "standard"
    document = "document"
    decision = "decision"
    policy = "policy"
    finding = "finding"
    other = "other"


# ---------------------------------------------------------------------------
# Domain 1 — Platform-breed
# ---------------------------------------------------------------------------


class Region(Base):
    __tablename__ = "regions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    centrum_tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[TenantType] = mapped_column(
        String(50), nullable=False
    )
    region_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("regions.id"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    external_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class UserTenantRole(Base):
    __tablename__ = "user_tenant_roles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    role: Mapped[TenantRoleEnum] = mapped_column(String(50), nullable=False)
    domain: Mapped[Optional[DomainEnum]] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class UserRegionRole(Base):
    __tablename__ = "user_region_roles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    region_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("regions.id"), nullable=False
    )
    role: Mapped[RegionRoleEnum] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class AIAuditLog(Base):
    __tablename__ = "ai_audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    agent_name: Mapped[str] = mapped_column(Text, nullable=False)
    step_execution_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ims_step_executions.id"), nullable=True
    )
    model: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    langfuse_trace_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    feedback: Mapped[Optional[AIFeedbackEnum]] = mapped_column(String(20), nullable=True)
    feedback_comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


# ---------------------------------------------------------------------------
# Domain 2 — Inrichtingsmodus
# ---------------------------------------------------------------------------


class IMSStep(Base):
    __tablename__ = "ims_steps"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    number: Mapped[str] = mapped_column(String(10), nullable=False)
    phase: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    waarom_nu: Mapped[str] = mapped_column(Text, nullable=False)
    required_gremium: Mapped[GremiumEnum] = mapped_column(String(50), nullable=False)
    is_optional: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    domain: Mapped[Optional[DomainEnum]] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class IMSStepDependency(Base):
    __tablename__ = "ims_step_dependencies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    step_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ims_steps.id"), nullable=False
    )
    depends_on_step_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ims_steps.id"), nullable=False
    )
    dependency_type: Mapped[DependencyTypeEnum] = mapped_column(
        String(1), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class IMSStepExecution(Base):
    __tablename__ = "ims_step_executions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    step_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ims_steps.id"), nullable=False
    )
    cyclus_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[StepStatusEnum] = mapped_column(String(20), nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    skipped: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    skip_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    skip_logged_by: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class IMSDecision(Base):
    """Immutable — no updated_at."""

    __tablename__ = "ims_decisions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    number: Mapped[str] = mapped_column(String(10), nullable=False)
    step_execution_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ims_step_executions.id"), nullable=True
    )
    decision_type: Mapped[DecisionTypeEnum] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    grondslag: Mapped[str] = mapped_column(Text, nullable=False)
    gremium: Mapped[GremiumEnum] = mapped_column(String(50), nullable=False)
    decided_by_name: Mapped[str] = mapped_column(String(200), nullable=False)
    decided_by_role: Mapped[str] = mapped_column(String(200), nullable=False)
    decided_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    valid_until: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    motivation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    alternatives: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    iso_clause: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    supersedes_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ims_decisions.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )


class IMSDocument(Base):
    __tablename__ = "ims_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    step_execution_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ims_step_executions.id"), nullable=True
    )
    document_type: Mapped[DocumentTypeEnum] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[Optional[DomainEnum]] = mapped_column(String(10), nullable=True)
    visibility: Mapped[VisibilityEnum] = mapped_column(String(20), nullable=False)
    withdrawn_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class IMSDocumentVersion(Base):
    """Immutable — no updated_at."""

    __tablename__ = "ims_document_versions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ims_documents.id"), nullable=False
    )
    version_number: Mapped[str] = mapped_column(String(20), nullable=False)
    content_json: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    status: Mapped[DocumentVersionStatusEnum] = mapped_column(
        String(20), nullable=False
    )
    generated_by_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    vastgesteld_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    vastgesteld_by_name: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True
    )
    vastgesteld_by_role: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True
    )
    decision_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ims_decisions.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )


class IMSStepInputDocument(Base):
    __tablename__ = "ims_step_input_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    step_execution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ims_step_executions.id"), nullable=False
    )
    source_type: Mapped[InputDocumentSourceTypeEnum] = mapped_column(
        String(20), nullable=False
    )
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[InputDocumentStatusEnum] = mapped_column(String(20), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    uploaded_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class IMSGapAnalysisResult(Base):
    """Immutable — no updated_at."""

    __tablename__ = "ims_gap_analysis_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    input_document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ims_step_input_documents.id"), nullable=False
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    field_reference: Mapped[str] = mapped_column(Text, nullable=False)
    ai_suggestion: Mapped[str] = mapped_column(Text, nullable=False)
    uncertainty: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    validated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    validated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    validated_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )


# ---------------------------------------------------------------------------
# Domain 3 — Normen & mapping
# ---------------------------------------------------------------------------


class IMSStandard(Base):
    __tablename__ = "ims_standards"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    published_at: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[StandardStatusEnum] = mapped_column(String(20), nullable=False)
    superseded_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ims_standards.id"), nullable=True
    )
    domain: Mapped[DomainEnum] = mapped_column(String(10), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class IMSRequirement(Base):
    __tablename__ = "ims_requirements"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    standard_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ims_standards.id"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[DomainEnum] = mapped_column(String(10), nullable=False)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class IMSRequirementMapping(Base):
    __tablename__ = "ims_requirement_mappings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source_requirement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ims_requirements.id"), nullable=False
    )
    target_requirement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ims_requirements.id"), nullable=False
    )
    norm_version_source: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[Decimal] = mapped_column(
        Numeric(3, 2), nullable=False
    )
    created_by: Mapped[MappingCreatedByEnum] = mapped_column(String(10), nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    orphaned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class IMSTenantNormenkader(Base):
    __tablename__ = "ims_tenant_normenkader"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    standard_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ims_standards.id"), nullable=False
    )
    adopted_at: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    decision_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ims_decisions.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class IMSStandardIngestion(Base):
    __tablename__ = "ims_standard_ingestions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    uploaded_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    source_type: Mapped[IngestionSourceTypeEnum] = mapped_column(
        String(10), nullable=False
    )
    source_path: Mapped[str] = mapped_column(Text, nullable=False)
    detected_standard_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ims_standards.id"), nullable=True
    )
    detected_version: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    status: Mapped[IngestionStatusEnum] = mapped_column(String(20), nullable=False)
    parsed_requirements_json: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reviewed_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


# ---------------------------------------------------------------------------
# Domain 4 — GRC-kern
# ---------------------------------------------------------------------------


class IMSScope(Base):
    __tablename__ = "ims_scopes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    type: Mapped[ScopeTypeEnum] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ims_scopes.id"), nullable=True
    )
    domain: Mapped[Optional[DomainEnum]] = mapped_column(String(10), nullable=True)
    is_critical: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verwerkt_pii: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ext_verwerking_ref: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class IMSRisk(Base):
    __tablename__ = "ims_risks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    scope_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ims_scopes.id"), nullable=False
    )
    domain: Mapped[DomainEnum] = mapped_column(String(10), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    likelihood: Mapped[int] = mapped_column(Integer, nullable=False)
    impact: Mapped[int] = mapped_column(Integer, nullable=False)
    financial_impact_eur: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True
    )
    risk_level: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[RiskStatusEnum] = mapped_column(String(20), nullable=False)
    owner_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    cyclus_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    treatment_decision_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ims_decisions.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class IMSControl(Base):
    __tablename__ = "ims_controls"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    requirement_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ims_requirements.id"), nullable=True
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[DomainEnum] = mapped_column(String(10), nullable=False)
    owner_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    implementation_status: Mapped[ImplementationStatusEnum] = mapped_column(
        String(20), nullable=False
    )
    implementation_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class IMSRiskControlLink(Base):
    """Junction table — composite PK only, no id UUID, no timestamps."""

    __tablename__ = "ims_risk_control_links"

    risk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ims_risks.id"), primary_key=True
    )
    control_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ims_controls.id"), primary_key=True
    )


class IMSAssessment(Base):
    __tablename__ = "ims_assessments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    assessment_type: Mapped[AssessmentTypeEnum] = mapped_column(
        String(30), nullable=False
    )
    scope_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ims_scopes.id"), nullable=True
    )
    domain: Mapped[Optional[DomainEnum]] = mapped_column(String(10), nullable=True)
    planned_at: Mapped[date] = mapped_column(Date, nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[AssessmentStatusEnum] = mapped_column(String(20), nullable=False)
    cyclus_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    document_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ims_documents.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class IMSFinding(Base):
    __tablename__ = "ims_findings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ims_assessments.id"), nullable=False
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[FindingSeverityEnum] = mapped_column(String(20), nullable=False)
    status: Mapped[FindingStatusEnum] = mapped_column(String(20), nullable=False)
    requirement_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ims_requirements.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class IMSCorrectiveAction(Base):
    __tablename__ = "ims_corrective_actions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    finding_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ims_findings.id"), nullable=True
    )
    risk_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ims_risks.id"), nullable=True
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    owner_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[ActionStatusEnum] = mapped_column(String(20), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class IMSEvidence(Base):
    __tablename__ = "ims_evidence"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    control_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ims_controls.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_type: Mapped[EvidenceTypeEnum] = mapped_column(String(20), nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    collected_at: Mapped[date] = mapped_column(Date, nullable=False)
    valid_until: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    collected_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class IMSIncident(Base):
    __tablename__ = "ims_incidents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    incident_type: Mapped[IncidentTypeEnum] = mapped_column(String(30), nullable=False)
    severity: Mapped[IncidentSeverityEnum] = mapped_column(String(20), nullable=False)
    status: Mapped[IncidentStatusEnum] = mapped_column(String(20), nullable=False)
    reported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    external_ticket_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    corrective_action_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ims_corrective_actions.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


# ---------------------------------------------------------------------------
# Domain 5 — Scores
# ---------------------------------------------------------------------------


class IMSMaturityProfile(Base):
    __tablename__ = "ims_maturity_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    domain: Mapped[DomainEnum] = mapped_column(String(10), nullable=False)
    existing_registers: Mapped[ExistingRegistersEnum] = mapped_column(
        String(20), nullable=False
    )
    existing_analyses: Mapped[ExistingRegistersEnum] = mapped_column(
        String(20), nullable=False
    )
    coordination_capacity: Mapped[CoordinationCapacityEnum] = mapped_column(
        String(20), nullable=False
    )
    linemanagement_structure: Mapped[LineManagementStructureEnum] = mapped_column(
        String(20), nullable=False
    )
    recommended_option: Mapped[Optional[RecommendedOptionEnum]] = mapped_column(
        String(1), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class IMSSetupScore(Base):
    __tablename__ = "ims_setup_scores"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    domain: Mapped[ScoreDomainEnum] = mapped_column(String(10), nullable=False)
    cyclus_year: Mapped[int] = mapped_column(Integer, nullable=False)
    score_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    steps_completed: Mapped[int] = mapped_column(Integer, nullable=False)
    steps_total: Mapped[int] = mapped_column(Integer, nullable=False)
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class IMSGRCScore(Base):
    __tablename__ = "ims_grc_scores"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    domain: Mapped[DomainEnum] = mapped_column(String(10), nullable=False)
    cyclus_year: Mapped[int] = mapped_column(Integer, nullable=False)
    score_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    components_json: Mapped[Any] = mapped_column(JSONB, nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


# ---------------------------------------------------------------------------
# Domain 6 — RAG-store
# ---------------------------------------------------------------------------


class IMSKnowledgeChunk(Base):
    __tablename__ = "ims_knowledge_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    layer: Mapped[KnowledgeLayerEnum] = mapped_column(String(20), nullable=False)
    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True
    )
    source_type: Mapped[KnowledgeSourceTypeEnum] = mapped_column(
        String(20), nullable=False
    )
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[Any] = mapped_column(Vector(1536), nullable=False)
    model_used: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
