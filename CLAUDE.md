# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

IMS (Integrated Management System) is a Governance, Risk, and Compliance (GRC) platform for ISMS, PIMS, and BCMS. Core philosophy: **"The Model leads. The API guards. Tools execute. AI supports."**

## Commands

### Running the Application
```bash
# Start database and API via Docker
docker-compose up -d

# Access points:
# - API Docs (Swagger): http://localhost:8000/docs (development only)
# - Health check: http://localhost:8000/api/v1/health

# Run database migrations
docker-compose exec api alembic upgrade head
```

### Local Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Workflow

**Na elke code-wijziging: ALTIJD zelf committen en pushen naar origin.** Niet vragen, gewoon doen.

```bash
git add <files> && git commit -m "..." && git push origin main
```

- `origin` = GitHub — **altijd automatisch pushen na wijzigingen**

## Architecture

### 4-Layer Strict Separation

1. **Layer 1 (Model)**: SQLAlchemy 2.0 models in `backend/app/models/core_models.py` — single source of truth
2. **Layer 2 (API)**: FastAPI in `backend/app/api/` — gatekeeper enforcing RBAC and validation
3. **Layer 3 (Tools)**: Frontend (Next.js — planned) — geen business logic
4. **Layer 4 (AI)**: Mistral via Scaleway (EU) of lokaal Ollama

### Key Backend Structure
```
backend/
├── Dockerfile
├── requirements.txt
├── alembic.ini
├── alembic/
│   ├── env.py
│   └── versions/001_initial_schema.py   ← 32 tabellen, 67 indexen
└── app/
    ├── main.py           # FastAPI app + CORS + lifespan
    ├── core/
    │   ├── config.py     # pydantic-settings (DB, AI, JWT via .env)
    │   └── db.py         # async engine + AsyncSessionLocal + get_db
    ├── api/v1/
    │   ├── api.py        # Router
    │   └── endpoints/
    │       └── health.py # GET /api/v1/health
    └── models/
        └── core_models.py  # 32 SQLAlchemy 2.0 models, 6 domeinen
```

### Data Model Domains (in core_models.py)

- **Governance**: Standard, Requirement, RequirementMapping (Rosetta Stone for cross-framework mapping), Policy
- **Scope Management**: Scope (hierarchical: Organization→Cluster→Process→Asset→Supplier), ScopeDependency, BIA ratings
- **Risk Management**: Risk (impact/likelihood heatmap), Measure, MeasureRiskLink
- **Verification (PDCA Check)**: Assessment (DPIA/Pentest/Audit/Self-Assessment), Evidence, Finding
- **Improvement (PDCA Act)**: CorrectiveAction, Incident, Exception (waivers)
- **RBAC**: User, Role (Admin/ProcessOwner/Editor/Viewer), UserScopeRole
- **AI/RAG**: OrganizationContext, KnowledgeArtifact, Dashboard (generative UI configs)

### Configuration

Environment variables via `.env` file or defaults in `backend/app/core/config.py`:
- Database: `POSTGRES_SERVER`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- AI: `AI_API_BASE` (defaults to `http://localhost:11434/v1` for local Ollama), `AI_MODEL_NAME`

## Skills

Claude Code skills are stored externally at `~/.claude/skills/` (178 skills), not in this repo. Key sources:

- **claude-skills** (secondsky): `https://github.com/secondsky/claude-skills` — 169 plugins covering API, security, testing, database, frontend, and more
- **skill-seekers** (yusufkaraaslan): `https://github.com/yusufkaraaslan/Skill_Seekers` — generates LLM skills from docs, codebases, and GitHub repos

### IMS-relevant skills (installed)

| Skill | Purpose |
|-------|---------|
| `api-error-handling` | Standardized error responses across 24 API routers |
| `api-testing` | pytest patterns for FastAPI endpoint coverage |
| `database-schema-design` | Schema guidance for 40+ SQLModel entities |
| `access-control-rbac` | RBAC enforcement for UserScopeRole model |
| `api-pagination` | Robust pagination for GRC data endpoints |
| `logging-best-practices` | Audit logging for compliance |
| `health-check-endpoints` | Application-level health checks (db, ollama, integrations) |
| `api-security-hardening` | Multi-tenant API hardening (CORS, headers, rate limiting) |
| `websocket-implementation` | Real-time updates and webhook integration |
| `sql-query-optimization` | Query performance for pgvector + multi-tenant filtering |
| `skill-seekers` | Generate new skills from documentation or codebases |
| `mcp-builder` | 4-phase guide for building MCP servers (Python FastMCP / Node TypeScript) |
| `webapp-testing` | Playwright-based web app testing — screenshots, DOM inspection, server lifecycle |
| `claude-code-showcase` | Reference patterns for skills, agents, hooks, commands, and CI/CD workflows |
| `prowler-mcp` | Cloud security posture — 1000+ checks, 70+ compliance frameworks, remediation |

### Managing skills

```bash
# Install a plugin from claude-skills marketplace
claude plugin install <plugin-name>@claude-skills

# Generate a new skill from docs
skill-seekers scrape --url https://docs.example.com
skill-seekers package output/example/ --target claude

# Skills location
ls ~/.claude/skills/
```

## Agent Sync Rule

**After every frontend or functionality change**, check if the corresponding domain agent in `backend/app/agents/domains/` is up to date:

1. Identify which domain agent(s) the change affects (e.g. risks page → `risk_agent.py`, policy wizard → `policy_agent.py`)
2. Read the agent's `get_system_prompt()` — does it mention the new/changed capability?
3. Check `get_tools()` — does the agent have the tools needed to support the user with this feature?
4. If not → update the system prompt and/or tools so the AI assistant can guide users on the new functionality

**Domain agents** (`backend/app/agents/domains/`):

| Agent | Domain | Covers |
|-------|--------|--------|
| `risk_agent` | Risk management | Risks, In Control, MAPGOOD, decisions |
| `policy_agent` | Governance | Policies, principles, traceability |
| `bcm_agent` | Business continuity | BIA, continuity plans |
| `compliance_agent` | Compliance | Frameworks, requirements, mappings |
| `incident_agent` | Incidents | Incident management, response |
| `privacy_agent` | Privacy | AVG/GDPR, DPIA |
| `scope_agent` | Scope management | Scopes, dependencies, hierarchy |
| `assessment_agent` | Verification | Assessments, audits, evidence |
| `measure_agent` | Controls | Measures, control implementation |
| `supplier_agent` | Suppliers | Third-party management |
| `improvement_agent` | Improvement | Corrective actions, exceptions |
| `maturity_agent` | Maturity | Maturity assessments |
| `planning_agent` | Planning | Planning & roadmaps |
| `report_agent` | Reporting | Reports & dashboards |
| `workflow_agent` | Workflow | Status transitions, approvals |
| `objectives_agent` | Objectives | Goals & KPIs |
| `admin_agent` | Administration | Users, roles, configuration |

> The user must always get accurate, up-to-date guidance from the AI assistant — never let the agents fall behind the actual application.

## Design Principles

- **EU Data Sovereignty**: AI defaults to localhost. Never configure external AI APIs without explicit legal clearance.
- **RBAC Enforcement**: All access control flows through UserScopeRole linking users to scopes with specific roles.
- **Workflow States**: Policies follow Draft→Review→Approved→Published. Assessments follow Planned→Active→Completed.
- **Rosetta Stone Pattern**: RequirementMapping enables many-to-many mapping between different frameworks (BIO↔ISO27001) with AI confidence scores.
