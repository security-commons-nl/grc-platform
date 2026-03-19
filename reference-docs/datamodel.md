# IMS — Datamodel

*Vastgesteld: 2026-03-19*
*Status: ontwerp — nog niet geïmplementeerd*

Alle tabellen hebben prefix `ims_`. Platform-brede tabellen (users, tenants) hebben geen prefix.
Elke tabel heeft minimaal: `id UUID PRIMARY KEY DEFAULT gen_random_uuid()`, `created_at TIMESTAMPTZ DEFAULT now()`.

---

## Domein 1 — Platform-breed

### `tenants`
Eén rij per gemeente of organisatie.

| Veld | Type | Toelichting |
|------|------|-------------|
| id | UUID PK | |
| name | TEXT | "Gemeente Leiden" |
| type | ENUM | `single` \| `centrum` |
| region_id | UUID FK → regions | Alleen bij centrumregeling |
| is_active | BOOL | Soft-delete |

### `regions`
Een regio groepeert meerdere gemeenten. De centrumgemeente is norm-eigenaar.

| Veld | Type | Toelichting |
|------|------|-------------|
| id | UUID PK | |
| name | TEXT | "Leidse Regio" |
| centrum_tenant_id | UUID FK → tenants | Norm-eigenaar — enige die `regionaal` mag publiceren |

### `users`
Platform-brede gebruikerstabel. Authenticatie via JWT (extern of Keycloak).

| Veld | Type | Toelichting |
|------|------|-------------|
| id | UUID PK | |
| tenant_id | UUID FK → tenants | Thuistenant |
| external_id | TEXT UNIQUE | Keycloak sub of eigen auth-ID |
| name | TEXT | Volledige naam |
| email | TEXT | |
| is_active | BOOL | |

### `user_tenant_roles`
RBAC per tenant. Een gebruiker kan meerdere rollen hebben binnen één tenant.

| Veld | Type | Toelichting |
|------|------|-------------|
| id | UUID PK | |
| user_id | UUID FK → users | |
| tenant_id | UUID FK → tenants | |
| role | ENUM | `admin` \| `sims_lid` \| `tims_lid` \| `discipline_eigenaar` \| `lijnmanager` \| `viewer` |
| domain | ENUM NULL | `ISMS` \| `PIMS` \| `BCMS` \| NULL (geldt voor alle domeinen) |

**Mandateringsregel:** `sims_lid` vereist voor restrisico-acceptatie en beleidsafwijkingen (K3).

### `user_region_roles`
Regionale rol bovenop de lokale rol. Alleen voor functies die regionaal opereren (CISO, FG, toezichthouder).

| Veld | Type | Toelichting |
|------|------|-------------|
| id | UUID PK | |
| user_id | UUID FK → users | |
| region_id | UUID FK → regions | |
| role | ENUM | `regionaal_toezichthouder` \| `regionaal_viewer` |

### `ai_audit_logs`
Elke AI-interactie wordt gelogd — auditbaarheid by design (architectuurprincipe 1.2).

| Veld | Type | Toelichting |
|------|------|-------------|
| id | UUID PK | |
| tenant_id | UUID FK → tenants | |
| user_id | UUID FK → users NULL | |
| agent_name | TEXT | "governance-agent", "gap-agent", etc. |
| step_execution_id | UUID FK NULL | Koppeling aan processtap |
| model | TEXT | "mistral-small-latest" |
| prompt_tokens | INT | |
| completion_tokens | INT | |
| langfuse_trace_id | TEXT NULL | Voor observability |
| feedback | ENUM NULL | `positief` \| `negatief` |
| feedback_comment | TEXT NULL | |

---

## Domein 2 — Inrichtingsmodus

### `ims_steps`
De 22 processtappen — statische definitietabel, niet per tenant.

| Veld | Type | Toelichting |
|------|------|-------------|
| id | UUID PK | |
| number | TEXT | "1", "2a", "2b", "3a", ... |
| phase | INT | 0, 1, 2, 3 |
| name | TEXT | "Bestuurlijk commitment" |
| waarom_nu | TEXT | Uitleg voor de gebruiker |
| required_gremium | ENUM | `sims` \| `tims` \| `lijnmanagement` \| `discipline_eigenaar` |
| is_optional | BOOL | Alleen Fase 3-stappen |
| domain | ENUM NULL | `ISMS` \| `PIMS` \| `BCMS` \| NULL (geldt voor alle) |

### `ims_step_dependencies`
B/W-afhankelijkheden tussen stappen (K4 dataflow-tabellen).

| Veld | Type | Toelichting |
|------|------|-------------|
| id | UUID PK | |
| step_id | UUID FK → ims_steps | De stap die wacht |
| depends_on_step_id | UUID FK → ims_steps | De stap die eerst af moet zijn |
| dependency_type | ENUM | `B` (blokkerend) \| `W` (waarschuwing) |

### `ims_step_executions`
Eén rij per stap per tenant per cyclus. De kern van de inrichtingsmodus.

| Veld | Type | Toelichting |
|------|------|-------------|
| id | UUID PK | |
| tenant_id | UUID FK → tenants | |
| step_id | UUID FK → ims_steps | |
| cyclus_id | INT NULL | Jaar (2026, 2027, ...) — alleen Fase 2+ |
| status | ENUM | `niet_gestart` \| `in_uitvoering` \| `concept` \| `in_review` \| `vastgesteld` |
| started_at | TIMESTAMPTZ NULL | |
| completed_at | TIMESTAMPTZ NULL | |
| skipped | BOOL DEFAULT false | |
| skip_reason | TEXT NULL | Waarom overgeslagen |
| skip_logged_by | TEXT NULL | Naam van persoon die skip accordeerde |

**Ontwerpkeuze:** `cyclus_id` is NULL voor Fase 0/1 (eenmalig). Fase 2-stappen krijgen een jaarlijkse `cyclus_id`. Zo is stap 13 van 2026 los van stap 13 van 2027.

### `ims_decisions` — Besluitlog
Het centrale, immutable besluitregister. Nummering is doorlopend per tenant.

| Veld | Type | Toelichting |
|------|------|-------------|
| id | UUID PK | |
| tenant_id | UUID FK → tenants | |
| number | TEXT | "0001", "0002", ... — uniek per tenant |
| step_execution_id | UUID FK NULL | Koppeling aan processtap (optioneel) |
| decision_type | ENUM | `normaal` \| `restrisico_acceptatie` \| `beleidsafwijking` \| `fase_overgang` \| `non_compliance` |
| content | TEXT | Wat is er besloten |
| grondslag | TEXT | ISO-clause of systeemvereiste |
| gremium | ENUM | `sims` \| `tims` \| `discipline_eigenaar` \| `lijnmanager` |
| decided_by_name | TEXT | Volledige naam accordeur |
| decided_by_role | TEXT | Functietitel accordeur |
| decided_at | TIMESTAMPTZ | |
| valid_until | TEXT NULL | Datum of "tot herziening" |
| motivation | TEXT NULL | Redenering (bij niet-standaard besluiten) |
| alternatives | TEXT NULL | Overwogen opties |
| iso_clause | TEXT NULL | Bijv. "ISO 27001 §4.3" |
| supersedes_id | UUID FK → ims_decisions NULL | Bij herziening: verwijzing naar origineel |

**Immutability:** geen UPDATE of DELETE op deze tabel. Correcties via nieuw record met `supersedes_id`.
**Mandatering:** applicatielaag valideert dat `restrisico_acceptatie` en `beleidsafwijking` alleen door `sims_lid` worden geaccordeerd.

### `ims_documents`
Een document is een levend artefact met meerdere versies. Niet de inhoud — die zit in `ims_document_versions`.

| Veld | Type | Toelichting |
|------|------|-------------|
| id | UUID PK | |
| tenant_id | UUID FK → tenants | |
| step_execution_id | UUID FK NULL | Welke stap heeft dit document gegenereerd |
| document_type | ENUM | `handboek` \| `soa` \| `risicoregister` \| `auditrapportage` \| `managementreview` \| `bcp` \| `dpia` \| `bia` \| `normenkader` \| `besluitlog_export` \| `overig` |
| title | TEXT | |
| domain | ENUM NULL | `ISMS` \| `PIMS` \| `BCMS` \| NULL |
| visibility | ENUM | `privé` \| `regionaal` |
| withdrawn_at | TIMESTAMPTZ NULL | Bij visibility-downgrade: tombstone-datum (K11) |

### `ims_document_versions`
Elke versie van een document. De database is altijd leidend — dit is de bron, niet een bestand.

| Veld | Type | Toelichting |
|------|------|-------------|
| id | UUID PK | |
| document_id | UUID FK → ims_documents | |
| version_number | TEXT | "1.0", "1.1", "2.0" |
| content_json | JSONB | Gestructureerde documentinhoud per sectie |
| status | ENUM | `concept` \| `in_review` \| `vastgesteld` |
| generated_by_agent | TEXT NULL | Welke agent heeft dit concept gegenereerd |
| created_by_user_id | UUID FK → users NULL | |
| vastgesteld_at | TIMESTAMPTZ NULL | |
| vastgesteld_by_name | TEXT NULL | |
| vastgesteld_by_role | TEXT NULL | |
| decision_id | UUID FK → ims_decisions NULL | Koppeling aan besluitlog-entry |

**Ontwerpkeuze:** `content_json` bevat de volledige documentstructuur als JSON (secties, placeholders ingevuld). Exportfunctie rendert dit on-demand naar PDF/Word. Nooit bestandsopslag voor inhoud.

---

## Domein 3 — Normen & mapping

### `ims_standards`
Normatieve kaders met versioning (K9).

| Veld | Type | Toelichting |
|------|------|-------------|
| id | UUID PK | |
| name | TEXT | "BIO", "ISO 27001", "ISO 27701", "ISO 22301", "AVG" |
| version | TEXT | "2.0", "2022", "2019" |
| published_at | DATE | |
| status | ENUM | `actief` \| `vervallen` |
| superseded_by_id | UUID FK → ims_standards NULL | BIO 2.0 → BIO 3.0 zodra die bestaat |
| domain | ENUM | `ISMS` \| `PIMS` \| `BCMS` \| `all` |

### `ims_requirements`
Individuele normeisen, gekoppeld aan een specifieke versie van een standaard.

| Veld | Type | Toelichting |
|------|------|-------------|
| id | UUID PK | |
| standard_id | UUID FK → ims_standards | Versie-specifiek |
| code | TEXT | "OT.1.1", "A.5.1", "7.4" |
| title | TEXT | |
| description | TEXT | |
| domain | ENUM | `ISMS` \| `PIMS` \| `BCMS` \| `all` |
| is_mandatory | BOOL | ISO shall-eis (V) of aanbevolen (A) |

### `ims_requirement_mappings`
Rosetta Stone: relaties tussen normeisen van verschillende standaarden.

| Veld | Type | Toelichting |
|------|------|-------------|
| id | UUID PK | |
| source_requirement_id | UUID FK → ims_requirements | Bijv. BIO 2.0 OT.1.1 |
| target_requirement_id | UUID FK → ims_requirements | Bijv. ISO 27001 A.5.1 |
| norm_version_source | TEXT | "BIO 2.0" — denormalisatie voor query-gemak |
| confidence_score | DECIMAL(3,2) | 0.00–1.00 — AI-betrouwbaarheidsscore |
| created_by | ENUM | `human` \| `ai` |
| verified | BOOL | Handmatig geverifieerd door 2e-lijnsrol |
| orphaned | BOOL DEFAULT false | Vlag bij normupdate — wacht op remapping |

### `ims_tenant_normenkader`
Welke normen volgt deze tenant?

| Veld | Type | Toelichting |
|------|------|-------------|
| id | UUID PK | |
| tenant_id | UUID FK → tenants | |
| standard_id | UUID FK → ims_standards | |
| adopted_at | DATE | |
| is_active | BOOL | |
| decision_id | UUID FK → ims_decisions NULL | Koppeling aan besluitlog (stap 6) |

---

## Domein 4 — GRC-kern

### `ims_scopes`
Hiërarchisch scopemodel: Organisatie → Cluster → Proces → Asset / Leverancier.

| Veld | Type | Toelichting |
|------|------|-------------|
| id | UUID PK | |
| tenant_id | UUID FK → tenants | |
| type | ENUM | `organisatie` \| `cluster` \| `proces` \| `asset` \| `leverancier` |
| name | TEXT | |
| parent_id | UUID FK → ims_scopes NULL | Hiërarchie |
| domain | ENUM NULL | `ISMS` \| `PIMS` \| `BCMS` \| NULL |
| is_critical | BOOL | Kritiek proces/asset (BCM) |

### `ims_risks`
Risico's per tenant, gekoppeld aan scope.

| Veld | Type | Toelichting |
|------|------|-------------|
| id | UUID PK | |
| tenant_id | UUID FK → tenants | |
| scope_id | UUID FK → ims_scopes | |
| domain | ENUM | `ISMS` \| `PIMS` \| `BCMS` |
| title | TEXT | |
| description | TEXT | |
| likelihood | INT | 1–5 |
| impact | INT | 1–5 |
| risk_score | INT GENERATED | `likelihood * impact` (computed column) |
| risk_level | ENUM GENERATED | `groen` \| `geel` \| `oranje` \| `rood` |
| status | ENUM | `open` \| `in_behandeling` \| `geaccepteerd` \| `gesloten` |
| owner_user_id | UUID FK → users NULL | |
| cyclus_id | INT NULL | Jaar |
| treatment_decision_id | UUID FK → ims_decisions NULL | Bij acceptatie: koppeling aan besluitlog |

**Escalatieladder:**
- Groen (score 1-4): discipline-eigenaar
- Geel (5-9): TIMS
- Oranje (10-14): SIMS
- Rood (15-25): Directieteam

### `ims_controls`
Maatregelen — kunnen gekoppeld zijn aan een noreis of standalone zijn.

| Veld | Type | Toelichting |
|------|------|-------------|
| id | UUID PK | |
| tenant_id | UUID FK → tenants | |
| requirement_id | UUID FK → ims_requirements NULL | Koppeling aan norm (optioneel) |
| title | TEXT | |
| description | TEXT | |
| domain | ENUM | `ISMS` \| `PIMS` \| `BCMS` |
| owner_user_id | UUID FK → users NULL | |
| implementation_status | ENUM | `niet_gestart` \| `in_uitvoering` \| `geïmplementeerd` \| `geverifieerd` |
| implementation_date | DATE NULL | |

### `ims_risk_control_links`
Veel-op-veel: risico's worden gemitigeerd door controls.

| Veld | Type | Toelichting |
|------|------|-------------|
| risk_id | UUID FK → ims_risks | |
| control_id | UUID FK → ims_controls | |

### `ims_assessments`
Audits, DPIA's, pentests, self-assessments, BC-oefeningen.

| Veld | Type | Toelichting |
|------|------|-------------|
| id | UUID PK | |
| tenant_id | UUID FK → tenants | |
| assessment_type | ENUM | `audit` \| `dpia` \| `pentest` \| `self_assessment` \| `bc_oefening` |
| scope_id | UUID FK → ims_scopes NULL | |
| domain | ENUM NULL | |
| planned_at | DATE | |
| started_at | TIMESTAMPTZ NULL | |
| completed_at | TIMESTAMPTZ NULL | |
| status | ENUM | `gepland` \| `actief` \| `afgerond` \| `geannuleerd` |
| cyclus_id | INT NULL | Jaar |
| document_id | UUID FK → ims_documents NULL | Auditrapportage |

### `ims_findings`
Bevindingen uit assessments.

| Veld | Type | Toelichting |
|------|------|-------------|
| id | UUID PK | |
| assessment_id | UUID FK → ims_assessments | |
| tenant_id | UUID FK → tenants | |
| title | TEXT | |
| description | TEXT | |
| severity | ENUM | `kritiek` \| `hoog` \| `gemiddeld` \| `laag` \| `info` |
| status | ENUM | `open` \| `in_behandeling` \| `gesloten` |
| requirement_id | UUID FK → ims_requirements NULL | Welke noreis is geraakt |

### `ims_corrective_actions`
Verbeteracties — voortkomend uit bevindingen, risico's of management review.

| Veld | Type | Toelichting |
|------|------|-------------|
| id | UUID PK | |
| tenant_id | UUID FK → tenants | |
| finding_id | UUID FK → ims_findings NULL | |
| risk_id | UUID FK → ims_risks NULL | |
| title | TEXT | |
| description | TEXT | |
| owner_user_id | UUID FK → users NULL | |
| due_date | DATE | |
| status | ENUM | `open` \| `in_uitvoering` \| `afgerond` |
| completed_at | TIMESTAMPTZ NULL | |

### `ims_evidence`
Bewijs dat een control werkt — gekoppeld aan een control.

| Veld | Type | Toelichting |
|------|------|-------------|
| id | UUID PK | |
| tenant_id | UUID FK → tenants | |
| control_id | UUID FK → ims_controls | |
| title | TEXT | |
| evidence_type | ENUM | `document` \| `screenshot` \| `log` \| `attestation` |
| storage_path | TEXT | Pad in object storage (MinIO/Azure Blob) |
| collected_at | DATE | |
| valid_until | DATE NULL | Wanneer verloopt dit bewijs |
| collected_by_user_id | UUID FK → users NULL | |

### `ims_incidents`
Incidenten worden geregistreerd in het platform (niet beheerd — dat is TopDesk). Aggregaat voor management review.

| Veld | Type | Toelichting |
|------|------|-------------|
| id | UUID PK | |
| tenant_id | UUID FK → tenants | |
| title | TEXT | |
| incident_type | ENUM | `informatiebeveiliging` \| `privacy` \| `continuiteit` |
| severity | ENUM | `kritiek` \| `hoog` \| `gemiddeld` \| `laag` |
| status | ENUM | `open` \| `in_behandeling` \| `afgerond` |
| reported_at | TIMESTAMPTZ | |
| resolved_at | TIMESTAMPTZ NULL | |
| external_ticket_id | TEXT NULL | TopDesk/ServiceNow referentie |
| corrective_action_id | UUID FK → ims_corrective_actions NULL | |

---

## Domein 5 — Scores

### `ims_maturity_profiles`
Het volwassenheidsprofiel per tenant per domein — groeit tijdens stap 4/5/7/8/9.

| Veld | Type | Toelichting |
|------|------|-------------|
| id | UUID PK | |
| tenant_id | UUID FK → tenants | |
| domain | ENUM | `ISMS` \| `PIMS` \| `BCMS` |
| existing_registers | ENUM | `aanwezig` \| `gedeeltelijk` \| `afwezig` |
| existing_analyses | ENUM | `aanwezig` \| `gedeeltelijk` \| `afwezig` |
| coordination_capacity | ENUM | `hoog` \| `gemiddeld` \| `laag` |
| linemanagement_structure | ENUM | `formeel` \| `informeel` |
| recommended_option | ENUM | `B` \| `C` |
| updated_at | TIMESTAMPTZ | |

### `ims_setup_scores`
Inrichtingsscore per tenant per domein per jaar (K12).

| Veld | Type | Toelichting |
|------|------|-------------|
| id | UUID PK | |
| tenant_id | UUID FK → tenants | |
| domain | ENUM | `ISMS` \| `PIMS` \| `BCMS` \| `totaal` |
| cyclus_year | INT | 2026, 2027, ... |
| score_pct | DECIMAL(5,2) | 0.00–100.00 |
| steps_completed | INT | Aantal afgeronde stappen |
| steps_total | INT | Totaal van toepassing zijnde stappen |
| confirmed_at | TIMESTAMPTZ NULL | Jaarlijkse herbevestiging |
| calculated_at | TIMESTAMPTZ | |

### `ims_grc_scores`
GRC-score per tenant per domein per jaar — data-gedreven, daalt als activiteit uitblijft (K12).

| Veld | Type | Toelichting |
|------|------|-------------|
| id | UUID PK | |
| tenant_id | UUID FK → tenants | |
| domain | ENUM | `ISMS` \| `PIMS` \| `BCMS` \| `totaal` |
| cyclus_year | INT | |
| score_pct | DECIMAL(5,2) | 0.00–100.00 |
| components_json | JSONB | Uitsplitsing per component (controls, evidence, audits, ...) |
| calculated_at | TIMESTAMPTZ | |

---

## Domein 6 — RAG-store

### `ims_knowledge_chunks`
Twee-laags RAG-store (K15). pgvector native — geen aparte vector-database.

| Veld | Type | Toelichting |
|------|------|-------------|
| id | UUID PK | |
| layer | ENUM | `normatief` \| `organisatie` |
| tenant_id | UUID FK → tenants NULL | NULL = normatieve laag (gedeeld) |
| source_type | ENUM | `standaard` \| `blueprint` \| `beleid` \| `besluit` \| `handboek_versie` |
| source_id | UUID NULL | Verwijzing naar oorspronkelijke entiteit |
| chunk_index | INT | Volgorde binnen het brondocument |
| content | TEXT | De tekst van dit chunk |
| embedding | VECTOR(1536) | pgvector embedding |
| model_used | TEXT | Embeddings-model (bijv. "text-embedding-3-small") |

**Toegangsregel:** queries op `layer = 'organisatie'` filteren altijd op `tenant_id`. Cross-tenant leaks zijn architectureel onmogelijk via deze kolom.

---

## Relatie-overzicht (vereenvoudigd)

```
tenants ──────────────────────────────────────────────────────┐
  │                                                            │
  ├── users (via tenant_id)                                    │
  │     └── user_tenant_roles                                  │
  │     └── user_region_roles                                  │
  │                                                            │
  ├── ims_step_executions → ims_steps (definitie)              │
  │     └── ims_decisions (besluitlog)                         │
  │     └── ims_documents → ims_document_versions              │
  │                                                            │
  ├── ims_tenant_normenkader → ims_standards                   │
  │                              └── ims_requirements          │
  │                                    └── ims_requirement_mappings
  │                                                            │
  ├── ims_scopes (hiërarchisch)                                │
  │     └── ims_risks → ims_risk_control_links → ims_controls  │
  │     └── ims_assessments → ims_findings                     │
  │                             └── ims_corrective_actions     │
  │                                                            │
  ├── ims_controls → ims_evidence                              │
  │                                                            │
  ├── ims_maturity_profiles                                     │
  ├── ims_setup_scores                                         │
  ├── ims_grc_scores                                           │
  │                                                            │
  └── ims_knowledge_chunks (layer=organisatie)                 │
                                                               │
ims_knowledge_chunks (layer=normatief, tenant_id=NULL) ────────┘
```

---

## Ontwerpbeslissingen

| Beslissing | Keuze | Reden |
|-----------|-------|-------|
| UUID als primary key | Ja, overal | Geen sequentie-afhankelijkheid, veilig voor export |
| Soft delete | Alleen `tenants` en `users` | Overige entiteiten zijn immutable of archiveerbaar via status |
| `content_json` in document_versions | JSONB | Flexibel per documenttype, rendert on-demand naar PDF/Word |
| Geen aparte vector-DB | pgvector in PostgreSQL | Één database, geen extra afhankelijkheid |
| `risk_score` als computed column | `likelihood * impact` | Altijd consistent, nooit out-of-sync |
| `cyclus_id` als INT (jaar) | 2026, 2027 | Leesbaar, eenvoudig te filteren, vanzelf oplopend |
| Besluitlog immutable | Geen UPDATE/DELETE | Audit-integriteit — correcties via `supersedes_id` |
| Tombstone bij visibility-downgrade | `withdrawn_at` op ims_documents | Andere gemeenten zien datum terugtrekking, nooit stille verwijdering |

---

*Volgende stap: datamodel valideren → eerste migrations schrijven → API-skeleton bouwen*
