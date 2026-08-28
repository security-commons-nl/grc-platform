# Roadmap

> Het platform is opgebouwd uit zeven modules (M0–M6). Zie [`docs/modules.md`](docs/modules.md) voor de modulaire opbouw. Deze roadmap beschrijft wat per module gepland staat.

## Huidige staat

Het GRC-platform is functioneel voor de inrichtingsmodus, dagelijks GRC-gebruik, AI-governance en kwantitatieve risicokwantificatie.

**Operationeel (M0 + M1 + M2 + M3 + M4 + M5):**
- **M0** Platform — multi-tenant met RBAC, Row Level Security op 27 tabellen, rate-limiting, audit-trail, monitoring, backup-pipeline
- **M1** Normen & Mapping — BIO 2.0, ISO 27001, ISO 27701, ISO 22301, AVG, NIST AI RMF 1.0, RAG-pipeline op normatieve documenten
- **M2** GRC-engine — risico's, controls, assessments, evidence, incidenten, plus org-units (RFC 0002) en tenant-specifieke custom velden (RFC 0001) op alle vier kernentiteiten
- **M3** IMS-inrichtingswizard — 22 stappen door 4 fasen, 7 AI-domeinagenten, AIAuditLog
- **M4** AI Governance — AI-systemenregister + EU AI Act-classifier, HITL-checkpoints, NHI agent-tokens, AI Conformity Assessment
- **M5** Risicokwantificatie — Monte Carlo simulatie (uniform + triangular), simulatie-historie, histogram + natuurlijke-taal-interpretatie
- Docker-gebaseerde installatie + comprehensive e2e UI → API → DB-tests (17 Playwright-specs / 46 tests; 51 vitest unit-tests; 245+ pytest backend-tests)

---

## Actieve sporen

Twee modules zijn nu in actieve ontwikkeling. Andere modules zijn bewust geparkeerd tot een van deze twee is afgerond.

### Spoor 1 — Productie-readiness (M0)

Klaar voor productie-gebruik bij gemeenten. **Module-focus: M0 productie-hard maken.**

- [x] Klikbaar likelihood-impact matrix-grid in risicoregister (vervangt dropdowns; heatmap boven tabel) — M2
- [x] HTTPS via Caddy reverse proxy (documentatie) — M0 — zie [`docs/deployment-caddy.md`](docs/deployment-caddy.md)
- [x] Rate limiting op API-endpoints — M0 — `slowapi` met instelbare limits per `.env` (`RATE_LIMIT_DEFAULT`, `RATE_LIMIT_AUTH`); auth-endpoints strenger; `/health` exempt
- [x] Geautomatiseerde backup-strategie PostgreSQL — M0 — zie [`docs/backup.md`](docs/backup.md), `scripts/backup-postgres.sh` + restore + end-to-end pipeline-test
- [x] Monitoring en observability — M0 — zie [`docs/monitoring.md`](docs/monitoring.md): `/health/details` endpoint, structured JSON logging in productie, Langfuse-config-detectie, alerting-drempels
- [x] Deployment-documentatie voor IT-beheerders — M0 — zie [`docs/deployment.md`](docs/deployment.md) (5-fasen handleiding: voorbereiden, installeren, initialiseren, verifiëren, onderhouden)
- [x] Security hardening checklist — M0 — zie [`docs/security-hardening.md`](docs/security-hardening.md) (10 categorieën, statussen ✅/🛠️/💡) + geautomatiseerde `scripts/security-check.sh`

### Spoor 2 — AI Governance Module (M4)

Uitbreiding met AI-governance functionaliteit. Aansluiting op EU AI Act (verordening 2024/1689) en NIST AI RMF. **Module-focus: M4 bouwen.**

- [x] AI-systemenregister — catalogiseer alle AI-toepassingen per organisatie — M4 — tabel `ims_ai_systems`, CRUD-endpoints onder `/api/v1/ai-systems`, RLS-geïsoleerd
- [x] EU AI Act risicoclassificatie per AI-systeem (verboden / hoog-risico / beperkt / minimaal) — M4 — `eu_ai_act_risk` veld op `ims_ai_systems` (Alembic 010); deterministische classifier in `app/services/eu_ai_act_classifier.py`; advies-endpoint `/api/v1/ai-systems/classify-suggestion`; criteria-documentatie [`docs/eu-ai-act-classification.md`](docs/eu-ai-act-classification.md)
- [x] NIST AI RMF als normenkader naast BIO 2.0 en ISO 27001 — M1 / M4 — Alembic 011 voegt het normenkader (v1.0, domain `AIMS`) + 4 kernfunctie-requirements (GOVERN, MAP, MEASURE, MANAGE) toe
- [x] AI Conformiteitsbeoordeling als assessment-type — M2 / M4 — `assessment_type='ai_conformity'` + `ai_system_id` FK op `ims_assessments` (Alembic 012), filter op AI-systeem in list endpoint, validatie dat conformiteit altijd aan een geregistreerd AI-systeem gekoppeld is
- [x] Non-Human Identity (NHI) support — agent-tokens met beperkte scope en TTL — M0 / M4 — `scope`-claim (lijst capabilities), default TTL 60 min (max 24h), koppeling aan `ai_system_id` met cross-tenant verificatie, `require_scope()` dependency
- [x] AI-audit log uitbreiding — HITL-checkpoints en menselijk toezicht registratie — M0 / M4 — append-only `ai_hitl_checkpoints` tabel (UPDATE/DELETE ingetrokken), endpoint `/api/v1/ai-hitl-checkpoints`, reviewer afgeleid uit JWT om impersonatie te voorkomen

Detailvoorstel: [`docs/ai-governance-uitbreiding.md`](docs/ai-governance-uitbreiding.md).

---

## Geparkeerde sporen

Gepland, maar bewust uitgesteld tot de actieve sporen zijn afgerond. Niet geschrapt — wel niet *nu*.

### M4 V2 — EU AI Act 2027 readiness (geparkeerd)

Aanleiding: Europese Commissie publiceerde 12 mei 2026 een 167-pagina ontwerp-richtsnoer voor classificatie van high-risk AI-systemen. Compliance-deadline verschoven naar 2 december 2027 (politiek akkoord EU-raad). Onze huidige M4-implementatie dekt de basis (register + keyword-classifier + HITL); de nieuwe guidelines voegen detail toe dat we kunnen verwerken.

**Quick wins (totaal ~2 dagen werk):**
- [ ] Annex III sub-categorieën als gestructureerde keuzes in `/beheer/ai-systemen` (road traffic management, evaluating learning outcomes, credit scoring, ...) met voorbeelden in tooltip. Classifier kan dan veel preciezer adviseren — M4
- [ ] Article 6(3) "narrow procedural task" exemption-wizard binnen het AI-systeem-formulier, met motivatie als bewijslast op `ims_ai_systems` — M4
- [ ] 167-page guidelines-PDF ingesten in `ims_knowledge_chunks` (normatief, tenant_id=NULL) zodat onze 7 AI-agents in de inrichtingsmodus eruit kunnen citeren — M1 / M4

**Vervolg-RFCs (uit comments-discussie):**
- [ ] **RFC 0006 — HITL review-kwaliteit-indicators**. Aanleiding: Nathan Schoenkin's punt dat "rubber stamp" approvals geen meaningful oversight zijn (art. 14). Toevoegen: review-tijd, motivatie-lengte-drempel, expliciete bias-checklist-velden. Doel: automation-bias detectie binnen audit-trail.
- [ ] **RFC 0007 — Operationele governance-dashboard per AI-systeem**. Aanleiding: het in de AI Act-praktijk gemaakte punt dat Articles 9-14 (risk management, data quality, technical documentation, record-keeping, transparency, human oversight, accuracy + robustness + cybersecurity) operationeel moeten kloppen, niet alleen op papier. Dashboard: status per artikel + bewijslinks naar evidence/controls/incidenten.

**Bron:** [`docs/eu-ai-act-classification.md`](docs/eu-ai-act-classification.md) (huidige criteria), [draft Commission guidelines](https://digital-strategy.ec.europa.eu/en/library/draft-commission-guidelines-classification-high-risk-ai-systems).

### M6 — Inter-organisatorische samenwerking (geparkeerd)

Schaalbaar naar meerdere organisaties en regio's.

- [ ] Regionaal dashboard — compliance-scores delen tussen gemeenten — M6
- [ ] Governance-tooling voor centrumgemeente-constructies — M6
- [ ] Uitgebreide rapportage-module — M6 / M2
- [ ] Community-bijdragen: templates, aanpakken, best practices — M3

---

## M5 Risicokwantificatie — scope-beperkt

**Status: kern operationeel, uitbreidingen bewust uitgesteld.**

Kwantitatief risicomanagement is toegevoegd in een doelbewust beperkte vorm:

- [x] Financiële impact-range (`financial_impact_min_eur`, `financial_impact_max_eur`) — M5 — Alembic 014
- [x] Distributie-veld op risico (uniform, triangular) — M5
- [x] Monte Carlo-simulatie-endpoint `POST /api/v1/risks/{id}/simulate` met percentielen, VaR-95/99, expected loss — M5
- [x] Reproduceerbaarheid via optionele `seed`-parameter — M5

Volledige documentatie: [`docs/risico-kwantificatie.md`](docs/risico-kwantificatie.md).

**Bewust niet in deze iteratie** — uitbreiden zodra er bredere klantvraag is:

- [ ] Organisatie-units (team / cluster / afdeling) onder tenant
- [ ] Planning-en-control-cyclus en organisatiedoelen als first-class entiteiten
- [ ] Lognormal-distributie en andere extra verdelingstypes
- [ ] Aggregatie/portfolio-simulatie over meerdere risico's
- [ ] Correlaties tussen gerelateerde risico's

Voor uitbreidingen: open een GitHub Discussion met de concrete use case.

---

## Werkwijze parallelle sporen

De twee actieve sporen lopen parallel maar onafhankelijk:
- Spoor 1 raakt vooral `backend/app/core/*`, deployment-docs en infrastructuur. Weinig schemawijziging.
- Spoor 2 raakt nieuwe tabellen, nieuwe endpoints, nieuwe UI-routes. Bouwt voort op M0/M1/M2.

Beide sporen zijn af-bare eenheden — elk levert zelfstandig waarde op.

---

## Bijdragen

Heb je ideeën, wil je een feature aanvragen of zelf bijdragen? Zie [CONTRIBUTING.md](https://github.com/security-commons-nl/.github/blob/main/CONTRIBUTING.md) of open een [issue](https://github.com/security-commons-nl/grc-platform/issues).
