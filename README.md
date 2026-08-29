# grc-platform

GRC-platform voor ISMS, PIMS en BCMS in een systeem.

Status: in gebruik. Draait bij een organisatie en heeft groene tests.

> **Model-gedreven GRC-platform voor ISMS, PIMS en BCMS - met lokale AI, PDCA-workflow en Nederlandse compliance.**
>
> Internationaal ook bekend als een Integrated Management System (IMS).

[![Bijdragen](https://img.shields.io/badge/📝_Bijdragen-238636?style=for-the-badge)](../../issues/new/choose)&nbsp;&nbsp;&nbsp;&nbsp;[![Meepraten](https://img.shields.io/badge/💬_Meepraten-0969da?style=for-the-badge)](../../discussions)

👉 **Iets delen, feedback geven of een vraag stellen?** Klik op een van de knoppen hierboven - geen Git-ervaring nodig. Zie [CONTRIBUTING.md](CONTRIBUTING.md) voor meer opties.

Het GRC-platform is een Governance, Risk & Compliance-platform dat **normen, risico's, controls, audits en bewijs** centraal beheert. Gebouwd voor gemeenten en publieke organisaties die meerdere managementsystemen willen combineren in **een enkele bron van waarheid**.

## Voor wie

CISO's, ISO's en privacy officers bij publieke organisaties.

## Snel starten

```bash
# Clone en start
git clone https://github.com/security-commons-nl/grc-platform.git
cd grc-platform
cp .env.example .env    # Pas wachtwoorden aan
docker-compose up -d --build

# Database migraties (inclusief seed data)
docker-compose exec api alembic upgrade head

# Tests draaien
docker-compose exec db psql -U postgres -c "CREATE DATABASE ims_test;"
docker-compose exec db psql -U postgres -d ims_test -c "CREATE EXTENSION IF NOT EXISTS vector;"
docker-compose exec api pytest --tb=short
```

### Toegangspunten

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:3000 |
| **API Docs** | http://localhost:8000/docs |
| **Health** | http://localhost:8000/api/v1/health |

## Bijdragen

Zie de [CONTRIBUTING](https://github.com/security-commons-nl/.github/blob/main/CONTRIBUTING.md) van de organisatie: daar staat per project een formulier, ook zonder Git-ervaring.

Zie [CONTRIBUTING.md](CONTRIBUTING.md) voor hoe je iets kan delen, melden of verbeteren - met of zonder Git-ervaring.

## Licentie

EUPL-1.2, zie [LICENSE](LICENSE).

## Platform in cijfers
| Categorie | Aantal |
|-----------|--------|
| Databasetabellen | 41 |
| Alembic-migraties | 17 (schema, RLS, AI Governance, M5-risicokwantificatie + simulatie-historie, custom_attributes, organizational_units) |
| API-routers | 22 |
| Backend tests | 247 (pytest) |
| Frontend unit tests | 55 (Vitest + RTL + MSW, 12 spec-files) |
| Frontend e2e tests | 18 specs / 48 tests (Playwright - auth, navigation, inrichting, M4 AI-systemen, M5 simulatie, RFC-extensions, admin + beheer flows met UI → API → DB-checks incl. findings-create) |
| Frontend routes | 19 |
| RBAC-rollen | 6 |
| RLS-policies | 27 tabellen |
| Seed-stappen | 24 (22 uniek + 2a/2b, 3a/3b) |
| Normenkaders | 6 (BIO 2.0, ISO 27001, ISO 27701, ISO 22301, AVG, NIST AI RMF 1.0) |

## Tech Stack
| Component | Technologie |
|-----------|-------------|
| **Backend** | FastAPI + Python 3.12 |
| **ORM** | SQLAlchemy 2.0 async |
| **Database** | PostgreSQL 16 + pgvector |
| **Migraties** | Alembic |
| **Frontend** | Next.js 16 + React 19 + TypeScript + TailwindCSS v4 |
| **Auth** | JWT (HS256), OIDC-ready |
| **Containers** | Docker Compose (db, api, frontend) |
| **Tests** | pytest + httpx async (backend); Vitest + React Testing Library + MSW (frontend unit); Playwright (e2e) |
| **Visualisatie** | recharts (Monte Carlo histogram, percentielen) |

## Architectuur
```
Laag 1: MODEL (Data)     - SQLAlchemy 2.0 + PostgreSQL - single source of truth
Laag 2: API   (Logica)   - FastAPI + JWT + RBAC + RLS - gatekeeper
Laag 3: TOOLS (UI)       - Next.js 16 + React 19 - dunne glasplaat, geen business logic
Laag 4: AI    (Support)  - Mistral/Ollama (EU) - altijd adviserend, nooit beslissend
```

## Repo-structuur
```
grc-platform/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # App + CORS + lifespan
│   │   ├── core/              # config, db, auth, rate-limit
│   │   ├── models/            # SQLAlchemy 2.0 modellen (41 tabellen)
│   │   ├── schemas/           # Pydantic v2 schemas (per module)
│   │   ├── services/          # custom_fields, org_units, simulation, agents/*
│   │   └── api/v1/endpoints/  # 22 CRUD-routers
│   ├── alembic/versions/      # 17 migraties
│   └── tests/                 # 247 tests (pytest async)
├── frontend/                   # Next.js 16 + React 19 frontend
│   ├── src/
│   │   ├── app/               # 19 routes (login, inrichten/*, beheer/*, admin/*)
│   │   ├── components/        # UI, layout, beheer, shared (OrgUnitSelect, CustomFieldsForm)
│   │   ├── lib/               # API client, types, hooks, auth
│   │   ├── providers/         # AuthProvider
│   │   └── test/              # MSW handlers + setup
│   ├── e2e/                   # 17 Playwright-specs incl. UI → API → DB-helpers
│   └── vitest.config.ts       # coverage-ratchet 20/50/40/20 (V1)
├── ims-proces/                 # Procesbeschrijving IMS-inrichtingswizard
├── docs/                       # Gebruikers- + contributordocumentatie + 5 RFCs
├── ROADMAP.md                  # Publieke roadmap
├── CHANGELOG.md                # Wijzigingen per release/werkperiode
└── docker-compose.yml          # 3 containers: db, api, frontend
```

## Oude codebase
De v0-codebase (Reflex frontend, 100+ SQLModel entiteiten) is gearchiveerd op branch `archive/v0-old-codebase`.

## Principes
Dit project volgt de [architectuur- en communityprincipes](https://github.com/security-commons-nl/.github/blob/main/PRINCIPLES.md) van security-commons-nl: EU-soevereiniteit, AI altijd adviserend, auditbaarheid by design, least privilege en open source als standaard.
