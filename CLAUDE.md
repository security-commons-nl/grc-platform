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
# - API Docs (Swagger): http://localhost:8000/docs
# - PGAdmin: http://localhost:5050 (admin@ims.local / admin)
```

### Local Backend Development
```bash
cd IMS/backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Architecture

### 4-Layer Strict Separation

1. **Layer 1 (Model)**: SQLModel definitions in `backend/app/models/core_models.py` - single source of truth
2. **Layer 2 (API)**: FastAPI in `backend/app/api/` - gatekeeper enforcing RBAC and validation
3. **Layer 3 (Tools)**: Frontend (planned React/Vue) - "dumb" glass pane with no business logic
4. **Layer 4 (AI)**: Local-first Ollama/Mistral - no cloud data leakage by default

### Key Backend Structure
```
IMS/backend/app/
├── main.py           # FastAPI app initialization with lifespan
├── core/
│   ├── config.py     # Settings (DB, AI config via pydantic-settings)
│   └── db.py         # Database session management
├── api/v1/
│   ├── api.py        # Router configuration
│   └── endpoints/    # CRUD endpoints
└── models/
    └── core_models.py  # All SQLModel entities
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

## Design Principles

- **EU Data Sovereignty**: AI defaults to localhost. Never configure external AI APIs without explicit legal clearance.
- **RBAC Enforcement**: All access control flows through UserScopeRole linking users to scopes with specific roles.
- **Workflow States**: Policies follow Draft→Review→Approved→Published. Assessments follow Planned→Active→Completed.
- **Rosetta Stone Pattern**: RequirementMapping enables many-to-many mapping between different frameworks (BIO↔ISO27001) with AI confidence scores.
