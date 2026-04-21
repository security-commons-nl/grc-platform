# grc-platform — ontwikkelaarsgids

Gids voor contributors die aan deze codebase werken.

## Project

IMS (Integrated Management System) is een Governance, Risk, and Compliance (GRC) platform voor ISMS, PIMS, en BCMS. Kernfilosofie: **"The Model leads. The API guards. Tools execute. AI supports."**

## Commands

### Applicatie draaien
```bash
# Start alle containers (db, api, frontend)
docker-compose up -d --build

# Database-migraties (3 migraties: schema → RLS → seed data)
docker-compose exec api alembic upgrade head

# Endpoints:
# - Frontend:          http://localhost:3000
# - API-docs (Swagger): http://localhost:8000/docs (development only)
# - Health check:       http://localhost:8000/api/v1/health
```

### Tests draaien
```bash
# Volledige suite (105 tests)
docker-compose exec api pytest --tb=short

# Eén domein
docker-compose exec api pytest tests/test_risks.py -v
```

### Lokale development
```bash
# Backend
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload

# Frontend
cd frontend && npm install && npm run dev
```

## Architectuur

### 4-laagse scheiding

1. **Layer 1 (Model)**: SQLAlchemy 2.0 modellen in `backend/app/models/core_models.py` — single source of truth
2. **Layer 2 (API)**: FastAPI in `backend/app/api/` — gatekeeper die RBAC en validatie afdwingt
3. **Layer 3 (Tools)**: Next.js 15 frontend in `frontend/` — geen business logic
4. **Layer 4 (AI)**: Mistral via Scaleway (EU) of lokaal Ollama

### Backend structuur
```
backend/
├── Dockerfile
├── requirements.txt
├── alembic.ini
├── alembic/
│   ├── env.py
│   └── versions/
│       ├── 001_initial_schema.py   ← 32 tabellen, 67 indexen
│       ├── 002_enable_rls.py       ← Row Level Security op 21 tabellen
│       └── 003_seed_reference_data.py ← 24 stappen, 26 afhankelijkheden, 5 standaarden, tenant Leiden
├── tests/                           ← 15 testbestanden, 105 tests
└── app/
    ├── main.py           # FastAPI app + CORS + lifespan
    ├── core/
    │   ├── config.py     # pydantic-settings (DB, AI, JWT, CORS via .env)
    │   ├── db.py         # async engine + AsyncSessionLocal + get_db
    │   └── auth.py       # JWT create/decode, get_current_user, require_role()
    ├── schemas/           # 14 Pydantic v2 schema-modules (Create/Update/Response)
    ├── api/v1/
    │   ├── api.py        # 15 routers
    │   └── endpoints/    # auth, tenants, steps, decisions, documents, standards,
    │                     # scopes, risks, controls, assessments, evidence,
    │                     # incidents, scores, knowledge, health
    └── models/
        └── core_models.py  # 32 SQLAlchemy 2.0 models, 6 domeinen
```

### Frontend structuur
```
frontend/
├── Dockerfile
├── package.json
└── src/
    ├── app/
    │   ├── login/page.tsx              # Dev-token login (OIDC-ready)
    │   └── (protected)/
    │       ├── layout.tsx              # Auth guard + sidebar + header
    │       ├── inrichten/              # Inrichtingsmodus (22 stappen)
    │       │   ├── page.tsx            # Stappen-overzicht
    │       │   ├── [stepId]/page.tsx   # Stap-detail + wizard
    │       │   ├── besluiten/page.tsx  # Besluitlog
    │       │   └── documenten/page.tsx # Documentviewer
    │       ├── beheer/                 # Beheermodus (GRC)
    │       │   ├── page.tsx            # Dashboard (12-cellenmatrix)
    │       │   ├── risicos/            # Risico-register
    │       │   ├── controls/           # Control-inventaris
    │       │   ├── assessments/        # Assessment-planner
    │       │   ├── bewijs/             # Evidence
    │       │   ├── bevindingen/        # Findings
    │       │   └── incidenten/         # Incident-register
    │       └── admin/                  # Beheer
    │           ├── gebruikers/         # Gebruikersbeheer
    │           └── tenant/             # Tenant-instellingen
    ├── components/
    │   ├── layout/    # sidebar, header, page-wrapper
    │   ├── ui/        # button, card, badge, input, select, tooltip, etc.
    │   ├── inrichten/ # step-card, step-progress-grid, decision-log-table, etc.
    │   ├── beheer/    # kpi-matrix, risk-table, control-table, etc.
    │   ├── ai/        # contextual-hint, chat-island, chat-panel (planned)
    │   └── shared/    # score-bar, status-badge, waarom-tooltip, role-guard
    ├── lib/
    │   ├── api-client.ts   # Typed fetch wrapper
    │   ├── api-types.ts    # TypeScript interfaces
    │   ├── auth.ts         # JWT decode + localStorage
    │   ├── constants.ts    # Rolhierarchie, statuslabels, kleuren
    │   ├── step-config.ts  # 24 stapdefinities (data-driven)
    │   └── hooks/          # SWR hooks per domein
    └── providers/          # Auth, tenant, SWR providers
```

### Data-modellen (6 domeinen, 32 tabellen)

- **Platform-breed**: tenants, regions, users, user_tenant_roles, user_region_roles, ai_audit_logs
- **Inrichtingsmodus**: ims_steps, ims_step_dependencies, ims_step_executions, ims_decisions, ims_documents, ims_document_versions, ims_step_input_documents, ims_gap_analysis_results
- **Normen & mapping**: ims_standards, ims_requirements, ims_requirement_mappings, ims_tenant_normenkader, ims_standard_ingestions
- **GRC-kern**: ims_scopes, ims_risks, ims_controls, ims_risk_control_links, ims_assessments, ims_findings, ims_corrective_actions, ims_evidence, ims_incidents
- **Scores**: ims_maturity_profiles, ims_setup_scores, ims_grc_scores
- **RAG-store**: ims_knowledge_chunks (pgvector, twee lagen: normatief + organisatie)

### Authenticatie & autorisatie

- **JWT** met dev-token (development) en agent-token (service accounts)
- **RBAC**: 6 rollen met hiërarchie: admin > strategisch_lid > tactisch_lid > discipline_eigenaar > lijnmanager > viewer
- **RLS**: Row Level Security op 21 tenant-scoped tabellen
- **OIDC-ready**: auth-laag is voorbereid op externe identity providers

### Configuratie

Environment variables via `.env`:
- Database: `POSTGRES_SERVER`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- AI: `AI_API_BASE`, `AI_MODEL_NAME`
- Auth: `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`
- CORS: `ALLOWED_ORIGINS` (default: `http://localhost:3000`)
- Environment: `ENVIRONMENT` (development/production)

### UI-principes (K14)

- **Geen dropdowns voor statuswijzigingen** — gebruik directe actieknoppen
- **Role-aware**: elke view gefilterd op gebruikersrol
- **Step-aware**: actieve stap centraal, toekomstige stappen gedempt
- **Complexity ceiling**: max 5 vragen per wizard-scherm
- **AI is altijd adviserend**: AI-concepten altijd gelabeld als "concept"

## Ontwerpprincipes

- **EU Data Sovereignty**: AI defaults naar localhost. Externe AI-APIs alleen met expliciete juridische clearance.
- **RBAC-afdwinging**: alle toegang via JWT met tenant_id + role. RLS als defense-in-depth.
- **Onveranderlijke audit trail**: `ims_decisions` en `ims_document_versions` hebben geen UPDATE/DELETE.
- **Rosetta Stone-patroon**: `RequirementMapping` maakt cross-framework mapping (BIO↔ISO27001) mogelijk met AI confidence scores.
- **Database leading**: documenten zijn gegenereerde views van DB-data, niet opgeslagen bestanden.
- **Elke bouwsteen heeft een eval**: geen code zonder test.
- **Documentatie is auto-generated**: `python generate-docs.py` genereert `docs/platform-overzicht.html` (functioneel) + `docs/architectuur.html` (technisch) uit de codebase. Nooit handmatig HTML bewerken.
