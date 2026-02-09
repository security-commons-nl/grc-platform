from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column
from pgvector.sqlalchemy import Vector
from datetime import datetime
from enum import Enum

# --- Layer 1: The Model (Schematic) ---

# =============================================================================
# ENUMS
# =============================================================================

class FrameworkType(str, Enum):
    BIO = "BIO"
    ISO27001 = "ISO27001"
    AVG = "AVG"
    BCM = "BCM"
    NEN7510 = "NEN7510"
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
    CLOSED = "Closed"

class AuditResult(str, Enum):
    PASS = "Pass"
    FAIL = "Fail"
    PARTIAL = "Partial"
    NOT_ASSESSED = "Not Assessed"

class Language(str, Enum):
    NL = "nl"
    EN = "en"

class TenantRole(str, Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"

class MappingType(str, Enum):
    EQUIVALENT = "Equivalent"
    SUBSET = "Subset"
    SUPERSET = "Superset"
    RELATED = "Related"

class ScopeType(str, Enum):
    ORGANIZATION = "Organization"
    CLUSTER = "Cluster"
    DEPARTMENT = "Department"  # Afdeling - between Cluster and Process
    PROCESS = "Process"
    ASSET = "Asset"
    SUPPLIER = "Supplier"
    VIRTUAL = "Virtual"  # Cross-cutting virtual scope

class ClassificationLevel(str, Enum):
    PUBLIC = "Public"
    INTERNAL = "Internal"
    CONFIDENTIAL = "Confidential"
    SECRET = "Secret"

class AssetType(str, Enum):
    """Type of asset for Scope entries with type=ASSET"""
    HARDWARE = "Hardware"
    SOFTWARE = "Software"
    DATA = "Data"
    PEOPLE = "People"
    FACILITY = "Facility"
    SERVICE = "Service"
    NETWORK = "Network"

class Role(str, Enum):
    """Unified role model based on Three Lines model."""
    BEHEERDER = "Beheerder"          # Platform admin, cross-tenant
    COORDINATOR = "Coordinator"      # 2nd line, cross-tenant, user management
    EIGENAAR = "Eigenaar"            # 1st line, scope-bound, risk acceptance
    MEDEWERKER = "Medewerker"        # 1st line, scope-bound, controls & tasks
    TOEZICHTHOUDER = "Toezichthouder"  # 3rd line, read all + write findings

class TenantRelationshipType(str, Enum):
    """Types of relationships between tenants"""
    SHARED_SERVICES = "Shared Services"  # SSC provides services to consumer
    PARENT_CHILD = "Parent-Child"  # Hierarchical (e.g., Province -> Municipality)
    FEDERATION = "Federation"  # Peer collaboration
    PROCESSOR = "Processor"  # Data processor relationship (AVG)

class Theme(str, Enum):
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"

class PolicyState(str, Enum):
    DRAFT = "Draft"
    REVIEW = "Review"
    APPROVED = "Approved"
    PUBLISHED = "Published"
    ARCHIVED = "Archived"

class VerificationStatus(str, Enum):
    UNVERIFIED = "Unverified"
    PENDING_APPROVAL = "Pending Approval"
    VERIFIED = "Verified"
    REJECTED = "Rejected"

class AssessmentType(str, Enum):
    DPIA = "DPIA"
    PENTEST = "Pentest"
    AUDIT = "Audit"
    SELF_ASSESSMENT = "Self-Assessment"
    COMPLIANCE_JOURNEY = "Compliance Journey"
    BIA = "BIA"
    SUPPLIER_ASSESSMENT = "Supplier Assessment"
    MATURITY_ASSESSMENT = "Maturity Assessment"

class AssessmentPhase(str, Enum):
    """7-phase workflow for assessments"""
    REQUESTED    = "Aangevraagd"
    PLANNING     = "Planning"
    PREPARATION  = "Voorbereiding"
    IN_PROGRESS  = "In uitvoering"
    REVIEW       = "Review"
    REPORTING    = "Rapportage"
    COMPLETED    = "Afgerond"
    CANCELLED    = "Geannuleerd"

class ImplementationStatus(str, Enum):
    """Status of control implementation for Statement of Applicability"""
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    IMPLEMENTED = "Implemented"
    NOT_APPLICABLE = "Not Applicable"

class FindingSeverity(str, Enum):
    """Severity level for audit findings"""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    OBSERVATION = "Observation"

# --- PIMS / AVG Enums ---

class LegalBasis(str, Enum):
    """Legal basis for processing personal data (Art. 6 AVG)"""
    CONSENT = "Toestemming"
    CONTRACT = "Overeenkomst"
    LEGAL_OBLIGATION = "Wettelijke verplichting"
    VITAL_INTEREST = "Vitaal belang"
    PUBLIC_TASK = "Publieke taak"
    LEGITIMATE_INTEREST = "Gerechtvaardigd belang"

class DataSubjectRequestType(str, Enum):
    """Types of data subject requests under GDPR"""
    ACCESS = "Inzage"              # Art. 15
    RECTIFICATION = "Correctie"    # Art. 16
    ERASURE = "Verwijdering"       # Art. 17
    RESTRICTION = "Beperking"      # Art. 18
    PORTABILITY = "Overdraagbaarheid"  # Art. 20
    OBJECTION = "Bezwaar"          # Art. 21

class SpecialDataCategory(str, Enum):
    """Special categories of personal data (Art. 9 AVG)"""
    RACIAL_ETHNIC = "Ras of etnische afkomst"
    POLITICAL = "Politieke opvattingen"
    RELIGIOUS = "Religieuze overtuigingen"
    TRADE_UNION = "Lidmaatschap vakbond"
    GENETIC = "Genetische gegevens"
    BIOMETRIC = "Biometrische gegevens"
    HEALTH = "Gezondheidsgegevens"
    SEXUAL = "Seksueel gedrag of gerichtheid"
    CRIMINAL = "Strafrechtelijke gegevens"

# --- BCMS Enums ---

class PlanType(str, Enum):
    """Types of continuity plans"""
    BCP = "Business Continuity Plan"
    DRP = "Disaster Recovery Plan"
    CRISIS_MANAGEMENT = "Crisismanagementplan"
    COMMUNICATION = "Crisiscommunicatieplan"
    IT_RECOVERY = "IT Herstelplan"
    PANDEMIC = "Pandemieplan"

class TestType(str, Enum):
    """Types of continuity tests"""
    TABLETOP = "Tabletop Exercise"
    WALKTHROUGH = "Walkthrough"
    SIMULATION = "Simulation"
    FULL_TEST = "Full Interruption Test"
    COMPONENT_TEST = "Component Test"

# --- Document & Audit Enums ---

class DocumentType(str, Enum):
    """Types of documents in the system"""
    POLICY = "Beleid"
    PROCEDURE = "Procedure"
    GUIDELINE = "Richtlijn"
    FORM = "Formulier"
    EVIDENCE = "Bewijs"
    CONTRACT = "Contract"
    REPORT = "Rapport"
    STANDARD = "Norm"

class AuditAction(str, Enum):
    """Actions tracked in audit log"""
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    STATUS_CHANGE = "STATUS_CHANGE"
    APPROVE = "APPROVE"
    REJECT = "REJECT"

# --- Notification Enums ---

class NotificationType(str, Enum):
    """Types of notifications"""
    DEADLINE_APPROACHING = "Deadline Approaching"
    DEADLINE_OVERDUE = "Deadline Overdue"
    APPROVAL_NEEDED = "Approval Needed"
    ASSIGNMENT = "Assignment"
    MENTION = "Mention"
    STATUS_CHANGE = "Status Change"
    COMMENT = "Comment"
    REVIEW_DUE = "Review Due"
    DATA_BREACH = "Data Breach"
    INCIDENT = "Incident"

class NotificationPriority(str, Enum):
    """Priority levels for notifications"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"

# --- Assessment Question Enums ---

class QuestionType(str, Enum):
    """Types of assessment questions"""
    YES_NO = "Yes/No"
    YES_NO_NA = "Yes/No/N.A."
    SCALE_1_4 = "Scale 1-4"
    SCALE_1_5 = "Scale 1-5"
    SCALE_1_10 = "Scale 1-10"
    TEXT = "Text"
    MULTIPLE_CHOICE = "Multiple Choice"
    MULTI_SELECT = "Multi Select"
    DATE = "Date"
    FILE_UPLOAD = "File Upload"

# --- Maturity Enums ---

class MaturityLevel(int, Enum):
    """Maturity levels (typically 0-5 based on CMMI)"""
    LEVEL_0_INCOMPLETE = 0
    LEVEL_1_INITIAL = 1
    LEVEL_2_MANAGED = 2
    LEVEL_3_DEFINED = 3
    LEVEL_4_QUANTITATIVELY_MANAGED = 4
    LEVEL_5_OPTIMIZING = 5

class MaturityDomain(str, Enum):
    """Domains for maturity assessment"""
    ISMS = "Information Security"
    PIMS = "Privacy"
    BCMS = "Business Continuity"
    RISK_MANAGEMENT = "Risk Management"
    ASSET_MANAGEMENT = "Asset Management"
    ACCESS_CONTROL = "Access Control"
    CRYPTOGRAPHY = "Cryptography"
    PHYSICAL_SECURITY = "Physical Security"
    OPERATIONS_SECURITY = "Operations Security"
    COMMUNICATIONS_SECURITY = "Communications Security"
    INCIDENT_MANAGEMENT = "Incident Management"
    COMPLIANCE = "Compliance"


# --- MAPGOOD Threat Categories ---

class ThreatCategory(str, Enum):
    """MAPGOOD threat categorization (Dutch standard)"""
    MENSELIJK = "Menselijk falen"  # Human error
    APPLICATIE = "Applicatie/Software falen"  # Application/software failure
    PROCES = "Proces falen"  # Process failure
    GEGEVENS = "Gegevens/Data issues"  # Data issues
    OMGEVING = "Omgeving"  # Environmental (fire, flood, power)
    OPZET = "Opzettelijk handelen"  # Intentional/malicious acts
    DERDEN = "Derden"  # Third parties


class ThreatActorType(str, Enum):
    """Types of threat actors"""
    SCRIPT_KIDDIE = "Script Kiddie"
    HACKTIVIST = "Hacktivist"
    ORGANIZED_CRIME = "Georganiseerde misdaad"
    NATION_STATE = "Natiestaat"
    INSIDER_MALICIOUS = "Kwaadwillende insider"
    INSIDER_NEGLIGENT = "Nalatige insider"
    COMPETITOR = "Concurrent"
    TERRORIST = "Terrorist"
    UNKNOWN = "Onbekend"


class ThreatActorMotivation(str, Enum):
    """Motivations of threat actors"""
    FINANCIAL = "Financieel gewin"
    ESPIONAGE = "Spionage"
    DISRUPTION = "Verstoring"
    IDEOLOGY = "Ideologie"
    REVENGE = "Wraak"
    CURIOSITY = "Nieuwsgierigheid"
    ACCIDENTAL = "Onbedoeld"
    UNKNOWN = "Onbekend"


class IssueType(str, Enum):
    """Types of issues/problems"""
    STRUCTURAL = "Structureel probleem"  # Recurring/systemic
    INCIDENTAL = "Incidenteel"  # One-time occurrence
    COMPLIANCE_GAP = "Compliance gap"  # Gap in compliance
    PROCESS_DEFICIENCY = "Procesdeficiëntie"  # Process weakness
    TECHNICAL_DEBT = "Technische schuld"  # Technical debt


class AttentionQuadrant(str, Enum):
    """
    "In Control" model - determines HOW MUCH attention a risk gets.
    Based on Impact (inherent) vs Vulnerability (residual likelihood after controls).

    Matrix:
                         IMPACT
                    Laag          Hoog
             ┌────────────┬────────────┐
      Hoog   │  MONITOR   │  MITIGATE  │
   Kwets-    │            │            │
   baarheid  ├────────────┼────────────┤
      Laag   │   ACCEPT   │ ASSURANCE  │
             └────────────┴────────────┘
    """
    MITIGATE = "Mitigeren"  # High Impact + High Vulnerability → Active treatment needed
    ASSURANCE = "Zekerheid verkrijgen"  # High Impact + Low Vulnerability → Verify controls work
    MONITOR = "Meten & monitoren"  # Low Impact + High Vulnerability → Track and watch
    ACCEPT = "Accepteren"  # Low Impact + Low Vulnerability → Minimal attention


class MitigationApproach(str, Enum):
    """
    Traditional risk treatment options - used within MITIGATE quadrant.
    Answers: "HOW do we reduce this risk?"
    """
    REDUCE = "Reduceren"  # Implement controls to reduce likelihood/impact
    TRANSFER = "Overdragen"  # Transfer to third party (insurance, outsourcing)
    AVOID = "Vermijden"  # Eliminate the risk source entirely (stop the activity)


class AccessRequestStatus(str, Enum):
    """Status of access requests"""
    PENDING = "Pending"
    APPROVED = "Approved"
    DENIED = "Denied"
    EXPIRED = "Expired"
    REVOKED = "Revoked"


class RiskAppetiteLevel(str, Enum):
    """Risk appetite levels for the organization"""
    AVERSE = "Risicomijdend"  # Avoid risks, only essential activities
    MINIMAL = "Minimaal"  # Very low tolerance, strong controls required
    CAUTIOUS = "Voorzichtig"  # Prefer safe options, limited risk-taking
    MODERATE = "Gematigd"  # Balanced approach, acceptable risks for benefits
    OPEN = "Open"  # Willing to take risks for significant benefits
    HUNGRY = "Risicozoekend"  # Actively seeking high-risk/high-reward opportunities


class ManagementReviewStatus(str, Enum):
    """Status of management reviews"""
    PLANNED = "Gepland"
    IN_PROGRESS = "In uitvoering"
    COMPLETED = "Afgerond"
    CANCELLED = "Geannuleerd"


class PlanningItemType(str, Enum):
    """Types of items in the compliance/audit planning"""
    INTERNAL_AUDIT = "Interne audit"
    EXTERNAL_AUDIT = "Externe audit"
    CERTIFICATION = "Certificering"
    RECERTIFICATION = "Hercertificering"
    MANAGEMENT_REVIEW = "Directiebeoordeling"
    RISK_ASSESSMENT = "Risicobeoordeling"
    BIA = "Business Impact Analyse"
    PENTEST = "Penetratietest"
    COMPLIANCE_CHECK = "Compliance check"
    SUPPLIER_AUDIT = "Leveranciersaudit"
    DPIA = "DPIA"
    OTHER = "Overig"


class InitiativeStatus(str, Enum):
    """Status of improvement initiatives"""
    IDEA = "Idee"
    PROPOSED = "Voorgesteld"
    APPROVED = "Goedgekeurd"
    IN_PROGRESS = "In uitvoering"
    ON_HOLD = "On hold"
    COMPLETED = "Afgerond"
    CANCELLED = "Geannuleerd"


class InitiativePriority(str, Enum):
    """Priority of improvement initiatives"""
    CRITICAL = "Kritiek"
    HIGH = "Hoog"
    MEDIUM = "Middel"
    LOW = "Laag"


class ObjectiveDomain(str, Enum):
    """Domain for security/privacy/BCM objectives"""
    ISMS = "Informatiebeveiliging"
    PIMS = "Privacy"
    BCMS = "Business Continuity"
    INTEGRATED = "Geïntegreerd"


class ObjectiveStatus(str, Enum):
    """Status of an objective"""
    DRAFT = "Concept"
    ACTIVE = "Actief"
    ACHIEVED = "Behaald"
    NOT_ACHIEVED = "Niet behaald"
    CANCELLED = "Geannuleerd"


class KPITrend(str, Enum):
    """Trend direction for KPI"""
    IMPROVING = "Verbeterend"
    STABLE = "Stabiel"
    DECLINING = "Verslechterend"
    UNKNOWN = "Onbekend"


class WorkflowStatus(str, Enum):
    """Status of a workflow instance"""
    NOT_STARTED = "Niet gestart"
    IN_PROGRESS = "In behandeling"
    WAITING_APPROVAL = "Wacht op goedkeuring"
    APPROVED = "Goedgekeurd"
    REJECTED = "Afgewezen"
    COMPLETED = "Afgerond"
    CANCELLED = "Geannuleerd"


class IntegrationStatus(str, Enum):
    """Status of an external integration"""
    ACTIVE = "Actief"
    INACTIVE = "Inactief"
    ERROR = "Fout"
    PENDING_SETUP = "Configuratie nodig"


class ReportFrequency(str, Enum):
    """Frequency for scheduled reports"""
    DAILY = "Dagelijks"
    WEEKLY = "Wekelijks"
    MONTHLY = "Maandelijks"
    QUARTERLY = "Per kwartaal"
    YEARLY = "Jaarlijks"
    ON_DEMAND = "Op aanvraag"


# =============================================================================
# BACKLOG
# =============================================================================

class BacklogType(str, Enum):
    """Type of backlog item"""
    TECHNICAL = "Technisch"
    FUNCTIONAL = "Functioneel"
    PROCESS = "Proces"
    TOOL = "Tooling"
    AI = "Artificial Intelligence"
    OTHER = "Overig"


class BacklogPriority(str, Enum):
    """Priority of backlog item (Admin controlled)"""
    LOW = "Laag"
    MEDIUM = "Middel"
    HIGH = "Hoog"
    CRITICAL = "Kritiek"


class BacklogStatus(str, Enum):
    """Status of backlog item"""
    NEW = "Nieuw"
    REVIEW = "In Review"
    APPROVED = "Goedgekeurd"
    IN_PROGRESS = "In Uitvoering"
    DONE = "Gereed"
    REJECTED = "Afgewezen"


# =============================================================================
# HIAAT 1: BESLUITLOG (Decision Log)
# =============================================================================

class DecisionType(str, Enum):
    """Types of management decisions"""
    RISK_ACCEPTANCE = "Restrisico-acceptatie"
    PRIORITIZATION = "Prioritering"
    DEVIATION = "Afwijking"
    SCOPE_CHANGE = "Scopewijziging"
    POLICY_APPROVAL = "Beleidsgoedkeuring"

class DecisionStatus(str, Enum):
    """Status of a management decision"""
    ACTIVE = "Actief"
    EXPIRED = "Verlopen"
    REVOKED = "Ingetrokken"
    SUPERSEDED = "Vervangen"


# =============================================================================
# HIAAT 2: SCOPE GOVERNANCE
# =============================================================================

class ScopeGovernanceStatus(str, Enum):
    """Governance status of a scope declaration"""
    CONCEPT = "Concept"
    ESTABLISHED = "Vastgesteld"
    EXPIRED = "Verlopen"


# =============================================================================
# HIAAT 3: RISICOKADER (Risk Framework)
# =============================================================================

class RiskFrameworkStatus(str, Enum):
    """Status of a risk framework"""
    DRAFT = "Concept"
    ACTIVE = "Actief"
    ARCHIVED = "Gearchiveerd"


# =============================================================================
# HIAAT 4: BEHANDELSTRATEGIE (Treatment Strategy)
# =============================================================================

class TreatmentStrategy(str, Enum):
    """Mandatory risk treatment strategy"""
    AVOID = "Vermijden"
    REDUCE = "Reduceren"
    TRANSFER = "Overdragen"
    ACCEPT = "Accepteren"


class AcceptanceStatus(str, Enum):
    """Acceptance status for scope-contextualized risk acceptance."""
    PROPOSED = "Voorgesteld"
    ACCEPTED = "Geaccepteerd"
    REJECTED = "Afgewezen"
    EXPIRED = "Verlopen"


# =============================================================================
# HIAAT 5: IN-CONTROL STATUS
# =============================================================================

class InControlLevel(str, Enum):
    """In-control assessment level"""
    IN_CONTROL = "In control"
    LIMITED_CONTROL = "Beperkt in control"
    NOT_IN_CONTROL = "Niet in control"


# =============================================================================
# ORGANIZATION PROFILE ENUMS
# =============================================================================

class OrgType(str, Enum):
    GEMEENTE = "Gemeente"
    PROVINCIE = "Provincie"
    WATERSCHAP = "Waterschap"
    ZBO = "ZBO"
    SSC = "Shared Service Center"
    MINISTERIE = "Ministerie"
    ZORGINSTELLING = "Zorginstelling"
    ONDERWIJSINSTELLING = "Onderwijsinstelling"
    BEDRIJF = "Bedrijf"
    OVERIG = "Overig"

class Sector(str, Enum):
    OVERHEID = "Overheid"
    ZORG = "Zorg"
    ONDERWIJS = "Onderwijs"
    FINANCIEEL = "Financieel"
    IT_DIENSTVERLENING = "IT-dienstverlening"
    TRANSPORT = "Transport"
    ENERGIE = "Energie"
    OVERIG = "Overig"

class EmployeeRange(str, Enum):
    SMALL = "1-50"
    MEDIUM = "51-200"
    LARGE = "201-500"
    ENTERPRISE = "500+"

class GeographicScope(str, Enum):
    LOCAL = "Lokaal"
    REGIONAL = "Regionaal"
    NATIONAL = "Nationaal"
    INTERNATIONAL = "Internationaal"

class CloudStrategy(str, Enum):
    ON_PREMISES = "On-premises"
    HYBRID = "Hybrid"
    CLOUD_FIRST = "Cloud-first"
    FULL_CLOUD = "Full-cloud"

class GovernanceMaturity(str, Enum):
    STARTING = "Startend"
    BASIC = "Basis"
    DEFINED = "Gedefinieerd"
    MANAGED = "Beheerst"
    OPTIMIZED = "Geoptimaliseerd"

class ProfileRiskAppetite(str, Enum):
    LOW = "Laag"
    MEDIUM = "Midden"
    HIGH = "Hoog"

class TrainingFrequency(str, Enum):
    NONE = "Geen"
    YEARLY = "Jaarlijks"
    BIANNUAL = "Halfjaarlijks"
    CONTINUOUS = "Doorlopend"

class MaxDowntime(str, Enum):
    HOURS = "Uren"
    DAY = "Dag"
    WEEK = "Week"

class ProcessingCountRange(str, Enum):
    SMALL = "1-10"
    MEDIUM = "11-50"
    LARGE = "51-100"
    VERY_LARGE = "100+"


# =============================================================================
# HIAAT 6: BELEID-TRACE
# =============================================================================
# (No new enums needed — uses existing PolicyState)


class BacklogItem(SQLModel, table=True):
    """
    Backlog item for improvement requests and ideas.
    Uses User Story format: "Als [rol], wil ik [actie], zodat [doel]"
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: Optional[int] = Field(default=None, foreign_key="tenant.id")

    title: str  # Auto-generated from user story or manual
    description: str  # Legacy field, can be empty for new items
    
    # User Story Format (preferred for new items)
    user_role: Optional[str] = None      # "Als een Process Owner..."
    user_want: Optional[str] = None      # "...wil ik rapportages exporteren..."
    user_so_that: Optional[str] = None   # "...zodat ik aan management kan rapporteren"
    
    item_type: BacklogType = BacklogType.FUNCTIONAL
    priority: BacklogPriority = BacklogPriority.MEDIUM  # Set by admin only
    status: BacklogStatus = BacklogStatus.NEW  # Set by admin only

    # Submitter info
    submitted_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    submitter_name: Optional[str] = None # Cached name for display
    
    # Admin notes
    admin_notes: Optional[str] = None
    
    # Voting/Score (future proofing)
    votes: int = 0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# TENANT (MULTI-TENANCY)
# =============================================================================

class Tenant(SQLModel, table=True):
    """
    Tenant represents an organization (e.g., a municipality) using the platform.
    All data is isolated per tenant.
    """
    id: Optional[int] = Field(default=None, primary_key=True)

    name: str  # "Gemeente Amsterdam"
    slug: str = Field(unique=True)  # "amsterdam" - used in URLs
    display_name: Optional[str] = None

    # Contact info
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    billing_email: Optional[str] = None

    # Address
    address: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    country: str = "NL"

    # Settings (JSON for tenant-specific configuration)
    settings: Optional[str] = None  # JSON: {"default_language": "nl", "features": [...]}

    # Subscription / Licensing
    subscription_tier: Optional[str] = None  # "free", "professional", "enterprise"
    subscription_expires: Optional[datetime] = None
    max_users: Optional[int] = None

    # Tenant type for shared services model
    tenant_type: Optional[str] = None  # "municipality", "province", "ssc", "ministry"
    is_service_provider: bool = False  # Is this a shared service center?

    # Status
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    users: List["TenantUser"] = Relationship(back_populates="tenant")
    scopes: List["Scope"] = Relationship(back_populates="tenant")


class TenantUser(SQLModel, table=True):
    """
    Links Users to Tenants with tenant-level roles.
    A user can belong to multiple tenants.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id")
    user_id: int = Field(foreign_key="user.id")
    role: TenantRole = TenantRole.MEMBER

    # Invitation tracking
    invited_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    invited_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None

    is_default: bool = False  # First membership per user is default
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    tenant: Optional[Tenant] = Relationship(back_populates="users")
    user: Optional["User"] = Relationship(
        back_populates="tenant_memberships",
        sa_relationship_kwargs={"foreign_keys": "[TenantUser.user_id]"}
    )


class TenantRelationship(SQLModel, table=True):
    """
    Models relationships between tenants for shared services.
    E.g., "SSC Bedrijfsvoering" provides services to "Gemeente Amsterdam"
    """
    id: Optional[int] = Field(default=None, primary_key=True)

    # The tenant providing services/controls
    provider_tenant_id: int = Field(foreign_key="tenant.id")
    # The tenant consuming/benefiting from services
    consumer_tenant_id: int = Field(foreign_key="tenant.id")

    relationship_type: TenantRelationshipType = TenantRelationshipType.SHARED_SERVICES

    # Description of the relationship
    name: str  # e.g., "ICT Dienstverlening"
    description: Optional[str] = None

    # Contract/agreement reference
    agreement_reference: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    # What is shared by default
    share_controls: bool = True  # Auto-share controls
    share_scopes: bool = True  # Auto-share scopes (e.g., infrastructure)
    share_assessments: bool = False  # Share assessment results

    # Status
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    provider: Optional[Tenant] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[TenantRelationship.provider_tenant_id]"}
    )
    consumer: Optional[Tenant] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[TenantRelationship.consumer_tenant_id]"}
    )


class SharedControl(SQLModel, table=True):
    """
    Shares a control from one tenant (provider) to others (consumers).
    Enables central controls to be visible in consuming tenants' compliance.
    """
    id: Optional[int] = Field(default=None, primary_key=True)

    # The original control (owned by provider tenant)
    control_id: int = Field(foreign_key="control.id")

    # The tenant receiving/using this shared control
    consumer_tenant_id: int = Field(foreign_key="tenant.id")

    # Optional: specific tenant relationship this falls under
    relationship_id: Optional[int] = Field(default=None, foreign_key="tenantrelationship.id")

    # How this control applies to the consumer
    applicability_notes: Optional[str] = None  # "Applies to all VDI users"

    # Consumer can add local context
    local_notes: Optional[str] = None
    local_contact_id: Optional[int] = Field(default=None, foreign_key="user.id")  # Local responsible person

    # Visibility settings
    visible_in_reports: bool = True  # Show in compliance reports
    visible_in_soa: bool = True  # Show in Statement of Applicability

    # Consumer acknowledgment
    acknowledged: bool = False
    acknowledged_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    acknowledged_at: Optional[datetime] = None

    # Status
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SharedScope(SQLModel, table=True):
    """
    Shares a scope (e.g., central infrastructure) from provider to consumers.
    Enables central assets/processes to be visible in consuming tenants.
    """
    id: Optional[int] = Field(default=None, primary_key=True)

    # The original scope (owned by provider tenant)
    scope_id: int = Field(foreign_key="scope.id")

    # The tenant receiving visibility of this scope
    consumer_tenant_id: int = Field(foreign_key="tenant.id")

    # Optional: specific tenant relationship this falls under
    relationship_id: Optional[int] = Field(default=None, foreign_key="tenantrelationship.id")

    # How this scope applies to the consumer
    usage_description: Optional[str] = None  # "Gebruikt voor email en bestandsopslag"

    # Consumer can have local ownership/contact
    local_owner_id: Optional[int] = Field(default=None, foreign_key="user.id")

    # What the consumer can see
    visibility_level: str = "full"  # "full", "summary", "exists_only"

    # Can consumer's risks link to this scope?
    allow_risk_linking: bool = True

    # Can consumer create local controls for this scope?
    allow_local_controls: bool = True

    # Status
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class VirtualScopeMember(SQLModel, table=True):
    """
    Links scopes to virtual (cross-cutting) scopes.
    E.g., "All systems processing personal data" contains multiple scopes.
    """
    id: Optional[int] = Field(default=None, primary_key=True)

    # The virtual scope (must have type=VIRTUAL)
    virtual_scope_id: int = Field(foreign_key="scope.id")

    # The member scope
    member_scope_id: int = Field(foreign_key="scope.id")

    # Why is this scope a member?
    inclusion_reason: Optional[str] = None  # "Verwerkt persoonsgegevens"

    # Auto-included by rule or manually added?
    auto_included: bool = False
    inclusion_rule: Optional[str] = None  # JSON rule that auto-included this

    created_at: datetime = Field(default_factory=datetime.utcnow)


class AccessRequest(SQLModel, table=True):
    """
    Request for temporary access to view details of shared controls/scopes.
    Default is summary-only; details require explicit permission.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    # Who is requesting
    requester_id: int = Field(foreign_key="user.id")
    requester_tenant_id: int = Field(foreign_key="tenant.id")

    # What are they requesting access to
    entity_type: str  # "Measure", "Scope", "Assessment", "Evidence"
    entity_id: int

    # The tenant that owns the entity
    owner_tenant_id: int = Field(foreign_key="tenant.id")

    # Request details
    reason: str  # Why do they need access?
    access_level: str = "read"  # "read", "read_evidence", "full"

    # Duration
    requested_days: int = 30  # How many days of access requested
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None

    # Approval
    status: AccessRequestStatus = AccessRequestStatus.PENDING
    decided_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    decided_at: Optional[datetime] = None
    decision_reason: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# THREAT & VULNERABILITY CATALOG (MAPGOOD)
# =============================================================================

class ThreatActor(SQLModel, table=True):
    """
    Catalog of threat actors.
    Can be global (tenant_id=NULL) or tenant-specific.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: Optional[int] = Field(default=None, foreign_key="tenant.id")

    name: str  # "Georganiseerde cybercriminelen"
    description: Optional[str] = None

    actor_type: ThreatActorType
    motivation: Optional[ThreatActorMotivation] = None

    # Capability assessment
    capability_level: Optional[RiskLevel] = None  # How sophisticated?
    resources: Optional[str] = None  # "Hoog budget, geavanceerde tools"

    # Targeting
    typical_targets: Optional[str] = None  # "Financiële instellingen, overheid"
    typical_methods: Optional[str] = None  # "Phishing, ransomware"

    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Threat(SQLModel, table=True):
    """
    Catalog of threats (MAPGOOD-based).
    Can be global or tenant-specific.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: Optional[int] = Field(default=None, foreign_key="tenant.id")

    code: Optional[str] = None  # "T-001"
    name: str  # "Ransomware aanval"
    description: Optional[str] = None

    # MAPGOOD category
    category: ThreatCategory

    # Optional link to typical threat actors
    typical_actor_type: Optional[ThreatActorType] = None

    # Impact if realized
    typical_impact: Optional[str] = None  # "Dataverlies, operationele verstoring"
    cia_impact: Optional[str] = None  # "CIA" - which aspects affected

    # Likelihood context
    prevalence: Optional[str] = None  # "Hoog in publieke sector"

    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    vulnerabilities: List["Vulnerability"] = Relationship(back_populates="threat")


class Vulnerability(SQLModel, table=True):
    """
    Catalog of vulnerabilities that threats can exploit.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: Optional[int] = Field(default=None, foreign_key="tenant.id")

    code: Optional[str] = None  # "V-001"
    name: str  # "Ontbrekende MFA"
    description: Optional[str] = None

    # Link to threat this vulnerability enables
    threat_id: Optional[int] = Field(default=None, foreign_key="threat.id")

    # What type of weakness
    vulnerability_type: Optional[str] = None  # "Technical", "Process", "People"

    # How to detect this vulnerability
    detection_method: Optional[str] = None

    # How to remediate
    remediation_guidance: Optional[str] = None

    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    threat: Optional[Threat] = Relationship(back_populates="vulnerabilities")


# =============================================================================
# RISK & MEASURE CATALOGS (Templates)
# =============================================================================

class RiskTemplate(SQLModel, table=True):
    """
    Catalog/template of common risks.
    Global (tenant_id=NULL) or tenant-specific additions.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: Optional[int] = Field(default=None, foreign_key="tenant.id")

    code: Optional[str] = None  # "R-001"
    name: str  # "Ongeautoriseerde toegang tot systemen"
    description: str

    # MAPGOOD links
    threat_id: Optional[int] = Field(default=None, foreign_key="threat.id")
    threat_category: Optional[ThreatCategory] = None

    # Default risk levels (can be adjusted per instance)
    default_likelihood: Optional[RiskLevel] = None
    default_impact: Optional[RiskLevel] = None

    # Which scope types is this risk relevant for?
    applicable_scope_types: Optional[str] = None  # JSON: ["PROCESS", "ASSET"]

    # Suggested measures
    suggested_measure_ids: Optional[str] = None  # JSON: [1, 5, 12]

    # Category for grouping
    risk_category: Optional[str] = None  # "Operationeel", "Compliance"

    # AI-generated?
    ai_generated: bool = False
    ai_confidence: Optional[float] = None

    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Measure(SQLModel, table=True):
    """
    Catalog of reusable, generic measures (maatregelen).
    These are normative building blocks from standards/best practices.
    Context-independent and policy-oriented.

    Example: "Toegang tot informatie wordt beperkt tot geautoriseerde personen."

    Note: Measures are implemented via Controls (context-specific implementations).
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: Optional[int] = Field(default=None, foreign_key="tenant.id")

    code: Optional[str] = None  # "M-001"
    name: str  # "Multi-Factor Authenticatie implementeren"
    description: Optional[str] = None

    # Classification
    control_type: Optional[str] = None  # "Preventive", "Detective", "Corrective"
    automation_level: Optional[str] = None  # "Manual", "Semi-automated", "Automated"

    # Which requirements does this typically cover?
    typical_requirement_ids: Optional[str] = None  # JSON: [1, 5, 12]

    # Which risks does this typically mitigate?
    typical_risk_ids: Optional[str] = None  # JSON: [3, 7]

    # Implementation guidance
    implementation_guidance: Optional[str] = None
    estimated_effort: Optional[str] = None  # "Klein", "Middel", "Groot"

    # Effectiveness
    typical_effectiveness: Optional[int] = None  # 0-100%

    # Category
    measure_category: Optional[str] = None  # "Toegangsbeheer", "Netwerk"

    # AI-generated?
    ai_generated: bool = False
    ai_confidence: Optional[float] = None

    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    control_links: List["ControlMeasureLink"] = Relationship(back_populates="measure")


# =============================================================================
# ISSUE / PROBLEM MANAGEMENT
# =============================================================================

class Issue(SQLModel, table=True):
    """
    Structural issue/problem that groups related findings and incidents.
    When findings or incidents are NOT incidental, they point to an underlying Issue.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    title: str
    description: str

    issue_type: IssueType = IssueType.STRUCTURAL

    # Severity
    severity: FindingSeverity = FindingSeverity.MEDIUM

    # Root cause analysis
    root_cause: Optional[str] = None
    contributing_factors: Optional[str] = None

    # Scope
    scope_id: Optional[int] = Field(default=None, foreign_key="scope.id")

    # Risk link (if this issue represents an unmitigated risk)
    risk_id: Optional[int] = Field(default=None, foreign_key="risk.id")

    # Owner responsible for resolution
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")

    # Status
    status: Status = Status.ACTIVE
    resolved_at: Optional[datetime] = None
    resolved_by_id: Optional[int] = Field(default=None, foreign_key="user.id")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    findings: List["Finding"] = Relationship(back_populates="issue")
    incidents: List["Incident"] = Relationship(back_populates="issue")
    corrective_actions: List["CorrectiveAction"] = Relationship(back_populates="issue")


# =============================================================================
# GAP ANALYSIS (Standard Version Changes)
# =============================================================================

class GapAnalysis(SQLModel, table=True):
    """
    Gap analysis when a new version of a standard is released.
    Compares old version compliance to new version requirements.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    title: str
    description: Optional[str] = None

    # Which standards are being compared
    old_standard_id: int = Field(foreign_key="standard.id")
    new_standard_id: int = Field(foreign_key="standard.id")

    # Scope of analysis
    scope_id: Optional[int] = Field(default=None, foreign_key="scope.id")

    # Analysis results (summary)
    total_old_requirements: int = 0
    total_new_requirements: int = 0
    mapped_requirements: int = 0  # Requirements that map between versions
    new_requirements: int = 0  # Net new in new version
    removed_requirements: int = 0  # Removed from old version

    # Compliance impact
    current_compliance_pct: Optional[float] = None  # Before migration
    projected_compliance_pct: Optional[float] = None  # After migration (based on mappings)
    gap_count: int = 0  # Requirements needing new controls

    # AI analysis
    ai_analysis_summary: Optional[str] = None
    ai_recommendations: Optional[str] = None

    # Status
    status: Status = Status.DRAFT
    completed_at: Optional[datetime] = None
    approved_by_id: Optional[int] = Field(default=None, foreign_key="user.id")

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    gap_items: List["GapAnalysisItem"] = Relationship(back_populates="gap_analysis")


class GapAnalysisItem(SQLModel, table=True):
    """
    Individual item in a gap analysis - one per new requirement.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    gap_analysis_id: int = Field(foreign_key="gapanalysis.id")

    # The new requirement being analyzed
    new_requirement_id: int = Field(foreign_key="requirement.id")

    # Mapped old requirement (if any)
    old_requirement_id: Optional[int] = Field(default=None, foreign_key="requirement.id")

    # Mapping confidence (from RequirementMapping or AI)
    mapping_confidence: Optional[float] = None  # 0.0 to 1.0

    # Current state
    is_covered: bool = False  # Do existing controls cover this?
    existing_control_id: Optional[int] = Field(default=None, foreign_key="control.id")

    # Gap assessment
    has_gap: bool = True
    gap_description: Optional[str] = None
    effort_estimate: Optional[str] = None  # "Klein", "Middel", "Groot"

    # Resolution
    resolution_status: ImplementationStatus = ImplementationStatus.NOT_STARTED
    planned_measure_id: Optional[int] = Field(default=None, foreign_key="measure.id")  # From measure catalog
    notes: Optional[str] = None

    # AI recommendations
    ai_recommendation: Optional[str] = None

    gap_analysis: Optional[GapAnalysis] = Relationship(back_populates="gap_items")


# =============================================================================
# LINK TABLES (Many-to-Many)
# =============================================================================

class RequirementMapping(SQLModel, table=True):
    """
    The Centralized Mapping Table ("Rosetta Stone").
    Links Requirement A (Source) -> Requirement B (Target).
    """
    source_id: Optional[int] = Field(default=None, foreign_key="requirement.id", primary_key=True)
    target_id: Optional[int] = Field(default=None, foreign_key="requirement.id", primary_key=True)

    type: MappingType = MappingType.EQUIVALENT
    justification: Optional[str] = None
    confidence_score: Optional[float] = None  # 0.0 to 1.0 (for AI suggestions)
    
    # Relationships
    source: "Requirement" = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "RequirementMapping.source_id==Requirement.id",
            "foreign_keys": "[RequirementMapping.source_id]"
        }
    )
    target: "Requirement" = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "RequirementMapping.target_id==Requirement.id",
            "foreign_keys": "[RequirementMapping.target_id]"
        }
    )

class ScopeDependency(SQLModel, table=True):
    """Many-to-Many link for Scope dependencies"""
    depender_id: Optional[int] = Field(default=None, foreign_key="scope.id", primary_key=True)
    provider_id: Optional[int] = Field(default=None, foreign_key="scope.id", primary_key=True)

    dependency_type: Optional[str] = None  # "data_flow", "service", "infrastructure"
    criticality: ClassificationLevel = ClassificationLevel.INTERNAL

class ControlRiskLink(SQLModel, table=True):
    """Many-to-Many link between Control and Risk (DEPRECATED: use ControlRiskScopeLink)"""
    risk_id: Optional[int] = Field(default=None, foreign_key="risk.id", primary_key=True)
    control_id: Optional[int] = Field(default=None, foreign_key="control.id", primary_key=True)
    mitigation_percent: int = 100

    risk: "Risk" = Relationship(back_populates="control_links")
    control: "Control" = Relationship(back_populates="risk_links")


class ControlRiskScopeLink(SQLModel, table=True):
    """Links a Control to a scope-contextualized Risk (RiskScope)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)
    control_id: int = Field(foreign_key="control.id", index=True)
    risk_scope_id: int = Field(foreign_key="riskscope.id", index=True)

    mitigation_percent: int = 100

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    control: Optional["Control"] = Relationship(back_populates="risk_scope_links")
    risk_scope: Optional["RiskScope"] = Relationship(back_populates="control_links")


class ControlRequirementLink(SQLModel, table=True):
    """
    Many-to-Many link between Control and Requirement.
    One control can cover multiple requirements (partially or fully).
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    control_id: int = Field(foreign_key="control.id")
    requirement_id: int = Field(foreign_key="requirement.id")

    # How much does this control cover the requirement?
    coverage_percentage: int = 100  # 0-100%

    # Coverage details
    coverage_description: Optional[str] = None  # How does it cover?
    gaps: Optional[str] = None  # What's not covered?

    # AI assessment
    ai_assessed: bool = False
    ai_confidence: Optional[float] = None  # 0.0 to 1.0
    ai_reasoning: Optional[str] = None

    # Status
    is_verified: bool = False
    verified_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    verified_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)


class ControlMeasureLink(SQLModel, table=True):
    """
    Many-to-Many link between Control (implementation) and Measure (catalog).
    A Control can implement multiple Measures, and a Measure can be
    implemented by multiple Controls in different contexts.
    """
    control_id: Optional[int] = Field(default=None, foreign_key="control.id", primary_key=True)
    measure_id: Optional[int] = Field(default=None, foreign_key="measure.id", primary_key=True)

    # How much of the measure does this control implement?
    coverage_percentage: int = 100  # 0-100%

    # Notes about implementation specifics
    notes: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)

    control: "Control" = Relationship(back_populates="measure_links")
    measure: "Measure" = Relationship(back_populates="control_links")


class RiskThreatLink(SQLModel, table=True):
    """Links a specific Risk to Threats and Vulnerabilities"""
    id: Optional[int] = Field(default=None, primary_key=True)
    risk_id: int = Field(foreign_key="risk.id")

    # Threat (from MAPGOOD catalog)
    threat_id: Optional[int] = Field(default=None, foreign_key="threat.id")

    # Vulnerability that enables the threat
    vulnerability_id: Optional[int] = Field(default=None, foreign_key="vulnerability.id")

    # Threat actor (optional)
    threat_actor_id: Optional[int] = Field(default=None, foreign_key="threatactor.id")

    # Likelihood that this threat/vulnerability combination occurs
    likelihood_contribution: Optional[RiskLevel] = None

    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class IncidentControlLink(SQLModel, table=True):
    """
    Many-to-Many link between Incident and Control.
    Tracks which controls failed during an incident (root cause analysis).
    """
    incident_id: Optional[int] = Field(default=None, foreign_key="incident.id", primary_key=True)
    control_id: Optional[int] = Field(default=None, foreign_key="control.id", primary_key=True)

    failure_description: Optional[str] = None  # How the control failed
    contributed_to_incident: bool = True  # Did this control failure contribute?

    created_at: datetime = Field(default_factory=datetime.utcnow)

    incident: "Incident" = Relationship(back_populates="control_links")
    control: "Control" = Relationship(back_populates="incident_links")


class InitiativeObjectiveLink(SQLModel, table=True):
    """
    Many-to-Many link between Initiative and Objective (ISO 27001 6.2 + 10.2).
    Tracks which improvement initiatives contribute to which objectives.
    """
    initiative_id: Optional[int] = Field(default=None, foreign_key="initiative.id", primary_key=True)
    objective_id: Optional[int] = Field(default=None, foreign_key="objective.id", primary_key=True)

    contribution_description: Optional[str] = None  # How does this initiative contribute?

    created_at: datetime = Field(default_factory=datetime.utcnow)

    initiative: "Initiative" = Relationship(back_populates="objective_links")
    objective: "Objective" = Relationship(back_populates="initiative_links")


# =============================================================================
# HIAAT 1: BESLUITLOG (Decision Log)
# =============================================================================

class Decision(SQLModel, table=True):
    """
    Formal management decision (managementbesluit).
    Every significant risk acceptance, prioritization, or deviation
    must be recorded as an auditable decision.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    # Core fields
    decision_type: DecisionType
    decision_text: str
    decision_maker_id: Optional[int] = Field(default=None, foreign_key="user.id")  # management role
    decision_date: datetime = Field(default_factory=datetime.utcnow)

    # Validity
    valid_until: Optional[datetime] = None  # Herijkdatum
    status: DecisionStatus = DecisionStatus.ACTIVE

    # Links (optional — a decision can relate to one or more risks)
    scope_id: Optional[int] = Field(default=None, foreign_key="scope.id")

    # Link to ManagementReview (ISO 27001 9.3.3 - decisions from review)
    management_review_id: Optional[int] = Field(default=None, foreign_key="managementreview.id")

    # Audit trail
    justification: Optional[str] = None
    conditions: Optional[str] = None  # Voorwaarden bij het besluit

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    risk_links: List["DecisionRiskLink"] = Relationship(back_populates="decision")
    risk_scope_links: List["DecisionRiskScopeLink"] = Relationship(back_populates="decision")
    management_review: Optional["ManagementReview"] = Relationship(back_populates="decisions")


class DecisionRiskLink(SQLModel, table=True):
    """Links a Decision to one or more Risks (DEPRECATED: use DecisionRiskScopeLink)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    decision_id: int = Field(foreign_key="decision.id")
    risk_id: int = Field(foreign_key="risk.id")

    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    decision: Optional["Decision"] = Relationship(back_populates="risk_links")


class DecisionRiskScopeLink(SQLModel, table=True):
    """Links a Decision to a scope-contextualized Risk (RiskScope)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)
    decision_id: int = Field(foreign_key="decision.id", index=True)
    risk_scope_id: int = Field(foreign_key="riskscope.id", index=True)

    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    decision: Optional["Decision"] = Relationship(back_populates="risk_scope_links")
    risk_scope: Optional["RiskScope"] = Relationship(back_populates="decision_links")


# =============================================================================
# HIAAT 3: RISICOKADER (Risk Framework)
# =============================================================================

class RiskFramework(SQLModel, table=True):
    """
    Risk framework that defines how risks are assessed.
    Contains impact definitions, likelihood definitions,
    risk tolerance, and decision rules.
    One active framework per tenant/scope at a time.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)
    scope_id: Optional[int] = Field(default=None, foreign_key="scope.id")

    name: str  # e.g. "IMS Risicokader 2025"
    version: int = 1
    status: RiskFrameworkStatus = RiskFrameworkStatus.DRAFT

    # Impact definitions (JSON)
    # {"LOW": {"description": "...", "financial": "< 10k", "cia": "..."}, ...}
    impact_definitions: str  # JSON

    # Likelihood definitions (JSON)
    # {"LOW": {"description": "...", "frequency": "< 1x per 5 jaar"}, ...}
    likelihood_definitions: str  # JSON

    # Risk tolerance / appetite per level
    # {"threshold": "HIGH", "description": "Risks above HIGH require management decision"}
    risk_tolerance: str  # JSON

    # Decision rules
    # {"dt_decision_required_above": 9, "auto_accept_below": 2}
    decision_rules: str  # JSON

    # Ownership
    established_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    established_date: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# HIAAT 5: IN-CONTROL STATUS
# =============================================================================

class InControlAssessment(SQLModel, table=True):
    """
    In-control status per scope, assessed periodically.
    Auto-calculated but must be formally established by management.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)
    scope_id: int = Field(foreign_key="scope.id")

    # Assessment result
    level: InControlLevel = InControlLevel.NOT_IN_CONTROL
    domain: Optional[str] = None  # "ISMS", "PIMS", "BCMS" or None for integrated

    # Supporting data (snapshot at time of assessment)
    open_risks_count: int = 0
    high_risks_count: int = 0
    missing_controls_count: int = 0
    open_findings_count: int = 0
    overdue_actions_count: int = 0

    # Formal assessment
    justification: str  # Motivatie bij "in control"
    assessed_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    established_by_id: Optional[int] = Field(default=None, foreign_key="user.id")  # management
    established_date: Optional[datetime] = None

    # Period
    assessment_date: datetime = Field(default_factory=datetime.utcnow)
    valid_until: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# HIAAT 6: BELEID-TRACE (Policy Principles)
# =============================================================================

class PolicyPrinciple(SQLModel, table=True):
    """
    A normative principle derived from a Policy.
    Creates the traceability chain: Policy → Principle → Risk → Control.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)
    policy_id: int = Field(foreign_key="policy.id")

    code: Optional[str] = None  # e.g. "BP-001"
    title: str
    description: Optional[str] = None

    # Ordering
    order: int = 0

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    policy: Optional["Policy"] = Relationship(back_populates="principles")


# =============================================================================
# GOVERNANCE ENTITIES
# =============================================================================

class Standard(SQLModel, table=True):
    """
    Represents a standard/framework (e.g., BIO 1.04, ISO 27001:2022).
    Standards are shared across tenants (global reference data).
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    version: str
    type: FrameworkType
    description: Optional[str] = None
    effective_date: Optional[datetime] = None

    # If tenant_id is NULL, it's a global standard; otherwise tenant-specific
    tenant_id: Optional[int] = Field(default=None, foreign_key="tenant.id")

    requirements: List["Requirement"] = Relationship(back_populates="standard")
    questions: List["AssessmentQuestion"] = Relationship(back_populates="standard")

class Requirement(SQLModel, table=True):
    """
    Specific text/rule from a Standard (e.g., "BIO 1.2.3: Use MFA").
    This is the Norm/Obligation.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    standard_id: Optional[int] = Field(default=None, foreign_key="standard.id")
    code: str

    title: str
    description: str
    language: Language = Language.NL

    title_en: Optional[str] = None
    description_en: Optional[str] = None

    # Control category for grouping
    category: Optional[str] = None  # e.g., "Access Control", "Cryptography"

    standard: Optional[Standard] = Relationship(back_populates="requirements")
    controls: List["Control"] = Relationship(back_populates="requirement")
    applicability_statements: List["ApplicabilityStatement"] = Relationship(back_populates="requirement")
    questions: List["AssessmentQuestion"] = Relationship(back_populates="requirement")

    # Mappings (Linked via RequirementMapping)
    # We use explicit relationships to the mapping table to access metadata (confidence, justification)
    outgoing_mappings: List["RequirementMapping"] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "Requirement.id==RequirementMapping.source_id",
            "foreign_keys": "[RequirementMapping.source_id]"
        }
    )

    incoming_mappings: List["RequirementMapping"] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "Requirement.id==RequirementMapping.target_id",
            "foreign_keys": "[RequirementMapping.target_id]"
        }
    )


# =============================================================================
# SCOPE & ASSET MANAGEMENT
# =============================================================================

class Scope(SQLModel, table=True):
    """
    The target of governance (Process, Asset, Organization, Supplier).
    Hierarchical: Organization -> Cluster -> Process -> Asset
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)  # REQUIRED for multi-tenancy
    parent_id: Optional[int] = Field(default=None, foreign_key="scope.id")

    name: str
    type: ScopeType = ScopeType.PROCESS
    description: Optional[str] = None
    owner: Optional[str] = None

    accountable_user_id: Optional[int] = Field(default=None, foreign_key="user.id")

    # --- Asset-specific fields (when type=ASSET) ---
    asset_type: Optional[AssetType] = None
    location: Optional[str] = None
    data_classification: Optional[ClassificationLevel] = None

    # --- Supplier-specific fields (when type=SUPPLIER) ---
    vendor_contact_name: Optional[str] = None
    vendor_contact_email: Optional[str] = None
    contract_start_date: Optional[datetime] = None
    contract_end_date: Optional[datetime] = None

    # --- BIA / Classification (BIV) ---
    availability_rating: ClassificationLevel = ClassificationLevel.INTERNAL
    integrity_rating: ClassificationLevel = ClassificationLevel.INTERNAL
    confidentiality_rating: ClassificationLevel = ClassificationLevel.INTERNAL

    # --- BCMS: Recovery Objectives ---
    rto_hours: Optional[int] = None  # Recovery Time Objective
    rpo_hours: Optional[int] = None  # Recovery Point Objective
    mtpd_hours: Optional[int] = None  # Maximum Tolerable Period of Disruption

    # --- Governance (Hiaat 2: Bestuurlijke scope-objecten) ---
    governance_status: Optional[ScopeGovernanceStatus] = None  # Concept / Vastgesteld / Verlopen
    scope_motivation: Optional[str] = None  # Why in/out of scope
    in_scope: bool = True  # True = in scope, False = explicitly out of scope
    validity_year: Optional[int] = None  # e.g. 2025
    established_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    established_date: Optional[datetime] = None

    # --- Shared Services Support ---
    is_shared: bool = False  # Can this scope be shared with consuming tenants?
    shared_with_all_consumers: bool = False  # Auto-share with all related consumers?

    # --- External Integration Sync ---
    external_id: Optional[str] = Field(default=None, index=True)  # ID in external system
    external_source: Optional[str] = None  # "topdesk", "servicenow", "proquro", "bluedolphin"
    last_synced: Optional[datetime] = None  # Last sync timestamp

    # --- Status ---
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tenant: Optional[Tenant] = Relationship(back_populates="scopes")
    risks: List["Risk"] = Relationship(back_populates="scope")
    risk_scopes: List["RiskScope"] = Relationship(back_populates="scope")
    user_roles: List["UserScopeRole"] = Relationship(back_populates="scope")
    incidents: List["Incident"] = Relationship(back_populates="scope")
    exceptions: List["Exception"] = Relationship(back_populates="scope")
    processing_activities: List["ProcessingActivity"] = Relationship(back_populates="scope")
    continuity_plans: List["ContinuityPlan"] = Relationship(back_populates="scope")
    applicability_statements: List["ApplicabilityStatement"] = Relationship(back_populates="scope")
    processor_agreements: List["ProcessorAgreement"] = Relationship(back_populates="supplier")
    documents: List["Document"] = Relationship(back_populates="scope")
    maturity_assessments: List["MaturityAssessment"] = Relationship(back_populates="scope")

    children: List["Scope"] = Relationship(
        sa_relationship_kwargs={
            "cascade": "all",
            "remote_side": "Scope.id"
        }
    )

    dependencies: List["Scope"] = Relationship(
        back_populates="dependents",
        link_model=ScopeDependency,
        sa_relationship_kwargs={
            "primaryjoin": "Scope.id==ScopeDependency.depender_id",
            "secondaryjoin": "Scope.id==ScopeDependency.provider_id"
        }
    )

    dependents: List["Scope"] = Relationship(
        back_populates="dependencies",
        link_model=ScopeDependency,
        sa_relationship_kwargs={
            "primaryjoin": "Scope.id==ScopeDependency.provider_id",
            "secondaryjoin": "Scope.id==ScopeDependency.depender_id"
        }
    )


# =============================================================================
# STATEMENT OF APPLICABILITY (ISMS)
# =============================================================================

class CoverageType(str, Enum):
    """How a requirement is covered in the SoA"""
    LOCAL = "Local"  # Covered by own control
    SHARED = "Shared"  # Covered by shared/central control
    COMBINED = "Combined"  # Both local and shared controls
    NOT_COVERED = "Not Covered"  # Applicable but no control yet
    NOT_APPLICABLE = "Not Applicable"  # Requirement doesn't apply


class ApplicabilityStatement(SQLModel, table=True):
    """
    Statement of Applicability (SoA) - declares which requirements
    are applicable to which scope and why.

    Supports both local and shared (central) controls.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)
    scope_id: int = Field(foreign_key="scope.id")
    requirement_id: int = Field(foreign_key="requirement.id")

    is_applicable: bool = True
    justification: str  # Why applicable or not
    implementation_status: ImplementationStatus = ImplementationStatus.NOT_STARTED

    # --- Coverage Source ---
    coverage_type: CoverageType = CoverageType.NOT_COVERED

    # Local control (owned by this tenant)
    local_control_id: Optional[int] = Field(default=None, foreign_key="control.id")

    # Shared control (from service provider)
    shared_control_id: Optional[int] = Field(default=None, foreign_key="sharedcontrol.id")

    # If shared: which tenant provides this coverage?
    provider_tenant_id: Optional[int] = Field(default=None, foreign_key="tenant.id")

    # --- Local Assessment of Shared Control ---
    # Consumer can assess if the shared control adequately covers their needs
    shared_control_adequate: Optional[bool] = None  # Does the shared control fully cover this?
    local_gap_description: Optional[str] = None  # What gaps exist?
    local_compensating_controls: Optional[str] = None  # Any additional local controls needed?

    # --- Evidence of implementation ---
    implementation_notes: Optional[str] = None
    target_date: Optional[datetime] = None

    # Separate status tracking for local vs shared
    local_status: Optional[ImplementationStatus] = None
    shared_status: Optional[ImplementationStatus] = None

    # --- Review & Sign-off ---
    last_reviewed_at: Optional[datetime] = None
    reviewed_by_id: Optional[int] = Field(default=None, foreign_key="user.id")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    scope: Optional[Scope] = Relationship(back_populates="applicability_statements")
    requirement: Optional[Requirement] = Relationship(back_populates="applicability_statements")
    local_control: Optional["Control"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[ApplicabilityStatement.local_control_id]"}
    )
    shared_control: Optional["SharedControl"] = Relationship()
    provider_tenant: Optional["Tenant"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[ApplicabilityStatement.provider_tenant_id]"}
    )


# =============================================================================
# RISK MANAGEMENT
# =============================================================================

class Risk(SQLModel, table=True):
    """
    A potential negative event linked to a Scope.
    Supports the "In Control" risk management model:
    - Inherent risk (before controls)
    - Residual risk / Vulnerability (after controls)
    - Treatment strategy based on Impact vs Vulnerability matrix
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)
    scope_id: Optional[int] = Field(default=None, foreign_key="scope.id")

    title: str
    description: Optional[str] = None
    risk_category: Optional[str] = None  # e.g., "Operational", "Compliance", "Strategic"

    # From template? (for catalog-based risks)
    template_id: Optional[int] = Field(default=None, foreign_key="risktemplate.id")

    # MAPGOOD threat category
    threat_category: Optional[ThreatCategory] = None

    # Legacy free-text fields (for backward compatibility)
    threat_source: Optional[str] = None
    vulnerability: Optional[str] = None

    # ==========================================================================
    # "IN CONTROL" MODEL - RISK ASSESSMENT
    # ==========================================================================

    # --- Inherent Risk (before controls) ---
    # This is the "raw" risk if no controls were in place
    inherent_likelihood: Optional[RiskLevel] = None
    inherent_impact: Optional[RiskLevel] = None

    # Calculated inherent risk score (1-16 based on 4x4 matrix)
    # LOW=1, MEDIUM=2, HIGH=3, CRITICAL=4 → score = likelihood × impact
    inherent_risk_score: Optional[int] = None

    # --- Residual Risk / Vulnerability (after controls) ---
    # This represents the "Kwetsbaarheid" in the In Control model
    # How vulnerable are we AFTER considering existing controls?
    residual_likelihood: Optional[RiskLevel] = None
    residual_impact: Optional[RiskLevel] = None

    # Calculated residual risk score
    residual_risk_score: Optional[int] = None

    # --- Vulnerability Score ("Kwetsbaarheid") ---
    # Combines residual likelihood with control effectiveness
    # Higher score = more vulnerable = less effective controls
    vulnerability_score: Optional[int] = None  # 0-100, higher = more vulnerable

    # Control effectiveness (aggregated from linked controls)
    control_effectiveness_pct: Optional[int] = None  # 0-100%

    # ==========================================================================
    # ATTENTION STRATEGY (In Control Quadrant)
    # ==========================================================================

    # Which quadrant is this risk in? (based on Impact × Vulnerability)
    # Determines HOW MUCH attention/resources this risk gets
    attention_quadrant: Optional[AttentionQuadrant] = None

    # AI-suggested quadrant (can differ from manual override)
    ai_suggested_quadrant: Optional[AttentionQuadrant] = None

    # ==========================================================================
    # MITIGATION APPROACH (only relevant if quadrant = MITIGATE)
    # ==========================================================================

    # HOW do we treat this risk? (only applicable in MITIGATE quadrant)
    mitigation_approach: Optional[MitigationApproach] = None  # Reduce / Transfer / Avoid

    # Justification for the chosen approach
    treatment_justification: Optional[str] = None

    # ==========================================================================
    # HIAAT 4: BEHANDELSTRATEGIE (mandatory treatment strategy)
    # ==========================================================================
    treatment_strategy: Optional[TreatmentStrategy] = None  # Vermijden/Reduceren/Overdragen/Accepteren
    transfer_party: Optional[str] = None  # Leverancier/verzekeraar (required if strategy=Transfer)

    # ==========================================================================
    # HIAAT 6: BELEID-TRACE (link to policy principle)
    # ==========================================================================
    policy_principle_id: Optional[int] = Field(default=None, foreign_key="policyprinciple.id")

    # Link to ProcessingActivity (ISO 27701 / AVG - privacy risk traceability)
    processing_activity_id: Optional[int] = Field(default=None, foreign_key="processingactivity.id")

    # ==========================================================================
    # RISK ACCEPTANCE
    # ==========================================================================

    risk_accepted: bool = False
    accepted_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    acceptance_date: Optional[datetime] = None
    acceptance_justification: Optional[str] = None

    # Risk appetite threshold - at what level is acceptance allowed?
    risk_appetite_threshold: Optional[RiskLevel] = None

    # ==========================================================================
    # REVIEW & MONITORING
    # ==========================================================================

    last_review_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None

    # Review frequency depends on treatment strategy
    # MITIGATE: frequent (quarterly), ASSURANCE: annual audit, MONITOR: continuous, ACCEPT: rare
    review_frequency_months: Optional[int] = None

    # Is this a "critical risk" that needs management attention?
    is_critical: bool = False

    status: Status = Status.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    scope: Optional[Scope] = Relationship(back_populates="risks")
    control_links: List["ControlRiskLink"] = Relationship(back_populates="risk")
    processing_activity: Optional["ProcessingActivity"] = Relationship(back_populates="risks")
    risk_scopes: List["RiskScope"] = Relationship(back_populates="risk")
    corrective_actions: List["CorrectiveAction"] = Relationship(back_populates="risk")


class RiskScope(SQLModel, table=True):
    """
    Contextualisatie van een generiek Risk binnen een specifieke Scope.
    Bevat scope-specifieke scores, eigenaar, behandelstrategie en acceptatie.
    Eenzelfde Risk kan in meerdere Scopes voorkomen met eigen context.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    risk_id: int = Field(foreign_key="risk.id", index=True)
    scope_id: int = Field(foreign_key="scope.id", index=True)

    # --- Inherent Risk (per scope) ---
    inherent_likelihood: Optional[RiskLevel] = None
    inherent_impact: Optional[RiskLevel] = None
    inherent_risk_score: Optional[int] = None  # 1-16

    # --- Residual Risk (per scope, after controls) ---
    residual_likelihood: Optional[RiskLevel] = None
    residual_impact: Optional[RiskLevel] = None
    residual_risk_score: Optional[int] = None  # 1-16

    # --- Vulnerability & Control Effectiveness ---
    vulnerability_score: Optional[int] = None  # 0-100
    control_effectiveness_pct: Optional[int] = None  # 0-100%

    # --- Attention Strategy (In Control Quadrant) ---
    attention_quadrant: Optional[AttentionQuadrant] = None
    ai_suggested_quadrant: Optional[AttentionQuadrant] = None

    # --- Treatment ---
    mitigation_approach: Optional[MitigationApproach] = None
    treatment_strategy: Optional[TreatmentStrategy] = None
    treatment_justification: Optional[str] = None
    transfer_party: Optional[str] = None

    # --- Governance per scope ---
    owner_user_id: Optional[int] = Field(default=None, foreign_key="user.id")

    # --- Acceptance ---
    acceptance_status: AcceptanceStatus = AcceptanceStatus.PROPOSED
    accepted_by_decision_id: Optional[int] = Field(default=None, foreign_key="decision.id")
    risk_accepted: bool = False
    accepted_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    acceptance_date: Optional[datetime] = None
    acceptance_justification: Optional[str] = None
    risk_appetite_threshold: Optional[RiskLevel] = None

    # --- Review ---
    last_review_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    review_frequency_months: Optional[int] = None
    is_critical: bool = False

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    risk: Optional[Risk] = Relationship(back_populates="risk_scopes")
    scope: Optional["Scope"] = Relationship(back_populates="risk_scopes")
    control_links: List["ControlRiskScopeLink"] = Relationship(back_populates="risk_scope")
    decision_links: List["DecisionRiskScopeLink"] = Relationship(back_populates="risk_scope")


class RiskQuantificationProfile(SQLModel, table=True):
    """
    Configuration for Monte Carlo simulation mappings.
    Maps Qualitative Risk Levels (Low/Med/High/Critical) to Quantitative ranges.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    # Global default mappings
    # Stored as JSON: { "LOW": {"freq_min": 0, "freq_max": 0.5, "impact_min": 0, "impact_max": 1000}, ... }
    global_config: str

    # Category overrides
    # Stored as JSON: { "Legal": { "CRITICAL": {"impact_min": 1000000, "impact_max": 5000000} }, ... }
    category_configs: Optional[str] = None

    currency: str = "EUR"
    iterations: int = 10000  # Default iterations

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# CONTROLS (Context-specific implementations)
# =============================================================================

class Control(SQLModel, table=True):
    """
    Context-specific, testable implementation of measures.
    Tied to a specific scope (organization, process, system).

    Examples:
    - "Azure AD: MFA + Conditional Access" (for Measure: "Implement access control")
    - "YubiKeys for admin accounts in Finance dept"

    NOTE: Controls are testable and can fail. They implement abstract Measures.
    IMS tracks controls but does NOT execute them - execution happens in
    operational systems (TopDesk, Azure AD, etc.)
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)
    scope_id: Optional[int] = Field(default=None, foreign_key="scope.id")

    # Legacy single requirement link (use ControlRequirementLink for many-to-many)
    requirement_id: Optional[int] = Field(default=None, foreign_key="requirement.id")

    title: str
    description: Optional[str] = None

    # Control type classification
    control_type: Optional[str] = None  # "Preventive", "Detective", "Corrective"
    automation_level: Optional[str] = None  # "Manual", "Semi-automated", "Automated"

    status: Status = Status.DRAFT
    implementation_date: Optional[datetime] = None

    # Effectiveness (testable!)
    last_tested: Optional[datetime] = None
    test_result: Optional[AuditResult] = None
    effectiveness_percentage: Optional[int] = None  # 0-100%

    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")

    # --- External System Integration ---
    # Where is this control actually managed/executed?
    external_system: Optional[str] = None  # e.g., "TopDesk", "Azure AD", "ServiceNow"
    external_reference: Optional[str] = None  # e.g., "CHG-12345", "Policy-001"
    external_url: Optional[str] = None  # Direct link to item in external system

    # --- Shared Services Support ---
    is_shared: bool = False  # Can this control be shared with other tenants?
    shared_with_all_consumers: bool = False  # Auto-share with all related consumers?
    share_evidence: bool = True  # Include evidence when sharing?

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    requirement: Optional[Requirement] = Relationship(back_populates="controls")
    risk_links: List["ControlRiskLink"] = Relationship(back_populates="control")
    risk_scope_links: List["ControlRiskScopeLink"] = Relationship(back_populates="control")
    evidences: List["Evidence"] = Relationship(back_populates="control")
    measure_links: List["ControlMeasureLink"] = Relationship(back_populates="control")
    incident_links: List["IncidentControlLink"] = Relationship(back_populates="control")
    corrective_actions: List["CorrectiveAction"] = Relationship(
        back_populates="control",
        sa_relationship_kwargs={"foreign_keys": "[CorrectiveAction.control_id]"},
    )


# =============================================================================
# INCIDENTS & EXCEPTIONS
# =============================================================================

class Incident(SQLModel, table=True):
    """
    Real-world security incidents or data breaches.
    Extended with GDPR data breach fields.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    title: str
    description: Optional[str] = None
    date_occurred: datetime = Field(default_factory=datetime.utcnow)
    date_detected: Optional[datetime] = None
    date_resolved: Optional[datetime] = None
    status: Status = Status.ACTIVE

    scope_id: Optional[int] = Field(default=None, foreign_key="scope.id")
    reported_by_id: Optional[int] = Field(default=None, foreign_key="user.id")

    # Classification
    incident_type: Optional[str] = None  # "Security", "Privacy", "Availability"
    severity: FindingSeverity = FindingSeverity.MEDIUM

    # Impact Assessment
    cia_impact: Optional[str] = None  # "Confidentiality", "Integrity", "Availability"
    business_impact: Optional[str] = None

    # Root Cause Analysis
    root_cause: Optional[str] = None
    contributing_factors: Optional[str] = None

    # --- AVG / Data Breach Specific Fields ---
    is_data_breach: bool = False
    data_subjects_affected: Optional[int] = None
    personal_data_categories: Optional[str] = None  # What data was breached
    special_categories_involved: bool = False

    # Notification to Authority (Art. 33 AVG)
    notified_to_authority: bool = False
    authority_notification_date: Optional[datetime] = None
    authority_notification_deadline: Optional[datetime] = None  # 72 hours from detection
    authority_reference: Optional[str] = None  # Reference number from AP

    # Notification to Data Subjects (Art. 34 AVG)
    notified_to_subjects: bool = False
    subject_notification_date: Optional[datetime] = None
    subject_notification_method: Optional[str] = None

    # Is this incidental or part of a structural issue?
    is_incidental: bool = True  # True = one-off, False = structural problem
    issue_id: Optional[int] = Field(default=None, foreign_key="issue.id")  # Link to Issue if structural

    # Link to ContinuityPlan (ISO 22301 8.4.4 - which plan was activated)
    continuity_plan_id: Optional[int] = Field(default=None, foreign_key="continuityplan.id")

    # Link to ProcessingActivity (AVG Art. 33/34 - which processing was affected in data breach)
    processing_activity_id: Optional[int] = Field(default=None, foreign_key="processingactivity.id")

    # --- External System Integration ---
    # Where is this incident tracked operationally?
    external_system: Optional[str] = None  # e.g., "TopDesk", "ServiceNow"
    external_reference: Optional[str] = None  # e.g., "INC-12345"
    external_id: Optional[str] = Field(default=None, index=True)  # Unique ID in external system
    external_source: Optional[str] = None  # "topdesk", "servicenow" (lowercase for consistency)
    last_synced: Optional[datetime] = None  # Last sync timestamp
    external_url: Optional[str] = None  # Direct link to incident ticket

    # Relationships
    scope: Optional[Scope] = Relationship(back_populates="incidents")
    corrective_actions: List["CorrectiveAction"] = Relationship(back_populates="incident")
    issue: Optional["Issue"] = Relationship(back_populates="incidents")
    continuity_plan: Optional["ContinuityPlan"] = Relationship(back_populates="incidents")
    processing_activity: Optional["ProcessingActivity"] = Relationship(back_populates="incidents")
    control_links: List["IncidentControlLink"] = Relationship(back_populates="incident")


class Exception(SQLModel, table=True):
    """
    Formal Waiver / Exemption from a Requirement.
    "We know we are non-compliant, but we accept it until date X."
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    title: str
    justification: str

    # Risk acceptance for the exception
    accepted_risk_level: RiskLevel = RiskLevel.LOW
    compensating_controls: Optional[str] = None

    # Timeline
    request_date: datetime = Field(default_factory=datetime.utcnow)
    approval_date: Optional[datetime] = None
    expiration_date: datetime

    status: Status = Status.DRAFT  # Draft -> Active -> Expired

    scope_id: Optional[int] = Field(default=None, foreign_key="scope.id")
    requirement_id: Optional[int] = Field(default=None, foreign_key="requirement.id")
    requested_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    approved_by_id: Optional[int] = Field(default=None, foreign_key="user.id")

    # Link to Risk (ISO 27001 - exception = risk acceptance)
    risk_id: Optional[int] = Field(default=None, foreign_key="risk.id")

    scope: Optional[Scope] = Relationship(back_populates="exceptions")
    requirement: Optional[Requirement] = Relationship()


# =============================================================================
# VERIFICATION (ASSESSMENTS)
# =============================================================================

class Assessment(SQLModel, table=True):
    """
    A generic "Traject" or "Campaign" to verify compliance.
    Supports DPIA, Audits, Pentests, Self-Assessments, etc.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    title: str
    description: Optional[str] = None
    type: AssessmentType = AssessmentType.SELF_ASSESSMENT

    # Timeline
    start_date: datetime = Field(default_factory=datetime.utcnow)
    deadline: Optional[datetime] = None
    completed_date: Optional[datetime] = None

    status: Status = Status.ACTIVE

    scope_id: Optional[int] = Field(default=None, foreign_key="scope.id")
    standard_id: Optional[int] = Field(default=None, foreign_key="standard.id")

    # Link to ProcessingActivity (AVG Art. 35 - for DPIA assessments)
    processing_activity_id: Optional[int] = Field(default=None, foreign_key="processingactivity.id")

    # Team
    lead_assessor_id: Optional[int] = Field(default=None, foreign_key="user.id")
    external_assessor: Optional[str] = None  # For external audits

    # Workflow
    phase: Optional[str] = Field(default="Aangevraagd")
    methodology: Optional[str] = None
    next_assessment_date: Optional[datetime] = None

    # Results
    overall_result: Optional[AuditResult] = None
    executive_summary: Optional[str] = None

    # BIA Snapshot (populated when type=BIA and phase=Afgerond)
    bia_cia_label: Optional[str] = None       # e.g. "C3-I2-A4"
    bia_rto_hours: Optional[int] = None
    bia_rpo_hours: Optional[int] = None
    bia_mtpd_hours: Optional[int] = None
    bia_bcp_required: Optional[bool] = None

    lead_assessor: Optional["User"] = Relationship(back_populates="assessments_led")
    findings: List["Finding"] = Relationship(back_populates="assessment")
    standard: Optional["Standard"] = Relationship()
    responses: List["AssessmentResponse"] = Relationship(back_populates="assessment")
    processing_activity: Optional["ProcessingActivity"] = Relationship(back_populates="assessments")
    continuity_tests: List["ContinuityTest"] = Relationship(back_populates="assessment")


class Evidence(SQLModel, table=True):
    """Proof that a control is working"""
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)
    control_id: Optional[int] = Field(default=None, foreign_key="control.id")
    assessment_id: Optional[int] = Field(default=None, foreign_key="assessment.id")

    title: str
    description: Optional[str] = None
    evidence_type: Optional[str] = None  # "Screenshot", "Log", "Report", "Config"

    url: Optional[str] = None
    file_path: Optional[str] = None

    collected_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # AI Analysis
    ai_analysis: Optional[str] = None
    ai_result: Optional[AuditResult] = None

    control: Optional[Control] = Relationship(back_populates="evidences")


# =============================================================================
# ASSESSMENT QUESTIONS & RESPONSES (CHECKLISTS)
# =============================================================================

class AssessmentQuestion(SQLModel, table=True):
    """
    Questions/checklist items for assessments.
    Can be linked to a Standard (global) or created per-tenant.
    """
    id: Optional[int] = Field(default=None, primary_key=True)

    # If tenant_id is NULL, it's a global question template
    tenant_id: Optional[int] = Field(default=None, foreign_key="tenant.id")

    # Link to standard/requirement (optional)
    standard_id: Optional[int] = Field(default=None, foreign_key="standard.id")
    requirement_id: Optional[int] = Field(default=None, foreign_key="requirement.id")

    # Question content
    code: Optional[str] = None  # e.g., "BIO-1.2.3-Q1"
    question_text: str
    question_text_en: Optional[str] = None

    # Help text / guidance
    guidance: Optional[str] = None
    guidance_en: Optional[str] = None

    # Question type
    question_type: QuestionType = QuestionType.YES_NO
    options: Optional[str] = None  # JSON for multiple choice options

    # Ordering & Grouping
    category: Optional[str] = None  # Section/category name
    section: Optional[str] = None  # Sub-section
    order: int = 0

    # Scoring
    weight: float = 1.0  # Weight for scoring
    passing_answer: Optional[str] = None  # What constitutes a "pass"

    # Status
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    standard: Optional[Standard] = Relationship(back_populates="questions")
    requirement: Optional[Requirement] = Relationship(back_populates="questions")
    responses: List["AssessmentResponse"] = Relationship(back_populates="question")


class AssessmentResponse(SQLModel, table=True):
    """
    Response to an assessment question within a specific assessment.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    assessment_id: int = Field(foreign_key="assessment.id")
    question_id: int = Field(foreign_key="assessmentquestion.id")

    # Response value
    response_value: Optional[str] = None  # The actual answer
    response_text: Optional[str] = None  # Additional notes/explanation

    # Assessment result
    result: Optional[AuditResult] = None  # Pass/Fail/Partial
    score: Optional[float] = None  # Calculated score

    # Evidence link
    evidence_id: Optional[int] = Field(default=None, foreign_key="evidence.id")

    # Who & When
    assessed_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    assessed_at: Optional[datetime] = None

    # Review
    reviewed_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    assessment: Optional[Assessment] = Relationship(back_populates="responses")
    question: Optional[AssessmentQuestion] = Relationship(back_populates="responses")


# =============================================================================
# BIA THRESHOLD CONFIGURATION
# =============================================================================

class BIAThreshold(SQLModel, table=True):
    """Configurable BIA score → CIA/RTO/RPO mapping per tenant."""
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: Optional[int] = Field(default=None, foreign_key="tenant.id")  # NULL = global default

    score: int                              # 1, 2, 3 or 4
    label: str                              # "Laag", "Midden", "Hoog", "Kritiek"
    classification_level: str               # "Public", "Internal", "Confidential", "Secret"
    rto_hours: int                          # Recovery Time Objective in hours
    rpo_hours: int                          # Recovery Point Objective in hours
    mtpd_hours: int                         # Max Tolerable Period of Disruption in hours
    rto_label: str                          # "< 1 week", "< 24 uur", etc.
    rpo_label: str                          # "< 24 uur", "< 4 uur", etc.
    plan_required: bool                     # Continuity plan mandatory?
    plan_label: Optional[str] = None        # "Nee", "Basis BCP", "Uitgebreid BCP", "Full DR Plan"


# =============================================================================
# IMPROVEMENT (FINDINGS & ACTIONS)
# =============================================================================

class Finding(SQLModel, table=True):
    """A gap found during an Assessment or Incident"""
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)
    assessment_id: Optional[int] = Field(default=None, foreign_key="assessment.id")

    title: str
    description: str
    severity: FindingSeverity = FindingSeverity.MEDIUM

    # What's affected
    control_id: Optional[int] = Field(default=None, foreign_key="control.id")
    requirement_id: Optional[int] = Field(default=None, foreign_key="requirement.id")

    # Is this incidental or part of a structural issue?
    is_incidental: bool = True  # True = one-off, False = structural problem
    issue_id: Optional[int] = Field(default=None, foreign_key="issue.id")  # Link to Issue if structural

    # Evidence of the finding
    evidence: Optional[str] = None

    # Recommendation
    recommendation: Optional[str] = None

    status: Status = Status.ACTIVE
    found_date: datetime = Field(default_factory=datetime.utcnow)

    assessment: Optional[Assessment] = Relationship(back_populates="findings")
    corrective_actions: List["CorrectiveAction"] = Relationship(back_populates="finding")
    issue: Optional["Issue"] = Relationship(back_populates="findings")


class CorrectiveAction(SQLModel, table=True):
    """The task to fix the Finding, Incident, or Issue"""
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    # Can be linked to Finding, Incident, Issue, Initiative, Risk, or Control
    finding_id: Optional[int] = Field(default=None, foreign_key="finding.id")
    incident_id: Optional[int] = Field(default=None, foreign_key="incident.id")
    issue_id: Optional[int] = Field(default=None, foreign_key="issue.id")
    initiative_id: Optional[int] = Field(default=None, foreign_key="initiative.id")
    risk_id: Optional[int] = Field(default=None, foreign_key="risk.id")
    control_id: Optional[int] = Field(default=None, foreign_key="control.id")

    title: str
    description: Optional[str] = None

    # What type of action
    action_type: Optional[str] = None  # "Preventive", "Corrective", "Detective"

    # Assignment
    assigned_to_id: Optional[int] = Field(default=None, foreign_key="user.id")

    # Timeline
    due_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None

    # Status
    completed: bool = False
    verified: bool = False
    verified_by_id: Optional[int] = Field(default=None, foreign_key="user.id")

    # Priority
    priority: FindingSeverity = FindingSeverity.MEDIUM

    # Result
    result_notes: Optional[str] = None
    control_created_id: Optional[int] = Field(default=None, foreign_key="control.id")  # If action resulted in new control

    # --- External System Integration ---
    # Where is this action actually being executed?
    external_system: Optional[str] = None  # e.g., "TopDesk", "Azure DevOps"
    external_reference: Optional[str] = None  # e.g., "INC-67890", "TASK-123"
    external_url: Optional[str] = None  # Direct link to ticket/task in external system

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    finding: Optional[Finding] = Relationship(back_populates="corrective_actions")
    incident: Optional["Incident"] = Relationship(back_populates="corrective_actions")
    issue: Optional["Issue"] = Relationship(back_populates="corrective_actions")
    initiative: Optional["Initiative"] = Relationship(back_populates="corrective_actions")
    risk: Optional["Risk"] = Relationship(back_populates="corrective_actions")
    control: Optional["Control"] = Relationship(
        back_populates="corrective_actions",
        sa_relationship_kwargs={"foreign_keys": "[CorrectiveAction.control_id]"},
    )


# =============================================================================
# PIMS / AVG - PROCESSING ACTIVITIES (Art. 30)
# =============================================================================

class ProcessingActivity(SQLModel, table=True):
    """
    Register of Processing Activities (Art. 30 AVG).
    Mandatory documentation of all personal data processing.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)
    scope_id: int = Field(foreign_key="scope.id")

    name: str  # e.g., "Salarisadministratie"
    purpose: str  # Processing purpose

    # Legal basis (Art. 6 AVG)
    legal_basis: LegalBasis
    legal_basis_specification: Optional[str] = None  # e.g., specific law or legitimate interest

    # Data subjects
    data_subject_categories: str  # e.g., "Medewerkers, sollicitanten"

    # Personal data categories
    personal_data_categories: str  # e.g., "NAW, BSN, salaris"
    special_categories: bool = False
    special_categories_types: Optional[str] = None  # Which special categories
    special_categories_basis: Optional[str] = None  # Legal basis for special categories

    # Recipients
    recipients: Optional[str] = None  # Internal and external recipients
    recipient_categories: Optional[str] = None

    # International transfers
    third_country_transfer: bool = False
    transfer_countries: Optional[str] = None
    transfer_safeguards: Optional[str] = None  # SCCs, adequacy decision, BCRs

    # Retention
    retention_period: str  # e.g., "7 jaar na einde dienstverband"
    retention_criteria: Optional[str] = None

    # Security measures reference
    security_description: Optional[str] = None

    # Source of data
    data_source: Optional[str] = None  # "Betrokkene zelf", "Derde partij"

    # Automated decision making
    automated_decision_making: bool = False
    automated_decision_description: Optional[str] = None

    # DPIA required?
    dpia_required: bool = False
    dpia_reference: Optional[str] = None

    # Status
    status: Status = Status.ACTIVE
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
    last_review_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    scope: Optional[Scope] = Relationship(back_populates="processing_activities")
    processor_agreements: List["ProcessorAgreement"] = Relationship(back_populates="processing_activity")
    risks: List["Risk"] = Relationship(back_populates="processing_activity")
    assessments: List["Assessment"] = Relationship(back_populates="processing_activity")
    incidents: List["Incident"] = Relationship(back_populates="processing_activity")


class DataSubjectRequest(SQLModel, table=True):
    """
    Data Subject Requests under GDPR (Art. 15-22).
    Track and manage requests from data subjects.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    request_type: DataSubjectRequestType

    # Requester information
    requester_name: str
    requester_email: str
    requester_phone: Optional[str] = None

    # Identity verification
    identity_verified: bool = False
    verification_method: Optional[str] = None
    verification_date: Optional[datetime] = None

    # Request details
    request_details: str
    scope_id: Optional[int] = Field(default=None, foreign_key="scope.id")

    # Timeline (Art. 12: response within 1 month)
    received_date: datetime = Field(default_factory=datetime.utcnow)
    deadline: datetime  # 1 month from received_date
    extended_deadline: Optional[datetime] = None  # Can extend by 2 months
    extension_reason: Optional[str] = None

    # Processing
    status: Status = Status.ACTIVE
    handled_by_id: Optional[int] = Field(default=None, foreign_key="user.id")

    # Response
    response_date: Optional[datetime] = None
    response: Optional[str] = None
    response_method: Optional[str] = None

    # If refused
    refusal_reason: Optional[str] = None

    # Notes
    internal_notes: Optional[str] = None


class ProcessorAgreement(SQLModel, table=True):
    """
    Processor Agreements (Art. 28 AVG).
    Contracts with suppliers who process personal data.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    supplier_id: int = Field(foreign_key="scope.id")  # Scope with type=SUPPLIER
    processing_activity_id: Optional[int] = Field(default=None, foreign_key="processingactivity.id")

    title: str
    description: Optional[str] = None

    # Contract details
    signed_date: Optional[datetime] = None
    effective_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None

    # Key terms
    processing_description: str  # What processing is authorized
    subprocessors_allowed: bool = False
    subprocessor_list: Optional[str] = None

    # Security requirements
    security_requirements: Optional[str] = None
    audit_rights: bool = True

    # Data handling
    data_return_deletion: Optional[str] = None  # What happens at contract end
    breach_notification_hours: int = 24  # Hours to notify of breach

    # Document reference
    document_url: Optional[str] = None

    # Status
    status: Status = Status.ACTIVE
    last_review_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None

    supplier: Optional[Scope] = Relationship(back_populates="processor_agreements")
    processing_activity: Optional[ProcessingActivity] = Relationship(back_populates="processor_agreements")


# =============================================================================
# BCMS - CONTINUITY MANAGEMENT
# =============================================================================

class ContinuityPlan(SQLModel, table=True):
    """
    Business Continuity Plans linked to Scopes.
    Includes BCP, DRP, Crisis Management plans.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)
    scope_id: int = Field(foreign_key="scope.id")

    title: str
    plan_type: PlanType
    description: Optional[str] = None

    # Content (or reference to document)
    content: Optional[str] = None
    document_url: Optional[str] = None

    version: int = 1
    status: PolicyState = PolicyState.DRAFT

    # Ownership
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")

    # Activation criteria
    activation_triggers: Optional[str] = None
    activation_authority: Optional[str] = None

    # Key contacts
    crisis_team: Optional[str] = None  # JSON or comma-separated

    # Review & Testing
    last_tested: Optional[datetime] = None
    last_review_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    scope: Optional[Scope] = Relationship(back_populates="continuity_plans")
    tests: List["ContinuityTest"] = Relationship(back_populates="plan")
    incidents: List["Incident"] = Relationship(back_populates="continuity_plan")


class ContinuityTest(SQLModel, table=True):
    """
    Tests and exercises of continuity plans.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)
    plan_id: int = Field(foreign_key="continuityplan.id")

    title: str
    test_type: TestType

    # Planning
    scheduled_date: datetime
    actual_date: Optional[datetime] = None

    # Execution
    scenario: str  # What was tested
    participants: Optional[str] = None
    duration_hours: Optional[float] = None

    # Results
    status: Status = Status.DRAFT  # Planned -> Active -> Completed
    objectives_met: Optional[bool] = None
    results_summary: Optional[str] = None

    # Lessons learned
    lessons_learned: Optional[str] = None
    improvements_identified: Optional[str] = None

    # Follow-up
    next_test_date: Optional[datetime] = None

    # Link to Assessment (ISO 22301 8.5 + 10.1 - test results feed PDCA via findings)
    assessment_id: Optional[int] = Field(default=None, foreign_key="assessment.id")

    plan: Optional[ContinuityPlan] = Relationship(back_populates="tests")
    assessment: Optional["Assessment"] = Relationship(back_populates="continuity_tests")


# =============================================================================
# DOCUMENT MANAGEMENT
# =============================================================================

class Document(SQLModel, table=True):
    """
    Generic document management for policies, procedures, evidence, etc.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    title: str
    description: Optional[str] = None
    document_type: DocumentType

    # File reference
    file_url: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None

    # Version control
    version: int = 1
    version_notes: Optional[str] = None

    # Status & Workflow
    status: PolicyState = PolicyState.DRAFT

    # Ownership
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
    created_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    approved_by_id: Optional[int] = Field(default=None, foreign_key="user.id")

    # Links
    scope_id: Optional[int] = Field(default=None, foreign_key="scope.id")
    requirement_id: Optional[int] = Field(default=None, foreign_key="requirement.id")

    # Review cycle
    effective_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    review_date: Optional[datetime] = None

    # Classification
    classification: ClassificationLevel = ClassificationLevel.INTERNAL

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    scope: Optional[Scope] = Relationship(back_populates="documents")


# =============================================================================
# RISK APPETITE (Organizational Level)
# =============================================================================

class RiskAppetite(SQLModel, table=True):
    """
    Risk appetite definition at organizational (tenant) level.
    Defines how much risk the organization is willing to accept per domain.

    This is a key input for the "In Control" model:
    - Determines thresholds for when risks need treatment
    - Guides the treatment_strategy selection
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    # Overall organizational risk appetite
    overall_appetite: RiskAppetiteLevel = RiskAppetiteLevel.CAUTIOUS

    # Domain-specific appetites (can differ per domain)
    # Information Security
    isms_appetite: Optional[RiskAppetiteLevel] = None
    isms_description: Optional[str] = None

    # Privacy
    pims_appetite: Optional[RiskAppetiteLevel] = None
    pims_description: Optional[str] = None

    # Business Continuity
    bcms_appetite: Optional[RiskAppetiteLevel] = None
    bcms_description: Optional[str] = None

    # Financial risks
    financial_appetite: Optional[RiskAppetiteLevel] = None
    financial_description: Optional[str] = None

    # Reputational risks
    reputational_appetite: Optional[RiskAppetiteLevel] = None
    reputational_description: Optional[str] = None

    # Compliance/Legal risks
    compliance_appetite: Optional[RiskAppetiteLevel] = None
    compliance_description: Optional[str] = None

    # Thresholds for risk acceptance
    # Below this level, risks can be accepted without escalation
    auto_accept_threshold: RiskLevel = RiskLevel.LOW

    # Above this level, risks MUST be escalated to management
    escalation_threshold: RiskLevel = RiskLevel.HIGH

    # Maximum acceptable residual risk score (1-16)
    max_acceptable_risk_score: int = 6

    # Impact correlation per category (JSON)
    # Maps RiskLevel to financial/quantitative ranges for dynamic heatmap thresholds
    # Structure: {"financial": {"LOW": 10000, "MEDIUM": 100000, "HIGH": 500000, "CRITICAL": 1000000},
    #             "legal": {...}, "reputation": {...}, "operational": {...}}
    impact_correlation: Optional[str] = None  # JSON

    # Financial threshold value (€) - the appetite expressed as max acceptable single-event loss
    financial_threshold_value: Optional[int] = None  # e.g. 50000 = €50k

    # General risk appetite statement (for policies/documentation)
    appetite_statement: Optional[str] = None

    # Approval
    approved_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    approved_at: Optional[datetime] = None

    # Validity
    effective_date: datetime = Field(default_factory=datetime.utcnow)
    next_review_date: Optional[datetime] = None

    # Version control
    version: int = 1
    is_current: bool = True  # Only one should be current per tenant

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# MANAGEMENT REVIEW (ISO Requirement)
# =============================================================================

class ManagementReview(SQLModel, table=True):
    """
    Management Review / Directiebeoordeling.
    Required by ISO 27001 (9.3), ISO 22301 (9.3), and other standards.

    Periodic review by top management of the management system's
    performance, adequacy, and effectiveness.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    title: str  # e.g., "Directiebeoordeling Q4 2024"
    description: Optional[str] = None

    # Which domains are covered?
    covers_isms: bool = True
    covers_pims: bool = True
    covers_bcms: bool = True

    # Meeting details
    meeting_date: datetime
    attendees: Optional[str] = None  # JSON array or comma-separated
    chair_id: Optional[int] = Field(default=None, foreign_key="user.id")
    minutes_url: Optional[str] = None  # Link to meeting minutes

    # Status
    status: ManagementReviewStatus = ManagementReviewStatus.PLANNED

    # ==========================================================================
    # INPUT ITEMS (ISO 27001 9.3.2)
    # ==========================================================================

    # a) Status of actions from previous reviews
    previous_actions_status: Optional[str] = None

    # b) Changes in external and internal issues
    context_changes: Optional[str] = None

    # c) Feedback on information security performance:
    # - Nonconformities and corrective actions
    nonconformities_summary: Optional[str] = None
    open_findings_count: Optional[int] = None
    closed_findings_count: Optional[int] = None

    # - Monitoring and measurement results
    kpi_summary: Optional[str] = None

    # - Audit results
    audit_results_summary: Optional[str] = None

    # - Fulfilment of objectives
    objectives_status: Optional[str] = None

    # d) Feedback from interested parties
    stakeholder_feedback: Optional[str] = None

    # e) Results of risk assessment and treatment plan status
    risk_assessment_summary: Optional[str] = None
    risk_treatment_status: Optional[str] = None
    critical_risks_count: Optional[int] = None

    # f) Opportunities for continual improvement
    improvement_opportunities: Optional[str] = None

    # Incident summary
    incidents_summary: Optional[str] = None
    incidents_count: Optional[int] = None
    data_breaches_count: Optional[int] = None

    # ==========================================================================
    # OUTPUT / DECISIONS (ISO 27001 9.3.3)
    # ==========================================================================

    # Decisions and actions related to:
    # - Continual improvement opportunities
    improvement_decisions: Optional[str] = None

    # - Any needs for changes to the management system
    system_change_decisions: Optional[str] = None

    # - Resource needs
    resource_decisions: Optional[str] = None

    # Overall conclusions
    conclusions: Optional[str] = None

    # Overall assessment of management system effectiveness
    system_effectiveness: Optional[str] = None  # "Effective", "Partially Effective", "Not Effective"

    # ==========================================================================
    # FOLLOW-UP
    # ==========================================================================

    # Actions arising from this review
    action_items: Optional[str] = None  # JSON array of action items

    # Next review
    next_review_date: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    initiatives: List["Initiative"] = Relationship(back_populates="management_review")
    decisions: List["Decision"] = Relationship(back_populates="management_review")


# =============================================================================
# COMPLIANCE/AUDIT PLANNING (Jaarplanning)
# =============================================================================

class CompliancePlanningItem(SQLModel, table=True):
    """
    Compliance and Audit Planning / Jaarplanning.
    Central calendar for all planned compliance activities:
    - Internal audits
    - External audits
    - Certifications
    - Risk assessments
    - Pentests
    - Management reviews
    - etc.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    # Planning item details
    title: str
    description: Optional[str] = None
    item_type: PlanningItemType

    # Which standard/framework is this for?
    standard_id: Optional[int] = Field(default=None, foreign_key="standard.id")

    # Scope of the activity
    scope_id: Optional[int] = Field(default=None, foreign_key="scope.id")
    scope_description: Optional[str] = None  # Or free text if broader

    # Planning year
    planning_year: int  # e.g., 2024

    # Timing
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None

    # Frequency (for recurring items)
    is_recurring: bool = False
    recurrence_months: Optional[int] = None  # Every X months

    # Responsibility
    responsible_id: Optional[int] = Field(default=None, foreign_key="user.id")
    responsible_team: Optional[str] = None

    # External party (for external audits)
    external_party: Optional[str] = None  # e.g., "KPMG", "Deloitte"
    external_contact: Optional[str] = None

    # Budget/Cost (optional)
    estimated_days: Optional[float] = None
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None

    # Status
    status: Status = Status.DRAFT  # Draft, Active (planned), Closed (completed)

    # Link to resulting assessment (when executed)
    assessment_id: Optional[int] = Field(default=None, foreign_key="assessment.id")

    # Link to management review (if applicable)
    management_review_id: Optional[int] = Field(default=None, foreign_key="managementreview.id")

    # Notes
    notes: Optional[str] = None
    lessons_learned: Optional[str] = None

    # Approval (for the planning)
    approved_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    approved_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# IMPROVEMENT INITIATIVES / VERBETERPROJECTEN
# =============================================================================

class Initiative(SQLModel, table=True):
    """
    Improvement Initiatives / Verbeterprojecten.
    Larger improvement efforts that go beyond single corrective actions.

    Examples:
    - "Implementatie MFA voor alle medewerkers"
    - "Migratie naar nieuwe backup-oplossing"
    - "ISO 27001 certificeringstraject"
    - "Privacy by Design implementatie"

    Can bundle multiple CorrectiveActions and link to Risks/Findings.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    # Initiative details
    title: str
    description: str
    business_case: Optional[str] = None  # Why is this initiative needed?

    # Classification
    initiative_type: Optional[str] = None  # "Security", "Privacy", "BCM", "Compliance", "Operational"
    priority: InitiativePriority = InitiativePriority.MEDIUM

    # Which domains does this improve?
    improves_isms: bool = False
    improves_pims: bool = False
    improves_bcms: bool = False

    # Status
    status: InitiativeStatus = InitiativeStatus.IDEA

    # Ownership
    sponsor_id: Optional[int] = Field(default=None, foreign_key="user.id")  # Executive sponsor
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")  # Day-to-day owner
    team_members: Optional[str] = None  # JSON array of user IDs

    # Timeline
    proposed_date: Optional[datetime] = None
    approved_date: Optional[datetime] = None
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None

    # Progress tracking
    progress_percentage: int = 0  # 0-100%
    progress_notes: Optional[str] = None
    last_status_update: Optional[datetime] = None

    # Scope
    scope_id: Optional[int] = Field(default=None, foreign_key="scope.id")

    # Links to what triggered this initiative
    # Could come from: Management Review, Audit Finding, Risk, Incident
    management_review_id: Optional[int] = Field(default=None, foreign_key="managementreview.id")
    risk_id: Optional[int] = Field(default=None, foreign_key="risk.id")
    finding_id: Optional[int] = Field(default=None, foreign_key="finding.id")
    incident_id: Optional[int] = Field(default=None, foreign_key="incident.id")

    # Expected outcomes
    expected_outcomes: Optional[str] = None
    success_criteria: Optional[str] = None

    # Risks and dependencies
    risks_and_dependencies: Optional[str] = None

    # Resources
    estimated_effort_days: Optional[float] = None
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None

    # Results (when completed)
    actual_outcomes: Optional[str] = None
    lessons_learned: Optional[str] = None

    # --- External System Integration ---
    # Where is this initiative/project actually managed?
    external_system: Optional[str] = None  # e.g., "MS Project", "TopDesk", "Azure DevOps"
    external_reference: Optional[str] = None  # e.g., "PRJ-001", "CHG-456"
    external_url: Optional[str] = None  # Direct link to project in external system

    # Review
    next_review_date: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    management_review: Optional[ManagementReview] = Relationship(back_populates="initiatives")
    milestones: List["InitiativeMilestone"] = Relationship(back_populates="initiative")
    corrective_actions: List["CorrectiveAction"] = Relationship(back_populates="initiative")
    objective_links: List["InitiativeObjectiveLink"] = Relationship(back_populates="initiative")


class InitiativeMilestone(SQLModel, table=True):
    """
    Milestones within an Initiative.
    Tracks key deliverables and checkpoints.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    initiative_id: int = Field(foreign_key="initiative.id")

    title: str
    description: Optional[str] = None

    # Timeline
    planned_date: datetime
    actual_date: Optional[datetime] = None

    # Status
    is_completed: bool = False
    completed_by_id: Optional[int] = Field(default=None, foreign_key="user.id")

    # Deliverables
    deliverables: Optional[str] = None
    evidence_url: Optional[str] = None

    # Order
    sequence: int = 0

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    initiative: Optional[Initiative] = Relationship(back_populates="milestones")


# =============================================================================
# REVIEW SCHEDULING
# =============================================================================

class ReviewSchedule(SQLModel, table=True):
    """
    Recurring reviews and deadlines for any entity.
    Enables calendar-based compliance management.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    # What is being reviewed
    entity_type: str  # "Policy", "Risk", "ContinuityPlan", "ProcessingActivity"
    entity_id: int

    title: str
    description: Optional[str] = None

    # Schedule
    frequency_months: int  # Review every X months
    last_review: Optional[datetime] = None
    next_review: datetime

    # Assignment
    responsible_id: int = Field(foreign_key="user.id")

    # Notification
    reminder_days_before: int = 14  # Days before next_review to send reminder

    # Status
    is_active: bool = True

    created_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# AUDIT TRAIL
# =============================================================================

class AuditLog(SQLModel, table=True):
    """
    Comprehensive audit trail for all changes.
    Who changed what, when, and what were the values.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    # What changed
    entity_type: str  # "Risk", "Measure", "Incident", etc.
    entity_id: int

    # What happened
    action: AuditAction
    field_name: Optional[str] = None  # Specific field if UPDATE

    # Values
    old_value: Optional[str] = None  # JSON for complex values
    new_value: Optional[str] = None

    # Who & When
    changed_by_id: int = Field(foreign_key="user.id")
    changed_at: datetime = Field(default_factory=datetime.utcnow)

    # Context
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None

    # Additional context
    reason: Optional[str] = None  # Why the change was made


# =============================================================================
# NOTIFICATIONS
# =============================================================================

class Notification(SQLModel, table=True):
    """
    Notifications for users about deadlines, assignments, approvals, etc.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    # Recipient
    recipient_id: int = Field(foreign_key="user.id")

    # Notification type & priority
    notification_type: NotificationType
    priority: NotificationPriority = NotificationPriority.MEDIUM

    # Content
    title: str
    message: str
    action_url: Optional[str] = None  # Link to relevant page

    # Reference to related entity (polymorphic)
    entity_type: Optional[str] = None  # "Risk", "Assessment", "Incident", etc.
    entity_id: Optional[int] = None

    # Status
    is_read: bool = False
    read_at: Optional[datetime] = None

    is_dismissed: bool = False
    dismissed_at: Optional[datetime] = None

    # Email notification
    email_sent: bool = False
    email_sent_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None  # Auto-dismiss after this date

    # Relationships
    recipient: Optional["User"] = Relationship(back_populates="notifications")


# =============================================================================
# COMMENTS (POLYMORPHIC)
# =============================================================================

class Comment(SQLModel, table=True):
    """
    Comments/discussion on any entity.
    Polymorphic design using entity_type and entity_id.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    # What is being commented on (polymorphic reference)
    entity_type: str  # "Risk", "Incident", "Finding", "Assessment", etc.
    entity_id: int

    # Comment content
    content: str

    # Author
    author_id: int = Field(foreign_key="user.id")

    # Threading (for replies)
    parent_id: Optional[int] = Field(default=None, foreign_key="comment.id")

    # Mentions (JSON array of user IDs)
    mentions: Optional[str] = None  # JSON: [1, 5, 12]

    # Edit tracking
    is_edited: bool = False
    edited_at: Optional[datetime] = None

    # Status
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    author: Optional["User"] = Relationship(back_populates="comments")
    replies: List["Comment"] = Relationship(
        sa_relationship_kwargs={
            "cascade": "all",
            "remote_side": "Comment.id"
        }
    )


# =============================================================================
# ATTACHMENTS (POLYMORPHIC)
# =============================================================================

class Attachment(SQLModel, table=True):
    """
    File attachments for any entity.
    Polymorphic design using entity_type and entity_id.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    # What is this attached to (polymorphic reference)
    entity_type: str  # "Incident", "Finding", "Risk", "Assessment", etc.
    entity_id: int

    # File information
    file_name: str
    file_path: str  # Storage path
    file_url: Optional[str] = None  # Public URL if available
    file_size: int  # Bytes
    mime_type: str

    # Metadata
    title: Optional[str] = None  # Display name (if different from file_name)
    description: Optional[str] = None

    # Classification
    classification: ClassificationLevel = ClassificationLevel.INTERNAL

    # Upload info
    uploaded_by_id: int = Field(foreign_key="user.id")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

    # Virus scan (if applicable)
    scan_status: Optional[str] = None  # "pending", "clean", "infected"
    scanned_at: Optional[datetime] = None

    # Status
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by_id: Optional[int] = Field(default=None, foreign_key="user.id")


# =============================================================================
# MATURITY ASSESSMENT
# =============================================================================

class MaturityAssessment(SQLModel, table=True):
    """
    Maturity assessment for tracking progress over time.
    Can be at tenant level (overall) or scope level (specific area).
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    # Optional scope (if NULL, it's a tenant-wide assessment)
    scope_id: Optional[int] = Field(default=None, foreign_key="scope.id")

    title: str
    description: Optional[str] = None

    # Assessment period
    assessment_date: datetime = Field(default_factory=datetime.utcnow)
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None

    # Overall scores
    overall_current_level: Optional[MaturityLevel] = None
    overall_target_level: Optional[MaturityLevel] = None

    # Assessor
    assessed_by_id: Optional[int] = Field(default=None, foreign_key="user.id")

    # Status
    status: Status = Status.DRAFT

    # Notes
    executive_summary: Optional[str] = None
    methodology: Optional[str] = None  # e.g., "CMMI", "ISO 27001 Maturity"

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    scope: Optional[Scope] = Relationship(back_populates="maturity_assessments")
    domain_scores: List["MaturityDomainScore"] = Relationship(back_populates="assessment")


class MaturityDomainScore(SQLModel, table=True):
    """
    Maturity scores per domain within an assessment.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    assessment_id: int = Field(foreign_key="maturityassessment.id")

    # Domain being assessed
    domain: MaturityDomain

    # Scores
    current_level: MaturityLevel
    target_level: MaturityLevel

    # Gap analysis
    gap: int = 0  # target_level - current_level
    priority: FindingSeverity = FindingSeverity.MEDIUM

    # Evidence / Justification
    justification: Optional[str] = None
    evidence_summary: Optional[str] = None

    # Improvement recommendations
    recommendations: Optional[str] = None

    # Relationships
    assessment: Optional[MaturityAssessment] = Relationship(back_populates="domain_scores")


# =============================================================================
# IDENTITY & ACCESS MANAGEMENT
# =============================================================================

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    email: str = Field(unique=True)
    full_name: Optional[str] = None

    password_hash: Optional[str] = Field(default=None, exclude=True)

    is_active: bool = True
    is_superuser: bool = False  # Platform-wide superuser (not tenant-specific)

    # External identity
    external_id: Optional[str] = None  # For SSO integration

    # Contact
    phone: Optional[str] = None
    department: Optional[str] = None
    job_title: Optional[str] = None

    # Preferences
    theme: Theme = Theme.SYSTEM
    preferred_language: Language = Language.NL

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    # Relationships
    tenant_memberships: List["TenantUser"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "[TenantUser.user_id]"}
    )
    scope_roles: List["UserScopeRole"] = Relationship(back_populates="user")
    assessments_led: List["Assessment"] = Relationship(back_populates="lead_assessor")
    notifications: List["Notification"] = Relationship(back_populates="recipient")
    comments: List["Comment"] = Relationship(back_populates="author")


class UserRead(SQLModel):
    """User response schema — excludes password_hash."""
    id: Optional[int] = None
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    external_id: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    job_title: Optional[str] = None
    theme: Theme = Theme.SYSTEM
    preferred_language: Language = Language.NL
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None


class UserScopeRole(SQLModel, table=True):
    """Link User to Scope with a specific Role"""
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    scope_id: Optional[int] = Field(default=None, foreign_key="scope.id")
    role: Role

    # Validity period (optional)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None

    user: Optional[User] = Relationship(back_populates="scope_roles")
    scope: Optional[Scope] = Relationship(back_populates="user_roles")


# =============================================================================
# AI / KNOWLEDGE MANAGEMENT
# =============================================================================

class Policy(SQLModel, table=True):
    """
    A concrete Policy document (e.g. "Access Control Policy v1").
    Drafted by AI or Human, Approved by Human.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    title: str
    content: Optional[str] = None
    state: PolicyState = PolicyState.DRAFT
    version: int = 1

    # Links
    scope_id: Optional[int] = Field(default=None, foreign_key="scope.id")
    requirement_id: Optional[int] = Field(default=None, foreign_key="requirement.id")

    # Ownership
    created_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    approved_by_id: Optional[int] = Field(default=None, foreign_key="user.id")

    # Timeline
    effective_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    review_date: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Hiaat 6: Policy Principles relationship
    principles: List["PolicyPrinciple"] = Relationship(back_populates="policy")


class OrganizationContext(SQLModel, table=True):
    """
    High-level context for AI Policy drafting (Mission, Vision, Strategy).
    This serves as the "System Prompt" context for the Organization.
    TENANT-SPECIFIC knowledge.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    key: str  # e.g., "MISSION", "VISION", "RISK_APPETITE"
    content: str

    category: Optional[str] = None  # "Strategy", "Risk Appetite", "Culture"

    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by_id: Optional[int] = Field(default=None, foreign_key="user.id")


class OrganizationProfile(SQLModel, table=True):
    """
    Structured organization profile for onboarding and AI context.
    One record per tenant. All fields nullable (wizard can be filled step-by-step).
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", unique=True, index=True)

    # --- Blok 1: Identiteit ---
    org_type: Optional[str] = None  # OrgType enum value
    sector: Optional[str] = None  # Sector enum value
    employee_count: Optional[str] = None  # EmployeeRange enum value
    location_count: Optional[int] = None
    geographic_scope: Optional[str] = None  # GeographicScope enum value
    parent_organization: Optional[str] = None
    core_services: Optional[str] = None  # Free text, AI parses

    # --- Blok 2: Governance ---
    existing_certifications: Optional[str] = None  # JSON list
    applicable_frameworks: Optional[str] = None  # JSON list
    has_security_officer: Optional[bool] = None
    has_dpo: Optional[bool] = None
    governance_maturity: Optional[str] = None  # GovernanceMaturity enum value
    risk_appetite_availability: Optional[str] = None  # ProfileRiskAppetite enum value
    risk_appetite_integrity: Optional[str] = None  # ProfileRiskAppetite enum value
    risk_appetite_confidentiality: Optional[str] = None  # ProfileRiskAppetite enum value

    # --- Blok 3: IT-Landschap ---
    cloud_strategy: Optional[str] = None  # CloudStrategy enum value
    cloud_providers: Optional[str] = None  # JSON list
    workstation_count: Optional[str] = None  # EmployeeRange enum value
    has_remote_work: Optional[bool] = None
    has_byod: Optional[bool] = None
    critical_systems: Optional[str] = None  # Free text
    outsourced_it: Optional[bool] = None
    primary_it_supplier: Optional[str] = None

    # --- Blok 4: Privacy ---
    processes_personal_data: Optional[bool] = None
    data_subject_types: Optional[str] = None  # JSON list
    has_special_categories: Optional[bool] = None
    international_transfers: Optional[bool] = None
    processing_count_estimate: Optional[str] = None  # ProcessingCountRange enum value

    # --- Blok 5: Continuiteit ---
    has_bcp: Optional[bool] = None
    has_incident_response_plan: Optional[bool] = None
    max_tolerable_downtime: Optional[str] = None  # MaxDowntime enum value
    critical_process_count: Optional[int] = None
    key_dependencies: Optional[str] = None  # Free text

    # --- Blok 6: Mensen ---
    has_awareness_program: Optional[bool] = None
    has_background_checks: Optional[bool] = None
    training_frequency: Optional[str] = None  # TrainingFrequency enum value

    # --- Meta ---
    wizard_completed: bool = False
    wizard_current_step: int = 0
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by_id: Optional[int] = Field(default=None, foreign_key="user.id")


class AIKnowledgeBase(SQLModel, table=True):
    """
    Platform and methodology knowledge for the AI assistant.
    GLOBAL knowledge (tenant_id=NULL) or tenant-specific additions.

    This is the "brain" of the AI - what it knows about:
    - The IMS platform itself
    - Risk management methodologies (In Control, traditional)
    - Frameworks (BIO, ISO 27001, AVG)
    - Best practices
    - Terminology
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: Optional[int] = Field(default=None, foreign_key="tenant.id")  # NULL = global

    # Identification
    key: str  # Unique identifier, e.g., "METHODOLOGY_LEIDEN", "FRAMEWORK_BIO"
    title: str  # Human readable title

    # Content
    content: str  # The actual knowledge (markdown supported)

    # Categorization
    category: str  # "platform", "methodology", "framework", "best_practice", "terminology"
    subcategory: Optional[str] = None  # More specific grouping

    # For terminology/glossary entries
    is_glossary_term: bool = False
    term: Optional[str] = None  # The term being defined
    aliases: Optional[str] = None  # JSON array of alternative names

    # When should AI use this knowledge?
    applicable_contexts: Optional[str] = None  # JSON: ["risk_assessment", "policy_writing"]
    applicable_entity_types: Optional[str] = None  # JSON: ["Risk", "Measure"]

    # Priority/Relevance
    priority: int = 0  # Higher = more important, shown first
    always_include: bool = False  # Always include in AI context

    # Versioning
    version: int = 1
    is_active: bool = True

    # Source
    source: Optional[str] = None  # Where did this knowledge come from?
    source_url: Optional[str] = None

    # Embedding for RAG
    is_embedded: bool = False
    embedded_at: Optional[datetime] = None
    embedding: Optional[List[float]] = Field(default=None, sa_column=Column(Vector))

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AIPromptTemplate(SQLModel, table=True):
    """
    Reusable prompt templates for the AI assistant.
    Defines how AI should behave in different situations.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: Optional[int] = Field(default=None, foreign_key="tenant.id")  # NULL = global

    # Identification
    name: str  # e.g., "risk_quadrant_advisor", "policy_reviewer"
    description: Optional[str] = None

    # When to use this template
    trigger_context: str  # "risk_detail", "policy_edit", "workflow_step", etc.
    trigger_entity_type: Optional[str] = None  # "Risk", "Policy", etc.
    trigger_action: Optional[str] = None  # "classify", "review", "suggest"

    # The prompt template
    # Variables: {entity}, {user_role}, {org_context}, {methodology_context}
    system_prompt: str  # Instructions for AI behavior
    initial_message: Optional[str] = None  # First message AI sends

    # What knowledge to include
    include_knowledge_categories: Optional[str] = None  # JSON: ["methodology", "framework"]
    include_knowledge_keys: Optional[str] = None  # JSON: specific keys to always include

    # Behavior settings
    temperature: float = 0.7  # AI creativity (0=deterministic, 1=creative)
    max_tokens: Optional[int] = None

    # Can users customize?
    user_customizable: bool = False

    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class KnowledgeArtifact(SQLModel, table=True):
    """
    Raw inputs for RAG (Documents, Interview Transcripts, Policy Drafts).
    AI Agents (Voice/Doc) deposit information here.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    title: str
    content: str
    source_type: str  # "INTERVIEW", "UPLOAD", "WEBSITE"
    author_agent: Optional[str] = None

    # Links for context
    scope_id: Optional[int] = Field(default=None, foreign_key="scope.id")

    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    verified_by_id: Optional[int] = Field(default=None, foreign_key="user.id")

    # Embedding status (for RAG)
    is_embedded: bool = False
    embedded_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)


class Dashboard(SQLModel, table=True):
    """
    A custom view/dashboard generated by AI based on a user prompt.
    Stores the layout configuration (JSON) to be rendered by the Frontend.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    title: str
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")

    generation_prompt: str
    layout_config: str  # JSON

    is_shared: bool = False

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# AI ASSISTANT (Continuous Chat Island)
# =============================================================================

# =============================================================================
# AI AGENTS & TOOLS
# =============================================================================

class AIAgent(SQLModel, table=True):
    """
    Definition of an AI Agent with specific expertise.
    Each agent knows WHAT to do (domain knowledge, prompts).
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: Optional[int] = Field(default=None, foreign_key="tenant.id")  # NULL = global

    # Identification
    name: str  # e.g., "risk_agent", "compliance_agent"
    display_name: str  # e.g., "Risk Expert", "Compliance Adviseur"
    description: str  # What this agent does
    icon: Optional[str] = None  # Icon for UI
    color: Optional[str] = None  # Color for UI

    # Domain
    domain: str  # "isms", "pims", "bcms", "management", "system"
    expertise_areas: str  # JSON array: ["risk_assessment", "mapgood", "in_control_model"]

    # When to activate this agent
    trigger_contexts: str  # JSON: ["risk_detail", "risk_list", "risk_create"]
    trigger_entity_types: Optional[str] = None  # JSON: ["Risk", "RiskTemplate"]

    # Agent behavior
    system_prompt: str  # Core instructions for this agent
    personality: Optional[str] = None  # Tone, style
    language: str = "nl"  # Primary language

    # Knowledge access
    knowledge_categories: str  # JSON: which AIKnowledgeBase categories to include
    always_include_keys: Optional[str] = None  # JSON: specific knowledge keys always included

    # Capabilities
    can_create_suggestions: bool = True
    can_execute_actions: bool = False  # Can directly modify data?
    requires_confirmation: bool = True  # User must confirm changes?

    # Status
    is_active: bool = True
    version: int = 1

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tool_access: List["AIAgentToolAccess"] = Relationship(back_populates="agent")


class AITool(SQLModel, table=True):
    """
    Definition of a Tool that agents can use.
    Tools know HOW to do things (fetch data, write data, call APIs).
    """
    id: Optional[int] = Field(default=None, primary_key=True)

    # Identification
    name: str  # e.g., "get_risk", "search_measures", "create_suggestion"
    display_name: str  # e.g., "Risico ophalen"
    description: str  # What this tool does (also used in prompt)

    # Categorization
    category: str  # "read", "write", "knowledge", "external", "utility"

    # What entity/resource does this tool work with?
    target_entity_type: Optional[str] = None  # "Risk", "Measure", NULL for utilities
    target_resource: Optional[str] = None  # "database", "knowledge_base", "topdesk", "azure_ad"

    # Tool signature (for LLM function calling)
    parameters_schema: str  # JSON Schema of parameters
    returns_schema: Optional[str] = None  # JSON Schema of return value

    # Implementation reference
    implementation_class: str  # Python class/function path
    is_async: bool = False

    # Safety
    is_read_only: bool = True  # Does not modify data
    requires_confirmation: bool = False  # Requires user confirmation before execution
    risk_level: str = "low"  # "low", "medium", "high" - for audit/monitoring

    # Rate limiting
    max_calls_per_minute: Optional[int] = None

    # Status
    is_active: bool = True

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    agent_access: List["AIAgentToolAccess"] = Relationship(back_populates="tool")


class AIAgentToolAccess(SQLModel, table=True):
    """
    Links Agents to Tools they can use.
    Defines permissions and context for tool usage.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    agent_id: int = Field(foreign_key="aiagent.id")
    tool_id: int = Field(foreign_key="aitool.id")

    # Is this tool always available or only in certain contexts?
    always_available: bool = True
    available_contexts: Optional[str] = None  # JSON: specific contexts where tool is available

    # Permission level
    permission_level: str = "full"  # "full", "read_only", "limited"

    # Can the agent use this tool without asking user?
    auto_execute: bool = False  # True = agent can call without confirmation

    # Usage hints for the agent
    usage_hint: Optional[str] = None  # When/how should agent use this tool

    # Priority (for tool selection)
    priority: int = 0  # Higher = preferred when multiple tools could work

    is_active: bool = True

    # Relationships
    agent: Optional[AIAgent] = Relationship(back_populates="tool_access")
    tool: Optional[AITool] = Relationship(back_populates="agent_access")


class AIToolExecution(SQLModel, table=True):
    """
    Log of tool executions for audit and learning.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    # Context
    conversation_id: Optional[int] = Field(default=None, foreign_key="aiconversation.id")
    agent_id: int = Field(foreign_key="aiagent.id")
    tool_id: int = Field(foreign_key="aitool.id")

    # Execution details
    parameters: str  # JSON: what parameters were passed
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None

    # Result
    success: bool = False
    result: Optional[str] = None  # JSON: result data (truncated if large)
    error_message: Optional[str] = None

    # User interaction
    required_confirmation: bool = False
    user_confirmed: Optional[bool] = None
    confirmed_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    confirmed_at: Optional[datetime] = None

    # What did this tool execution affect?
    affected_entity_type: Optional[str] = None
    affected_entity_id: Optional[int] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# AI ASSISTANT (Continuous Chat Island)
# =============================================================================

class AIConversation(SQLModel, table=True):
    """
    AI conversation/chat session.
    The "AI island" at the bottom of the screen - always available,
    context-aware, helps users make decisions through dialogue.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)
    user_id: int = Field(foreign_key="user.id")

    # Which agent is handling this conversation?
    current_agent_id: Optional[int] = Field(default=None, foreign_key="aiagent.id")

    # Agent switches during conversation
    agent_switches: Optional[str] = None  # JSON: [{"from": 1, "to": 2, "at": "...", "reason": "..."}]

    # Conversation metadata
    title: Optional[str] = None  # Auto-generated or user-defined

    # Context: what is the user looking at?
    context_entity_type: Optional[str] = None  # "Risk", "Measure", "Assessment", etc.
    context_entity_id: Optional[int] = None
    context_page: Optional[str] = None  # "/risks/123", "/dashboard"

    # Conversation state
    is_active: bool = True

    # What was the conversation about? (for later reference)
    summary: Optional[str] = None  # AI-generated summary
    topics: Optional[str] = None  # JSON array of topics discussed

    # Did this conversation lead to actions?
    resulted_in_changes: bool = False
    changes_summary: Optional[str] = None  # What was created/modified

    started_at: datetime = Field(default_factory=datetime.utcnow)
    last_message_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

    # Relationships
    messages: List["AIConversationMessage"] = Relationship(back_populates="conversation")
    suggestions: List["AISuggestion"] = Relationship(back_populates="conversation")


class AIConversationMessage(SQLModel, table=True):
    """
    Individual message in an AI conversation.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="aiconversation.id")

    # Who sent this message?
    role: str  # "user", "assistant", "system"

    # Message content
    content: str

    # For assistant messages: what was the intent?
    intent: Optional[str] = None  # "question", "suggestion", "explanation", "action_proposal"

    # Attachments/references
    referenced_entities: Optional[str] = None  # JSON: [{"type": "Risk", "id": 123}, ...]

    # Feedback
    was_helpful: Optional[bool] = None
    feedback_note: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: Optional[AIConversation] = Relationship(back_populates="messages")


class AISuggestion(SQLModel, table=True):
    """
    AI suggestion that can be accepted/rejected by the user.
    When AI proposes a change (e.g., "I suggest quadrant MITIGATE"),
    it creates a suggestion that the user can accept with one click.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)
    conversation_id: Optional[int] = Field(default=None, foreign_key="aiconversation.id")

    # What is being suggested?
    suggestion_type: str  # "field_update", "create_entity", "workflow_transition", "classification"

    # Target entity
    target_entity_type: str  # "Risk", "Measure", etc.
    target_entity_id: Optional[int] = None  # NULL if creating new

    # The suggested change
    field_name: Optional[str] = None  # Which field to update
    suggested_value: str  # JSON encoded value
    current_value: Optional[str] = None  # JSON encoded current value

    # AI's reasoning
    reasoning: str  # Why AI suggests this
    confidence: Optional[float] = None  # 0.0 to 1.0

    # Based on what context?
    context_summary: Optional[str] = None  # What info AI used to make suggestion

    # User decision
    status: str = "pending"  # "pending", "accepted", "rejected", "modified"
    decided_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    decided_at: Optional[datetime] = None

    # If modified: what did user change it to?
    final_value: Optional[str] = None
    rejection_reason: Optional[str] = None

    # Was this applied?
    applied: bool = False
    applied_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None  # Suggestion expires if not acted upon

    # Relationships
    conversation: Optional[AIConversation] = Relationship(back_populates="suggestions")


# =============================================================================
# OBJECTIVES & KPIs (ISO 27001 §6.2)
# =============================================================================

class Objective(SQLModel, table=True):
    """
    Security/Privacy/BCM Objectives as required by ISO 27001 §6.2.
    Must be measurable, monitored, and reviewed.

    Example: "Reduce security incidents by 20% in 2024"
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    title: str
    description: str

    # Domain
    domain: ObjectiveDomain = ObjectiveDomain.ISMS

    # What needs to be done to achieve this?
    actions_required: Optional[str] = None

    # Resources needed
    resources_required: Optional[str] = None

    # Who is responsible?
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")

    # Timeline
    target_date: Optional[datetime] = None
    start_date: Optional[datetime] = None

    # Status
    status: ObjectiveStatus = ObjectiveStatus.DRAFT

    # Link to scope (optional - can be organization-wide)
    scope_id: Optional[int] = Field(default=None, foreign_key="scope.id")

    # Link to risks this objective addresses
    related_risks: Optional[str] = None  # JSON array of risk IDs

    # Progress
    progress_percentage: int = 0
    progress_notes: Optional[str] = None

    # Review
    last_reviewed_at: Optional[datetime] = None
    next_review_date: Optional[datetime] = None

    # Year/Period
    period_year: Optional[int] = None  # e.g., 2024

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    kpis: List["ObjectiveKPI"] = Relationship(back_populates="objective")
    initiative_links: List["InitiativeObjectiveLink"] = Relationship(back_populates="objective")


class ObjectiveKPI(SQLModel, table=True):
    """
    Key Performance Indicator linked to an Objective.
    Defines what to measure and target values.

    Example: "Number of security incidents per month" with target < 5
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    objective_id: int = Field(foreign_key="objective.id")

    name: str
    description: Optional[str] = None

    # What to measure
    metric_name: str  # e.g., "Aantal incidenten"
    unit: Optional[str] = None  # e.g., "per maand", "%", "dagen"

    # Target values
    target_value: float
    target_direction: str = "lower"  # "lower" = lower is better, "higher" = higher is better

    # Thresholds for status
    green_threshold: Optional[float] = None  # Good
    amber_threshold: Optional[float] = None  # Warning
    red_threshold: Optional[float] = None  # Critical

    # Current status
    current_value: Optional[float] = None
    current_trend: KPITrend = KPITrend.UNKNOWN
    last_measured_at: Optional[datetime] = None

    # How often to measure
    measurement_frequency: Optional[str] = None  # "Monthly", "Quarterly"

    # Data source
    data_source: Optional[str] = None  # Where does the data come from?
    is_automated: bool = False  # Can be automatically collected?

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    objective: Optional[Objective] = Relationship(back_populates="kpis")
    measurements: List["KPIMeasurement"] = Relationship(back_populates="kpi")


class KPIMeasurement(SQLModel, table=True):
    """
    Individual measurement/data point for a KPI.
    Historical tracking of KPI values over time.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    kpi_id: int = Field(foreign_key="objectivekpi.id")

    # Measurement
    value: float
    measurement_date: datetime

    # Period this measurement covers
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None

    # Context
    notes: Optional[str] = None
    measured_by_id: Optional[int] = Field(default=None, foreign_key="user.id")

    # Was this auto-collected or manual?
    is_automated: bool = False
    data_source: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    kpi: Optional[ObjectiveKPI] = Relationship(back_populates="measurements")


# =============================================================================
# TAGS / LABELS (Generic Tagging System)
# =============================================================================

class Tag(SQLModel, table=True):
    """
    Reusable tags/labels for organizing and filtering entities.
    Tags are tenant-specific.

    Examples: "Kritiek", "HR-gerelateerd", "Cloud", "Externe audit"
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    name: str
    description: Optional[str] = None

    # Visual
    color: Optional[str] = None  # Hex color code, e.g., "#FF5733"
    icon: Optional[str] = None  # Icon name

    # Category for grouping tags
    category: Optional[str] = None  # e.g., "Priority", "Department", "Type"

    # Is this a system tag (cannot be deleted)?
    is_system: bool = False

    created_at: datetime = Field(default_factory=datetime.utcnow)


class EntityTag(SQLModel, table=True):
    """
    Links tags to any entity (polymorphic tagging).
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)
    tag_id: int = Field(foreign_key="tag.id")

    # Which entity is tagged (polymorphic)
    entity_type: str  # "Risk", "Measure", "Scope", "Incident", etc.
    entity_id: int

    # Who tagged it
    tagged_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    tagged_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# SYSTEM & TENANT SETTINGS
# =============================================================================

class SystemSetting(SQLModel, table=True):
    """
    Global system-wide settings (platform level).
    """
    id: Optional[int] = Field(default=None, primary_key=True)

    key: str = Field(unique=True)  # e.g., "default_language", "max_file_size_mb"
    value: str  # JSON encoded value
    value_type: str = "string"  # "string", "number", "boolean", "json"

    description: Optional[str] = None
    category: Optional[str] = None  # "General", "Security", "Email", "AI"

    # Can tenants override this?
    tenant_overridable: bool = True

    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by_id: Optional[int] = Field(default=None, foreign_key="user.id")


class TenantSetting(SQLModel, table=True):
    """
    Tenant-specific settings that override system defaults.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    key: str  # Same key as SystemSetting
    value: str  # JSON encoded value

    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by_id: Optional[int] = Field(default=None, foreign_key="user.id")


# =============================================================================
# INTEGRATION CONFIGURATION
# =============================================================================

class IntegrationConfig(SQLModel, table=True):
    """
    Configuration for external system integrations.
    Stores connection details for TopDesk, Azure AD, etc.

    NOTE: Sensitive data (API keys, passwords) should be encrypted
    or stored in a secrets manager - not plain text!
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    # Integration identification
    name: str  # e.g., "TopDesk Productie"
    system_type: str  # e.g., "TopDesk", "Azure AD", "ServiceNow"
    description: Optional[str] = None

    # Connection details
    base_url: Optional[str] = None  # e.g., "https://company.topdesk.net"
    api_version: Optional[str] = None

    # Authentication (NOTE: encrypt sensitive fields!)
    auth_type: Optional[str] = None  # "api_key", "oauth2", "basic"
    # These should be encrypted or use a secrets manager:
    credentials_reference: Optional[str] = None  # Reference to secrets manager

    # What does this integration do?
    sync_controls: bool = False  # Sync controls to/from
    sync_incidents: bool = False  # Sync incidents
    sync_changes: bool = False  # Sync change requests
    sync_users: bool = False  # Sync users (e.g., from Azure AD)

    # Sync settings
    sync_direction: str = "both"  # "inbound", "outbound", "both"
    sync_frequency_minutes: Optional[int] = None  # How often to sync
    last_sync_at: Optional[datetime] = None
    next_sync_at: Optional[datetime] = None

    # Status
    status: IntegrationStatus = IntegrationStatus.PENDING_SETUP
    last_error: Optional[str] = None
    last_error_at: Optional[datetime] = None

    # Mapping configuration (how fields map between systems)
    field_mapping: Optional[str] = None  # JSON mapping config

    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    sync_logs: List["IntegrationSyncLog"] = Relationship(back_populates="integration")


class IntegrationSyncLog(SQLModel, table=True):
    """
    Log of synchronization runs with external systems.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    integration_id: int = Field(foreign_key="integrationconfig.id")

    # Sync details
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None

    # Direction
    direction: str  # "inbound", "outbound"

    # Results
    success: bool = False
    records_processed: int = 0
    records_created: int = 0
    records_updated: int = 0
    records_failed: int = 0

    # Errors
    error_message: Optional[str] = None
    error_details: Optional[str] = None  # JSON with detailed errors

    # Relationships
    integration: Optional[IntegrationConfig] = Relationship(back_populates="sync_logs")


# =============================================================================
# REPORT TEMPLATES & SCHEDULED REPORTS
# =============================================================================

class ReportTemplate(SQLModel, table=True):
    """
    Saved report configurations.
    Can be used to generate reports on-demand or on schedule.

    NOTE: AI can also generate ad-hoc reports, but templates
    provide consistency and repeatability.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    name: str
    description: Optional[str] = None

    # Report type
    report_type: str  # "compliance", "risk", "incident", "management_review", "custom"

    # What's included
    include_sections: Optional[str] = None  # JSON array of sections

    # Filters
    scope_id: Optional[int] = Field(default=None, foreign_key="scope.id")
    standard_id: Optional[int] = Field(default=None, foreign_key="standard.id")
    date_range_type: Optional[str] = None  # "last_month", "last_quarter", "custom"
    filters: Optional[str] = None  # JSON with additional filters

    # Output format
    output_format: str = "pdf"  # "pdf", "excel", "word", "html"

    # Template content (for custom reports)
    template_content: Optional[str] = None  # HTML/Markdown template

    # AI generation prompt (for AI-assisted reports)
    ai_prompt: Optional[str] = None

    # Ownership
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
    is_shared: bool = False

    # Status
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    scheduled_reports: List["ScheduledReport"] = Relationship(back_populates="template")


class ScheduledReport(SQLModel, table=True):
    """
    Scheduled/recurring report generation.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)
    template_id: int = Field(foreign_key="reporttemplate.id")

    name: str

    # Schedule
    frequency: ReportFrequency = ReportFrequency.MONTHLY
    day_of_week: Optional[int] = None  # 0=Monday for weekly
    day_of_month: Optional[int] = None  # For monthly
    time_of_day: Optional[str] = None  # "09:00"

    # Recipients
    recipients: Optional[str] = None  # JSON array of email addresses or user IDs
    send_email: bool = True

    # Next/Last run
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None

    # Status
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    template: Optional[ReportTemplate] = Relationship(back_populates="scheduled_reports")
    executions: List["ReportExecution"] = Relationship(back_populates="scheduled_report")


class ReportExecution(SQLModel, table=True):
    """
    History of generated reports.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)

    # Can be from template or ad-hoc
    template_id: Optional[int] = Field(default=None, foreign_key="reporttemplate.id")
    scheduled_report_id: Optional[int] = Field(default=None, foreign_key="scheduledreport.id")

    # Execution details
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    success: bool = False

    # Generated by
    generated_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    is_automated: bool = False  # Was this a scheduled run?

    # Output
    output_format: str = "pdf"
    file_path: Optional[str] = None
    file_url: Optional[str] = None
    file_size: Optional[int] = None

    # Error handling
    error_message: Optional[str] = None

    # Parameters used
    parameters: Optional[str] = None  # JSON with filters/parameters used

    # Relationships
    scheduled_report: Optional[ScheduledReport] = Relationship(back_populates="executions")


# =============================================================================
# WORKFLOW ENGINE (Visual Process Tracking)
# =============================================================================

class WorkflowDefinition(SQLModel, table=True):
    """
    Defines a workflow/process with states and transitions.
    Reusable across different entity types.

    Examples:
    - "Policy Approval Workflow"
    - "Risk Acceptance Workflow"
    - "Exception Request Workflow"
    - "Incident Handling Workflow"
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: Optional[int] = Field(default=None, foreign_key="tenant.id")  # NULL = global template

    name: str
    description: Optional[str] = None

    # What entity types can use this workflow?
    applicable_entity_types: str  # JSON array: ["Policy", "Risk", "Exception"]

    # Is this the default workflow for these entity types?
    is_default: bool = False

    # Visual representation (for frontend rendering)
    # JSON with layout information for visual diagram
    visual_config: Optional[str] = None

    # Version control
    version: int = 1
    is_active: bool = True

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    states: List["WorkflowState"] = Relationship(back_populates="workflow")
    transitions: List["WorkflowTransition"] = Relationship(back_populates="workflow")


class WorkflowState(SQLModel, table=True):
    """
    A state/step in a workflow.

    Example states for Policy Approval:
    1. "Draft" (initial)
    2. "Review"
    3. "Approval"
    4. "Published" (final)
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    workflow_id: int = Field(foreign_key="workflowdefinition.id")

    name: str  # e.g., "Concept", "Review", "Goedkeuring", "Gepubliceerd"
    description: Optional[str] = None

    # State type
    is_initial: bool = False  # Starting state
    is_final: bool = False  # End state (completed)
    is_rejection: bool = False  # Rejected/cancelled state

    # Visual
    color: Optional[str] = None  # For diagram
    icon: Optional[str] = None
    sequence: int = 0  # Order in the workflow

    # Actions required in this state
    required_actions: Optional[str] = None  # What needs to happen here?

    # Who can act in this state?
    allowed_roles: Optional[str] = None  # JSON array of roles

    # SLA/Timing
    expected_duration_days: Optional[int] = None
    escalation_after_days: Optional[int] = None

    # --- AI Assistance Configuration ---
    # What should AI help with in this state?
    ai_assistance_enabled: bool = True

    # Prompt template for AI guidance in this state
    # Variables: {entity_type}, {entity_title}, {user_role}, {previous_steps}
    ai_guidance_prompt: Optional[str] = None  # "Help me review this {entity_type}..."

    # What should AI check before allowing transition?
    ai_validation_prompt: Optional[str] = None  # "Check if all required fields are complete..."

    # Checklist items AI should verify
    ai_checklist: Optional[str] = None  # JSON array of checks

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    workflow: Optional[WorkflowDefinition] = Relationship(back_populates="states")


class WorkflowTransition(SQLModel, table=True):
    """
    Allowed transitions between workflow states.
    Defines who can trigger the transition and what conditions apply.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    workflow_id: int = Field(foreign_key="workflowdefinition.id")

    # From -> To
    from_state_id: int = Field(foreign_key="workflowstate.id")
    to_state_id: int = Field(foreign_key="workflowstate.id")

    name: str  # e.g., "Submit for Review", "Approve", "Reject", "Request Changes"
    description: Optional[str] = None

    # Who can trigger this transition?
    allowed_roles: Optional[str] = None  # JSON array of roles
    requires_approval: bool = False
    approver_roles: Optional[str] = None  # Who must approve?

    # Conditions
    conditions: Optional[str] = None  # JSON conditions that must be met

    # Is a comment required for this transition?
    requires_comment: bool = False

    # Actions to perform on transition
    on_transition_actions: Optional[str] = None  # JSON: notifications, field updates

    # --- AI Assistance for Transitions ---
    # AI validates before allowing transition
    ai_pre_validation_enabled: bool = False
    ai_pre_validation_prompt: Optional[str] = None  # "Check if ready to move to next step..."

    # For approval transitions: AI generates summary for approver
    ai_approval_summary_enabled: bool = False
    ai_approval_summary_prompt: Optional[str] = None  # "Summarize this for the approver..."

    # For rejection: AI suggests improvements
    ai_rejection_suggestions_enabled: bool = False

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    workflow: Optional[WorkflowDefinition] = Relationship(back_populates="transitions")


class WorkflowInstance(SQLModel, table=True):
    """
    An active workflow for a specific entity.
    Tracks current state and history.

    When a Policy enters a workflow, a WorkflowInstance is created.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)
    workflow_id: int = Field(foreign_key="workflowdefinition.id")

    # Which entity is going through this workflow?
    entity_type: str  # "Policy", "Risk", "Exception"
    entity_id: int

    # Current state
    current_state_id: int = Field(foreign_key="workflowstate.id")
    status: WorkflowStatus = WorkflowStatus.IN_PROGRESS

    # Started/Completed
    started_at: datetime = Field(default_factory=datetime.utcnow)
    started_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    completed_at: Optional[datetime] = None

    # Current step info
    entered_current_state_at: Optional[datetime] = None
    current_state_deadline: Optional[datetime] = None

    # Assignees
    current_assignee_id: Optional[int] = Field(default=None, foreign_key="user.id")
    current_approver_id: Optional[int] = Field(default=None, foreign_key="user.id")

    # Summary
    total_steps_completed: int = 0
    total_steps_remaining: int = 0

    # --- AI Assistance Status ---
    ai_assistance_enabled: bool = True

    # Current AI guidance for this step
    current_ai_guidance: Optional[str] = None
    ai_guidance_generated_at: Optional[datetime] = None

    # AI-identified blockers or issues
    ai_identified_issues: Optional[str] = None  # JSON array of issues

    # AI confidence that workflow will complete successfully
    ai_completion_confidence: Optional[float] = None  # 0.0 to 1.0

    # AI-predicted completion date (based on historical data)
    ai_predicted_completion: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    history: List["WorkflowStepHistory"] = Relationship(back_populates="workflow_instance")


class WorkflowStepHistory(SQLModel, table=True):
    """
    History of state transitions in a workflow instance.
    Complete audit trail of the workflow progress.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    workflow_instance_id: int = Field(foreign_key="workflowinstance.id")

    # State at this step
    state_id: int = Field(foreign_key="workflowstate.id")
    state_name: str  # Denormalized for history

    # Step number (1, 2, 3...)
    step_number: int

    # When did we enter/exit this state?
    entered_at: datetime
    exited_at: Optional[datetime] = None
    duration_hours: Optional[float] = None

    # Who was responsible?
    assignee_id: Optional[int] = Field(default=None, foreign_key="user.id")

    # Transition that led to next state
    transition_id: Optional[int] = Field(default=None, foreign_key="workflowtransition.id")
    transition_name: Optional[str] = None
    transitioned_by_id: Optional[int] = Field(default=None, foreign_key="user.id")

    # Comments/Notes
    comment: Optional[str] = None

    # Was this an approval?
    was_approval: bool = False
    approval_decision: Optional[str] = None  # "approved", "rejected"

    # --- AI Generated Content at this Step ---
    # AI guidance shown to user at this step
    ai_guidance_shown: Optional[str] = None

    # AI validation result before transition
    ai_validation_result: Optional[str] = None  # JSON: {passed: bool, issues: [...]}
    ai_validation_passed: Optional[bool] = None

    # AI summary for approver (if approval step)
    ai_approval_summary: Optional[str] = None

    # AI suggestions after rejection
    ai_improvement_suggestions: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    workflow_instance: Optional[WorkflowInstance] = Relationship(back_populates="history")
