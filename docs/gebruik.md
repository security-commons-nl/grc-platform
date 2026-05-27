# GRC-platform — Gebruikershandleiding

> Voor CISO's, ISO's, strategisch/tactisch gremium-leden, discipline-eigenaren, lijnmanagers en concernadviseurs risicomanagement die het platform inrichten of dagelijks gebruiken.
>
> Laatste update: 2026-05-13. Voor installatie + deployment: [`deployment.md`](deployment.md). Voor architectuur: [`architectuur.md`](architectuur.md).

---

## Inhoud

1. [Inloggen en eerste oriëntatie](#1-inloggen-en-eerste-oriëntatie)
2. [Rollen — wie mag wat](#2-rollen--wie-mag-wat)
3. [Inrichtingswizard — IMS opbouwen in 22 stappen](#3-inrichtingswizard--ims-opbouwen-in-22-stappen)
4. [Dagelijks gebruik — Beheer](#4-dagelijks-gebruik--beheer)
5. [Risicokwantificatie — Monte Carlo](#5-risicokwantificatie--monte-carlo-m5)
6. [AI Governance — EU AI Act & menselijk toezicht](#6-ai-governance--eu-ai-act--menselijk-toezicht-m4)
7. [Admin — Organisatie, custom velden, tokens, gebruikers](#7-admin--organisatie-custom-velden-tokens-gebruikers)
8. [Multi-tenancy en data-isolatie](#8-multi-tenancy-en-data-isolatie)
9. [Veelvoorkomende foutmeldingen](#9-veelvoorkomende-foutmeldingen)

---

## 1. Inloggen en eerste oriëntatie

Na installatie bereik je het platform op `http://localhost:3000` (of de domeinnaam die in [`deployment-caddy.md`](deployment-caddy.md) is geconfigureerd).

**Inloggen — ontwikkelmodus**

Het loginscherm toont:

- **User ID** — random gegenereerd UUID per browser-sessie (read-only)
- **Tenant ID** — vooringevuld op de seed-tenant (`00000000-0000-0000-0000-000000000001`)
- **Rol** — dropdown met 6 rollen

Kies een rol en klik **Inloggen**. Je komt op `/inrichten`, het overzicht van de inrichtingsstappen.

> **Let op:** dev-tokens hebben een TTL van 60 minuten. Voor productie zet je SSO/OIDC voor — zie [`configuratie.md`](configuratie.md) § Authenticatie.

**Navigatie**

De sidebar links groepeert het werk in vier blokken:

| Blok | Routes | Wie gebruikt het |
|------|--------|------------------|
| **Inrichten** | `/inrichten` (overzicht), `/inrichten/[stap]`, `/inrichten/besluiten`, `/inrichten/documenten` | strategisch + tactisch gremium tijdens IMS-opbouw |
| **Beheer** | `/beheer` (dashboard), `/beheer/risicos`, `/beheer/controls`, `/beheer/assessments`, `/beheer/bevindingen`, `/beheer/bewijs`, `/beheer/incidenten`, `/beheer/ai-systemen`, `/beheer/hitl-checkpoints` | dagelijks GRC-werk |
| **Admin** | `/admin/organisatie`, `/admin/velden`, `/admin/gebruikers`, `/admin/agent-tokens`, `/admin/tenant` | alleen rol `admin` |
| **Profiel** | rechtsboven: rol, uitloggen | iedereen |

---

## 2. Rollen — wie mag wat

Het platform kent **6 RBAC-rollen** (hoog → laag):

| Rol | Wat je kan |
|-----|------------|
| **admin** | Volledige toegang, gebruikersbeheer, tenant-instellingen, agent-tokens uitgeven, custom velden + org-units beheren |
| **strategisch_lid** | Strategisch gremium (was: SIMS) — besluitvorming op inrichtingsniveau, HITL-reviews vastleggen |
| **tactisch_lid** | Tactisch gremium (was: TIMS) — risico's, controls, assessments aanmaken/bijwerken, HITL-reviews vastleggen |
| **discipline_eigenaar** | Verantwoordelijke voor een specifiek discipline (ISMS/PIMS/BCMS) — bewerken binnen eigen domein |
| **lijnmanager** | Inzage in eigen scope + acties uitvoeren op toegewezen risico's/controls |
| **viewer** | Alleen-lezen |

**Hoe rollen werken**

- Rollen zitten in `ims_user_tenant_roles` — een gebruiker kan **meerdere rollen** hebben in dezelfde tenant.
- Een rol kan **domein-specifiek** zijn (`ISMS`, `PIMS`, `BCMS`) of domein-overstijgend.
- Backend dwingt rollen af via `require_role()` op endpoints; UI verbergt knoppen waar je geen recht op hebt.

---

## 3. Inrichtingswizard — IMS opbouwen in 22 stappen

Voor organisaties die nog geen volwassen ISMS/PIMS/BCMS hebben. Eenmalig doorlopen, daarna periodiek bijwerken.

### De vier fasen

| Fase | Stappen | Wat je doet |
|------|---------|-------------|
| **0. Voorbereiding** | 1–2 | Domeinkeuze (ISMS/PIMS/BCMS) + scope-afbakening |
| **1. Fundament** | 3–7 | Beleid, rollen, bestuurlijk draagvlak, risicobereidheid |
| **2. Analyse** | 8–13 | Assets, dreigingen, kwetsbaarheden, gap-analyse, risicoregister |
| **3. Maatregelen** | 14–18 | Controls selecteren uit BIO/ISO, implementatieplan, eigenaren |
| **4. Werking** | 19–22 | Monitoring, audits, incident-response, managementreview |

### Per stap

Elke stap (`/inrichten/[stepId]`) bevat:

- **Uitleg + voorbeeld** — wat je hier doet, met een ingevuld voorbeeld
- **AI-assistent (chat-paneel rechts)** — domein-agent met RAG-context op normen + eerdere besluiten. Antwoorden zijn altijd **adviserend, nooit beslissend**, en gemarkeerd `AI CONCEPT — verifieer handmatig`.
- **Outputs** — concrete artefacten (een besluit, een document, een lijst risico's) die aan de stap gekoppeld worden via "koppel-knoppen"
- **Stap-vaststellen** — pas mogelijk als alle verplichte outputs aangeleverd zijn (`StepReadiness`-check) en strategisch_lid of admin de vaststelling doet

### Besluitlog en documenten

- `/inrichten/besluiten` — chronologisch overzicht van alle bestuurlijke besluiten. Onveranderlijk (geen UPDATE/DELETE in DB).
- `/inrichten/documenten` — versies van beleidsdocumenten, met `vastgesteld_by_name` + datum + welk besluit hen vaststelde. Export naar Markdown of HTML.

### Stap-afhankelijkheden

Sommige stappen kunnen pas starten als andere `vastgesteld` zijn (bv. risicoregister vereist voltooide asset-analyse). De UI toont dit als `🔒 Vereist stap N`.

---

## 4. Dagelijks gebruik — Beheer

### Dashboard — `/beheer`

Eén pagina-overzicht met:

- **Drie domein-tegels** (ISMS / PIMS / BCMS) met inrichtingsscore per domein + aantal afgeronde stappen
- **Vier KPI-tegels**: open risico's, controls, open bevindingen, recente incidenten
- **Inrichtingsvoortgang** — balk met "N van 22 stappen afgerond"

Bedoeld voor managementreview en wekelijkse stand-ups.

### Risico's — `/beheer/risicos`

- **Lijst + risicokaart** — 5×5 matrix likelihood × impact met aantal risico's per cel
- **Nieuw risico** — formulier vraagt scope, domein, titel, beschrijving, likelihood (1–5), impact (1–5), optionele kwantitatieve impact (zie [§5](#5-risicokwantificatie--monte-carlo-m5))
- **Organisatie-eenheid** (RFC 0002) — dropdown om risico te koppelen aan cluster/team/afdeling. Laat leeg voor tenant-niveau.
- **Custom velden** (RFC 0001) — als de admin tenant-specifieke velden heeft gedefinieerd (zie `/admin/velden`) verschijnen ze automatisch onderaan het formulier.
- **Filter** bovenaan: filter op organisatie-eenheid, optioneel **inclusief sub-units** (recursive descendants-walk).

Risico's met `impact_distribution` gevuld krijgen een **Simuleer**-knop in de tabel.

### Controls — `/beheer/controls`

- Lijst van beheersmaatregelen, gekoppeld aan requirements uit normenkaders.
- **Nieuwe control** — titel, domein, implementatiestatus (`gepland` / `in_uitvoering` / `operationeel` / `niet_effectief`), beschrijving.
- **Organisatie-eenheid + custom velden** — zelfde mechaniek als risico's. Een control op cluster-niveau wordt zichtbaar als je dat cluster filtert op het risico-dashboard.
- Filter op organisatie-eenheid + sub-units.

### Assessments — `/beheer/assessments`

Audits, DPIA's, pentests, BC-oefeningen, gap-analyses, management reviews.

- **Nieuw assessment** — type, domein, geplande datum, optionele scope.
- **AI Conformity-assessment** — extra type voor EU AI Act art. 6+9 conformiteitsbeoordeling, vereist koppeling aan een AI-systeem.
- Organisatie-eenheid + custom velden idem als bij risico's en controls.

### Bevindingen — `/beheer/bevindingen`

- **Nieuwe bevinding** — knop bovenaan opent een formulier met verplichte velden: assessment (dropdown), titel, ernst (laag/midden/hoog/kritiek), status (open/in_behandeling/afgesloten), optionele beschrijving.
- Een bevinding hangt **altijd aan een assessment** (audit-trail-conventie). Als er nog geen assessments zijn, is de knop disabled met een waarschuwingsbalk die je naar `/beheer/assessments` verwijst.
- Op de pagina filter je verder op ernst en status. Corrective actions kun je via de API koppelen aan een bevinding (UI-knop volgt in vervolg-iteratie).

### Bewijs — `/beheer/bewijs`

- Bewijsstukken (`document` / `screenshot` / `log` / `rapport` / `verklaring`) gekoppeld aan controls.
- Verzameldatum + optionele geldigheid-tot voor periodieke hercertificering.
- Storage_path verwijst naar locatie buiten DB (S3, MinIO, fileshare).

### Incidenten — `/beheer/incidenten`

- Datalek, beveiligingsincident, beschikbaarheid, compliance, overig.
- `reported_at` wordt automatisch op `now()` gezet; bewerk in DB als je een ouder incident registreert.
- Severity-filter + status-filter.

---

## 5. Risicokwantificatie — Monte Carlo (M5)

Naast de kwalitatieve likelihood × impact-score kun je een **financiële range** opgeven en daarop simuleren.

### Setup per risico

In het risico-aanmaakformulier (of via PATCH op een bestaand risico):

1. Klap **"+ Kwantitatieve impact (optioneel)"** open.
2. Kies een distributie:
   - **Uniform** — min/max bedrag (geen modus)
   - **Triangular** — min, meest waarschijnlijk, max
3. Vul de bedragen.

Pas vanaf hier verschijnt de **Simuleer**-knop in de tabel.

### Simulatie draaien

Klik **Simuleer** → 10.000 iteraties (default). Boven aan de pagina verschijnt:

- **Histogram** (30 klassen) met VaR-95 + VaR-99 referentielijnen
- **Percentielen-staaf** (p5, p25, p50, p75, p95, p99)
- **Natuurlijke-taal-interpretatie**:
  - "Verwachte schade per voorval is € X"
  - "In 1 op de 20 gevallen loopt de schade op tot meer dan € P95"
  - Conditionele waarschuwing bij grote spreiding (P95 − P5 > 1.5× expected loss)
  - Conditionele waarschuwing bij materieel staartrisico

### Historie

Elke simulatie wordt automatisch opgeslagen in `ims_risk_simulations`. API: `GET /api/v1/risks/{id}/simulations` voor paginerende lijst. Optioneel label + note per run via query-parameters.

Reproduceerbaarheid: stuur `?seed=42` voor identieke uitkomst.

---

## 6. AI Governance — EU AI Act & menselijk toezicht (M4)

Voor organisaties met AI-systemen die onder de EU AI Act (verordening 2024/1689) vallen.

### AI-systemenregister — `/beheer/ai-systemen`

- **Nieuw AI-systeem** — naam, leverancier, systeem-type (chatbot, beslis-ondersteuning, classificatie, monitoring, ...), beschrijving, use case.
- **Classificatie-advies opvragen** — deterministische keyword-classifier geeft een **suggested_risk** (`unacceptable` / `high` / `limited` / `minimal`), reasoning en welke keywords het triggerde. Advies is **adviserend, geen besluit**.
- **Advies overnemen** — vult het veld "Gekozen risico-categorie". Eindbeslissing blijft mens.
- Filter op risico-categorie + deployment-status.

> **Goed om te weten:** de classifier is geen wettelijke kwalificatie. Detail van regels in [`docs/eu-ai-act-classification.md`](eu-ai-act-classification.md).

### HITL-checkpoints — `/beheer/hitl-checkpoints`

Menselijk toezicht op AI-agent-activiteit (EU AI Act art. 14). Twee deelweergaven:

- **Audit-log-lijst** — alle agent-runs (`ai_audit_logs`) met agent-naam, model, prompt/completion-tokens, aantal reviews, laatste decision-badge.
- **Review-paneel** (klik **Bekijk**) — leg een eigen oordeel vast: `approved` / `rejected` / `modified` / `pending`, met **verplichte motivatie**. Historie groeit append-only.
- Filter "Alleen niet-gereviewd" om je werklijst te zien.

### NIST AI RMF als normenkader

Beschikbaar onder `/api/v1/standards/` als zesde normenkader (naast BIO 2.0, ISO 27001, ISO 27701, ISO 22301, AVG). Vier kernfunctie-requirements (Govern / Map / Measure / Manage). Koppel controls eraan zoals aan elk ander framework.

### AI Conformity Assessment

Een speciaal `assessment_type='ai_conformity'` vereist verplichte koppeling aan een AI-systeem. Gebruik dit voor conformiteitsbeoordeling onder EU AI Act art. 43.

---

## 7. Admin — Organisatie, custom velden, tokens, gebruikers

Alleen toegankelijk voor rol `admin`.

### Organisatie-eenheden — `/admin/organisatie`

Boom-editor voor hiërarchische organisatiestructuur (directie → cluster → afdeling → team).

- **Nieuwe eenheid** — naam, optionele code, type (`directie` / `cluster` / `afdeling` / `team` / `overig`), optionele parent (dropdown over bestaande units).
- **Max-diepte 6** afgedwongen.
- **Cycle-prevention** — een unit kan niet eigen voorouder worden (zowel server-side check als DB-CHECK `ck_org_unit_no_self_parent`).
- **Verwijderen** — alleen mogelijk als de unit geen sub-units heeft (anders 409 Conflict).

Eenheden worden gebruikt voor:

- Filtering op risico's, controls, assessments
- Aggregatie-rapportages (toekomstig)
- Eigenaarschap-toewijzing per cluster/team

### Custom velden — `/admin/velden`

Form-builder voor tenant-specifieke velden zonder code-wijziging.

- **Nieuw veld** — kies entity (`risk` / `control` / `assessment` / `finding`), veldnaam (snake_case, niet-botsend met kernkolommen zoals `tenant_id`, `status`, `likelihood`), label, type, optioneel verplicht.
- **4 veldtypes**:
  - **Tekst** — vrij tekstveld met maxLength
  - **Getal** — number-input
  - **Ja/nee** — boolean checkbox
  - **Keuzelijst** — komma-gescheiden waarden → string-enum
- Onder de motorkap genereert de UI een JSON-Schema-fragment dat server-side gevalideerd wordt. JSON-Schema-validatie blokkeert ongeldige waarden bij POST/PATCH.

Eens een veld is gedefinieerd, verschijnt het automatisch in het bijbehorende create-formulier. Verwijderen van een definitie laat bestaande waarden in de tabel staan.

### Agent-tokens — `/admin/agent-tokens`

Non-Human Identity (NHI) tokens uitgeven voor AI-agents en automatisering.

1. **Naam** van de agent (bv. `incident-summarizer`).
2. **Geldigheid** — 15 min / 1 uur (default) / 4 uur / 8 uur / 24 uur (maximum).
3. **Scopes** — multi-select uit 8 presets:
   - `risks:read` / `risks:write`
   - `controls:read` / `controls:write`
   - `assessments:read` / `assessments:write`
   - `hitl:write`
   - `documents:read`
4. **Optionele koppeling aan AI-systeem** — voor traceability.
5. **Two-step confirm** — knop "Token uitgeven..." opent een bevestigingsvraag; pas na "Ja, uitgeven" wordt de JWT aangemaakt.
6. **One-time JWT-display** — de token wordt **eenmalig getoond**. Kopieer hem direct naar de geheime-opslag van de agent.

> **Beveiligingsuitgangspunten:**
> - Kort-levend (max 24 uur) — bij lekken is blootstelling beperkt
> - Scope-beperkt — agent kan alleen wat je expliciet toestaat
> - Auditeerbaar — agent-acties verschijnen in `ai_audit_logs` en zijn reviewbaar via HITL
> - Herleidbaar tot uitgevende admin (EU AI Act art. 14 menselijk toezicht)

### Gebruikers — `/admin/gebruikers`

CRUD op gebruikers binnen je tenant + toewijzen van rol(len).

- **Nieuwe gebruiker** — naam, email, externe ID, rol, optioneel domein (`ISMS` / `PIMS` / `BCMS` / leeg = alle).
- **Status** — actief/inactief flag. Inactieve users kunnen niet inloggen maar blijven in audit-logs zichtbaar.

### Tenant-instellingen — `/admin/tenant`

Momenteel een placeholder die naar de Swagger UI verwijst (`/docs`). Tenant-naam, type en geavanceerde configuratie wijzig je via `PATCH /api/v1/tenants/{id}`.

---

## 8. Multi-tenancy en data-isolatie

Het platform draait één codebase + één database voor meerdere organisaties (tenants). Isolatie via twee lagen:

1. **Application layer** — elke endpoint filtert expliciet op `current_user.tenant_id`.
2. **Database layer** — PostgreSQL Row Level Security (RLS) op 27 tabellen. Zelfs als de applicatie zou falen, kan een tenant nooit data van een andere tenant zien.

Defense-in-depth: een platformbeheerder die per ongeluk inlogt als admin van tenant A ziet geen data van tenant B, ook niet via een ad-hoc SQL-query (mits via de `ims_app`-rol).

Cross-tenant koppelingen (bv. `organizational_unit_id` van een andere tenant in een risico-payload) worden expliciet geweigerd met HTTP 422 — niet alleen door RLS, ook door endpoint-validatie. Dat geeft je een nette foutmelding in plaats van een silent failure.

---

## 9. Veelvoorkomende foutmeldingen

| Melding | Oorzaak | Oplossing |
|---------|---------|-----------|
| `403 Forbidden — role X required` | Je rol heeft geen rechten voor deze actie | Vraag een admin om de juiste rol; of log uit en in als hogere rol |
| `422 organizational_unit_id verwijst niet naar een unit binnen deze tenant` | Cross-tenant koppeling of niet-bestaande UUID | Kies een unit uit de eigen organisatie-boom |
| `422 field_name botst met kernkolom` | Custom field-naam botst met `tenant_id`, `status`, ... | Kies een andere `field_name` |
| `409 unit heeft sub-units en kan niet verwijderd worden` | Verwijderen geblokkeerd zolang er kinderen zijn | Verwijder eerst alle sub-units (bottom-up) |
| `429 Rate limit exceeded: 10 per 1 minute` | Te veel auth-calls vanaf hetzelfde IP | Wacht 1 minuut. In productie: zet rate-limit per `.env` (`RATE_LIMIT_AUTH`) |
| `ai_conformity assessment requires ai_system_id` | Assessment van type `ai_conformity` zonder gekoppeld AI-systeem | Koppel een AI-systeem of kies een ander assessment-type |
| AI CONCEPT — verifieer handmatig | Document is door AI gegenereerd | Mens-in-de-lus: lees, bewerk, en zet de status op `vastgesteld` |

---

## Verder lezen

- **Architectuur** — [`docs/architectuur.md`](architectuur.md) (4-laagse model)
- **Modules** — [`docs/modules.md`](modules.md) (M0–M6 frame)
- **Risicokwantificatie diep** — [`docs/risico-kwantificatie.md`](risico-kwantificatie.md)
- **AI Governance diep** — [`docs/ai-governance-uitbreiding.md`](ai-governance-uitbreiding.md) + [`docs/eu-ai-act-classification.md`](eu-ai-act-classification.md)
- **RFC's** (architectuurbesluiten) — [`docs/rfc/`](rfc/)
- **Configuratie** — [`docs/configuratie.md`](configuratie.md) (env-vars, AI-keys, rate-limit)
- **Productie-deployment** — [`docs/deployment.md`](deployment.md) + [`docs/deployment-caddy.md`](deployment-caddy.md)
- **Security-hardening** — [`docs/security-hardening.md`](security-hardening.md)
- **Monitoring + backup** — [`docs/monitoring.md`](monitoring.md), [`docs/backup.md`](backup.md)
