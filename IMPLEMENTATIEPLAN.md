# IMS v1 — Implementatieplan

*Aangemaakt: 2026-03-20*
*Status: actief*

---

## Waar we staan

| Fase | Status |
|------|--------|
| Procesontwerp (CONTEXT.md K1-K15) | ✅ Af |
| Architectuurprincipes | ✅ Af |
| Datamodel (32 tabellen) | ✅ Af |
| RBAC permissiematrix | ✅ Af |
| API-security checklist | ✅ Af |
| GRC-score berekeningsmodel (12-cellenmatrix) | ✅ Af |
| Backend skeleton (Docker, FastAPI, Alembic) | ✅ Af |
| Database draait (migratie uitgevoerd) | ✅ Af |
| **→ Seed data** | **⬅ Hier zijn we** |
| API-endpoints | ❌ |
| Authenticatie (JWT + RBAC) | ❌ |
| Agent-infrastructuur (RAG-store) | ❌ |
| Frontend (Next.js) | ❌ |

---

## Stappen

### Stap 1 — Seed data ⬅ NU
De database is leeg. Zonder basisdata kan niets werken.

**Wat moet erin:**
- [ ] Tenant "Gemeente Leiden" (type: centrum)
- [ ] Region "Leidse Regio" (centrum_tenant: Leiden)
- [ ] De 22 processtappen in `ims_steps` (nummer, fase, naam, waarom_nu, gremium, domein)
- [ ] Stap-afhankelijkheden in `ims_step_dependencies` (B/W relaties uit CONTEXT.md)
- [ ] Basisstandaarden: BIO 2.0, ISO 27001:2022, ISO 27701:2019, ISO 22301:2019, AVG
- [ ] Admin-gebruiker (seed-user voor ontwikkeling)

**Resultaat:** platform heeft een werkbare startconfiguratie.

---

### Stap 2 — API-endpoints inrichtingsmodus
De eerste werkende endpoints waarmee een gebruiker door de 22 stappen kan navigeren.

**Endpoints:**
- [ ] `GET /api/v1/steps` — alle 22 stappen ophalen
- [ ] `GET /api/v1/tenants/{id}/step-executions` — voortgang per tenant
- [ ] `POST /api/v1/tenants/{id}/step-executions` — stap starten
- [ ] `PATCH /api/v1/tenants/{id}/step-executions/{id}` — status bijwerken
- [ ] `POST /api/v1/tenants/{id}/decisions` — besluit vastleggen (immutable)
- [ ] `GET /api/v1/tenants/{id}/decisions` — besluitlog ophalen
- [ ] `POST /api/v1/tenants/{id}/documents` — document aanmaken
- [ ] `POST /api/v1/tenants/{id}/documents/{id}/versions` — versie toevoegen
- [ ] `GET /api/v1/tenants/{id}/setup-score` — inrichtingsscore berekenen

**Resultaat:** de inrichtingsmodus werkt via de API.

---

### Stap 3 — API-endpoints GRC-kern
De PDCA-cyclus endpoints (beheermodus).

**Endpoints:**
- [ ] Scopes CRUD
- [ ] Risks CRUD + escalatieladder-validatie
- [ ] Controls CRUD + risk-control links
- [ ] Assessments CRUD (audit, DPIA, pentest, gap-analyse, management review)
- [ ] Findings CRUD
- [ ] Corrective actions CRUD
- [ ] Evidence CRUD
- [ ] Incidents CRUD
- [ ] GRC-score berekening (12-cellenmatrix)

**Resultaat:** de beheermodus werkt via de API.

---

### Stap 4 — Authenticatie & RBAC
JWT-gebaseerde auth met rolvalidatie.

- [ ] JWT RS256 login/refresh/logout endpoints
- [ ] `get_current_user` dependency (JWT → user)
- [ ] `require_role()` dependency (sectie 9 architectuurprincipes)
- [ ] Tenant-isolatie afdwingen (elke query filtert op tenant_id)
- [ ] Escalatieladder-validatie bij besluit-accordering

**Resultaat:** endpoints zijn beveiligd per rol.

---

### Stap 5 — Normen & mapping
Normenkader-beheer en de agentic inlading-workflow.

- [ ] Standards CRUD
- [ ] Requirements CRUD
- [ ] Requirement mappings (Rosetta Stone)
- [ ] Tenant-normenkader (welke normen volgt deze tenant)
- [ ] Standard ingestion endpoint (upload → agent parseert → review)

**Resultaat:** normenkaders zijn beheerbaar.

---

### Stap 6 — Agent-infrastructuur
RAG-store en domain agents.

- [ ] Knowledge chunks CRUD + embedding-pipeline
- [ ] pgvector similarity search endpoint
- [ ] AI audit logging
- [ ] Domain agent framework (orchestrator + 6-8 agents)
- [ ] Normenkader-inlading agent

**Resultaat:** AI-ondersteuning werkt.

---

### Stap 7 — Frontend (Next.js)
De gebruikersinterface.

- [ ] Look & feel bepalen (gesprek met gebruiker)
- [ ] Next.js project opzetten
- [ ] Inrichtingsmodus UI (stappen-wizard, besluitlog)
- [ ] GRC-dashboard (12-cellenmatrix, risico's, controls)
- [ ] Rapportage-views (bronrapportage → SIMS → DT → College)
- [ ] Rolgebaseerde navigatie (K14)

**Resultaat:** IMS is bruikbaar voor eindgebruikers.

---

### Stap 8 — Productie-readiness
- [ ] Caddy reverse proxy (HTTPS, security headers)
- [ ] Rate limiting configureren
- [ ] Backup-strategie PostgreSQL
- [ ] Monitoring (Langfuse voor AI, application health)
- [ ] Deployment-documentatie

**Resultaat:** IMS is deployable op VPS of Azure.

---

## Referentiedocumenten

| Document | Locatie |
|----------|---------|
| Procesontwerp | `ims-proces/CONTEXT.md` |
| Architectuurprincipes | `reference-docs/architectuur-principes.md` |
| Datamodel | `reference-docs/datamodel.md` |
| Kritische analyse | `reference-docs/kritische-analyse-ontwerp.md` |
| Rapportagemodel | SharePoint: Rapporteren/Rapportagemodel IMS (geconsolideerd).md |
| KPI-definities | SharePoint: Rapporteren/KPI-definities IMS (12 cellen).md |
