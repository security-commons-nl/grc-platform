# IMS - Complete Design Overview

> **Versie:** 1.0
> **Datum:** Februari 2025
> **Status:** Design Phase Complete

---

## Inhoudsopgave

1. [Visie & Filosofie](#1-visie--filosofie)
2. [Architectuur](#2-architectuur)
3. [Data Model](#3-data-model)
4. [Risk Management Methodiek](#4-risk-management-methodiek)
5. [Workflows & Processen](#5-workflows--processen)
6. [AI Systeem](#6-ai-systeem)
7. [Multi-Tenancy & Shared Services](#7-multi-tenancy--shared-services)
8. [Integraties](#8-integraties)
9. [Entity Reference](#9-entity-reference)
10. [Implementatie Roadmap](#10-implementatie-roadmap)

---

## 1. Visie & Filosofie

### 1.1 Wat is IMS?

IMS (Integrated Management System) is een **Governance, Risk & Compliance (GRC) platform** voor Nederlandse gemeenten en overheidsorganisaties. Het integreert:

- **ISMS** - Information Security Management System (ISO 27001, BIO)
- **PIMS** - Privacy Information Management System (AVG/GDPR)
- **BCMS** - Business Continuity Management System (ISO 22301)

### 1.2 De Kernfilosofie

> **"The Model leads. The API guards. Tools execute. AI supports."**

```
┌─────────────────────────────────────────────────────────────────┐
│  LAAG 1: THE MODEL (Data)                                       │
│  Single source of truth voor Norms, Risks, Controls             │
│  Tech: SQLModel + PostgreSQL                                    │
├─────────────────────────────────────────────────────────────────┤
│  LAAG 2: THE API (Logic)                                        │
│  Gatekeeper: RBAC, Validatie, Workflows                         │
│  Tech: FastAPI                                                  │
├─────────────────────────────────────────────────────────────────┤
│  LAAG 3: THE TOOLS (UI)                                         │
│  "Domme" glasplaat - geen business logic                        │
│  Tech: React/Vue                                                │
├─────────────────────────────────────────────────────────────────┤
│  LAAG 4: THE AI (Intelligence)                                  │
│  Lokaal/Privaat - geen cloud data leakage                       │
│  Tech: Ollama + Mistral                                         │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 Drie Zinnen Samenvatting

1. **Een centraal compliance dashboard** waar gemeenten hun risico's, maatregelen en audits beheren volgens de Leidse aanpak (Mitigeren / Zekerheid verkrijgen / Monitoren / Accepteren) — met voor elke norm (BIO, ISO 27001, AVG) inzicht in waar je staat.

2. **Visuele workflows** waarin je bij elk proces (risico-acceptatie, policy-goedkeuring, incident-afhandeling) exact ziet in welke stap je bent, wie aan zet is, en wat er nog moet gebeuren — met AI die je bij elke stap helpt en valideert.

3. **Geen operationele uitvoering**: IMS is de "administratieve waarheid" die registreert, rapporteert en bewijs verzamelt — de echte acties gebeuren in TopDesk, Azure AD en andere systemen waarmee IMS integreert.

### 1.4 Wat IMS WEL doet

- Registreren welke maatregelen er MOETEN zijn (Requirements)
- Vastleggen welke maatregelen er ZIJN (Measures)
- Tracken wat er nog moet gebeuren (CorrectiveActions, Initiatives)
- Bewijs verzamelen dat het werkt (Evidence)
- Rapporteren over compliance status
- AI-ondersteuning bij beslissingen

### 1.5 Wat IMS NIET doet

- Accounts aanmaken/verwijderen → Azure AD
- Servers patchen → SCCM/Intune
- Tickets afhandelen → TopDesk
- Firewalls configureren → Firewall management
- Backups maken → Backup software

---

## 2. Architectuur

### 2.1 Technologie Stack

| Component | Technologie | Reden |
|-----------|-------------|-------|
| **Backend** | Python + FastAPI | Native AI taal, async, type-safe |
| **ORM** | SQLModel | Pydantic + SQLAlchemy in één |
| **Database** | PostgreSQL 15+ | ACID, pgvector voor RAG |
| **Vector Store** | pgvector | Embeddings voor kennisbank |
| **LLM** | Ollama + Mistral | Lokaal, EU data sovereignty |
| **Frontend** | React (TBD) | Breed ecosysteem |
| **Auth** | JWT + Azure AD SSO | Enterprise ready |

### 2.2 Deployment

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ims
    ports:
      - "5432:5432"

  api:
    build: ./backend
    environment:
      AI_API_BASE: "http://ollama:11434/v1"
      AI_MODEL_NAME: "mistral"
    ports:
      - "8000:8000"

  ollama:
    image: ollama/ollama
    volumes:
      - ollama_data:/root/.ollama
```

### 2.3 Security Principes

| Principe | Implementatie |
|----------|---------------|
| **EU Data Sovereignty** | AI draait lokaal (Ollama), geen externe API calls |
| **Multi-Tenant Isolation** | Elke query bevat tenant_id filter |
| **RBAC** | Rollen per Scope (ProcessOwner, Editor, Viewer) |
| **Audit Trail** | Elke wijziging in AuditLog |
| **Encryption** | Data at rest + in transit |

---

## 3. Data Model

### 3.1 Overzicht (70+ Entities)

```
┌─────────────────────────────────────────────────────────────────┐
│                     MULTI-TENANCY (7)                            │
│  Tenant, TenantUser, TenantRelationship, SharedMeasure,         │
│  SharedScope, VirtualScopeMember, AccessRequest                  │
├─────────────────────────────────────────────────────────────────┤
│                     GOVERNANCE (8)                               │
│  Standard, Requirement, RequirementMapping, Policy, Document,    │
│  Scope, ScopeDependency, ApplicabilityStatement                 │
├─────────────────────────────────────────────────────────────────┤
│                     RISK MANAGEMENT (12)                         │
│  Risk, RiskTemplate, RiskAppetite, Threat, ThreatActor,         │
│  Vulnerability, RiskThreatLink, MeasureRiskLink, Issue,         │
│  GapAnalysis, GapAnalysisItem, MeasureRequirementLink           │
├─────────────────────────────────────────────────────────────────┤
│                     MEASURES (2)                                 │
│  Measure, MeasureTemplate                                        │
├─────────────────────────────────────────────────────────────────┤
│                     ASSESSMENT (7)                               │
│  Assessment, Finding, Evidence, AssessmentQuestion,              │
│  AssessmentResponse, MaturityAssessment, MaturityDomainScore    │
├─────────────────────────────────────────────────────────────────┤
│                     INCIDENTS (3)                                │
│  Incident, Exception, CorrectiveAction                          │
├─────────────────────────────────────────────────────────────────┤
│                     PRIVACY / PIMS (3)                           │
│  ProcessingActivity, DataSubjectRequest, ProcessorAgreement     │
├─────────────────────────────────────────────────────────────────┤
│                     BCM (2)                                      │
│  ContinuityPlan, ContinuityTest                                 │
├─────────────────────────────────────────────────────────────────┤
│                     PLANNING & MANAGEMENT (6)                    │
│  CompliancePlanningItem, ManagementReview, ReviewSchedule,      │
│  Initiative, InitiativeMilestone, RiskAppetite                  │
├─────────────────────────────────────────────────────────────────┤
│                     OBJECTIVES & KPIs (3)                        │
│  Objective, ObjectiveKPI, KPIMeasurement                        │
├─────────────────────────────────────────────────────────────────┤
│                     WORKFLOWS (5)                                │
│  WorkflowDefinition, WorkflowState, WorkflowTransition,         │
│  WorkflowInstance, WorkflowStepHistory                          │
├─────────────────────────────────────────────────────────────────┤
│                     USERS & ACCESS (3)                           │
│  User, UserScopeRole, TenantUser                                │
├─────────────────────────────────────────────────────────────────┤
│                     COMMUNICATION (4)                            │
│  Notification, Comment, Attachment, AuditLog                    │
├─────────────────────────────────────────────────────────────────┤
│                     TAGS & SETTINGS (4)                          │
│  Tag, EntityTag, SystemSetting, TenantSetting                   │
├─────────────────────────────────────────────────────────────────┤
│                     INTEGRATIONS (2)                             │
│  IntegrationConfig, IntegrationSyncLog                          │
├─────────────────────────────────────────────────────────────────┤
│                     REPORTS (3)                                  │
│  ReportTemplate, ScheduledReport, ReportExecution               │
├─────────────────────────────────────────────────────────────────┤
│                     AI SYSTEM (10)                               │
│  AIAgent, AITool, AIAgentToolAccess, AIToolExecution,           │
│  AIConversation, AIConversationMessage, AISuggestion,           │
│  AIKnowledgeBase, AIPromptTemplate, KnowledgeArtifact           │
├─────────────────────────────────────────────────────────────────┤
│                     AI SUPPORT (2)                               │
│  OrganizationContext, Dashboard                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Kernentiteiten

#### Tenant (Multi-tenancy root)
```python
class Tenant(SQLModel, table=True):
    id: int
    name: str                    # "Gemeente Amsterdam"
    slug: str                    # "amsterdam"
    tenant_type: str             # "municipality", "ssc", "province"
    is_service_provider: bool    # Is dit een SSC?
    settings: str                # JSON configuratie
```

#### Scope (Assets, Processen, Organisatie)
```python
class Scope(SQLModel, table=True):
    id: int
    tenant_id: int
    parent_id: int               # Hiërarchie
    name: str
    type: ScopeType              # ORGANIZATION, CLUSTER, DEPARTMENT, PROCESS, ASSET, SUPPLIER, VIRTUAL

    # BIA Classificatie
    availability_rating: ClassificationLevel
    integrity_rating: ClassificationLevel
    confidentiality_rating: ClassificationLevel

    # BCM
    rto_hours: int               # Recovery Time Objective
    rpo_hours: int               # Recovery Point Objective
```

#### Risk (Kern van risicobeheer)
```python
class Risk(SQLModel, table=True):
    id: int
    tenant_id: int
    scope_id: int

    title: str
    description: str
    threat_category: ThreatCategory  # MAPGOOD

    # Inherent (voor controls)
    inherent_likelihood: RiskLevel
    inherent_impact: RiskLevel
    inherent_risk_score: int     # 1-16

    # Residueel (na controls)
    residual_likelihood: RiskLevel
    residual_impact: RiskLevel
    vulnerability_score: int     # 0-100

    # Leiden model
    attention_quadrant: AttentionQuadrant  # MITIGATE, ASSURANCE, MONITOR, ACCEPT
    mitigation_approach: MitigationApproach  # REDUCE, TRANSFER, AVOID (alleen bij MITIGATE)

    # AI
    ai_suggested_quadrant: AttentionQuadrant
```

#### Measure (Maatregelen)
```python
class Measure(SQLModel, table=True):
    id: int
    tenant_id: int
    scope_id: int

    title: str
    description: str
    control_type: str            # Preventive, Detective, Corrective
    automation_level: str        # Manual, Semi-automated, Automated

    status: Status
    effectiveness_percentage: int  # 0-100%

    # External system link
    external_system: str         # "TopDesk"
    external_reference: str      # "CHG-12345"
    external_url: str

    # Shared services
    is_shared: bool
```

### 3.3 Relaties Diagram

```
                            ┌──────────┐
                            │  Tenant  │
                            └────┬─────┘
                                 │
           ┌─────────────────────┼─────────────────────┐
           │                     │                     │
           ▼                     ▼                     ▼
      ┌─────────┐          ┌─────────┐          ┌──────────┐
      │  Scope  │◄────────►│  Risk   │◄────────►│ Measure  │
      └────┬────┘          └────┬────┘          └────┬─────┘
           │                    │                    │
           │               ┌────┴────┐               │
           │               ▼         ▼               │
           │         ┌─────────┐ ┌────────┐          │
           │         │ Threat  │ │ Issue  │          │
           │         └─────────┘ └────────┘          │
           │                                         │
           ▼                                         ▼
    ┌─────────────┐                          ┌─────────────┐
    │ Assessment  │                          │ Requirement │
    └──────┬──────┘                          └──────┬──────┘
           │                                        │
           ▼                                        ▼
    ┌─────────────┐                          ┌─────────────┐
    │   Finding   │                          │  Standard   │
    └──────┬──────┘                          └─────────────┘
           │
           ▼
    ┌─────────────────┐
    │CorrectiveAction │
    └─────────────────┘
```

---

## 4. Risk Management Methodiek

### 4.1 Filosofie

> **"Niet elk risico verdient dezelfde aandacht."**

Je hebt beperkte capaciteit. Besteed die waar het ertoe doet.

### 4.2 Leiden "In Control" Model

Het Leiden model bepaalt hoeveel **aandacht** een risico krijgt, gebaseerd op twee assen:

| As | Vraag |
|----|-------|
| **Impact** | Hoe erg is het als dit misgaat? |
| **Kwetsbaarheid** | Hoe waarschijnlijk gaat het mis, gegeven onze huidige maatregelen? |

#### De Vier Kwadranten

```
                         IMPACT
                    Laag          Hoog
             ┌────────────┬────────────┐
      Hoog   │  MONITOR   │  MITIGATE  │
   Kwets-    │  "meten,   │  "actief   │
   baarheid  │   wachten" │  aanpakken"│
             ├────────────┼────────────┤
      Laag   │   ACCEPT   │ ASSURANCE  │
             │ "loslaten" │ "auditen,  │
             │            │  bewijzen" │
             └────────────┴────────────┘
```

| Kwadrant | Betekenis | Actie |
|----------|-----------|-------|
| **MITIGATE** | Hoog risico, hoge kwetsbaarheid | Actief aanpakken met maatregelen |
| **ASSURANCE** | Hoog risico, lage kwetsbaarheid | Bewijzen dat controls werken (audit) |
| **MONITOR** | Laag risico, hoge kwetsbaarheid | Meten en in de gaten houden |
| **ACCEPT** | Laag risico, lage kwetsbaarheid | Accepteren, focus elders |

### 4.3 Behandelaanpak (binnen MITIGATE)

Alleen als het kwadrant **MITIGATE** is, kies je een behandelaanpak:

| Aanpak | Betekenis | Voorbeeld |
|--------|-----------|-----------|
| **REDUCE** | Verminder kans of impact | MFA implementeren, encryptie |
| **TRANSFER** | Draag over naar derde partij | Verzekering, outsourcing |
| **AVOID** | Elimineer de risicobron | Stop met de activiteit |

### 4.4 MAPGOOD Dreigingscategorieën

Nederlandse standaard voor dreigingscategorisering:

| Letter | Categorie | Voorbeelden |
|--------|-----------|-------------|
| **M** | Menselijk falen | Fouten, social engineering |
| **A** | Applicatie falen | Software bugs, crashes |
| **P** | Proces falen | Procedurale fouten |
| **G** | Gegevens | Data kwaliteit, integriteit |
| **O** | Omgeving | Brand, overstroming, stroomuitval |
| **O** | Opzet | Bewuste aanvallen, sabotage |
| **D** | Derden | Leveranciers, ketenpartners |

### 4.5 Risk Appetite

Gedefinieerd op tenant niveau via `RiskAppetite`:

```python
class RiskAppetite(SQLModel, table=True):
    overall_appetite: RiskAppetiteLevel  # AVERSE, MINIMAL, CAUTIOUS, MODERATE, OPEN

    # Per domein
    isms_appetite: RiskAppetiteLevel
    pims_appetite: RiskAppetiteLevel
    bcms_appetite: RiskAppetiteLevel

    # Thresholds
    auto_accept_threshold: RiskLevel     # Tot dit niveau: automatisch accepteren
    escalation_threshold: RiskLevel      # Vanaf dit niveau: verplicht escaleren
    max_acceptable_risk_score: int       # Maximale residuele score (1-16)
```

---

## 5. Workflows & Processen

### 5.1 Generiek Workflow Systeem

Elk proces in IMS kan een workflow hebben:

```
WorkflowDefinition
       │
       ├── WorkflowState (1..n)
       │      • is_initial: bool
       │      • is_final: bool
       │      • ai_guidance_prompt: str
       │
       └── WorkflowTransition (1..n)
              • from_state → to_state
              • requires_approval: bool
              • ai_pre_validation_enabled: bool
```

### 5.2 Voorbeeld: Policy Goedkeuring

```
┌─────────┐    Submit    ┌─────────┐   Approve   ┌───────────┐   Publish   ┌───────────┐
│  DRAFT  │─────────────►│ REVIEW  │────────────►│ APPROVED  │────────────►│ PUBLISHED │
└─────────┘              └─────────┘             └───────────┘             └───────────┘
     │                        │                       │
     │    Request Changes     │      Reject           │
     ◄────────────────────────┤◄──────────────────────┤
```

### 5.3 Voorbeeld: Risk Acceptatie

```
┌────────────┐   Classify   ┌────────────┐   Treat   ┌───────────┐   Accept   ┌──────────┐
│ IDENTIFIED │─────────────►│ CLASSIFIED │─────────►│  TREATED  │───────────►│ ACCEPTED │
└────────────┘              └────────────┘          └───────────┘            └──────────┘
                                  │                       │
                                  │                       │    Escalate
                                  │                       ├───────────────►┌──────────┐
                                  │                       │                │ESCALATED │
                                  │   AI: Suggest         │                └──────────┘
                                  │   quadrant            │
                                  ▼                       │
                            ┌──────────┐                  │
                            │ AI Check │──────────────────┘
                            └──────────┘
```

### 5.4 Workflow Instance Tracking

Voor elke entity in een workflow:

```python
class WorkflowInstance(SQLModel, table=True):
    entity_type: str             # "Policy", "Risk", "Exception"
    entity_id: int

    current_state_id: int
    status: WorkflowStatus       # IN_PROGRESS, WAITING_APPROVAL, COMPLETED

    total_steps_completed: int
    total_steps_remaining: int

    # AI ondersteuning
    ai_assistance_enabled: bool
    current_ai_guidance: str
    ai_identified_issues: str    # JSON
```

### 5.5 AI bij Workflows

Elke workflow state kan AI-ondersteuning hebben:

| Moment | AI Functie |
|--------|------------|
| **Bij state entry** | Guidance: "Wat moet ik hier doen?" |
| **Voor transitie** | Validation: "Is alles compleet?" |
| **Bij approval** | Summary: samenvatting voor approver |
| **Na rejection** | Suggestions: verbeteradviezen |

---

## 6. AI Systeem

### 6.1 Overzicht

```
┌─────────────────────────────────────────────────────────────────┐
│                      AI CHAT ISLAND                              │
│  Altijd zichtbaar onderaan het scherm                           │
│  Context-aware: weet waar je bent                               │
│  Maakt suggesties die je met één klik accepteert               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   AGENT ORCHESTRATOR                             │
│  Selecteert juiste agent op basis van context                   │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
   ┌─────────┐          ┌─────────┐          ┌─────────┐
   │  Risk   │          │Compliance│         │ Privacy │
   │  Agent  │          │  Agent  │          │  Agent  │
   └────┬────┘          └────┬────┘          └────┬────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                             ▼
                      ┌─────────────┐
                      │    TOOLS    │
                      │  Read/Write │
                      │  Knowledge  │
                      └─────────────┘
```

### 6.2 Agents (17 totaal)

#### Domein Agents (12)

| Agent | Expertise | Trigger Contexts |
|-------|-----------|------------------|
| **Risk Agent** | Leiden model, MAPGOOD, classificatie | risk_* |
| **Measure Agent** | Control design, effectiviteit | measure_* |
| **Compliance Agent** | BIO, ISO 27001, AVG, mappings | standard_*, requirement_*, soa_* |
| **Scope Agent** | Assets, BIA, dependencies | scope_*, asset_* |
| **Policy Agent** | Beleidsdocumenten, drafting | policy_*, document_* |
| **Assessment Agent** | Audits, findings, evidence | assessment_*, finding_* |
| **Incident Agent** | Incident handling, data breaches | incident_* |
| **Privacy Agent** | AVG, verwerkingen, DPIA | processing_*, dsr_* |
| **BCM Agent** | Continuïteitsplannen, BIA | continuity_*, bia_* |
| **Supplier Agent** | Third-party risk | supplier_* |
| **Improvement Agent** | Issues, acties, initiatieven | issue_*, action_*, initiative_* |

#### Management Agents (3)

| Agent | Expertise | Trigger Contexts |
|-------|-----------|------------------|
| **Planning Agent** | Jaarplanning, management reviews | planning_*, review_* |
| **Objectives Agent** | Doelstellingen, KPIs | objective_*, kpi_* |
| **Maturity Agent** | Volwassenheidsmodellen | maturity_* |

#### Systeem Agents (2)

| Agent | Expertise | Trigger Contexts |
|-------|-----------|------------------|
| **Workflow Agent** | Processen, goedkeuringen | workflow_*, approval_* |
| **Report Agent** | Rapportage, dashboards | report_*, dashboard_* |
| **Admin Agent** | Beheer, configuratie | admin_*, settings_* |

### 6.3 Tools (50+)

#### Read Tools
- `get_risk`, `search_risks`, `get_measures_for_risk`
- `get_measure`, `search_measures`
- `get_scope`, `search_scopes`, `get_scope_dependencies`
- `get_standard`, `get_requirement`, `search_requirements`
- `get_assessment`, `get_findings_for_assessment`
- `get_incident`, `search_incidents`
- `get_processing_activity`, `get_dsr`
- `get_continuity_plan`
- `get_workflow_instance`, `get_available_transitions`

#### Write Tools
- `update_risk`, `set_attention_quadrant`, `set_mitigation_approach`
- `create_measure`, `update_measure`, `link_measure_to_risk`
- `create_finding`, `create_corrective_action`
- `execute_transition`

#### Knowledge Tools
- `search_knowledge` (RAG)
- `get_methodology`
- `get_framework_info`
- `get_glossary_term`
- `get_org_context`

#### Utility Tools
- `create_suggestion`
- `request_agent_collaboration`
- `send_notification`

#### External Tools (toekomst)
- `search_topdesk`, `get_topdesk_ticket`, `create_topdesk_ticket`
- `get_azure_user`, `search_azure_users`

### 6.4 Knowledge Base

#### Structuur

```
AIKnowledgeBase
├── category: "platform"
│   └── Hoe werkt IMS, workflows, rollen
│
├── category: "methodology"
│   ├── Leiden model
│   ├── MAPGOOD
│   └── Impact/kwetsbaarheid bepaling
│
├── category: "framework"
│   ├── BIO
│   ├── ISO 27001
│   └── AVG
│
├── category: "best_practice"
│   └── Praktische richtlijnen
│
└── category: "terminology"
    └── Definities en glossary
```

#### Context Stack

```
┌─────────────────────────────────────────┐
│  1. AIPromptTemplate (hoe te gedragen)  │  ← Per situatie
├─────────────────────────────────────────┤
│  2. AIKnowledgeBase (methodiek)         │  ← Globaal
├─────────────────────────────────────────┤
│  3. OrganizationContext (organisatie)   │  ← Per tenant
├─────────────────────────────────────────┤
│  4. Huidige entity context              │  ← Waar user nu is
├─────────────────────────────────────────┤
│  5. Conversatie historie                │  ← Wat al besproken is
└─────────────────────────────────────────┘
```

### 6.5 Suggestions Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  AI analyseert situatie                                         │
│                     ▼                                           │
│  AI maakt AISuggestion:                                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  💡 Suggestie                                           │   │
│  │  Veld: attention_quadrant                               │   │
│  │  Waarde: MITIGATE                                       │   │
│  │  Reden: "Hoge impact (financieel) + ontbrekende EDR"   │   │
│  │  Confidence: 0.85                                       │   │
│  │                                                         │   │
│  │  [Accepteren]  [Aanpassen]  [Afwijzen]                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                     ▼                                           │
│  User klikt [Accepteren]                                        │
│                     ▼                                           │
│  Waarde wordt direct opgeslagen in Risk                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. Multi-Tenancy & Shared Services

### 7.1 Tenant Model

```
┌─────────────────────────────────────────────────────────────────┐
│                    SSC Bedrijfsvoering                          │
│                    (is_service_provider: true)                  │
│                                                                  │
│  Centrale maatregelen:                                          │
│  - MFA voor alle medewerkers                                    │
│  - Firewall beheer                                              │
│  - Backup infrastructuur                                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
            TenantRelationship (SHARED_SERVICES)
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   Gemeente    │   │   Gemeente    │   │   Gemeente    │
│   Amsterdam   │   │   Rotterdam   │   │   Den Haag    │
│               │   │               │   │               │
│ Ziet centrale │   │ Ziet centrale │   │ Ziet centrale │
│ maatregelen   │   │ maatregelen   │   │ maatregelen   │
└───────────────┘   └───────────────┘   └───────────────┘
```

### 7.2 Shared Measures

```python
class SharedMeasure(SQLModel, table=True):
    measure_id: int              # Originele maatregel (bij provider)
    consumer_tenant_id: int      # Wie ziet deze maatregel

    applicability_notes: str     # Hoe past dit bij de consumer
    visible_in_soa: bool         # Toon in Statement of Applicability

    # Consumer acknowledgment
    acknowledged: bool
    acknowledged_by_id: int
```

### 7.3 Coverage Type in SoA

```python
class CoverageType(str, Enum):
    LOCAL = "Local"              # Eigen maatregel
    SHARED = "Shared"            # Centrale maatregel
    COMBINED = "Combined"        # Beide
    NOT_COVERED = "Not Covered"  # Nog geen maatregel
    NOT_APPLICABLE = "N/A"       # Niet van toepassing
```

---

## 8. Integraties

### 8.1 Externe Systeem Koppelingen

| Systeem | Richting | Wat wordt gesynchroniseerd |
|---------|----------|---------------------------|
| **TopDesk** | Bi-directioneel | Incidents, Changes, Tickets |
| **Azure AD** | Inbound | Users, Groups, Roles |
| **SharePoint** | Inbound | Documents, Evidence |

### 8.2 Integration Config

```python
class IntegrationConfig(SQLModel, table=True):
    tenant_id: int
    name: str                    # "TopDesk Productie"
    system_type: str             # "TopDesk", "Azure AD"

    base_url: str
    auth_type: str               # "api_key", "oauth2"
    credentials_reference: str   # Verwijzing naar secrets manager

    sync_measures: bool
    sync_incidents: bool
    sync_direction: str          # "inbound", "outbound", "both"
```

### 8.3 External References

Elke entity kan linken naar externe systemen:

```python
# Op Measure, CorrectiveAction, Initiative, Incident:
external_system: str         # "TopDesk"
external_reference: str      # "CHG-12345"
external_url: str            # "https://company.topdesk.net/..."
```

---

## 9. Entity Reference

### 9.1 Alle Entities per Categorie

#### Multi-Tenancy (7)
| Entity | Beschrijving |
|--------|--------------|
| `Tenant` | Organisatie/gemeente |
| `TenantUser` | User-tenant koppeling met rol |
| `TenantRelationship` | Relaties tussen tenants (SSC) |
| `SharedMeasure` | Gedeelde maatregel |
| `SharedScope` | Gedeelde scope/asset |
| `VirtualScopeMember` | Membership in virtuele scope |
| `AccessRequest` | Toegangsverzoek voor gedeelde data |

#### Governance (8)
| Entity | Beschrijving |
|--------|--------------|
| `Standard` | Framework (BIO, ISO 27001) |
| `Requirement` | Eis uit een standaard |
| `RequirementMapping` | Mapping tussen requirements |
| `Policy` | Beleidsdocument |
| `Document` | Algemeen document |
| `Scope` | Asset, proces, organisatie-eenheid |
| `ScopeDependency` | Afhankelijkheid tussen scopes |
| `ApplicabilityStatement` | SoA entry |

#### Risk Management (12)
| Entity | Beschrijving |
|--------|--------------|
| `Risk` | Risico met Leiden classificatie |
| `RiskTemplate` | Risico template/catalogus |
| `RiskAppetite` | Risk appetite per tenant |
| `Threat` | Dreiging (MAPGOOD) |
| `ThreatActor` | Dreigingsactor |
| `Vulnerability` | Kwetsbaarheid |
| `RiskThreatLink` | Link risico-dreiging |
| `MeasureRiskLink` | Link maatregel-risico |
| `MeasureRequirementLink` | Link maatregel-requirement |
| `Issue` | Structureel probleem |
| `GapAnalysis` | Gap analyse bij standaard update |
| `GapAnalysisItem` | Item in gap analyse |

#### Measures (2)
| Entity | Beschrijving |
|--------|--------------|
| `Measure` | Beveiligingsmaatregel |
| `MeasureTemplate` | Maatregel template/catalogus |

#### Assessment (7)
| Entity | Beschrijving |
|--------|--------------|
| `Assessment` | Audit/assessment |
| `Finding` | Bevinding |
| `Evidence` | Bewijs |
| `AssessmentQuestion` | Assessment vraag |
| `AssessmentResponse` | Antwoord op vraag |
| `MaturityAssessment` | Volwassenheidsmeting |
| `MaturityDomainScore` | Score per domein |

#### Incidents (3)
| Entity | Beschrijving |
|--------|--------------|
| `Incident` | Security/privacy incident |
| `Exception` | Waiver/uitzondering |
| `CorrectiveAction` | Correctieve actie |

#### Privacy / PIMS (3)
| Entity | Beschrijving |
|--------|--------------|
| `ProcessingActivity` | Verwerkingsactiviteit (Art. 30) |
| `DataSubjectRequest` | Verzoek betrokkene |
| `ProcessorAgreement` | Verwerkersovereenkomst |

#### BCM (2)
| Entity | Beschrijving |
|--------|--------------|
| `ContinuityPlan` | Continuïteitsplan |
| `ContinuityTest` | Test/oefening |

#### Planning & Management (6)
| Entity | Beschrijving |
|--------|--------------|
| `CompliancePlanningItem` | Item in jaarplanning |
| `ManagementReview` | Directiebeoordeling |
| `ReviewSchedule` | Review planning |
| `Initiative` | Verbeterinitiatief |
| `InitiativeMilestone` | Mijlpaal in initiatief |
| `RiskAppetite` | Risk appetite definitie |

#### Objectives & KPIs (3)
| Entity | Beschrijving |
|--------|--------------|
| `Objective` | ISMS/PIMS/BCMS doelstelling |
| `ObjectiveKPI` | KPI voor doelstelling |
| `KPIMeasurement` | KPI meting |

#### Workflows (5)
| Entity | Beschrijving |
|--------|--------------|
| `WorkflowDefinition` | Workflow definitie |
| `WorkflowState` | State in workflow |
| `WorkflowTransition` | Transitie tussen states |
| `WorkflowInstance` | Actieve workflow |
| `WorkflowStepHistory` | Historie van stappen |

#### Users & Access (3)
| Entity | Beschrijving |
|--------|--------------|
| `User` | Gebruiker |
| `UserScopeRole` | Rol per scope |
| `TenantUser` | Tenant membership |

#### Communication (4)
| Entity | Beschrijving |
|--------|--------------|
| `Notification` | Notificatie |
| `Comment` | Comment (polymorf) |
| `Attachment` | Bijlage (polymorf) |
| `AuditLog` | Audit trail |

#### Tags & Settings (4)
| Entity | Beschrijving |
|--------|--------------|
| `Tag` | Tag/label |
| `EntityTag` | Tag koppeling |
| `SystemSetting` | Systeem instelling |
| `TenantSetting` | Tenant instelling |

#### Integrations (2)
| Entity | Beschrijving |
|--------|--------------|
| `IntegrationConfig` | Integratie configuratie |
| `IntegrationSyncLog` | Sync log |

#### Reports (3)
| Entity | Beschrijving |
|--------|--------------|
| `ReportTemplate` | Rapport template |
| `ScheduledReport` | Gepland rapport |
| `ReportExecution` | Rapport uitvoering |

#### AI System (10)
| Entity | Beschrijving |
|--------|--------------|
| `AIAgent` | Agent definitie |
| `AITool` | Tool definitie |
| `AIAgentToolAccess` | Agent-tool koppeling |
| `AIToolExecution` | Tool execution log |
| `AIConversation` | Conversatie |
| `AIConversationMessage` | Bericht in conversatie |
| `AISuggestion` | AI suggestie |
| `AIKnowledgeBase` | Kennisbank item |
| `AIPromptTemplate` | Prompt template |
| `KnowledgeArtifact` | Ruwe kennis (RAG) |

#### AI Support (2)
| Entity | Beschrijving |
|--------|--------------|
| `OrganizationContext` | Organisatie context |
| `Dashboard` | AI-gegenereerd dashboard |

### 9.2 Belangrijke Enums

```python
# Risk Management
class AttentionQuadrant(str, Enum):
    MITIGATE = "Mitigeren"
    ASSURANCE = "Zekerheid verkrijgen"
    MONITOR = "Meten & monitoren"
    ACCEPT = "Accepteren"

class MitigationApproach(str, Enum):
    REDUCE = "Reduceren"
    TRANSFER = "Overdragen"
    AVOID = "Vermijden"

class ThreatCategory(str, Enum):  # MAPGOOD
    MENSELIJK = "Menselijk falen"
    APPLICATIE = "Applicatie/Software falen"
    PROCES = "Proces falen"
    GEGEVENS = "Gegevens/Data issues"
    OMGEVING = "Omgeving"
    OPZET = "Opzettelijk handelen"
    DERDEN = "Derden"

class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class RiskAppetiteLevel(str, Enum):
    AVERSE = "Risicomijdend"
    MINIMAL = "Minimaal"
    CAUTIOUS = "Voorzichtig"
    MODERATE = "Gematigd"
    OPEN = "Open"
    HUNGRY = "Risicozoekend"

# Scope
class ScopeType(str, Enum):
    ORGANIZATION = "Organization"
    CLUSTER = "Cluster"
    DEPARTMENT = "Department"
    PROCESS = "Process"
    ASSET = "Asset"
    SUPPLIER = "Supplier"
    VIRTUAL = "Virtual"

class ClassificationLevel(str, Enum):
    PUBLIC = "Public"
    INTERNAL = "Internal"
    CONFIDENTIAL = "Confidential"
    SECRET = "Secret"

# Frameworks
class FrameworkType(str, Enum):
    BIO = "BIO"
    ISO27001 = "ISO27001"
    AVG = "AVG"
    BCM = "BCM"
    NEN7510 = "NEN7510"

# Workflow
class WorkflowStatus(str, Enum):
    NOT_STARTED = "Niet gestart"
    IN_PROGRESS = "In behandeling"
    WAITING_APPROVAL = "Wacht op goedkeuring"
    APPROVED = "Goedgekeurd"
    REJECTED = "Afgewezen"
    COMPLETED = "Afgerond"
    CANCELLED = "Geannuleerd"

# Privacy
class LegalBasis(str, Enum):
    CONSENT = "Toestemming"
    CONTRACT = "Overeenkomst"
    LEGAL_OBLIGATION = "Wettelijke verplichting"
    VITAL_INTEREST = "Vitaal belang"
    PUBLIC_TASK = "Publieke taak"
    LEGITIMATE_INTEREST = "Gerechtvaardigd belang"
```

---

## 10. Implementatie Roadmap

### 10.1 Fases

```
┌─────────────────────────────────────────────────────────────────┐
│  FASE 1: Foundation (Week 1-4)                                  │
│  ─────────────────────────────────────────────────────────────  │
│  • Database setup (PostgreSQL + pgvector)                       │
│  • Alembic migraties                                            │
│  • FastAPI basis + auth                                         │
│  • Core CRUD endpoints (Tenant, Scope, Risk, Measure)           │
├─────────────────────────────────────────────────────────────────┤
│  FASE 2: Core Features (Week 5-8)                               │
│  ─────────────────────────────────────────────────────────────  │
│  • Workflow engine                                              │
│  • Assessment module                                            │
│  • Compliance/SoA module                                        │
│  • Basic reporting                                              │
├─────────────────────────────────────────────────────────────────┤
│  FASE 3: AI Integration (Week 9-12)                             │
│  ─────────────────────────────────────────────────────────────  │
│  • Ollama/Mistral setup                                         │
│  • Knowledge base vullen                                        │
│  • 2 pilot agents (Risk, Workflow)                              │
│  • AI Chat Island UI                                            │
├─────────────────────────────────────────────────────────────────┤
│  FASE 4: Full AI & Polish (Week 13-16)                          │
│  ─────────────────────────────────────────────────────────────  │
│  • Alle 17 agents                                               │
│  • Tool implementaties                                          │
│  • Suggestions system                                           │
│  • Performance optimalisatie                                    │
├─────────────────────────────────────────────────────────────────┤
│  FASE 5: Integrations (Week 17-20)                              │
│  ─────────────────────────────────────────────────────────────  │
│  • TopDesk integratie                                           │
│  • Azure AD SSO                                                 │
│  • SharePoint documenten                                        │
├─────────────────────────────────────────────────────────────────┤
│  FASE 6: Production Ready (Week 21-24)                          │
│  ─────────────────────────────────────────────────────────────  │
│  • Security hardening                                           │
│  • Performance testing                                          │
│  • Documentation                                                │
│  • Pilot deployment                                             │
└─────────────────────────────────────────────────────────────────┘
```

### 10.2 Gerelateerde Documenten

| Document | Locatie |
|----------|---------|
| Systeem Design | `DESIGN.md` |
| Quick Start | `README.md` |
| AI Knowledge Plan | `docs/AI_KNOWLEDGE_IMPLEMENTATION_PLAN.md` |
| AI Agents Plan | `docs/AI_AGENTS_IMPLEMENTATION_PLAN.md` |
| Data Model | `backend/app/models/core_models.py` |
| Config | `backend/app/core/config.py` |
| Docker Setup | `docker-compose.yml` |

---

## Appendix A: Beslissingen Log

| Beslissing | Rationale |
|------------|-----------|
| Python + FastAPI | Native AI taal, async, type-safe |
| Lokale LLM (Ollama) | EU data sovereignty, geen cloud leakage |
| Leiden model | Praktischer dan traditioneel, Nederlandse context |
| MAPGOOD | Nederlandse standaard voor dreigingen |
| Generieke workflows | Herbruikbaar voor alle processen |
| Multi-agent systeem | Specialisatie per domein |
| Geen HRM (nu) | Overkill voor MVP, later toevoegen indien nodig |
| External references | IMS registreert, TopDesk/Azure voert uit |

---

## Appendix B: Glossary

| Term | Definitie |
|------|-----------|
| **Attention Quadrant** | Leiden model kwadrant (Mitigate/Assurance/Monitor/Accept) |
| **BIA** | Business Impact Analysis |
| **BIO** | Baseline Informatiebeveiliging Overheid |
| **BIV** | Beschikbaarheid, Integriteit, Vertrouwelijkheid |
| **MAPGOOD** | Dreigingscategorisering (Menselijk, Applicatie, Proces, Gegevens, Omgeving, Opzet, Derden) |
| **RAG** | Retrieval Augmented Generation |
| **RTO** | Recovery Time Objective |
| **RPO** | Recovery Point Objective |
| **SoA** | Statement of Applicability |
| **SSC** | Shared Service Center |

---

*Einde document*
