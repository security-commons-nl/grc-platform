# grc-platform — Overview

> **Navigation aid.** This article shows WHERE things live (routes, models, files). Read actual source files before implementing new features or making changes.

**grc-platform** is a python project built with fastapi, using sqlalchemy for data persistence, organized as a microservices repo.

**Services:** `backend` (`backend`), `frontend` (`frontend`)

## Scale

132 API routes · 36 database models · 32 UI components · 75 library files · 6 middleware layers · 29 environment variables

## Subsystems

- **[Auth](./auth.md)** — 3 routes — touches: auth
- **[Agents](./agents.md)** — 5 routes — touches: auth, db
- **[Assessments](./assessments.md)** — 13 routes — touches: auth, db
- **[Controls](./controls.md)** — 3 routes — touches: auth, db
- **[Decisions](./decisions.md)** — 1 routes — touches: auth, db
- **[Documents](./documents.md)** — 15 routes — touches: auth, db
- **[Evidence](./evidence.md)** — 3 routes — touches: auth, db
- **[Health](./health.md)** — 1 routes — touches: auth, db
- **[Incidents](./incidents.md)** — 3 routes — touches: auth, db
- **[Knowledge](./knowledge.md)** — 3 routes — touches: auth, db
- **[Risks](./risks.md)** — 6 routes — touches: auth, db
- **[Scopes](./scopes.md)** — 3 routes — touches: auth, db
- **[Scores](./scores.md)** — 15 routes — touches: auth, db
- **[Standards](./standards.md)** — 22 routes — touches: auth, db
- **[Steps](./steps.md)** — 15 routes — touches: auth, db
- **[Tenants](./tenants.md)** — 19 routes — touches: auth, db
- **[Infra](./infra.md)** — 2 routes — touches: auth, db

**Database:** sqlalchemy, 36 models — see [database.md](./database.md)

**UI:** 32 components (react) — see [ui.md](./ui.md)

**Libraries:** 75 files — see [libraries.md](./libraries.md)

## High-Impact Files

Changes to these files have the widest blast radius across the codebase:

- `frontend\src\lib\hooks\use-api.ts` — imported by **4** files
- `frontend\src\components\inrichten\step-card.tsx` — imported by **1** files
- `frontend\src\components\ui\button.tsx` — imported by **1** files
- `frontend\src\lib\auth.ts` — imported by **1** files
- `frontend\src\lib\constants.ts` — imported by **1** files
- `frontend\src\lib\api-types.ts` — imported by **1** files

## Required Environment Variables

- `AI_API_KEY` — `.env.example`
- `LANGFUSE_HOST` — `.env.example`
- `LANGFUSE_PUBLIC_KEY` — `.env.example`
- `LANGFUSE_SECRET_KEY` — `.env.example`
- `NEXT_PUBLIC_API_URL` — `frontend\src\lib\constants.ts`

---
_Back to [index.md](./index.md) · Generated 2026-04-14_