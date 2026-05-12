# GRC-platform — Modules

> Het platform is opgebouwd uit zeven samenhangende modules. Drie zijn verplicht (M0–M2), vier zijn optioneel (M3–M6) en worden naar klantbehoefte gecombineerd.

Dit document beschrijft de modulaire opbouw. Zie [`ROADMAP.md`](../ROADMAP.md) voor wat per module gepland staat en [`docs/architectuur.md`](architectuur.md) voor de technische 4-laagse architectuur (Model / API / Tools / AI).

---

## Modulair overzicht

| Module | Naam | Backend | Frontend UI | Optioneel? |
|--------|------|---------|-------------|------------|
| **M0** | Platform | ✅ | n.v.t. (fundering) | Verplicht |
| **M1** | Normen & Mapping | ✅ | n.v.t. (kennislaag) | Verplicht |
| **M2** | GRC-engine | ✅ + extensible attributes (RFC 0001) + org-units (RFC 0002) | ✅ `/beheer/*` (UI-uitbreiding voor custom fields + units volgt) | Verplicht |
| **M3** | IMS-inrichtingswizard | ✅ | ✅ `/inrichten/*` | Optioneel |
| **M4** | AI Governance | ✅ | ✅ AI-systemen, HITL-review, agent-tokens | Optioneel |
| **M5** | Risicokwantificatie | ✅ scope-beperkt + historie | ⚠️ histogram + interpretatie (historie/CDF/PDF nog niet UI) | Optioneel |
| **M6** | Inter-org samenwerking | 🔮 Roadmap | 🔮 Roadmap | Optioneel |

**Statusduiding:**
- ✅ Operationeel — tests groen in CI, eindgebruiker kan feature gebruiken via UI of API
- ⚠️ Minimaal — basisfunctie aanwezig maar UI-ervaring is beperkt; uitbreiding gepland
- ❌ Niet aanwezig — backend werkt, frontend ontbreekt; alleen via API bereikbaar
- 🔮 Roadmap — nog niet gebouwd

### Afhankelijkheidsdiagram

```
M0 (Platform)
 └── M1 (Normen & Mapping)
      ├── M2 (GRC-engine)
      │    ├── M3 (IMS-inrichtingswizard)
      │    ├── M5 (Risicokwantificatie)
      │    └── M6 (Inter-org samenwerking)
      └── M4 (AI Governance)
```

---

## M0 — Platform

Multi-tenant fundering: auth (JWT), RBAC (6 rollen), Row Level Security op 21 tabellen, audit log, AI-client, config-management.

**Code-locatie:** `backend/app/core/*`, `backend/app/models/core_models.py` (tabellen `tenants`, `users`, `roles`, `ai_audit_logs`)

**Architectuurprincipes vastgelegd:**
- Database leading — schema-wijzigingen via Alembic-migratie
- Row Level Security als defense-in-depth, niet alleen applicatiefilter
- Onveranderlijke audit trail (`ims_decisions`, `ims_document_versions` zonder UPDATE/DELETE)
- EU Data Sovereignty — AI-provider configureerbaar, geen externe APIs zonder clearance

---

## M1 — Normen & Mapping

De kennis-fundering. Frameworks (BIO 2.0, ISO 27001, ISO 27701, ISO 22301, AVG) + requirements + cross-framework mapping (Rosetta Stone) + RAG-store voor semantisch zoeken op normatieve documenten.

**Code-locatie:** tabellen `ims_standards`, `ims_requirements`, `ims_requirement_mappings`, `ims_tenant_normenkader`, `ims_standard_ingestions`, `ims_knowledge_chunks` (pgvector).

**Onderscheidende eigenschap:** open cross-framework mapping. Een control die voldoet aan ISO 27001 A.5.1 is automatisch zichtbaar onder BIO 2.0 5.1.x — geen dubbele administratie.

---

## M2 — GRC-engine

Operationele GRC. Risico's met likelihood-impact-matrix, controls gekoppeld aan normen, periodieke assessments, findings, corrective actions, evidence met vervaldatum, incidenten met tijdlijn, scoping en scoring.

**Code-locatie:** tabellen `ims_risks`, `ims_controls`, `ims_risk_control_links`, `ims_assessments`, `ims_findings`, `ims_corrective_actions`, `ims_evidence`, `ims_incidents`, `ims_scopes`. UI onder `frontend/src/app/(protected)/beheer/*`.

**Doelgroep:** TIMS, lijnmanagement, auditor — dagelijks GRC-werk.

**Use case:** organisaties die al een (volwassen of beginnend) ISMS hebben en operationele tooling zoeken.

---

## M3 — IMS-inrichtingswizard

22-stappen wizard door 4 fasen (Fundament → Analyse → Maatregelen → Werking), 7 AI-domeinagenten met RAG-context per stap, automatische documentgeneratie (concepten gelabeld als `AI CONCEPT — verifieer handmatig`), besluitlog, gap-analyse, expliciete stap-afhankelijkheden.

**Code-locatie:** tabellen `ims_steps`, `ims_step_dependencies`, `ims_step_executions`, `ims_decisions`, `ims_documents`, `ims_document_versions`, `ims_step_input_documents`, `ims_gap_analysis_results`. UI onder `frontend/src/app/(protected)/inrichten/*`. Agents in `backend/app/services/agents/`. Procesbeschrijving in [`ims-proces/`](../ims-proces/).

**Doelgroep:** TIMS, CISO bij opstart van een IMS — eenmalige investering per organisatie.

**Use case:** organisaties die van scratch een ISMS/PIMS/BCMS willen opbouwen met begeleide methodologie.

---

## M4 — AI Governance

AI-systemenregister, EU AI Act-risicoclassificatie, NIST AI RMF als normenkader (uitbreiding van M1), AI Conformiteitsbeoordeling als assessment-type, HITL-checkpoints in audit log, Non-Human Identity-tokens met beperkte scope.

**Status:** backend volledig operationeel (alle zes bouwstenen, 43 tests) én **frontend UI geleverd** voor drie kernflows.

- `ims_ai_systems` register (CRUD onder `/api/v1/ai-systems`) — UI: `/beheer/ai-systemen` met filter, classifier-advies inline, badge per risico-categorie
- NIST AI RMF 1.0 als `AIMS`-domein normenkader met 4 kernfunctie-requirements
- `assessment_type='ai_conformity'` met verplichte koppeling aan AI-systeem
- Append-only `ai_hitl_checkpoints` voor menselijk-toezicht-audittrail (EU AI Act art. 14) — UI: `/beheer/hitl-checkpoints` met audit-log-lijst (review-status + telling), review-form met verplichte motivatie, historie per log
- NHI agent-tokens met scope-claim, TTL ≤ 24h, optionele koppeling aan AI-systeem — UI: `/admin/agent-tokens` met scope-multi-select, two-step confirm, one-time JWT-display
- Deterministische EU AI Act classifier met advies-endpoint en uitlegregels

Detail: [`docs/ai-governance-uitbreiding.md`](ai-governance-uitbreiding.md) (voorstel-doc) en [`docs/eu-ai-act-classification.md`](eu-ai-act-classification.md) (criteria).

**Use case:** organisaties met AI-systemen die onder EU AI Act (verordening 2024/1689) vallen.

---

## M5 — Risicokwantificatie (operationeel, scope-beperkt)

Financiële impact in min/max-ranges + Monte Carlo-simulatie als aanvulling op de kwalitatieve likelihood × impact-matrix.

**Status:** kern operationeel:
- `ims_risks` uitgebreid met `financial_impact_min_eur`, `financial_impact_max_eur`, `impact_distribution` (Alembic 014)
- Service `app/services/simulation/monte_carlo.py` met uniform en triangular distributies (NumPy)
- Endpoint `POST /api/v1/risks/{id}/simulate` met percentielen, VaR-95/99 en expected loss; optionele `?include_samples=true` voor histogram-rendering
- Simulatie-historie via `ims_risk_simulations` (Alembic 015): auto-save per run met optionele `?label` en `?note`, lijst-endpoint `GET /api/v1/risks/{id}/simulations`
- Reproduceerbaarheid via optionele `seed`-parameter
- Frontend: histogram (recharts) met VaR-95/99-referentielijnen, natuurlijke-taal-interpretatie, percentielen-staaf

**Use case:** organisaties met kwantitatieve risk-discipline (FAIR-achtig) — controllers, concernadviseurs risicomanagement.

**Bewust nog niet in deze iteratie:** organisatie-units, planning-en-control-cyclus, lognormal-distributie, portfolio-aggregatie, correlaties tussen risico's, CDF-visualisatie, scenario-vergelijking-UI, PDF-export. Zie [`docs/risico-kwantificatie.md`](risico-kwantificatie.md) sectie "Wat NIET in M5 zit" en [`docs/rfc/0005-m5-ui-uitbreiding.md`](rfc/0005-m5-ui-uitbreiding.md) voor het volledige UI-plan.

---

## M6 — Inter-org samenwerking (gepland)

Regionaal dashboard met compliance-scores gedeeld tussen gemeenten, governance-tooling voor centrumgemeente-constructies, uitgebreide rapportage-module.

**Status:** niet gebouwd. Zie [`ROADMAP.md`](../ROADMAP.md) Fase 3.

**Use case:** centrumgemeenten en regio's die meerdere gemeenten ondersteunen.

---

## Module-bundels per use case

| Bundel | Modules | Voor wie |
|--------|---------|----------|
| **Operationele GRC** | M0 + M1 + M2 | Organisatie met bestaand ISMS, zoekt tooling |
| **Starter (IMS van scratch)** | M0 + M1 + M2 + M3 | Organisatie zonder volwassen ISMS, wil begeleid opbouwen |
| **AI-ready** | M0 + M1 + M2 + M4 | Organisatie met AI-systemen onder EU AI Act |
| **Regio** | M0 + M1 + M2 + M6 | Centrumgemeente met buurgemeenten |
| **Kwantitatief** | M0 + M1 + M2 + M5 | Organisatie met kwantitatieve risk-discipline |
| **Volledig** | alle modules | Grote organisatie of regio met brede ambitie |

Bundels zijn geen losse deployments — alles draait in één codebase met één database. Modules verwijzen naar logische groeperingen van tabellen, endpoints en UI-routes die per klant aan/uit kunnen staan via feature-flags (toekomstig) of simpelweg ongebruikt blijven.

---

## Verhouding tot de 4-laagse architectuur

De [vierlaagse architectuur](architectuur.md) (Model / API / Tools / AI) is een **horizontale** indeling: elke module heeft zijn eigen tabellen (Laag 1), endpoints (Laag 2), UI (Laag 3) en eventueel AI-ondersteuning (Laag 4).

Modules zijn de **verticale** indeling: ze groeperen samenhangende functionaliteit over de 4 lagen heen.

```
                   M0    M1    M2    M3    M4    M5    M6
Laag 1 (Model)    [x]   [x]   [x]   [x]   [-]   [-]   [-]
Laag 2 (API)      [x]   [x]   [x]   [x]   [-]   [-]   [-]
Laag 3 (UI)       [-]   [-]   [x]   [x]   [-]   [-]   [-]
Laag 4 (AI)       [x]   [-]   [-]   [x]   [-]   [-]   [-]
```

`[x]` = aanwezig, `[-]` = (nog) niet aanwezig.

M0 heeft geen UI-routes — het is fundering. M1 heeft geen UI-routes — het is kennis-laag. M4–M6 moeten over alle vier lagen nog gebouwd worden.
