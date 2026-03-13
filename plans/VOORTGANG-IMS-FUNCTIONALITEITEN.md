# IMS — Integrated Management System

> **Model-gedreven GRC-platform voor ISMS, PIMS en BCMS — met lokale AI, PDCA-workflow en Nederlandse compliance.**

IMS is een volledig Governance, Risk & Compliance-platform dat **normen, risico's, controls, audits en bewijs** centraal beheert. Gebouwd voor organisaties (gemeenten, zorginstellingen, waterschappen, SSC's) die meerdere managementsystemen willen combineren in **een enkele bron van waarheid**, met strikte scheiding van data, logica en UI, en optionele **local-first AI** (EU data sovereignty).

---

## Platform in cijfers

| Onderdeel | Aantal | Toelichting |
|-----------|--------|-------------|
| **Data-entiteiten** | 90+ | 15 domeinen, multi-tenant aware, incl. RiskScope koppeltabel |
| **API-routers** | 34 | RESTful CRUD + gespecialiseerde operaties |
| **API-endpoints** | 220+ | Inclusief workflow-transities, BIA-berekening, simulatie, appetite-evaluatie |
| **AI-agenten** | 19 | Domein-specifieke LLM-experts met tools |
| **Frontend-pagina's** | 25 | Responsive (desktop + mobiel), volledig Nederlands |
| **Frameworks** | 10+ | BIO, ISO 27001/27002/27701/22301, AVG, NEN 7510, NIST, CIS |
| **Rollen (RBAC)** | 5 | Drie-lijnen model: Beheerder, Coordinator, Eigenaar, Medewerker, Toezichthouder |
| **Externe integraties** | 4 | TopDesk, ServiceNow, Proquro, BlueDolphin |

---

## Kernfilosofie

> **"The Model leads. The API guards. Tools execute. AI supports."**

```
Laag 1: MODEL (Data)     — SQLModel + PostgreSQL — single source of truth
Laag 2: API (Logica)     — FastAPI — gatekeeper voor RBAC, validatie, workflows
Laag 3: TOOLS (UI)       — Reflex (Python→React) — dunne glasplaat, geen business logic
Laag 4: AI (Intelligence) — Ollama/Mistral/Scaleway — lokaal-first, EU data sovereignty
```

---

## Wat IMS doet

### ISMS (Information Security Management System)
- **Risicobeheer** met "In Control"-model (4 kwadranten: Mitigeren / Zekerheid / Monitoren / Accepteren)
- **RiskScope contextualisatie** — risico's bestaan per scope met eigen scores, behandeling en acceptatie
- **Risicotolerantie (Risk Appetite)** — dynamische heatmap met 6 niveaus (Afkerig→Hongerig), per domein configureerbaar
- **MAPGOOD-dreigingsmodel** (Menselijk, Applicatie, Proces, Gegevens, Omgeving, Opzet, Derden)
- **Risicokader** met configureerbare impact/kans-schalen en appetite-thresholds
- **Rosetta Stone** — cross-framework mapping (BIO ↔ ISO 27001 ↔ AVG) met AI-confidence scores
- **Statement of Applicability (SoA)** per scope en standaard
- **Monte Carlo-risicosimulatie** voor financiele kwantificering
- **Formeel besluitlog** voor risicoacceptatie boven score 9

### PIMS (Privacy Information Management System)
- **Verwerkingsregister** (AVG Art. 30) met grondslagen, bewaartermijnen, doorgifte
- **Betrokkenenverzoeken** (Art. 15-22) met deadline-tracking (30 dagen)
- **Datalekmelding** met 72-uurs AP-deadline (Art. 33) en betrokkenen-notificatie (Art. 34)
- **Verwerkersovereenkomsten** (Art. 28) gekoppeld aan leveranciers
- **DPIA-ondersteuning** als assessmenttype met vragenlijst

### BCMS (Business Continuity Management System)
- **Business Impact Analysis (BIA)** met automatische CIA-scoring en RTO/RPO/MTPD-berekening
- **Continuiteitsplannen** (BCP, DRP, Crisismanagement, Communicatie, IT Recovery)
- **Continuiteitstesten** (Tabletop, Walkthrough, Simulatie, Full Interruption)
- **Automatische terugschrijving** van BIA-resultaten naar scope-classificatie

### Governance & Compliance
- **Beleidsmanagement** met workflow (Concept → Review → Goedgekeurd → Gepubliceerd)
- **Beleidsuitgangspunten** (Hiaat 6) — traceerbare keten Policy → Principe → Risico → Control
- **Jaarplanning** voor audits, certificeringen, management reviews
- **Management Review** (ISO 27001 §9.3 / ISO 22301 §9.3) met inputs/outputs
- **Doelstellingen & KPI's** (ISO 27001 §6.2) met meetwaarden en trends

### Assessments & Verificatie (PDCA Check)
- **8 assessmenttypes**: DPIA, Pentest, Audit, Self-Assessment, BIA, Compliance Journey, Supplier Assessment, Maturity Assessment
- **7-fasen workflow**: Aangevraagd → Planning → Voorbereiding → In uitvoering → Review → Rapportage → Afgerond
- **Bevindingen** met ernst-classificatie en koppeling aan controls/requirements
- **Bewijs** (Evidence) met AI-analyse mogelijkheid
- **Correctieve acties** met deadline-tracking en externe systeem-koppeling

### Verbetering (PDCA Act)
- **ACT-feedbackloop** (Hiaat 7) — finding sluiten vereist afgeronde correctieve actie
- **Verbeterinitiatieven** met mijlpalen, business case, en voortgang
- **Gap-analyse** bij standaard-versiewijzigingen (bijv. ISO 27001:2013 → 2022)
- **Issues** (structurele problemen) vs. incidentele bevindingen
- **Backlog** voor feature requests en verbeterideeeen

### AI-assistentie (19 agenten)
- **Domeinagenten** (11): Risk, Measure, Compliance, Policy, Privacy, BCM, Incident, Improvement, Assessment, Scope, Supplier
- **Managementagenten** (3): Planning, Objectives, Maturity
- **Systeemgenten** (5): Workflow, Report, Dashboard, Admin, Onboarding
- **RAG-kennisbank** op pgvector met organisatiecontext en methodologie
- **AI-suggesties** met accept/reject workflow en audit trail
- **Multi-provider fallback**: Mistral (FR) → Scaleway (FR) → Ollama (lokaal)

### Integraties & Rapportage
- **TopDesk** — bi-directionele sync van incidenten en correctieve acties
- **ServiceNow** — incidents, changes, users
- **Proquro / BlueDolphin** — compliance en risico-data
- **Executive dashboard** met KPI's, compliance %, heatmap, trends
- **Rapporttemplates** met scheduling (dagelijks/wekelijks/maandelijks/kwartaal)
- **Relatiegrafiek** — interactieve visualisatie van entity-relaties

---

## Architectuur

### Technologiestack

| Component | Technologie | Reden |
|-----------|-------------|-------|
| **Backend** | Python + FastAPI (async) | Native AI-taal, type-safe, high-concurrency |
| **ORM** | SQLModel | Pydantic + SQLAlchemy in een |
| **Database** | PostgreSQL 15 + pgvector | ACID, vector embeddings voor RAG |
| **AI** | LangChain + Ollama/Mistral/Scaleway | EU data sovereignty, multi-provider fallback |
| **Frontend** | Reflex (Python → React/Vite) | Full-stack Python, responsive UI |
| **Auth** | JWT + bcrypt | Enterprise-ready, scope-based RBAC |
| **Rate Limiting** | slowapi | DDoS-bescherming |
| **Migraties** | Alembic (14 versies) | Schema-evolutie |
| **Observability** | Langfuse (self-hosted) | LLM-tracing, EU-compliant |

### Datamodel (85+ entiteiten)

```
Multi-Tenancy (7)     Tenant, TenantUser, TenantRelationship, SharedControl, SharedScope, ...
Governance (8)        Standard, Requirement, RequirementMapping, Policy, PolicyPrinciple, ...
Scope (2)             Scope (hierarchisch), ScopeDependency
Risk Management (12)  Risk, RiskScope, RiskTemplate, RiskFramework, RiskAppetite, Threat, ThreatActor, ...
Controls (5)          Measure, Control, ControlMeasureLink, ControlRiskLink, ControlRiskScopeLink
Assessment (5)        Assessment, AssessmentQuestion, AssessmentResponse, Evidence, BIAThreshold
Improvement (4)       Finding, Issue, CorrectiveAction, GapAnalysis
Privacy (3)           ProcessingActivity, DataSubjectRequest, ProcessorAgreement
BCM (2)               ContinuityPlan, ContinuityTest
Incidents (2)         Incident, Exception
Management (6)        Decision, DecisionRiskScopeLink, ManagementReview, CompliancePlanningItem, InControlAssessment, ...
Objectives (3)        Objective, ObjectiveKPI, KPIMeasurement
Initiatives (3)       Initiative, InitiativeMilestone, BacklogItem
Workflows (5)         WorkflowDefinition, WorkflowState, WorkflowTransition, WorkflowInstance, ...
Documents (4)         Document, Attachment, Comment, Notification
Audit (3)             AuditLog, ReviewSchedule, Tag/EntityTag
AI System (10)        AIAgent, AITool, AIConversation, AISuggestion, AIKnowledgeBase, ...
Reports (3)           ReportTemplate, ScheduledReport, ReportExecution
Integrations (2)      IntegrationConfig, IntegrationSyncLog
Settings (2)          SystemSetting, TenantSetting
```

### Security & Compliance

| Principe | Implementatie |
|----------|---------------|
| **EU Data Sovereignty** | AI draait lokaal (Ollama) of EU-cloud (Mistral/Scaleway FR), nooit US |
| **Multi-Tenant Isolatie** | Elke query filtert op tenant_id, scope-based RBAC |
| **Drie-Lijnen Model** | 5 rollen: Beheerder, Coordinator, Eigenaar, Medewerker, Toezichthouder |
| **Audit Trail** | AuditLog op elke CREATE/UPDATE/DELETE/APPROVE/REJECT |
| **AI Governance** | AI adviseert, mens beslist (AVG Art. 22) — accept/reject workflow |

---

## Frontend (25 pagina's)

### Navigatiestructuur

```
MS Hub                       — PDCA-overzicht met metrics per fase (alleen Eigenaar+/Toezichthouder)
Dashboard                    — Executive overzicht, taken, heatmap, ACT-waarschuwingen

DOEN (Operationeel)
  Risico's                   — Risicoregister met 4x4 matrix, kwadranten, scope-contextualisatie
  Controls                   — Control-implementaties per scope met risico/RiskScope-koppeling
  Assessments                — 8 types, 7-fasen workflow, BIA-vragenlijst, bevindingen, acties
  Incidenten                 — Incident/datalek-registratie met ernst en status
  In-Control                 — Per-scope controle-status dashboard

ONTDEKKEN (Kennis & Analyse)
  Compliance (SoA)           — Statement of Applicability per scope/standaard
  Besluiten                  — Formeel besluitlog met risico-koppeling
  Frameworks                 — Standaarden, requirements, Rosetta Stone mappings
  Maatregelen                — Herbruikbare maatregelencatalogus
  Beleidsuitgangspunten      — Principes met traceerbaarheid naar controls
  Risicokader                — Impact/kans-schalen, appetite, activering
  Analyses                   — Monte Carlo-risicosimulatie
  Relaties                   — Interactieve entity-relatie grafiek
  Rapportage                 — Executive KPI's, compliance %, trends
  Backlog                    — Verbeterideeën en feature requests

INRICHTEN (Configuratie)
  Mijn Organisatie           — 6-staps onboarding wizard
  Risicotolerantie           — Dynamische risk appetite per domein, heatmap, evaluatie
  Beleid                     — Beleidsdocumenten met goedkeuringsworkflow
  Scopes                     — Organisatiehierarchie (Org→Cluster→Afdeling→Proces→Asset)
  Assets                     — IT-assets inventaris
  Leveranciers               — Third-party management

BEHEER (Administratie)
  Gebruikers                 — Accountbeheer, rolletoewijzing per scope
  Beheer                     — Wachtwoorden, systeemstatus, auditlog
```

### MS Hub & PDCA-reis

De **MS Hub** biedt een visueel PDCA-overzicht met metrics per fase en een **7-staps implementatiereis**:

1. Organisatie inrichten → `/organization`
2. Risicoprofiel → `/risks`
3. Governance → `/frameworks`
4. Controls & Maatregelen → `/controls`
5. Assessments → `/assessments`
6. Compliance → `/compliance`
7. Rapportage → `/reports`

---

## 9 Hiaten (Nederlandse compliance-features)

| # | Feature | Beschrijving | Pagina |
|---|---------|-------------|--------|
| 1 | **Besluitlog** | Formele besluiten met type, motivering, risico-koppeling en verloopdatum | `/decisions` |
| 2 | **Scope Governance** | Scope-vaststelling met bevoegdheid, geldigheid en automatische verloop | `/scopes` |
| 3 | **Risicokader** | Configureerbare schalen, appetite, activering als tenant-default | `/risk-framework` |
| 4 | **Organisatieprofiel** | 6-staps wizard (identiteit, governance, IT, privacy, continuiteit, mensen) | `/organization` |
| 5 | **In-Control Status** | Per-scope beoordeling: In control / Beperkt / Niet in control | `/in-control` |
| 6 | **Beleidsuitgangspunten** | Policy → Principe → Requirement → Control traceerbaarheid | `/policy-principles` |
| 7 | **ACT-feedbackloop** | Finding sluiten vereist afgeronde correctieve actie + overdue-waarschuwingen | Dashboard + Assessments |
| 8 | **RiskScope Contextualisatie** | Risico's bestaan per scope met eigen scores, behandeling en acceptatie | `/risks` |
| 9 | **Risicotolerantie** | Dynamische appetite per domein (6 niveaus), heatmap-zones, bulk-evaluatie | `/risk-appetite` |

---

## Quick Start

### 1) Configureer environment
```bash
cp .env.example .env
# Vul de waarden in (Postgres, AI providers, integraties)
```

### 2) Start de stack
```bash
docker-compose up -d
```

### 3) Start de frontend (lokale ontwikkeling)
```bash
cd frontend
python -m reflex run
```

### 4) Toegangspunten

| Service | URL | Doel |
|---------|-----|------|
| **Frontend** | http://localhost:3000 | Reflex UI |
| **API docs (Swagger)** | http://localhost:8000/docs | Interactieve API-documentatie |
| **pgAdmin** | http://localhost:5050 | Database-beheer |
| **Ollama** | http://localhost:11434 | Lokale LLM API |

---

## Repo-indeling

```
IMS/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py             # App-initialisatie, middleware, lifespan
│   │   ├── core/               # Config, database, RBAC, security, CRUD, risk_appetite_engine
│   │   ├── api/v1/
│   │   │   ├── api.py          # 34 router-registraties
│   │   │   └── endpoints/      # Endpoint-implementaties per domein
│   │   ├── models/
│   │   │   └── core_models.py  # 90+ SQLModel entiteiten (incl. RiskScope, ControlRiskScopeLink)
│   │   ├── agents/             # 19 AI-agenten met tools
│   │   │   ├── orchestrator.py # Agent-selectie op basis van context
│   │   │   └── domains/        # Domein-specifieke agenten
│   │   └── services/           # Knowledge, AI gateway, integraties, sync
│   └── alembic/                # 14 database-migraties
├── frontend/                   # Reflex frontend
│   └── ims/
│       ├── ims.py              # App + routing (25 pagina's)
│       ├── pages/              # Pagina-componenten
│       ├── state/              # 22+ reactive state classes
│       ├── components/         # Layout, heatmap, chat, grafiek, guidance
│       └── api/client.py       # 120+ API-methoden (httpx async)
├── plans/                      # Implementatieplannen en roadmaps
├── docs/                       # Ontwerp- en architectuurdocumentatie
├── docker-compose.yml          # 5 services (db, api, pgadmin, ollama, frontend)
└── .env.example                # Environment configuratie template
```

---

## Documentatie

| Document | Beschrijving |
|----------|--------------|
| **[Platform Features](docs/PLATFORM_FEATURES.md)** | Gedetailleerde beschrijving van alle functionaliteit per domein |
| [Complete Design Overview](docs/COMPLETE_DESIGN_OVERVIEW.md) | Volledig systeemontwerp (85+ entiteiten, workflows, AI) |
| [Architecture Principles](docs/ARCHITECTURE_PRINCIPLES.md) | 4-laags architectuurprincipes |
| [AI Agents Implementation](docs/AI_AGENTS_IMPLEMENTATION_PLAN.md) | 19 agenten, tools, handoff flows |
| [AI Knowledge Plan](docs/AI_KNOWLEDGE_IMPLEMENTATION_PLAN.md) | RAG-architectuur, embeddings, kennisbank |
| [Roles & Responsibilities](docs/IMS%20ROLES%20AND%20RESPONSIBILITIES.md) | Drie-lijnen model, rolbeschrijvingen |
| [Technical Decisions](docs/TECHNICAL_DECISIONS.md) | AI governance, performance, streaming |
| [Development Workflow](docs/DEVELOPMENT_WORKFLOW.md) | Git, CI/CD, deployment |
| [Gap Analysis](docs/GAP_ANALYSIS.md) | Feature-gap analyse |

---

## Recente wijzigingen (februari 2026)

### RiskScope Contextualisatie
Risico's zijn nu **scope-gebonden**: elk risico kan in meerdere scopes bestaan met eigen impact/kans-scores, behandelstrategie en acceptatiestatus. Nieuwe koppeltabellen (`RiskScope`, `ControlRiskScopeLink`, `DecisionRiskScopeLink`) ondersteunen scope-specifieke controls en besluiten. Alle domein-agenten zijn bijgewerkt om met RiskScope te werken.

### Risk Appetite Engine
Nieuwe **risicotolerantie-engine** met 6 niveaus (Afkerig, Minimaal, Voorzichtig, Gematigd, Open, Hongerig), configureerbaar per domein (ISMS, Privacy, BCM, Financieel, Reputatie, Compliance). Genereert een dynamische 4×4 heatmap met vier zones (Acceptabel, Voorwaardelijk, Escalatie, Onacceptabel). Evaluatie-endpoints beoordelen individuele RiskScopes of hele scopes/tenants tegen de ingestelde appetite. Frontend-pagina onder INRICHTEN met heatmap-visualisatie, domein-instellingen en evaluatie-statistieken.

### Navigatie-herstructurering
- Compliance en Besluiten verplaatst van DOEN naar ONTDEKKEN
- Nieuwe pagina **Risicotolerantie** onder INRICHTEN
- MS Hub zichtbaar voor Eigenaar+ en Toezichthouder
- Rol-gebaseerde navigatie: minimaal menu per rol (Medewerker ziet alleen DOEN)

### Bugfixes & stabilisatie
- Control-risico dropdown filtert nu al-gekoppelde risico's
- Enum-creatie in Alembic-migraties gebruikt raw SQL om duplicate-type fouten te voorkomen
- X-User-ID headers toegevoegd aan MS Hub, Report en Journey states
- Sidebar logo-uitlijning verbeterd
- VPS deployment-fixes (CORS, api_url, LocalStorage type safety)

## Status

IMS is actief in ontwikkeling en draait op een Hetzner VPS. De kernfunctionaliteit (risicobeheer, assessments, compliance, incidenten, AI-agenten, PDCA-workflow) is operationeel. Recente ontwikkeling richtte zich op RiskScope-contextualisatie, dynamische risicotolerantie en navigatie-herstructurering. Lopende ontwikkeling richt zich op productie-hardening, security-audit en enterprise-readiness.

---

## Licentie & Contact

IMS is proprietary software. Voor vragen of bijdragen, neem contact op met het ontwikkelteam.
