# GRC-platform

> **Model-gedreven GRC-platform voor ISMS, PIMS en BCMS — met lokale AI, PDCA-workflow en Nederlandse compliance.**
>
> Internationaal ook bekend als een Integrated Management System (IMS).

Het GRC-platform is een Governance, Risk & Compliance-platform dat **normen, risico's, controls, audits en bewijs** centraal beheert. Gebouwd voor gemeenten en publieke organisaties die meerdere managementsystemen willen combineren in **een enkele bron van waarheid**.

---

## Platform in cijfers

| Categorie | Aantal |
|-----------|--------|
| Databasetabellen | 32 |
| Alembic-migraties | 3 (schema, RLS, seed data) |
| API-routers | 15 |
| Backend tests | 105 |
| Frontend routes | 16 |
| RBAC-rollen | 6 |
| RLS-policies | 21 tabellen |
| Seed-stappen | 24 (22 uniek + 2a/2b, 3a/3b) |
| Normenkaders | 5 (BIO, ISO 27001, ISO 27701, ISO 22301, AVG) |

---

## Tech Stack

| Component | Technologie |
|-----------|-------------|
| **Backend** | FastAPI + Python 3.12 |
| **ORM** | SQLAlchemy 2.0 async |
| **Database** | PostgreSQL 16 + pgvector |
| **Migraties** | Alembic |
| **Frontend** | Next.js 15 + TypeScript + TailwindCSS v4 |
| **Auth** | JWT (HS256), OIDC-ready |
| **Containers** | Docker Compose (db, api, frontend) |
| **Tests** | pytest + httpx async |

---

## Architectuur

```
Laag 1: MODEL (Data)     — SQLAlchemy 2.0 + PostgreSQL — single source of truth
Laag 2: API   (Logica)   — FastAPI + JWT + RBAC + RLS — gatekeeper
Laag 3: TOOLS (UI)       — Next.js 15 — dunne glasplaat, geen business logic
Laag 4: AI    (Support)  — Mistral/Ollama (EU) — altijd adviserend, nooit beslissend
```

---

## Quick Start

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

---

## Repo-structuur

```
grc-platform/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # App + CORS + lifespan
│   │   ├── core/              # config, db, auth
│   │   ├── models/            # SQLAlchemy 2.0 modellen (32 tabellen)
│   │   ├── schemas/           # Pydantic v2 schemas (14 modules)
│   │   └── api/v1/endpoints/  # 15 CRUD-routers
│   ├── alembic/versions/      # 3 migraties
│   └── tests/                 # 15 testbestanden, 105 tests
├── frontend/                   # Next.js 15 frontend
│   └── src/
│       ├── app/               # 16 routes (login, inrichten, beheer, admin)
│       ├── components/        # UI, layout, inrichten, beheer, ai, shared
│       ├── lib/               # API client, types, hooks, auth
│       └── providers/         # Auth, tenant, SWR
├── ims-proces/                 # Procesbeschrijving IMS-inrichtingswizard
├── docs/                       # Gebruikers- en contributordocumentatie
├── ROADMAP.md                  # Publieke roadmap
└── docker-compose.yml          # 3 containers: db, api, frontend
```

---

## Oude codebase

De v0-codebase (Reflex frontend, 100+ SQLModel entiteiten) is gearchiveerd op branch `archive/v0-old-codebase`.

---

## Bijdragen

Zie [CONTRIBUTING.md](CONTRIBUTING.md) voor hoe je iets kan delen, melden of verbeteren — met of zonder Git-ervaring.

---

## Principes

Dit project volgt de [architectuur- en communityprincipes](https://github.com/security-commons-nl/.github/blob/main/PRINCIPLES.md) van security-commons-nl: EU-soevereiniteit, AI altijd adviserend, auditbaarheid by design, least privilege en open source als standaard.
