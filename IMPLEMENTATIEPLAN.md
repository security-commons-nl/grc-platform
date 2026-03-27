# IMS v1 — Implementatieplan

*Aangemaakt: 2026-03-20*
*Laatst bijgewerkt: 2026-03-27*
*Status: actief — frontend polish fase*

---

## Waar we staan

| Fase | Status | Datum |
|------|--------|-------|
| Procesontwerp (CONTEXT.md K1-K15) | ✅ | 2026-03-19 |
| Architectuurprincipes + RBAC + security | ✅ | 2026-03-19 |
| Datamodel (32 tabellen, 67 indexen) | ✅ | 2026-03-19 |
| GRC-score berekeningsmodel (12-cellenmatrix) | ✅ | 2026-03-20 |
| Backend skeleton (Docker, FastAPI, Alembic) | ✅ | 2026-03-20 |
| Seed data (24 stappen, 5 standaarden, tenant Leiden) | ✅ | 2026-03-27 |
| API-endpoints (15 routers, alle domeinen) | ✅ | 2026-03-20 |
| Tests (105 evals, 15 testbestanden) | ✅ | 2026-03-20 |
| Authenticatie (JWT + RBAC + RLS) | ✅ | 2026-03-25 |
| Frontend Fase 1 (auth, sidebar, navigatie) | ✅ | 2026-03-27 |
| Frontend Fase 2 (inrichtingsmodus) | ✅ | 2026-03-27 |
| Frontend Fase 3 (beheer-pagina's + formulieren) | ✅ | 2026-03-27 |
| **→ Frontend polish (knoppen, upload, stok-achter-deur)** | **⬅ Hier** | |
| Frontend Fase 4 (AI contextual hints + chat) | ❌ | |
| Agent-infrastructuur (RAG-store, domain agents) | ❌ | |
| Productie-readiness (Caddy, monitoring, backup) | ❌ | |

---

## Wat er staat

### Backend
- **3 Alembic-migraties:** schema (32 tabellen) → RLS (21 policies) → seed data
- **15 API-routers:** auth, tenants, steps, decisions, documents, standards, scopes, risks, controls, assessments, evidence, incidents, scores, knowledge, health
- **JWT auth:** dev-token + agent-token, RBAC met 6-level hiërarchie
- **RLS:** Row Level Security op alle tenant-scoped tabellen
- **105 tests:** alle groen

### Frontend
- **Next.js 15** + TypeScript + TailwindCSS v4
- **16 routes:** login, inrichten (overzicht, stap-detail, besluiten, documenten), beheer (dashboard, risico's, controls, assessments, bewijs, bevindingen, incidenten), admin (gebruikers, tenant)
- **Zakelijk-minimaal design:** blauw-neutraal, vaste sidebar (collapsible)
- **Formulieren:** besluiten, documenten, risico's, controls, assessments, incidenten

### Docker
- 3 containers: `db` (pgvector/pg16), `api` (FastAPI), `frontend` (Next.js)
- Poorten: 3000 (frontend), 8000 (API), 5432 (DB)

---

## Volgende stappen

### Nu — Frontend polish
- [ ] Dropdown vervangen door directe actieknoppen per status-overgang
- [ ] Stok-achter-de-deur: statuswijziging pas mogelijk na bijbehorende output (besluit/document)
- [ ] Document-upload bij stappen (secundaire invoerroute K6)
- [ ] Documentatie bijwerken (README, CLAUDE.md, architectuur-principes)

### Daarna — AI-integratie
- [ ] Contextual hints (subtiele banners per stap, max 80px)
- [ ] Chat-island (floating knop, 360px zijpaneel)
- [ ] RAG-store vullen (normatieve laag + organisatielaag)
- [ ] Domain agents bouwen (6-8 agents + orchestrator)

### Later — Productie
- [ ] Caddy reverse proxy (HTTPS, security headers)
- [ ] Rate limiting
- [ ] Backup-strategie PostgreSQL
- [ ] Monitoring (Langfuse)
- [ ] Deployment-documentatie

---

## Referentiedocumenten

| Document | Locatie |
|----------|---------|
| Procesontwerp | `ims-proces/CONTEXT.md` |
| Architectuurprincipes | `reference-docs/architectuur-principes.md` |
| Datamodel | `reference-docs/datamodel.md` |
| Kritische analyse | `reference-docs/kritische-analyse-ontwerp.md` |
| Rapportagemodel | SharePoint: `Rapporteren/Rapportagemodel IMS (geconsolideerd).md` |
| KPI-definities | SharePoint: `Rapporteren/KPI-definities IMS (12 cellen).md` |
