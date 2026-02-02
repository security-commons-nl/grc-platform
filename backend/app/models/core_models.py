from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from enum import Enum

# --- Layer 1: The Model (Schematic) ---

class FrameworkType(str, Enum):
    BIO = "BIO"
    ISO27001 = "ISO27001"
    AVG = "AVG"
    BCM = "BCM"
    OTHER = "Other"

class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class Status(str, Enum):
    DRAFT = "Draft"
    ACTIVE = "Active"
    DEPRECATED = "Deprecated"
    
class AuditResult(str, Enum):
    PASS = "Pass"
    FAIL = "Fail"
    PARTIAL = "Partial"

# --- Governance Entities (The "What") ---

class Standard(SQLModel, table=True):
    """
    Represents a standard/framework (e.g., BIO 1.04, ISO 27001:2022).
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str # e.g. "BIO"
    version: str # e.g. "1.04"
    type: FrameworkType
    description: Optional[str] = None
    
    requirements: List["Requirement"] = Relationship(back_populates="standard")

class MappingType(str, Enum):
    EQUIVALENT = "Equivalent" # 1:1 Match
    SUBSET = "Subset" # Source covers part of Target
    SUPERSET = "Superset" # Source covers Target + more
    RELATED = "Related" # Loosely related

class RequirementMapping(SQLModel, table=True):
    """
    The Centralized Mapping Table ("Rosetta Stone").
    Links Requirement A (Source) -> Requirement B (Target).
    """
    source_id: Optional[int] = Field(default=None, foreign_key="requirement.id", primary_key=True)
    target_id: Optional[int] = Field(default=None, foreign_key="requirement.id", primary_key=True)
    
    type: MappingType = MappingType.EQUIVALENT
    justification: Optional[str] = None # Why are they mapped? (AI can fill this)
    confidence_score: Optional[float] = None # 0.0 to 1.0 (for AI suggestions)

class Language(str, Enum):
    NL = "nl"
    EN = "en"

class Requirement(SQLModel, table=True):
    """
    Specific text/rule from a Standard (e.g., "BIO 1.2.3: Use MFA").
    This is the Norm/Obligation.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    standard_id: Optional[int] = Field(default=None, foreign_key="standard.id")
    code: str  # e.g., "1.2.3"
    
    # Primary Language (Default)
    title: str 
    description: str # The authoritative text (e.g. Dutch for BIO)
    language: Language = Language.NL
    
    # Secondary Language (Optional Translation)
    title_en: Optional[str] = None
    description_en: Optional[str] = None
    # In future: Use a separate Translation table if we need >2 languages
    
    standard: Optional[Standard] = Relationship(back_populates="requirements")
    measures: List["Measure"] = Relationship(back_populates="requirement")
    
    # Mappings (Outgoing: This requirement maps TO others)
    mappings: List["Requirement"] = Relationship(
        link_model=RequirementMapping,
        sa_relationship_kwargs={
            "primaryjoin": "Requirement.id==RequirementMapping.source_id",
            "secondaryjoin": "Requirement.id==RequirementMapping.target_id",
        }
    )
    
    # Reverse Mappings (Incoming: Others map TO this)
    mapped_by: List["Requirement"] = Relationship(
        link_model=RequirementMapping,
        sa_relationship_kwargs={
            "primaryjoin": "Requirement.id==RequirementMapping.target_id",
            "secondaryjoin": "Requirement.id==RequirementMapping.source_id",
        }
    )

# --- Scope & Asset Management (Shared Core) ---

class ScopeType(str, Enum):
    ORGANIZATION = "Organization"
    PROCESS = "Process"
    ASSET = "Asset"
    SUPPLIER = "Supplier"

class ScopeDependency(SQLModel, table=True):
    """ Many-to-Many link for Scope dependencies """
    depender_id: Optional[int] = Field(default=None, foreign_key="scope.id", primary_key=True)
    provider_id: Optional[int] = Field(default=None, foreign_key="scope.id", primary_key=True)

class ClassificationLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class Scope(SQLModel, table=True):
    """
    The target of governance (Process, Asset, Organization).
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str # e.g. "HR System"
    type: ScopeType = ScopeType.PROCESS
    description: Optional[str] = None
    owner: str # e.g. "Manager HR" (Placeholder for User ID)
    
    # BIA / Classification (BIV: Beschikbaarheid, Integriteit, Vertrouwelijkheid)
    availability_rating: ClassificationLevel = ClassificationLevel.LOW
    integrity_rating: ClassificationLevel = ClassificationLevel.LOW
    confidentiality_rating: ClassificationLevel = ClassificationLevel.LOW

    risks: List["Risk"] = Relationship(back_populates="scope")
    user_roles: List["UserScopeRole"] = Relationship(back_populates="scope")
    incidents: List["Incident"] = Relationship(back_populates="scope")
    exceptions: List["Exception"] = Relationship(back_populates="scope")
    
    # Dependencies: What this scope relies on (e.g. HR System relies on SQL Server)
    dependencies: List["Scope"] = Relationship(
        back_populates="dependents",
        link_model=ScopeDependency,
        sa_relationship_kwargs={
            "primaryjoin": "Scope.id==ScopeDependency.depender_id",
            "secondaryjoin": "Scope.id==ScopeDependency.provider_id"
        }
    )
    # Dependents: What relies on this scope
    dependents: List["Scope"] = Relationship(
        back_populates="dependencies",
        link_model=ScopeDependency,
        sa_relationship_kwargs={
            "primaryjoin": "Scope.id==ScopeDependency.provider_id",
            "secondaryjoin": "Scope.id==ScopeDependency.depender_id"
        }
    )

# --- Incidents & Exceptions (Operational GRC) ---

class Incident(SQLModel, table=True):
    """
    Real-world security incidents or data breaches.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    date_occurred: datetime = Field(default_factory=datetime.utcnow)
    status: Status = Status.ACTIVE # e.g. Open -> Closed
    
    scope_id: Optional[int] = Field(default=None, foreign_key="scope.id")
    scope: Optional[Scope] = Relationship(back_populates="incidents")
    
    # Post-Mortem
    root_cause: Optional[str] = None
    cia_impact: Optional[str] = None # e.g. "Confidentiality"
    
    corrective_actions: List["CorrectiveAction"] = Relationship(back_populates="incident")

class Exception(SQLModel, table=True):
    """
    Formal Waiver / Exemption from a Requirement.
    "We know we are non-compliant, but we accept it until date X."
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    justification: str
    expiration_date: datetime
    status: Status = Status.ACTIVE # Pending -> Active -> Expired
    
    scope_id: Optional[int] = Field(default=None, foreign_key="scope.id")
    requirement_id: Optional[int] = Field(default=None, foreign_key="requirement.id")
    approved_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    
    scope: Optional[Scope] = Relationship(back_populates="exceptions")
    requirement: Optional[Requirement] = Relationship()

# --- Verification (The "Check") ---

# --- Risk Management (The "Plan") ---

class Risk(SQLModel, table=True):
    """
    A potential negative event linked to a Scope.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    scope_id: Optional[int] = Field(default=None, foreign_key="scope.id")
    title: str
    description: str
    inherent_likelihood: RiskLevel
    inherent_impact: RiskLevel
    
    scope: Optional[Scope] = Relationship(back_populates="risks")
    measures: List["MeasureRiskLink"] = Relationship(back_populates="risk")

# --- Implementation (The "Do") ---

class Measure(SQLModel, table=True):
    """
    The actual implementation/control measure (e.g., "YubiKeys for admins").
    This satisfies a Requirement and mitigates a Risk.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    requirement_id: Optional[int] = Field(default=None, foreign_key="requirement.id")
    title: str
    description: str
    status: Status = Status.DRAFT
    
    requirement: Optional[Requirement] = Relationship(back_populates="measures")
    risks: List["MeasureRiskLink"] = Relationship(back_populates="measure")
    evidences: List["Evidence"] = Relationship(back_populates="measure")

class MeasureRiskLink(SQLModel, table=True):
    """ Many-to-Many link between Measure and Risk """
    risk_id: Optional[int] = Field(default=None, foreign_key="risk.id", primary_key=True)
    measure_id: Optional[int] = Field(default=None, foreign_key="measure.id", primary_key=True)
    mitigation_percent: int = 100 
    
    risk: "Risk" = Relationship(back_populates="measures")
    measure: "Measure" = Relationship(back_populates="risks")

# --- Verification (The "Check") ---

class Audit(SQLModel, table=True):
    """
    A point-in-time review event (e.g. "Internal Audit Q1 2026").
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    scope_id: Optional[int] = Field(default=None, foreign_key="scope.id")
    auditor_id: Optional[int] = Field(default=None, foreign_key="user.id")
    date: datetime = Field(default_factory=datetime.utcnow)
    status: Status = Status.ACTIVE # e.g. Planned, In Progress, Completed
    
    findings: List["Finding"] = Relationship(back_populates="audit")
    # In future: link to specific Standard being audited

class Evidence(SQLModel, table=True):
    """ Proof that a measure is working """
    id: Optional[int] = Field(default=None, primary_key=True)
    measure_id: Optional[int] = Field(default=None, foreign_key="measure.id")
    audit_id: Optional[int] = Field(default=None, foreign_key="audit.id") # Optional: Evidence can be specific to an audit
    title: str
    url: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    measure: Optional[Measure] = Relationship(back_populates="evidences")

# --- Improvement (The "Act") ---

class Finding(SQLModel, table=True):
    """ A gap found during Audit or Incident """
    id: Optional[int] = Field(default=None, primary_key=True)
    audit_id: Optional[int] = Field(default=None, foreign_key="audit.id") # Link to the specific Audit event
    title: str
    description: str
    measure_id: Optional[int] = Field(default=None, foreign_key="measure.id") # The broken measure
    
    audit: Optional[Audit] = Relationship(back_populates="findings")
    corrective_actions: List["CorrectiveAction"] = Relationship(back_populates="finding")

class CorrectiveAction(SQLModel, table=True):
    """ The task to fix the Finding """
    id: Optional[int] = Field(default=None, primary_key=True)
    finding_id: Optional[int] = Field(default=None, foreign_key="finding.id")
    incident_id: Optional[int] = Field(default=None, foreign_key="incident.id") # Can also come from incident
    title: str
    due_date: Optional[datetime] = None
    completed: bool = False
    
    finding: Optional[Finding] = Relationship(back_populates="corrective_actions")
    incident: Optional["Incident"] = Relationship(back_populates="corrective_actions")

# --- Identity & Access Management (RBAC) ---

class Theme(str, Enum):
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    email: str = Field(unique=True)
    is_active: bool = True
    is_superuser: bool = False
    
    # Preferences
    theme: Theme = Theme.SYSTEM
    preferred_language: Language = Language.NL
    
    scope_roles: List["UserScopeRole"] = Relationship(back_populates="user")

class Role(str, Enum):
    ADMIN = "Admin" # Can do everything in Scope
    PROCESS_OWNER = "ProcessOwner" # Can Accept Risks in Scope
    EDITOR = "Editor" # Can Edit Measures/Evidence
    VIEWER = "Viewer" # Read Only

class UserScopeRole(SQLModel, table=True):
    """ Link User to Scope with a specific Role """
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    scope_id: Optional[int] = Field(default=None, foreign_key="scope.id")
    role: Role
    
    user: Optional[User] = Relationship(back_populates="scope_roles")
    scope: Optional[Scope] = Relationship(back_populates="user_roles")

# --- Context & Knowledge (The "Brain" for AI/RAG) ---

class PolicyState(str, Enum):
    DRAFT = "Draft"
    REVIEW = "Review"
    APPROVED = "Approved"
    PUBLISHED = "Published"
    ARCHIVED = "Archived"

class Policy(SQLModel, table=True):
    """
    A concrete Policy document (e.g. "Access Control Policy v1").
    Drafted by AI or Human, Approved by Human.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    state: PolicyState = PolicyState.DRAFT
    version: int = 1
    
    created_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    approved_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    
    # Temporal link could go here (effective_date, expiration_date)

class OrganizationContext(SQLModel, table=True):
    """
    High-level context for AI Policy drafting (Mission, Vision, Strategy).
    This serves as the "System Prompt" context for the Organization.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(unique=True) # e.g., "MISSION", "VISION", "RISK_APPETITE_STATEMENT"
    content: str
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class VerificationStatus(str, Enum):
    UNVERIFIED = "Unverified" # Raw transcript
    PENDING_APPROVAL = "Pending Approval" # Sent to user for review
    VERIFIED = "Verified" # User confirmed accuracy
    REJECTED = "Rejected"

class KnowledgeArtifact(SQLModel, table=True):
    """
    Raw inputs for RAG (Documents, Interview Transcripts, Policy Drafts).
    AI Agents (Voice/Doc) deposit information here.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str # distinct from 'vector' (stored via pgvector extension later)
    source_type: str # "INTERVIEW", "UPLOAD", "WEBSITE"
    author_agent: Optional[str] = None # e.g. "VoiceInterviewer_v1"
    
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    verified_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    
    # In future: specific links to Scopes or Risks


class Dashboard(SQLModel, table=True):
    """
    A custom view/dashboard generated by AI based on a user prompt.
    Stores the layout configuration (JSON) to be rendered by the Frontend.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
    
    generation_prompt: str # e.g. "Show me all Critical Risks in the HR System"
    layout_config: str # JSON string: { "widgets": [ { "type": "heatmap", "filter": "HR" } ] }
    
    created_at: datetime = Field(default_factory=datetime.utcnow)



