# RFC 0004 — M4 Frontend UI (AI Governance beheer-routes)

> **Status:** V1 geïmplementeerd · **Auteur:** open-source projectteam · **Datum:** 2026-05-12 (status bijgewerkt 2026-05-13)
> **Type:** Frontend-uitbreiding · **Module-impact:** M4 (AI Governance) volledig
> **Beslissing nodig vóór:** demo aan organisaties met AI-systemen die EU AI Act-compliance moeten aantonen
>
> **Implementatie-stand (2026-05-13)**
> - `/beheer/ai-systemen` — CRUD met classifier-advies inline, badge per EU AI Act-risico, filter op risico-categorie en deployment-status.
> - `/beheer/hitl-checkpoints` — audit-log-lijst met review-telling + laatste decision, review-paneel met verplichte motivatie, append-only historie, filter "alleen niet-gereviewd".
> - `/admin/agent-tokens` — scope-multi-select uit 8 presets, two-step confirm, eenmalige JWT-display, optionele koppeling aan AI-systeem voor traceability.
> - Audit-logs-endpoint `/ai-hitl-checkpoints/audit-logs` met review-telling + last_decision per log voedt de werklijst.
> - Tests: 5 vitest-tests per AI-systemen, HITL, agent-tokens; e2e `m4-ai-systemen`, `admin-agent-tokens`, `beheer-hitl-review` met directe DB-verificatie.
> - **V2-werk in `[Unreleased]` van CHANGELOG**: detail-pagina per AI-systeem, edit-flow, `classification_override_note`-veld, HITL `parent_checkpoint_id` voor genest review.

---

## 1. Probleem

M4 (AI Governance) is in `docs/modules.md` als operationeel gemarkeerd op backend-niveau: AI-systemenregister, EU AI Act-classifier, NIST AI RMF als normenkader, AI conformity assessment, HITL-checkpoints, NHI agent-tokens — alle zes bouwstenen werken via API, met 43 backend-tests.

Wat er **niet** is: één frontend-route voor M4. Geen pagina onder `/beheer/ai-systemen`, geen HITL-review-UI, geen NHI-token-beheer voor admins. Eindgebruikers moeten vandaag via `curl`, Postman of het OpenAPI-`/docs`-endpoint werken om M4-functionaliteit te raken.

Gevolg: M4 is **demo-incompleet**. Een CISO of compliance-officer kan vandaag niet:

- Een AI-systeem registreren via UI
- EU AI Act-classificatie-advies inline opvragen
- HITL-checkpoints reviewen die door agents geschreven zijn
- NHI-token uitgeven aan een agent met scope-beperking

Voor een open-source platform met "AI-ready"-positionering in de README is dit een gat dat eerst gevuld moet voordat M4 als feature aan klanten verkocht kan worden.

---

## 2. Niet-doelen

Dit RFC behandelt **niet**:

- **Agent-conversaties UI** (chatten met agent vanuit een platform-pagina). Apart RFC; raakt M3-AI-laag, niet M4-governance.
- **NIST AI RMF-controls-UI** specifiek. NIST AI RMF zit in M1 (normenkader-tabel) — bestaande `/beheer/controls`-flow toont al NIST-controls dankzij Rosetta Stone-mapping. Geen aparte route nodig.
- **AI-conformiteitsbeoordeling UI**. Bestaande assessment-flow (`/beheer/assessments`) wordt uitgebreid met `assessment_type='ai_conformity'`-filter en AI-systeem-koppeling — niet als nieuwe route, maar als variant. Apart issue.
- **EU AI Act-classifier batch-mode** (meerdere systemen tegelijk classificeren). API ondersteunt het, UI alleen één-voor-één in V1.
- **Drift-monitoring / continue assessment**. Buiten scope.

---

## 3. Voorstel — drie nieuwe routes

### 3.1 `/beheer/ai-systemen` — AI-systemenregister

**Doel:** CRUD op `ims_ai_systems` met inline EU AI Act-classifier-advies.

**Pagina-componenten:**

| Component | Functie |
|-----------|---------|
| `AISystemList` | Lijst-view: naam, leverancier, type, classificatie-badge, eigenaar, status |
| `AISystemFilters` | Filter op classificatie (verboden / hoog / beperkt / minimaal), op leverancier, op zoektekst |
| `AISystemForm` | Create/edit-formulier met inline classifier-knop |
| `AISystemClassifierAdvice` | Toont uitlegregels van `/api/v1/ai-systems/classify-suggestion` naast invoer-velden |
| `AISystemDetail` | Detail-pagina met velden, gekoppelde assessments (filter op `ai_conformity`), HITL-checkpoints |

**Form-flow met classifier:**

1. Gebruiker vult kenmerken (sector, doel-doelgroep, beslissingsimpact, biometrie, ...) — komt overeen met classifier-input-schema
2. Knop "Classificatie-advies opvragen" → `POST /api/v1/ai-systems/classify-suggestion`
3. Response toont voorgestelde classificatie (`verboden | hoog | beperkt | minimaal`) + uitlegregels
4. Gebruiker accepteert advies (vult `eu_ai_act_risk`-veld) of overschrijft handmatig met motivatie
5. Submit → `POST /api/v1/ai-systems`

**Belangrijk:** classifier-advies is *advies*. UI maakt duidelijk dat de mens de classificatie beslist, niet de regel-engine. Toont audit-trail wanneer mens-overschrijft-advies via verplicht `classification_override_note`-veld (nieuw veld op `ims_ai_systems` — Alembic-migratie nodig, klein).

### 3.2 `/beheer/hitl-checkpoints` — Human-in-the-loop review

**Doel:** EU AI Act art. 14 ("menselijk toezicht") operationeel maken via UI. Agents schrijven HITL-checkpoints via API; mens reviewt via deze pagina.

**Pagina-componenten:**

| Component | Functie |
|-----------|---------|
| `HitlList` | Lijst van openstaande checkpoints (filter: `reviewed=false`) |
| `HitlDetail` | Detail: agent-naam, AI-systeem-koppeling, agent-output, beslismoment, geadviseerde-actie |
| `HitlReviewForm` | Reviewer kiest: `approve` / `reject` / `escalate` + verplichte motivatie |
| `HitlHistory` | Per AI-systeem: tijdlijn van checkpoints met reviewer-actie |

**Backend-aanpassing:** `ai_hitl_checkpoints`-tabel is vandaag append-only (UPDATE/DELETE ingetrokken). Review-actie wordt gemodelleerd als **nieuwe row** met `parent_checkpoint_id`-FK naar originele checkpoint. Behoudt append-only-invariant; review wordt onderdeel van keten, niet mutatie. Alembic-migratie voegt `parent_checkpoint_id` toe.

**RBAC:** `tactisch_lid` of `discipline_eigenaar` mag reviewen; `lijnmanager` ziet read-only.

**Default-view:** "Openstaande checkpoints in mijn scope" — niet de hele tenant. Voorkomt dat reviewer in een organisatie met veel AI-systemen verdrinkt.

### 3.3 `/admin/agent-tokens` — NHI-token-beheer

**Doel:** admin geeft een AI-agent een token uit met beperkte scope en TTL.

**Pagina-componenten:**

| Component | Functie |
|-----------|---------|
| `AgentTokenForm` | Velden: agent-naam, AI-systeem (optioneel FK), scope-lijst (multi-select uit vooraf-gedefinieerde capabilities), TTL (max 24h) |
| `AgentTokenIssued` | One-time-display van JWT na uitgifte (waarschuwing: "kopieer nu, wordt niet opnieuw getoond") |
| `AgentTokenAuditList` | Lijst van uitgegeven tokens (zonder JWT-inhoud — alleen metadata) uit `ai_audit_logs` |

**RBAC:** alleen `admin` van tenant.

**Backend-aanpassing:** `POST /api/v1/auth/agent-token` bestaat al. Audit-logging registreert uitgifte. UI voegt geen nieuwe endpoints toe.

**Vooraf-gedefinieerde scopes** (lijst in code, niet config):

- `risks:read`, `risks:write`
- `controls:read`, `controls:write`
- `assessments:read`, `assessments:write`
- `hitl:write` (agent mag checkpoints schrijven, niet reviewen)
- `documents:read`

Uitbreiden alleen met expliciete RFC — voorkomt scope-creep waar agents te veel rechten krijgen.

### 3.4 Navigatie-impact

`AppShell` / `Sidebar` krijgt nieuwe sectie **"AI-governance"** met drie items:

- AI-systemen (`/beheer/ai-systemen`) — zichtbaar voor alle rollen met assessment-toegang
- HITL-checkpoints (`/beheer/hitl-checkpoints`) — zichtbaar vanaf `discipline_eigenaar`
- Agent-tokens (`/admin/agent-tokens`) — alleen `admin`

Sectie is **conditioneel zichtbaar**: alleen tonen als tenant minstens één AI-systeem heeft geregistreerd OF tenant heeft `feature_ai_governance=true` in `ims_tenant_settings`. Niet-AI-tenants zien de sectie niet — voorkomt onnodige cognitive load.

### 3.5 Geen aparte state-management library

Bestaande pagina's gebruiken `useSWR` voor server-state, `useState` voor form-state, `useState`/`useReducer` voor lokale UI-state. Geen Zustand, geen Redux. Dit RFC houdt zich aan dat patroon. M4-UI introduceert geen nieuwe globale state.

---

## 4. Alternatieven (afgewezen of geparkeerd)

| Alternatief | Status |
|-------------|--------|
| **HITL-review als modal binnen AI-systeem-detail** | Afgewezen. Reviewer wil overzicht over alle openstaande checkpoints — modal-only-flow verbergt dat. |
| **AI-systemenregister als subroute van assessments** (`/beheer/assessments/ai-systemen`) | Afgewezen. AI-systeem leeft langer dan een assessment; eigen route. |
| **Agent-token-UI in tenant-instellingen** | Afgewezen. Tenant-instellingen is voor tenant-admin-config; agent-token-uitgifte is operationele actie. Aparte route maakt audit-flow duidelijker. |
| **Inline classifier in lijst-view** (klik op rij → advies) | Geparkeerd. UX-verbetering voor V2. V1 doet classifier in form. |
| **Drift-monitoring en re-classify-alerts** | Geparkeerd. Aparte module. |
| **Nieuw component-framework** (bv. Radix/shadcn naast bestaande UI) | Afgewezen. Bestaande `components/ui/*` (Card, Button, Badge, Input, Select) is voldoende. |

---

## 5. Risico's en mitigaties

| Risico | Mitigatie |
|--------|-----------|
| Classifier-advies wordt als "beslissing" gezien i.p.v. advies | UI-tekst expliciet "advies, niet beslissing". `classification_override_note` verplicht bij overschrijven. Tooltip met uitleg per regel uit `eu_ai_act_classifier.py`. |
| NHI-token-JWT lekt via screenshots / logs | One-time-display met expliciete waarschuwing. JWT staat niet in URL. Token-detail-pagina toont alleen metadata. |
| Reviewer overweldigd door HITL-volume | Default-filter op "mijn scope". Bulk-actie ("approve geselecteerde 5") parkeren voor V2 met eerst gebruiksdata om te zien hoeveel checkpoints werkelijk binnenkomen. |
| AI-governance-sectie zichtbaar voor tenants zonder AI | Conditioneel renderen (sectie 3.4). Tenant-admin kan handmatig aanzetten via instelling. |
| `parent_checkpoint_id`-keten te diep (eindeloze review-op-review) | Soft-cap: na 3 niveaus geen verdere review meer. Backend valideert. |
| Bestaand RBAC kent geen "review"-rol — wie mag reviewen? | Mapping: `discipline_eigenaar` of hoger. Geen nieuwe rol toevoegen. Bij vraag uit klant: vervolg-RFC. |
| Frontend-build groter door extra routes | Verwaarloosbaar (~30kB). Routes zijn server-rendered Next.js — code-splitting automatisch. |

---

## 6. Acceptatie-criteria

Dit RFC is "geïmplementeerd" wanneer:

- [ ] Routes `/beheer/ai-systemen`, `/beheer/ai-systemen/[id]`, `/beheer/hitl-checkpoints`, `/admin/agent-tokens` werken end-to-end
- [ ] Alembic-migratie voegt `classification_override_note` toe aan `ims_ai_systems` en `parent_checkpoint_id` aan `ai_hitl_checkpoints`
- [ ] Conditional navigation: AI-governance-sectie verschijnt alleen bij relevante tenant
- [ ] Backend-tests blijven groen; nieuwe tests dekken `parent_checkpoint_id`-validatie (geen cyclus, max diepte 3) en `classification_override_note`-verplicht-bij-overschrijven
- [ ] Frontend e2e Playwright-spec: AI-systeem registreren → classifier raadplegen → opslaan → assessment koppelen → HITL-checkpoint reviewen → agent-token uitgeven (admin-rol)
- [ ] `docs/modules.md` M4-sectie bijgewerkt: Frontend-status van ❌ naar ✅
- [ ] `docs/gebruik.md` (of nieuw `docs/ai-governance-gebruik.md`) beschrijft de drie flows voor eindgebruikers
- [ ] Screenshots van drie routes in `README.md` of `docs/platform-overzicht.html`

---

## 7. Open vragen voor discussie

1. **Wie mag `classification_override_note` schrijven**: enkel admin, of ook `tactisch_lid`? Voorstel: `tactisch_lid` of hoger, want classificatie raakt assessment-scope.
2. **Conditionele AI-governance-sectie**: zichtbaar op basis van AI-systeem-aantal (>0) of expliciete tenant-setting? Voorstel: tenant-setting voorrang; tellen alleen als fallback.
3. **HITL-default-filter "mijn scope"**: hoe definiëren we "mijn scope" voor reviewer? Voorstel: HITL-checkpoints aan AI-systemen waarvan `owner_user_id` = current user, plus checkpoints zonder eigenaar (algemene pool). Discussiepunt.
4. **NHI-token uitgifte-confirmation**: extra confirmation-dialog ("weet u zeker?") vóór genereren? Voorstel: ja, want JWT is moeilijk in te trekken vóór TTL (geen revocation-lijst in V1).
5. **Audit-trail in UI**: tonen we agent-token-uitgifte in `/admin/agent-tokens/audit`-tab, of alleen via `ai_audit_logs`-export? Voorstel: aparte audit-tab voor zichtbaarheid.
6. **Scope-lijst uitbreiding**: hoe voegen we later scopes toe zonder UI-redeploy? Voorstel: scope-lijst in `ims_tenant_settings` (per tenant of platform-wide). V1: hardcoded; V2: configurable.

---

## 8. Beslismomenten

- **Goedkeuring RFC** vóór frontend-routes worden geïmplementeerd
- **Per-tenant beslissing**: AI-governance-sectie aan/uit (sectie 3.4)
- **Mapping HITL-rol naar RBAC**: bevestiging dat `discipline_eigenaar` voldoende is, of nieuwe rol nodig
- **Acceptatie van scope-creep-grens**: hardcoded scope-lijst in V1, geen tenant-configurable scopes

---

## 9. Referenties

- `docs/ai-governance-uitbreiding.md` — oorspronkelijke voorstel-doc voor M4
- `docs/eu-ai-act-classification.md` — classifier-regels en criteria
- `ROADMAP.md` Spoor 2 — alle zes M4-bouwstenen
- `backend/app/api/v1/endpoints/ai_systems.py`, `ai_hitl.py`, `auth.py` (`/agent-token`) — bestaande endpoints
- EU AI Act art. 14 (menselijk toezicht), art. 16 (technische documentatie), art. 17 (kwaliteitsbeheersysteem)

---

## Changelog

| Datum | Wijziging | Door |
|-------|-----------|------|
| 2026-05-12 | Initieel concept | open-source projectteam |
