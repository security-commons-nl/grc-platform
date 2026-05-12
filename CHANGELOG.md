# Changelog

Alle noemenswaardige wijzigingen aan dit platform worden hier vastgelegd, geordend per release of werkperiode.

Format: gebaseerd op [Keep a Changelog](https://keepachangelog.com/). Versies worden bij majeur-mijlpalen geknipt; tot dan groeit `[Unreleased]` mee met `main`. Conventional commits in git log blijven de feitelijke audit-trail.

## [Unreleased] — 2026-05-12

Eindstand na zes feature-PR's (#54–#59) in één werkdag rond de 15-mei-deadline voor inbreng Tom/Luuk/Vasilis/Nick.

### Toegevoegd

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
| Databasetabellen | 35 |
| Alembic-migraties | 17 |
| API-routers | 19 |
| Backend Python-bestanden | 78 |
| Backend tests (pytest) | 240+ |
| Frontend TypeScript-bestanden | 59 |
| Frontend unit tests (Vitest) | 20 |
| Frontend e2e-specs (Playwright) | 5 |
| Normenkaders | 6 (BIO 2.0, ISO 27001, ISO 27701, ISO 22301, AVG, NIST AI RMF) |
| RBAC-rollen | 6 |
| RLS-policies | 23 tabellen |

---

## Module-statusoverzicht

| Module | Backend | Frontend |
|--------|---------|----------|
| **M0** Platform | ✅ multi-tenant + RBAC + RLS + audit + rate-limit + monitoring + backup | n.v.t. (fundering) |
| **M1** Normen & Mapping | ✅ 6 normenkaders + Rosetta Stone + RAG-store | n.v.t. (kennislaag) |
| **M2** GRC-engine | ✅ + extensible attributes (RFC 0001) + org-units (RFC 0002) | ✅ `/beheer/*` + `/admin/organisatie` + `/admin/velden` |
| **M3** IMS-inrichtingswizard | ✅ 22 stappen + 7 AI-agents + RAG | ✅ `/inrichten/*` |
| **M4** AI Governance | ✅ alle 6 bouwstenen | ✅ 3 routes (AI-systemen + HITL + agent-tokens) |
| **M5** Risicokwantificatie | ✅ kern + historie + range + Monte Carlo + VaR | ⚠️ histogram + interpretatie (CDF/vergelijking/PDF in V2) |
| **M6** Inter-org samenwerking | 🔮 Roadmap | 🔮 Roadmap |

---

## Komende verwachte updates

Niet vastgelegd in een gepland release, wel direct openstaand werk:
- Edit-flows voor org-units (verplaatsen binnen boom) en custom-fields (definities aanpassen).
- Custom-fields-UI op controls/assessments-pagina's (backend werkt al).
- `organizational_unit_id` als veld in control-create-UI en assessment-create-UI.
- Frontend-vitest-tests voor `OrgUnitSelect`, `CustomFieldsForm`, AI-systemen-form, HITL-review-form, agent-tokens-form.
- Refactor `setState-in-effect` in `auth-provider` en `sidebar` naar `useSyncExternalStore` (suppressed met `TODO(RFC 0003)`-marker).
- RFC 0005 V2: CDF-curve, scenario-vergelijking-UI, PDF-export via weasyprint, dedicated `/beheer/risicos/[id]/simulaties`-route.
- RFC 0004 V2: detail-pagina per AI-systeem, edit-flow, `classification_override_note` als DB-veld, HITL `parent_checkpoint_id` voor genest review.

---

## Conventies voor toekomstige changelog-entries

1. **Wat erin** — wijzigingen worden hier gegroepeerd onder `Toegevoegd` / `Veranderd` / `Gefixt` / `Verwijderd` / `Beveiliging`.
2. **Wat eruit** — pure refactors of intern-CI gaan niet in changelog (zie git log).
3. **Versie-knip** — bij ROADMAP-milestone (bv. v1.0 productie-rijp) wordt `[Unreleased]` versplitst en datum gestempeld.
4. **Bron** — elke PR die public-facing functionaliteit raakt zou een changelog-line moeten toevoegen. Voor nu retrofit: deze entry dekt PR #38 t/m #59.
