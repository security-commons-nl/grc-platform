# Changelog

Alle noemenswaardige wijzigingen aan dit platform worden hier vastgelegd, geordend per release of werkperiode.

Format: gebaseerd op [Keep a Changelog](https://keepachangelog.com/). Versies worden bij majeur-mijlpalen geknipt; tot dan groeit `[Unreleased]` mee met `main`. Conventional commits in git log blijven de feitelijke audit-trail.

## [Unreleased] — 2026-05-13

Tien feature-PR's (#54–#65) in de aanloop naar de 15-mei-deadline voor inbreng van eerste-ronde-reviewers (CISO + concernadviseur risicomanagement bij pilot-gemeente).

### Toegevoegd

**Comprehensive UI → API → DB e2e-coverage (PR #62)**
- Nieuw `frontend/e2e/helpers/`-pakket: gecachede dev-token-helper (omzeilt `RATE_LIMIT_AUTH=10/min`) en `queryScalar`/`rowExists` als dunne wrapper rond `docker compose exec psql`.
- 9 nieuwe Playwright-specs (20 tests) die elke beheer-/admin-UI-route door de happy-path lopen en na elke actie de onderliggende DB-rij direct in `ims_*` verifiëren — geen mocks: echte UI → API → DB.
- Specs: admin-organisatie (boom-CRUD, cycle-prevention), admin-velden (form-builder, JSON-Schema enum), admin-agent-tokens (NHI two-step + JWT-claim), beheer-hitl-review, beheer-controls CRUD, beheer-assessments + bevindingen + bewijs, beheer-incidenten, beheer-risicos extensies, dashboard + admin-read.

**Stabiliteits-fixes voor dev-stack onder e2e-druk (PR #62)**
- `docker-compose.yml`: frontend `mem_limit` 512m → 2g. Turbopack OOM'de tijdens on-demand-compile van zware routes (`/beheer/risicos` 7s); container herstartte telkens en tests kregen `ERR_EMPTY_RESPONSE`.
- `frontend/.dockerignore` toegevoegd zodat `COPY . .` geen stale lokale `node_modules` (next@16.2.4) over `npm ci`-resultaten (next@16.2.6) heen kopieert. Dit verwijderde de `Mismatching @next/swc version`-waarschuwing en dev-server-instabiliteit.
- Twee opeenvolgende full-suite-runs: 40/40 e2e pass, 0 retries, 0 container-restarts, geheugen stabiel ~1.3GB / 2GB.

**Node-base-image bump (PR #63)**
- `frontend/Dockerfile` node 25-slim → 26-slim. Vervangt dependabot #61 die op een stale branch zat van vóór de mem_limit-fix.

**M2 — RFC 0001 + 0002 door naar controls + assessments (PR #64)**
- Backend: `organizational_unit_id` (Optional) in Control/Assessment schemas (Create/Update/Response). POST/PATCH valideren cross-tenant (422). GET ondersteunt `?organizational_unit_id=&include_descendants=` met recursive-CTE-walk — identiek pattern als risico's. `custom_attributes` was er al, nu volledig in Response geëxposeerd. `ai_system_id` ook expliciet in `AssessmentResponse`.
- Frontend: `/beheer/controls` + `/beheer/assessments` krijgen `OrgUnitSelect` + `CustomFieldsForm` in create-form en filter-kaart op de lijst (zelfde pattern als `/beheer/risicos`). api-client `.list({ organizationalUnitId, includeDescendants })` op controls + assessments, plus `assessments.update()`.
- Tests: +5 pytest in `test_organizational_units.py` (control create-with-unit, cross-tenant-reject, descendants-filter; assessment create-with-unit + cross-tenant-reject). +6 e2e in twee nieuwe specs die UI-flow doorlopen en daarna direct in `ims_controls` / `ims_assessments` verifiëren via psql.

**Vitest-coverage uitgebreid (PR #65)**
- 20 → **51 vitest-tests** (+31), 4 → 11 spec-files.
- Nieuwe tests: `OrgUnitSelect` (4), `CustomFieldsForm` (7), AI-systemen-page (5), HITL-checkpoints-page (5), agent-tokens-page (4), Controls-page (3), Assessments-page (3).
- SWR-isolatie: elke test wrapt component in `<SWRConfig provider={() => new Map()}>` zodat caches niet over tests heen lekken.
- Coverage-ratchet: `vitest.config.ts` thresholds 1/1/1/1 → 20/50/40/20 (V1 uit RFC 0003). Actuals: ~27/76/49/27.

**M2 — GRC-engine uitbreidingen (RFC 0001 + 0002)**
- Custom-attributes (JSONB) op risk/control/assessment/finding met tenant-specifieke veld-definities (`ims_custom_field_definitions`), JSON-Schema-validatie, reserved-namespace-check tegen kernkolommen, additionalProperties=false op compound-schema.
- CRUD `/api/v1/custom-fields/` (admin-only) en `/admin/velden` form-builder-UI met 4 veld-types (Tekst, Getal, Ja/nee, Keuzelijst).
- Organizational units met parent-self-FK boom (`ims_organizational_units`), max-depth-6, cycle-prevention via PATCH, recursive-CTE descendants-walk.
- CRUD `/api/v1/organizational-units/` + `/tree` + `/{id}/descendants` en `/admin/organisatie` boom-editor-UI.
- Risk-list filter `?organizational_unit_id&include_descendants` + dropdown op risico-form. Org-unit-koppeling op risk/control/assessment/grc_scores.
- Herbruikbare frontend-components `OrgUnitSelect` + `CustomFieldsForm` (renders inputs uit JSON-Schema-type).

**M5 — Risicokwantificatie (kern + UI + historie)**
- Schema-uitbreiding `ims_risks` met `financial_impact_min_eur`, `financial_impact_max_eur`, `impact_distribution` (Alembic 014).
- Monte Carlo-service (`app/services/simulation/monte_carlo.py`) met uniform en triangular distributies, NumPy-implementatie, reproduceerbaar via optionele `seed`.
- Endpoint `POST /api/v1/risks/{id}/simulate` met percentielen p5–p99, VaR-95/99, expected loss en optioneel `?include_samples=true` voor histogram-rendering.
- Simulatie-historie via `ims_risk_simulations` (Alembic 015), auto-save per run met `?label`+`?note`, `GET /risks/{id}/simulations` paginerend.
- Frontend-componenten `SimulationHistogram` (recharts, 30 bins, VaR-lijnen) en `SimulationInterpretation` (natuurlijke-taal-uitleg met conditionele waarschuwingen voor grote spreiding en materieel staartrisico). Lazy-loaded via `next/dynamic`.

**M4 — AI Governance volledig operationeel**
- AI-systemenregister `ims_ai_systems` met EU AI Act-classifier (deterministisch, keyword-based, advies-only), NIST AI RMF 1.0 als zesde normenkader met 4 kernfunctie-requirements, AI-conformity-assessment-type met verplichte AI-systeem-koppeling.
- Append-only `ai_hitl_checkpoints` voor menselijk-toezicht-audittrail (EU AI Act art. 14) + NHI agent-tokens met scope-claim en TTL ≤ 24h, optioneel gekoppeld aan AI-systeem.
- Drie frontend-routes: `/beheer/ai-systemen` (CRUD met classifier-advies inline), `/beheer/hitl-checkpoints` (review-flow met verplichte motivatie + historie), `/admin/agent-tokens` (NHI-uitgifte met two-step confirm + one-time JWT-display).
- Audit-logs-list endpoint `/ai-hitl-checkpoints/audit-logs` met review-telling per log + last_decision (voor UI-werklijst).

**M0 — Productie-readiness**
- HTTPS via Caddy reverse proxy (documentatie + voorbeeldconfig).
- Rate limiting via SlowAPI met instelbare limits per `.env` (`RATE_LIMIT_DEFAULT`, `RATE_LIMIT_AUTH`).
- PostgreSQL backup-pipeline (`scripts/backup-postgres.sh` + restore + end-to-end pipeline-test) met documentatie in `docs/backup.md`.
- `/health/details` endpoint met structured JSON-logging in productie + Langfuse-config-detectie + alerting-drempels (`docs/monitoring.md`).
- 5-fasen deployment-handleiding voor IT-beheerders (`docs/deployment.md`).
- Security-hardening checklist (10 categorieën) met geautomatiseerde `scripts/security-check.sh`.

**Frontend test-stack (RFC 0003)**
- Vitest 3 + React Testing Library 16 + MSW 2 + jsdom 25.
- `vitest.config.ts` met jsdom, coverage-v8, path-alias, drempels start op 1% met ratchet-plan tot 70%.
- 20 unit-tests over 4 files: `lib/constants` (RBAC), `lib/format-error` (Pydantic/FastAPI shapes), `lib/api-client` (MSW-gemockt incl. `include_samples`-query), `simulation-interpretation`-component (conditional warnings).
- ESLint 10.3 → 9.36 downgrade om `eslint-plugin-react`-incompat met ESLint 10 op te lossen. Lint nu actief in CI met 0 errors.
- CI uitgebreid: `frontend.yml` doet lint + typecheck + test:coverage + coverage-upload + build; `tests.yml` doet `pytest --cov` met coverage als artifact.

**E2E coverage** (Playwright)
- 5 spec-files: auth + navigation + inrichting-flow (origineel), `m5-simulatie` (UI + API), `m4-ai-systemen` (UI + filter + classifier-determinisme), `rfc-extensions` (custom-fields + org-units API-flow).

**Documentatie**
- `docs/modules.md` — modulaire 7-blok-frame met afhankelijkheidsdiagram en eerlijke backend/frontend-statussplitsing.
- `docs/ai-governance-uitbreiding.md` — NIST AI RMF + AI architectuur + NHI-pattern.
- `docs/eu-ai-act-classification.md` — classifier-regels en criteria.
- `docs/risico-kwantificatie.md` — Monte Carlo-API + distributies + interpretatie.
- `docs/rfc/0001` t/m `0005` — gestructureerde RFC's voor extensible attributes, org-units, frontend-test-strategie, M4-frontend-UI, M5-UI-uitbreiding. RFC 0003+0004+0005 zijn V1 geïmplementeerd; 0001+0002 V1 idem.

### Veranderd

- ROADMAP geherformuleerd naar modulair frame met twee actieve sporen (M0 productie-readiness, M4 AI Governance) en geparkeerde M5+M6.
- README cijfers bijgewerkt naar 35 tabellen, 17 Alembic-migraties, 19 API-routers, 240+ backend tests, 20 frontend unit, 5 e2e-specs.

### Gefixt

- Rate-limit-handler stuurt nu altijd Retry-After-header.
- `ims_risk_simulations.user_id` nullable met existence-check in endpoint (NHI-tokens en dev-tokens hebben geen echte user-row).
- ESLint 10.3 + eslint-plugin-react incompatibiliteit opgelost via downgrade naar 9.36.
- Diverse e2e-strict-mode-conflicten in M4 + M5-specs (exact-match op headings en percentielen).

---

## Statistieken huidige stand (main)

| Categorie | Aantal |
|-----------|--------|
| Databasetabellen | 41 |
| Alembic-migraties | 17 |
| API-routers | 22 |
| Backend Python-bestanden | 78 |
| Backend tests (pytest) | 245+ |
| Frontend TypeScript-bestanden | 62 |
| Frontend unit tests (Vitest) | 51 (11 spec-files, coverage ~27/76/49/27) |
| Frontend e2e-specs (Playwright) | 17 specs (46 tests) |
| Normenkaders | 6 (BIO 2.0, ISO 27001, ISO 27701, ISO 22301, AVG, NIST AI RMF) |
| RBAC-rollen | 6 |
| RLS-policies | 27 tabellen |

---

## Module-statusoverzicht

| Module | Backend | Frontend |
|--------|---------|----------|
| **M0** Platform | ✅ multi-tenant + RBAC + RLS + audit + rate-limit + monitoring + backup | n.v.t. (fundering) |
| **M1** Normen & Mapping | ✅ 6 normenkaders + Rosetta Stone + RAG-store | n.v.t. (kennislaag) |
| **M2** GRC-engine | ✅ + extensible attributes (RFC 0001, alle 4 entiteiten) + org-units (RFC 0002, risk + control + assessment + scoring) | ✅ `/beheer/*` (risk + control + assessment met org-unit + custom-fields + filter) + `/admin/organisatie` + `/admin/velden` |
| **M3** IMS-inrichtingswizard | ✅ 22 stappen + 7 AI-agents + RAG | ✅ `/inrichten/*` |
| **M4** AI Governance | ✅ alle 6 bouwstenen | ✅ 3 routes (AI-systemen + HITL + agent-tokens) |
| **M5** Risicokwantificatie | ✅ kern + historie + range + Monte Carlo + VaR | ⚠️ histogram + interpretatie (CDF/vergelijking/PDF in V2) |
| **M6** Inter-org samenwerking | 🔮 Roadmap | 🔮 Roadmap |

---

## Komende verwachte updates

Niet vastgelegd in een gepland release, wel direct openstaand werk:
- Edit-flows voor org-units (verplaatsen binnen boom) en custom-fields (definities aanpassen).
- Refactor `setState-in-effect` in `auth-provider` en `sidebar` naar `useSyncExternalStore` (suppressed met `TODO(RFC 0003)`-marker).
- RFC 0005 V2: CDF-curve, scenario-vergelijking-UI, PDF-export via weasyprint, dedicated `/beheer/risicos/[id]/simulaties`-route.
- RFC 0004 V2: detail-pagina per AI-systeem, edit-flow, `classification_override_note` als DB-veld, HITL `parent_checkpoint_id` voor genest review.
- Vitest-coverage richting V2-ratchet (50/40/50/50) na vervolg-tests op `auth-provider`, hooks, en de inrichtings-pagina's.

---

## Conventies voor toekomstige changelog-entries

1. **Wat erin** — wijzigingen worden hier gegroepeerd onder `Toegevoegd` / `Veranderd` / `Gefixt` / `Verwijderd` / `Beveiliging`.
2. **Wat eruit** — pure refactors of intern-CI gaan niet in changelog (zie git log).
3. **Versie-knip** — bij ROADMAP-milestone (bv. v1.0 productie-rijp) wordt `[Unreleased]` versplitst en datum gestempeld.
4. **Bron** — elke PR die public-facing functionaliteit raakt zou een changelog-line moeten toevoegen. Voor nu retrofit: deze entry dekt PR #38 t/m #65.
