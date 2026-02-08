# IMS Platform Audit Report

> **Datum:** 2026-02-08
> **Scope:** Volledige analyse van frontend UX, backend API-integriteit, en AI-agent contextcompleetheid
> **Methodiek:** Geautomatiseerde code-analyse van alle 23 frontend pagina's, 125 API-clientmethodes, 32 backend routers, en 18 AI-agenten

---

## Inhoudsopgave

1. [Executive Summary](#1-executive-summary)
2. [Frontend UX — Waar gebruikers vastlopen](#2-frontend-ux--waar-gebruikers-vastlopen)
   - 2.1 Kritieke fouten (applicatie crasht)
   - 2.2 Hoge ernst (functionaliteitsverlies / stille dataverliezen)
   - 2.3 Gemiddelde ernst (ontbrekende features / incomplete workflows)
   - 2.4 Lage ernst (cosmetisch / misleidend)
3. [Backend API — Integriteitsfouten & beveiligingsrisico's](#3-backend-api--integriteitsfouten--beveiligingsrisicos)
   - 3.1 P0 — Blokkeert kernfunctionaliteit
   - 3.2 P1 — Incorrecte data
   - 3.3 P2 — Beveiligingsrisico's
   - 3.4 P3 — Operationeel / kwaliteit
4. [AI-Agenten — Contextcompleetheid](#4-ai-agenten--contextcompleetheid)
   - 4.1 Overzichtstabel
   - 4.2 Kritieke agenten (niet-functioneel)
   - 4.3 Hoge prioriteit (significante lacunes)
   - 4.4 Gemiddelde prioriteit (functioneel maar incompleet)
   - 4.5 Lage prioriteit (nice-to-have)
   - 4.6 Kennisbank (knowledge_tools)
   - 4.7 Tools inventaris
5. [Cross-domein samenvatting](#5-cross-domein-samenvatting)
6. [Prioriteitsmatrix — Top 20 fixes](#6-prioriteitsmatrix--top-20-fixes)

---

## 1. Executive Summary

### Cijfers

| Categorie | Aantal | Toelichting |
|-----------|--------|-------------|
| **Frontend UX-problemen** | 23 | 3 kritiek, 8 hoog, 7 gemiddeld, 5 laag |
| **Backend API-problemen** | 11 | 2 P0, 2 P1, 2 P2, 5 P3 |
| **AI-agenten geanalyseerd** | 18 | + 1 orchestrator |
| **AI-agenten niet-functioneel** | 6 | compliance, privacy, workflow, admin, report, measure |
| **AI-agenten met significante lacunes** | 4 | risk, bcm, incident, supplier |
| **Ontbrekende AI-tools** | 60+ | Geschat aantal benodigde nieuwe tools |
| **Ontbrekende kennismethodieken** | 10 | Waaronder Rosetta Stone, Monte Carlo, SoA |

### Kernbevindingen

1. **Twee complete domeinen (Incidenten en Beleid) zijn niet-functioneel** — de frontend UI is volledig gebouwd maar de API-client mist create/update/delete methodes. Elke schrijfactie crasht.

2. **RBAC-roltoewijzing is uitgeschakeld** — de dialoog in de gebruikerspagina is uitgecommentarieerd. Beheerders kunnen geen rollen toewijzen via de UI.

3. **De Standards API-route is dubbel geprefixt** — `/api/v1/standards/standards/` i.p.v. `/api/v1/standards/`. Het hele compliance-initializatieproces (SoA) is hierdoor geblokkeerd.

4. **6 van 18 AI-agenten zijn praktisch niet-functioneel** — ze claimen expertise maar hebben geen tools om hun domein te bedienen. Gebruikers krijgen conceptueel advies maar geen concrete acties.

5. **Stille datafout in In-Control berekening** — open bevindingen worden niet per scope gefilterd, waardoor elke scope dezelfde (onjuiste) telling krijgt.

---

## 2. Frontend UX — Waar gebruikers vastlopen

### 2.1 Kritieke fouten (applicatie crasht / totale feature-uitval)

#### UX-1: Incident CRUD volledig kapot — ontbrekende API-clientmethodes
- **Bestanden:** `frontend/ims/state/incident.py` (r174, 177, 211) + `frontend/ims/api/client.py` (r537-551)
- **Wat gebeurt er:** Gebruiker opent Incidenten → klikt "Nieuw Incident" → vult formulier in → klikt "Opslaan". De state roept `api_client.create_incident(data)` aan, maar deze methode bestaat niet in `client.py`. Alleen `get_incidents()` bestaat.
- **Gebruikerservaring:** Het formulier rendert perfect. Na klikken op opslaan verschijnt een cryptische `AttributeError`. Aanmaken, bewerken en verwijderen van incidenten faalt allemaal. **Het hele incidentbeheer is niet-functioneel.**
- **Impact:** Incidenten is een kern-GRC feature (ISO 27001 §A.5.24-28, AVG Art. 33-34).

#### UX-2: Beleid CRUD volledig kapot — ontbrekende API-clientmethodes
- **Bestanden:** `frontend/ims/state/policy.py` (r177, 180, 214) + `frontend/ims/api/client.py` (r557-574)
- **Wat gebeurt er:** Identiek aan UX-1. De state roept `create_policy()`, `update_policy()`, `delete_policy()` aan, maar alleen `get_policies()` bestaat.
- **Gebruikerservaring:** Beleidsdocumenten zijn zichtbaar maar kunnen nooit worden aangemaakt, bewerkt of verwijderd. **De volledige beleidsworkflow (Concept → Review → Goedgekeurd → Gepubliceerd) is niet-functioneel.**

#### UX-3: Dashboard quick-action knoppen zijn decoratief
- **Bestand:** `frontend/ims/pages/index.py` (r243-258)
- **Wat gebeurt er:** De drie prominente actieknoppen ("Nieuw Risico", "Start Assessment", "Meld Incident") hebben geen `on_click` handlers.
- **Gebruikerservaring:** Eerste pagina na login. Gebruiker ziet uitnodigende knoppen, klikt erop, er gebeurt niets. **Slechte eerste indruk.**

---

### 2.2 Hoge ernst (belangrijke functionaliteitsgaten / stille dataverliezen)

#### UX-4: Backlog pagina laadt geen data automatisch
- **Bestand:** `frontend/ims/pages/backlog.py` (r314-381)
- **Probleem:** Geen `on_mount=BacklogState.load_items`. Kanban-bord toont altijd "Geen backlog items gevonden" totdat gebruiker een filter wijzigt.
- **Fix:** Voeg `on_mount=BacklogState.load_items` toe aan de page component.

#### UX-5: RBAC-roltoewijzing dialoog is uitgecommentarieerd
- **Bestand:** `frontend/ims/pages/users.py` (r856)
- **Probleem:** `# role_assignment_dialog()` — de component is gedefinieerd (r625) maar niet gerenderd. De "Rollen beheren" knop laadt data en opent de state, maar de dialoog verschijnt nooit.
- **Impact:** **Het hele RBAC-systeem is onbruikbaar vanuit de frontend.** Beheerders kunnen geen gebruikers aan scopes met rollen toewijzen.
- **Fix:** Verwijder het `#` commentaarteken op regel 856.

#### UX-6: Besluit-formulier mist kritieke velden
- **Bestanden:** `frontend/ims/pages/decisions.py` (r10-78) + `frontend/ims/state/decision.py` (r25-28)
- **Probleem:** Het formulier toont alleen `besluittype`, `besluittekst` en `motivering`. De velden `geldig_tot` (verloopdatum), `scope_id` en `besluitnemer_id` zijn niet in de UI.
- **Impact:** Risicoacceptatie-besluiten zonder verloopdatum schenden ISO 27001. `besluitnemer_id` is standaard "1" (hardcoded).

#### UX-7: Besluit-Risico koppeling heeft geen UI
- **Bestanden:** `frontend/ims/pages/decisions.py` + `frontend/ims/api/client.py` (r1155-1171)
- **Probleem:** API-methodes `link_decision_risk()`, `unlink_decision_risk()`, `get_decision_risks()` bestaan, maar er is geen UI om risico's aan besluiten te koppelen.
- **Impact:** Besluiten bestaan geïsoleerd — een "restrisico-acceptatie" besluit kan niet visueel aan het geaccepteerde risico worden gekoppeld.

#### UX-8: Correctieve actie verliest deadline en verantwoordelijke
- **Bestand:** `frontend/ims/state/assessment.py` (r520-525)
- **Probleem:** `create_corrective_action()` bouwt de payload met alleen `title`, `description` en `status`. De velden `action_due_date` en `action_assigned_to` worden niet meegestuurd.
- **Gebruikerservaring:** Gebruiker vult deadline en verantwoordelijke in, klikt opslaan, data lijkt bewaard. Na herladen zijn deadline en verantwoordelijke weg. **Stille dataverlies.**
- **Impact:** Correctieve acties zonder deadlines ondermijnen de ACT-feedbackloop (Hiaat 7). Het dashboard toont nooit "overdue" waarschuwingen.

#### UX-9: Beleidsworkflow heeft geen statushandhaving
- **Bestand:** `frontend/ims/pages/policies.py` (r321-333)
- **Probleem:** De status-dropdown toont alle waarden (Concept, Review, Goedgekeurd, Gepubliceerd, Gearchiveerd). Elke gebruiker kan elke status in elke volgorde selecteren. Geen goedkeuringsproces, geen audittrail, geen bevestigingsdialoog.
- **Impact:** Beleid kan van "Concept" direct naar "Gepubliceerd" springen.

#### UX-10: Asset BIV-classificatie dropdowns gebruiken verkeerde waarden
- **Bestand:** `frontend/ims/pages/assets.py` (r223-282)
- **Probleem:** De BIV-dropdowns (Beschikbaarheid, Integriteit, Vertrouwelijkheid) gebruiken dataclassificatie-waarden ("Public", "Internal", "Confidential", "Secret") in plaats van BIV-niveaus ("Laag", "Gemiddeld", "Hoog", "Kritiek").
- **Impact:** BIV-ratings zijn nonsensicaal. BIA-berekeningen zijn gebaseerd op verkeerde data.

#### UX-11: Stille API-foutonderdrukking op meerdere pagina's
- **Bestanden:** `state/risk.py` (r111-113, 125-137), `state/decision.py` (r44), `state/risk_framework.py` (r36), `state/policy_principle.py` (r45)
- **Probleem:** Als de backend down is, tonen deze pagina's lege tabellen met "Geen items gevonden" zonder foutmelding. Gebruiker kan "geen data" niet onderscheiden van "systeem kapot".

---

### 2.3 Gemiddelde ernst (ontbrekende features / incomplete workflows)

#### UX-12: Assessment-fases kunnen non-lineair worden overgeslagen
- **Bestand:** `frontend/ims/pages/assessment_detail.py` (r75) + `state/assessment.py` (r422-434)
- **Probleem:** Elke fase-stap in de stepper is klikbaar. Gebruiker kan van "Aangevraagd" direct naar "Afgerond" springen.

#### UX-13: Risicokader-formulier vereist ruwe JSON-invoer
- **Bestand:** `frontend/ims/pages/risk_framework.py` (r65-101)
- **Probleem:** Impact- en kansdefinities moeten als JSON strings worden ingevoerd. Geen visuele editor, geen validatie.

#### UX-14: Leverancier-zoekfilter werkt niet
- **Bestand:** `frontend/ims/pages/suppliers.py` (r389-393)
- **Probleem:** Zoekveld heeft geen `on_change` handler. Puur decoratief.

#### UX-15: Organisatieprofiel-wizard heeft geen succesbevestiging
- **Bestand:** `frontend/ims/state/organization_profile.py` (r178-186)
- **Probleem:** Na opslaan sluit de wizard zonder bevestigingsmelding.

#### UX-16: 9 API-clientmethodes hebben geen frontend UI
- **Bestand:** `frontend/ims/api/client.py`
- **Methodes zonder UI:**
  - `start_assessment()` (r386) — geen knop om assessment te starten
  - `complete_assessment()` (r393) — geen knop om formeel af te ronden
  - `complete_corrective_action()` (r461) — geen manier om actie af te vinken
  - `update_finding()` (r425) — geen manier om bevindingen te bewerken
  - `close_finding()` (r432) — geen manier om bevindingen te sluiten
  - `establish_scope()` (r1407) — geen governance-statuscontroles
  - `expire_scope()` (r1416) — geen manier om scopes te laten verlopen
  - `activate_risk_framework()` (r1228) — geen manier om kader te activeren
  - `get_expired_decisions()` (r1173) — geen weergave voor verlopen besluiten

#### UX-17: Compliance-pagina muteert nested dict (Reflex pitfall)
- **Bestand:** `frontend/ims/state/compliance.py` (r186-199)
- **Probleem:** `self.editing_entry["is_applicable"] = value` — Reflex detecteert geen wijzigingen in geneste dicts. UI kan stale data tonen.

#### UX-18: Risicokader form-velden laden als verkeerd type
- **Bestand:** `frontend/ims/state/risk_framework.py` (r53-56)
- **Probleem:** Als de API JSON-objecten teruggeeft i.p.v. strings, tonen de text areas `[object Object]`.

---

### 2.4 Lage ernst (cosmetisch / misleidend)

#### UX-19: Risico-formulier standaard op MEDIUM/MEDIUM
- **Bestand:** `frontend/ims/state/risk.py` (r46-47)
- **Probleem:** Zonder expliciete selectie wordt een risico automatisch in het midden van de matrix geplaatst.

#### UX-20: Leverancier contractdatums kunnen niet worden ingevoerd
- **Bestanden:** `state/supplier.py` (r34-35) + `pages/suppliers.py`
- **Probleem:** State heeft `form_contract_start_date` en `form_contract_end_date` maar het formulier heeft geen datumvelden. "Binnenkort Verlopend" statcard toont altijd 0.

#### UX-21: Leverancier "Actief" status is hardcoded
- **Bestand:** `frontend/ims/pages/suppliers.py` (r262)
- **Probleem:** Elke leverancier toont altijd een groene "Actief" badge. Geen statusveld, geen manier om leveranciers inactief te maken.

#### UX-22: Backlog edit-dialoog misleidende titel
- **Bestand:** `frontend/ims/pages/backlog.py` (r242)
- **Probleem:** Titel zegt "Item Bekijken" maar bevat bewerkbare velden. User Story velden worden niet geladen bij bewerken.

#### UX-23: Tooltip wrapping icon_button in gebruikerspagina (bekende Reflex pitfall)
- **Bestand:** `frontend/ims/pages/users.py` (r115-122)
- **Probleem:** `rx.tooltip` wrapping `rx.icon_button` breekt `on_click` eventchain. Gecombineerd met UX-5 (uitgecommentarieerde dialoog) is deze feature dubbel kapot.

---

### Samenvattingstabel frontend

| Ernst | Aantal | Kernthema |
|-------|--------|-----------|
| Kritiek | 3 | Ontbrekende API-clientmethodes, dode dashboard-knoppen |
| Hoog | 8 | Uitgeschakelde RBAC, stille dataverliezen, geen workflow-handhaving, verkeerde datawaarden |
| Gemiddeld | 7 | Ontbrekende features, onbereikbare API-capabilities, Reflex nested dict pitfall |
| Laag | 5 | Cosmetisch, hardcoded waarden, misleidende labels |
| **Totaal** | **23** | |

---

## 3. Backend API — Integriteitsfouten & beveiligingsrisico's

### Methodiek

Alle 125 frontend API-clientmethodes zijn regel-voor-regel gecross-referenst met de daadwerkelijke `@router` decorators in 31 backend endpoint-bestanden.

### Resultaat overzicht

| Categorie | Aantal |
|-----------|--------|
| Totaal frontend API-methodes | 125 |
| Backend routes die bestaan en matchen | 124 |
| Routes met pad-duplicatie (effectief kapot) | 1 |
| Routes met parameter-mismatches | 2 |
| Stub-endpoints (placeholder data) | 1 |
| Data-integriteitfouten | 1 |
| Potentiële runtime-fouten | 1 |
| Beveiligingsproblemen | 2 |
| Operationele afhankelijkheden | 1 |

---

### 3.1 P0 — Blokkeert kernfunctionaliteit

#### API-1: Standards route dubbel geprefixt (KRITIEK)
- **Bestand:** `backend/app/api/v1/endpoints/standards.py`
- **Probleem:** De router heeft prefix `/standards` (via `api.py`), maar de routes zelf bevatten ook `/standards/`:
  ```python
  @router.get("/standards/", ...)     # Resulteert in /api/v1/standards/standards/
  @router.post("/standards/", ...)
  @router.get("/standards/{standard_id}", ...)
  ```
- **Impact:** De frontend roept `/api/v1/standards/` aan maar de backend luistert op `/api/v1/standards/standards/`. Resultaat: **404 Not Found**. Dit blokkeert:
  - Standards-dropdown in SoA-initialisatie
  - Framework-selectie in compliance-overzicht
  - Elke pagina die framework-data nodig heeft
- **Fix:** Wijzig `"/standards/"` naar `"/"`, `"/standards/{standard_id}"` naar `"/{standard_id}"`, etc. in `standards.py`.

#### API-2: Organization Profile `__fields__` toegang (KRITIEK)
- **Bestand:** `backend/app/api/v1/endpoints/organization_profile.py` (r77, 110, 143)
- **Probleem:** `{c: getattr(profile, c) for c in profile.__fields__}` — In Pydantic v2 is `__fields__` deprecated. Afhankelijk van de SQLModel-versie kan dit een `AttributeError` geven.
- **Impact:** Als incompatibel: de organisatieprofiel GET, PUT en PATCH geven allemaal 500-fouten. De onboarding-wizard is niet-functioneel.
- **Fix:** Vervang met `profile.model_dump()`.

---

### 3.2 P1 — Incorrecte data

#### API-3: In-Control bevindingentelling niet per scope gefilterd (HOOG)
- **Bestand:** `backend/app/api/v1/endpoints/in_control.py` (r62-68)
- **Probleem:** De WHERE-clausule filtert op `tenant_id` en `status` maar NIET op `scope_id`. Elke scope toont het totaal aantal open bevindingen van alle scopes.
- **Impact:** Scopes zonder bevindingen worden onterecht als `NIET_IN_CONTROL` gemarkeerd. Scopes met bevindingen lijken identiek aan andere scopes.
- **Fix:** Voeg `Finding.scope_id == scope_id` toe aan de WHERE-clausule (vereist evt. join via Assessment).

#### API-4: Simulatie risk_ids worden genegeerd (GEMIDDELD)
- **Bestand:** `backend/app/api/v1/endpoints/simulation.py` (r100)
- **Probleem:** `risk_ids: Optional[List[int]] = None` zonder `Query()` annotatie. FastAPI behandelt dit als een request body parameter, maar de frontend stuurt het als query parameters.
- **Impact:** Risk-selectie wordt genegeerd; simulatie draait altijd op ALLE risico's.
- **Fix:** Wijzig naar `risk_ids: Optional[List[int]] = Query(None)`.

---

### 3.3 P2 — Beveiligingsrisico's

#### API-5: Dashboard My-Tasks IDOR-kwetsbaarheid (GEMIDDELD)
- **Bestand:** `backend/app/api/v1/endpoints/dashboard.py` (r41-47)
- **Probleem:** `user_id: int = Query(...)` — elke gebruiker kan de takenlijst van elke andere gebruiker opvragen door een ander `user_id` mee te geven.
- **Impact:** Informatieonthulling. Eén gebruiker kan correctieve acties, review-toewijzingen en workflow-taken van andere gebruikers zien.
- **Fix:** Vervang `user_id` query param met `Depends(get_current_user)`.

#### API-6: Optionele tenant_id op rapportage-endpoints (GEMIDDELD)
- **Bestanden:** `reports.py` (6 endpoints), `risks.py` (2 endpoints)
- **Probleem:** `tenant_id: Optional[int] = None` — als weggelaten retourneren deze endpoints data over ALLE tenants.
- **Impact:** In een multi-tenant deployment is dit een data-isolatiefout. Frontend stuurt momenteel altijd tenant_id mee, maar elke API-consumer die het weglaat krijgt cross-tenant data.
- **Fix:** Maak `tenant_id` verplicht of haal het uit de auth-context.

---

### 3.4 P3 — Operationeel / kwaliteit

#### API-7: SoA-initialisatie vereist voorgezaaide data (HOOG — operationeel)
- **Bestand:** `backend/app/api/v1/endpoints/soa.py` (r188-198)
- **Probleem:** SoA-initialisatie vereist dat de `Standard` en `Requirement` tabellen gevuld zijn. Er zijn geen seed-scripts of migraties die dit doen. In combinatie met API-1 (standards 404) is de hele compliance-module niet-functioneel out-of-the-box.
- **Fix:** Maak een seed-script dat minimaal ISO 27001:2022 controls en BIO-requirements laadt.

#### API-8: Assessment complete enum-validatie (LAAG)
- **Bestand:** `backend/app/api/v1/endpoints/assessments.py` (r274-278)
- **Probleem:** `complete_assessment()` verwacht `AuditResult` enum. Als de frontend een Nederlandse label of verkeerde casing stuurt, faalt het met 422.

#### API-9: Reports maandelijkse trends retourneert placeholder data (LAAG)
- **Bestand:** `backend/app/api/v1/endpoints/reports.py` (r465-496)
- **Probleem:** `/reports/trends/monthly` retourneert alleen nullen. De frontend roept dit endpoint niet aan, dus geen huidige impact.

#### API-10: Incident Summary severity breakdown leeg (LAAG)
- **Bestand:** `backend/app/api/v1/endpoints/reports.py` (r406-411)
- **Probleem:** Severity breakdown dict wordt geïnitialiseerd maar nooit gevuld.

#### API-11: Assessment parameter type mismatch (LAAG)
- **Frontend stuurt `overall_result` als string, backend verwacht `AuditResult` enum.** Werkt zolang exacte enum-waarden worden gebruikt.

---

## 4. AI-Agenten — Contextcompleetheid

### 4.1 Overzichtstabel

| Agent | Doel | Tools | Status | Kernprobleem |
|-------|------|-------|--------|-------------|
| **compliance_agent** | Frameworks, SoA, mappings | 2 | KRITIEK | Geen tools voor Rosetta Stone, SoA, standards, requirements |
| **admin_agent** | Gebruikers, RBAC, systeem | 2 | KRITIEK | Geen tools voor gebruikersbeheer, roltoewijzing, auditlog |
| **workflow_agent** | Statusovergangen | 4 | KRITIEK | Geen tools voor de workflow-engine (5 modellen) |
| **measure_agent** | Maatregelen & controls | 7 | KRITIEK | `link_measure_to_risk` is KAPOT (retourneert "disabled"), geen Control-tools |
| **privacy_agent** | AVG/GDPR | 5 | KRITIEK | Geen tools voor verwerkingsregister, DSR's, verwerkersovereenkomsten |
| **report_agent** | Rapportage | 5 | KRITIEK | Geen tools voor rapport-generatie, KPI-aggregatie, dashboards |
| **risk_agent** | Risicobeheer | 14 | HOOG | Mist Monte Carlo, kwantitatieve risico's, scoring-formule |
| **bcm_agent** | Continuïteit | 6 | HOOG | Geen tools voor continuïteitsplannen en -testen |
| **incident_agent** | Incidenten | 6 | HOOG | Geen `list_incidents`, onvolledige breach-velden, verkeerde veldnamen |
| **supplier_agent** | Leveranciers | 4 | HOOG | Geen tools voor verwerkersovereenkomsten |
| **assessment_agent** | Assessments | 6 | GEMIDDELD | Mist `list_assessments`, BIA-drempels, bevindingen aanmaken |
| **improvement_agent** | Verbetering | 6 | GEMIDDELD | Geen initiatief/mijlpaal-tools, geen backlog-tools |
| **scope_agent** | Scopes | 6 | GEMIDDELD | Geen afhankelijkheden-tools, geen schrijf-tools |
| **planning_agent** | Jaarplanning | 4 | GEMIDDELD | Geen planning-items, management review tools |
| **onboarding_agent** | Organisatieprofiel | 2 | GEMIDDELD | Geen tools om profiel te lezen/schrijven |
| **policy_agent** | Beleid | 8 | LAAG | Mist statustransitie-tool, overdue review check |
| **objectives_agent** | Doelstellingen | 3 | LAAG | Geen doelstelling/KPI CRUD-tools |
| **maturity_agent** | Volwassenheid | 5 | LAAG | Geen assessment/domein-score tools, verouderde domeinlijst |

### Samenvatting

| Status | Aantal agenten |
|--------|---------------|
| KRITIEK (niet-functioneel voor hoofddoel) | 6 |
| HOOG (significante lacunes) | 4 |
| GEMIDDELD (functioneel maar incompleet) | 5 |
| LAAG (grotendeels adequaat) | 3 |
| **Totaal** | **18** |

---

### 4.2 Kritieke agenten (niet-functioneel)

#### AGENT-1: Compliance Agent — Geen enkele compliance-tool

**Huidige staat:** 2 tools (beide generieke kenniszoekopdrachten). Het systeem prompt kent BIO, ISO 27001, NEN 7510 en AVG bij naam maar kan niets opzoeken of tonen.

**Wat de agent WEL zou moeten kunnen:**

| Ontbrekende capability | Model/API | Impact |
|----------------------|-----------|--------|
| Rosetta Stone (RequirementMapping) | `RequirementMapping` met `MappingType` (EQUIVALENT, PARTIAL, SUPERSET, SUBSET, RELATED), `confidence_score` | Kernfeature van het platform — volledig onzichtbaar voor AI |
| Statement of Applicability | `ApplicabilityStatement` met `CoverageType`, `ImplementationStatus`, gap-beschrijvingen | Hele SoA-module niet via AI te beheren |
| Standards/Requirements browsen | `Standard`, `Requirement` met hierarchie | Agent kan niet antwoorden op "welke ISO 27001 controls gaan over access control?" |
| Compliance-overzicht per framework | API endpoint bestaat (`/soa/scope/{id}/summary`) | Geen compliance-percentage weergave |
| Gap-analyse | Via `ImplementationStatus` + `coverage_type` | Geen identificatie van ontbrekende controls |

**Aanbeveling:** Volledig herschrijven van systeem prompt + 7 nieuwe tools:
1. `list_standards` — enumerate geladen frameworks
2. `list_requirements` — filteren op standaard, parent, control_type
3. `search_requirements` — zoeken in requirement-titels/beschrijvingen
4. `get_requirement_mappings` — Rosetta Stone cross-framework links
5. `get_soa_status` — applicability statement per scope/framework
6. `get_compliance_overview` — compliance-percentages per framework
7. `get_gap_analysis` — requirements zonder controls

---

#### AGENT-2: Admin Agent — Kan geen administratie uitvoeren

**Huidige staat:** 2 tools (`list_scopes` + kenniszoek). Claimt expertise in gebruikersbeheer maar kan niets doen.

**Ontbrekende capabilities (10+):**

| Categorie | Ontbrekende tools |
|-----------|------------------|
| Gebruikersbeheer | `list_users`, `get_user`, `create_user`, `update_user` |
| RBAC | `assign_role`, `revoke_role`, `list_user_roles` |
| Audit | `query_audit_log` met filtering |
| Notificaties | `list_notifications` |
| Systeemstatus | `get_system_health`, `get_system_stats` |
| Instellingen | `get_tenant_settings`, `update_tenant_settings` |
| Integraties | `list_integrations`, `test_integration` |

**Extra:** Agent vermeldt 4 rollen (Admin, ProcessOwner, Editor, Viewer) maar het model heeft 5 rollen (mist CONFIGURER).

---

#### AGENT-3: Workflow Agent — Weet niets van de workflow-engine

**Huidige staat:** 4 read-tools voor individuele entiteiten. Systeem prompt beschrijft generieke workflow-concepten.

**Het platform heeft een VOLLEDIGE workflow-engine met 5 modellen:**

1. **WorkflowDefinition** — Herbruikbare workflow-templates met AI-configuratie
2. **WorkflowState** — Staten met SLA-timing en AI-assistentie (guidance, validatie, checklist)
3. **WorkflowTransition** — Overgangen met goedkeuring, condities en AI (pre-validatie, approval summary, rejection suggestions)
4. **WorkflowInstance** — Actieve workflow-tracking met AI-voorspellingen (completion confidence, predicted completion)
5. **WorkflowStepHistory** — Volledige audittrail met AI-samenvattingen

**De agent kent GEEN van deze modellen en heeft GEEN tools.** Ook is de assessment-workflow in het prompt VEROUDERD: beschrijft 4 fases ("Planned → Active → Completed → Follow-up") terwijl het systeem 7 fases heeft (Aangevraagd → Planning → Voorbereiding → In uitvoering → Review → Rapportage → Afgerond).

**Benodigde tools:** `list_workflow_definitions`, `get_workflow_instance`, `list_available_transitions`, `trigger_transition`, `get_workflow_history`

---

#### AGENT-4: Measure Agent — Kern-tool is kapot

**Huidige staat:** 7 tools waarvan er 1 KAPOT is.

**Kapotte tool:** `link_measure_to_risk` retourneert:
> *"This function is temporarily disabled. Measure-Risk linking is being refactored to Control-Risk linking."*

**Ontbrekend inzicht:** Het platform heeft TWEE aparte concepten:
- **Measure** — Abstract beveiligingsmaatregel (bijv. "Implementeer toegangscontrole")
- **Control** — Context-specifieke testbare implementatie (bijv. "Azure AD MFA voor Finance")

Het systeem prompt gebruikt "maatregelen (controls)" door elkaar. Er zijn geen Control-tools (CRUD, testen, control-risk linking, control-requirement linking).

**Benodigde tools:** `list_controls`, `get_control`, `create_control`, `link_control_to_risk`, `link_control_to_requirement`, `record_control_test`

---

#### AGENT-5: Privacy Agent — Geen GDPR-artifact tools

**Huidige staat:** 5 tools (scope-read + kenniszoek). Claimt expertise in verwerkingsregisters en betrokkenenverzoeken maar kan er niets mee doen.

**De drie kern GDPR-artifacts zijn volledig afwezig:**

| Artifact | Model | Velden | Tools |
|----------|-------|--------|-------|
| Verwerkingsregister (Art. 30) | `ProcessingActivity` (53 regels) | naam, doel, grondslag, betrokkenen-categorieën, bewaartermijnen, doorgifte, DPIA-vereiste | 0 |
| Betrokkenenverzoeken (Art. 15-22) | `DataSubjectRequest` | 8 verzoektypen, identiteitsverificatie, tijdlijn (30 dagen + verlenging), respons | 0 |
| Verwerkersovereenkomsten (Art. 28) | `ProcessorAgreement` | leverancier-koppeling, verwerking-beschrijving, sub-verwerkers, beveiligingseisen, auditrechten, data-locatie | 0 |

Daarnaast: het `Incident`-model heeft 14 breach-specifieke velden (data subjects affected, personal data categories, 72-uurs AP-deadline, etc.) waar de agent niets van weet.

---

#### AGENT-6: Report Agent — Geen rapportage-capabilities

**Huidige staat:** 5 read-tools (lijsten van risico's, maatregelen, beleid, scopes + kenniszoek). Kan geen enkel rapport genereren.

**Het platform heeft:**
- `ReportTemplate` — Jinja2 templates met data-queries
- `ScheduledReport` — Terugkerende rapportgeneratie
- `ReportExecution` — Gegenereerde rapporten met output-URL's
- `Dashboard` — Configureerbare dashboards

**Benodigde tools:** `list_report_templates`, `generate_report`, `get_dashboard_config`, `get_soa_report`, `get_in_control_summary`, `get_kpi_aggregation`

---

### 4.3 Hoge prioriteit (significante lacunes)

#### AGENT-7: Risk Agent — Mist kwantitatieve risicobeheer

De risk agent is het meest complete (14 tools) maar mist:

| Ontbrekend | Impact |
|-----------|--------|
| Monte Carlo simulatie | `RiskQuantificationProfile` model + API volledig geïmplementeerd, agent weet er niets van |
| Kwantitatieve risicobeoordeling | Model ondersteunt frequentie-bereiken en EUR impact, agent kent alleen kwalitatief (LOW/MEDIUM/HIGH/CRITICAL) |
| Vulnerability score (0-100) + control effectiveness (0-100) | Voedt de In Control kwadranten maar agent legt niet uit hoe |
| AI-gesuggereerd kwadrant | `ai_suggested_quadrant` veld bestaat, agent weet niet |
| Onderscheid `mitigation_approach` vs `treatment_strategy` | Twee aparte velden met verschillende semantiek, prompt verwart ze |
| Risk-Policy Principle link | `policy_principle_id` voor Hiaat 6 tracering, niet in prompt |
| Risk scoring formule | score = likelihood_value * impact_value (1-16), nergens gedocumenteerd |

#### AGENT-8: BCM Agent — Geen plan- en testtools

Agent heeft conceptuele BIA-kennis maar kan niet:
- Continuïteitsplannen bekijken/aanmaken (7 plantypes: BCP, DRP, Crisismanagement, Communicatie, Evacuatie, IT DR, Pandemie)
- Continuïteitstesten bekijken/registreren (7 testtypen: Tabletop, Walkthrough, Simulatie, Parallel, Full Interruption, Technical, Notification)
- BIA-drempels raadplegen

#### AGENT-9: Incident Agent — Onvolledige breach-afhandeling

- Geen `list_incidents` tool (kan alleen 1 incident op ID ophalen)
- `get_incident` tool retourneert `reported_at` maar model heeft `date_occurred`/`date_detected`/`date_resolved` (3 aparte timestamps)
- 14 breach-specifieke velden zijn onzichtbaar voor de agent
- Geen tool voor incident-control koppeling (`IncidentControlLink`)
- Geen 72-uurs deadline berekening

#### AGENT-10: Supplier Agent — Geen verwerkersovereenkomst-tools

- Claimt expertise in verwerkersovereenkomsten maar heeft 0 tools ervoor
- Kan geen leveranciersbeoordelingen aansturen
- Weet niets van shared controls concept

---

### 4.4 Gemiddelde prioriteit (functioneel maar incompleet)

| Agent | Ontbrekende capabilities |
|-------|------------------------|
| **assessment_agent** | Geen `list_assessments`, geen BIA-drempel tools, geen bevindingen aanmaken, geen evidence-tools, geen fase-transitie tool |
| **improvement_agent** | Geen initiatief/mijlpaal tracking (`Initiative` model = 100+ regels), geen `list_corrective_actions`, geen backlog-tools, geen exception/waiver beheer |
| **scope_agent** | Geen `ScopeDependency` tools, geen scope CRUD (alleen lezen), geen hiërarchie-traversal, asset-typen en classificatieniveaus niet gedocumenteerd |
| **planning_agent** | Geen `CompliancePlanningItem` tools (12 itemtypen), geen `ManagementReview` tools, geen initiatief-tools, geen backlog-tools |
| **onboarding_agent** | Geen tools om organisatieprofiel te lezen/schrijven/compleetheidscheck |

---

### 4.5 Lage prioriteit (nice-to-have)

| Agent | Ontbrekend |
|-------|-----------|
| **policy_agent** | Geen schrijftool voor policy-statustransitie, geen overdue review check, geen versie-beheer documentatie |
| **objectives_agent** | Geen Objective/KPI CRUD tools, geen KPI-metingen registreren, ObjectiveDomain (ISMS/PIMS/BCMS/Integrated) niet in prompt |
| **maturity_agent** | Geen MaturityAssessment/DomainScore tools, prompt vermeldt 13 domeinen maar model heeft er 18 |

---

### 4.6 Kennisbank (knowledge_tools.py)

#### Beschikbare methodieken (8):

| Sleutel | Status |
|---------|--------|
| `in_control` | Compleet en accuraat |
| `mapgood` | Compleet en accuraat |
| `bio` | Compleet (BBN1/BBN2/BBN3) |
| `iso27001` | Compleet (Annex A structuur) |
| `avg` | Compleet (7 principes, 6 grondslagen, 7 rechten, breach-notificatie) |
| `behandelstrategie` | Compleet (4 strategieën met hard rule) |
| `besluitlog` | Compleet (5 typen, 4 statussen) |
| `in_control_assessment` | Compleet (3 niveaus met berekening) |

#### Ontbrekende methodieken (10):

| Sleutel | Beschrijving | Prioriteit |
|---------|-------------|-----------|
| `rosetta_stone` | Cross-framework mapping met MappingType en AI confidence_score | KRITIEK |
| `soa` | Statement of Applicability met CoverageType en ImplementationStatus | KRITIEK |
| `monte_carlo` | Risicokwantificering met Poisson-frequentie, EUR impact, iteraties | HOOG |
| `workflow_engine` | WorkflowDefinition/State/Transition/Instance met AI-assistentie | HOOG |
| `privacy_artifacts` | ProcessingActivity (Art. 30), DSR (Art. 15-22), ProcessorAgreement (Art. 28) | HOOG |
| `data_breach_procedure` | Incident breach-velden, 72-uurs notificatie, AP-referentie | HOOG |
| `control_vs_measure` | Onderscheid abstract Measure vs context-specifiek testbaar Control | GEMIDDELD |
| `gap_analysis` | Vergelijking ImplementationStatus tegen requirements | GEMIDDELD |
| `rbac_model` | UserScopeRole binding-logica en de 5 rollen | GEMIDDELD |
| `initiative_lifecycle` | IDEA → PROPOSED → APPROVED → IN_PROGRESS → ON_HOLD → COMPLETED → CANCELLED | LAAG |

---

### 4.7 Tools inventaris

#### Read Tools (19 gedefinieerd):

| Tool | Gebruikt door | Opmerking |
|------|---------------|----------|
| `get_risk` | risk, bcm, incident, workflow, measure | OK |
| `list_risks` | 9 agenten | Meest gedeelde tool |
| `search_risks` | risk | OK |
| `get_measure` | assessment, measure | OK |
| `list_measures` | 7 agenten | OK |
| `get_policy` | policy, workflow | OK |
| `list_policies` | policy, report | OK |
| `get_scope` | privacy, bcm, scope, supplier | OK |
| `list_scopes` | 8 agenten | OK |
| `get_assessment` | assessment, workflow, improvement, maturity, planning | OK |
| `get_incident` | incident, improvement | Verkeerde veldnamen |
| `get_requirement` | policy | OK |
| `get_decision` | **GEEN agent** | Gedefinieerd maar NIET geïmporteerd |
| `list_decisions` | risk | OK |
| `check_decision_required` | risk | OK |
| `get_risk_framework` | risk | OK |
| `calculate_in_control` | risk, scope | OK |
| `get_in_control_dashboard` | scope | OK |
| `get_act_overdue` | assessment, improvement | OK |

#### Write Tools (8 gedefinieerd):

| Tool | Gebruikt door | Status |
|------|---------------|--------|
| `create_risk` | risk | Werkend |
| `update_risk` | risk | Werkend |
| `update_risk_treatment` | risk | Werkend |
| `create_decision` | risk | Werkend |
| `create_measure` | measure | Werkend |
| `update_measure` | measure | Werkend |
| `link_measure_to_risk` | measure | **KAPOT** — retourneert "disabled" |
| `create_corrective_action` | incident, improvement | Werkend |

#### Knowledge Tools (3 gedefinieerd):

| Tool | Gebruikt door | Opmerking |
|------|---------------|----------|
| `search_knowledge` | 14 agenten | OK |
| `get_methodology` | 7 agenten | OK (8 methodieken) |
| `classify_risk_quadrant` | **GEEN agent** | Gedefinieerd maar NIET geïmporteerd (risk_agent heeft eigen inline versie) |

#### Wezen (gedefinieerd maar ongebruikt):
1. `get_decision` — niet geïmporteerd door enige agent
2. `classify_risk_quadrant` — niet geïmporteerd (duplicaat van inline `classify_risk` in risk_agent)

---

## 5. Cross-domein samenvatting

### Patronen die meerdere gebieden raken

| Patroon | Frontend impact | Backend impact | AI-agent impact |
|---------|----------------|----------------|-----------------|
| **Compliance module** | Standards dropdown leeg (UX-16) | Route 404 (API-1), geen seed data (API-7) | Agent kent SoA en Rosetta Stone niet (AGENT-1) |
| **RBAC systeem** | Roldialoog uitgecommentarieerd (UX-5) | IDOR op dashboard (API-5) | Admin agent kan geen rollen toewijzen (AGENT-2) |
| **Incidentbeheer** | CRUD kapot (UX-1) | Severity breakdown leeg (API-10) | Agent mist list en breach-velden (AGENT-9) |
| **Beleidsbeheer** | CRUD kapot (UX-2), geen workflow-handhaving (UX-9) | — | Agent mist schrijftools (AGENT policy) |
| **BIA/In-Control** | BIV-waarden verkeerd (UX-10) | Scope-filter ontbreekt (API-3) | BCM agent mist BIA-tools (AGENT-8) |
| **Workflow-engine** | Assessment-fases overslaanbaar (UX-12) | — | Agent kent engine niet (AGENT-3) |
| **Privacy/AVG** | — | — | Agent mist alle 3 kern-artifacts (AGENT-5) |

---

## 6. Prioriteitsmatrix — Top 20 fixes

| # | Type | ID | Beschrijving | Ernst | Moeite |
|---|------|----|-------------|-------|--------|
| 1 | Frontend | UX-1 | Incident create/update/delete toevoegen aan `client.py` | KRITIEK | Laag (3 methodes) |
| 2 | Frontend | UX-2 | Policy create/update/delete toevoegen aan `client.py` | KRITIEK | Laag (3 methodes) |
| 3 | Backend | API-1 | Standards route prefix fixen in `standards.py` | KRITIEK | Laag (5 regels) |
| 4 | Frontend | UX-5 | RBAC dialoog uncommentariëren in `users.py` | KRITIEK | Minimaal (1 regel) |
| 5 | Backend | API-2 | `__fields__` → `model_dump()` in `organization_profile.py` | KRITIEK | Laag (3 regels) |
| 6 | Frontend | UX-3 | Dashboard quick-action knoppen `on_click` handlers toevoegen | KRITIEK | Laag |
| 7 | Frontend | UX-8 | Correctieve actie `due_date` en `assigned_to` meesturen | HOOG | Laag (2 regels) |
| 8 | Backend | API-3 | In-control finding scope filter toevoegen | HOOG | Gemiddeld |
| 9 | Frontend | UX-10 | BIV-dropdown waarden corrigeren (Laag/Gemiddeld/Hoog/Kritiek) | HOOG | Laag |
| 10 | Frontend | UX-4 | Backlog `on_mount` toevoegen | HOOG | Minimaal (1 regel) |
| 11 | Frontend | UX-6 | Besluit-formulier velden toevoegen (verloopdatum, scope, besluitnemer) | HOOG | Gemiddeld |
| 12 | Backend | API-4 | Simulatie `risk_ids` Query() annotatie toevoegen | GEMIDDELD | Laag (1 regel) |
| 13 | Backend | API-5 | Dashboard IDOR fixen met `get_current_user` | GEMIDDELD | Gemiddeld |
| 14 | AI | AGENT-1 | Compliance agent herschrijven + 7 tools | KRITIEK | Hoog |
| 15 | AI | AGENT-4 | Measure agent `link_measure_to_risk` fixen, Control-tools toevoegen | KRITIEK | Hoog |
| 16 | AI | AGENT-5 | Privacy agent GDPR-tools toevoegen | KRITIEK | Hoog |
| 17 | AI | AGENT-2 | Admin agent gebruikers/RBAC-tools toevoegen | KRITIEK | Hoog |
| 18 | AI | AGENT-3 | Workflow agent herschrijven met engine-tools | KRITIEK | Hoog |
| 19 | AI | AGENT-6 | Report agent rapportage-tools toevoegen | KRITIEK | Hoog |
| 20 | Backend | API-7 | Seed-script voor Standards/Requirements (ISO 27001, BIO) | HOOG | Gemiddeld |

---

> **Dit rapport is gegenereerd op basis van volledige code-analyse van het IMS-platform.** Alle genoemde regelnummers, bestandspaden en modelverwijzingen zijn geverifieerd tegen de actuele broncode.
