# Welkom, Bijdrager

Dit document is bedoeld voor nieuwe bijdragers. Het geeft je de context die je nodig hebt om effectief bij te dragen aan dit platform — zonder dat je eerst duizenden regels code hoeft te lezen.

---

## Wat is IMS?

IMS is een **Governance, Risk & Compliance (GRC)-platform** voor Nederlandse publieke organisaties: gemeenten, zorginstellingen, waterschappen en shared service centers.

Het combineert drie managementsystemen in één platform:

| Systeem | Standaard | Doel |
|---------|-----------|------|
| **ISMS** | ISO 27001 / BIO 2.0 | Informatiebeveiliging |
| **PIMS** | ISO 27701 / AVG | Privacy |
| **BCMS** | ISO 22301 | Bedrijfscontinuïteit |

De kerngedachte: organisaties hoeven niet drie losse systemen bij te houden. IMS is de **single source of truth** voor normen, risico's, controls, audits en bewijs.

---

## Hoe is het platform opgebouwd?

IMS volgt een strikte **4-laagse architectuur**:

```
Laag 1: MODEL   — SQLModel + PostgreSQL    — de data, de waarheid
Laag 2: API     — FastAPI                  — bewaker van RBAC, validatie, workflows
Laag 3: TOOLS   — Reflex (Python → React) — dunne UI, geen business logic
Laag 4: AI      — Ollama / Mistral / Scaleway — ondersteunt, beslist nooit
```

> **"The Model leads. The API guards. Tools execute. AI supports."**

Dit is geen suggestie — het is de wet. Business logic hoort in de API, nooit in de frontend. De AI adviseert, de mens beslist (AVG Art. 22).

---

## Mappenstructuur op hoofdlijnen

```
IMS-tooling/
├── backend/
│   └── app/
│       ├── main.py              # FastAPI initialisatie, middleware
│       ├── core/                # Config, DB-sessie, RBAC, security, risk appetite engine
│       ├── models/core_models.py  # 90+ entiteiten — begin hier voor datamodel
│       ├── api/v1/endpoints/    # Endpoints per domein (risks, controls, assessments, ...)
│       └── agents/domains/      # 19 AI-agenten, één per domein
├── frontend/ims/
│   ├── ims.py                   # App-routing, 25 pagina's
│   ├── pages/                   # Pagina-componenten
│   ├── state/                   # Reactieve state (22+ classes)
│   └── api/client.py            # 120+ API-aanroepen (httpx async)
├── ims-proces/                  # Methodologie & procesgidsen (zie hieronder)
├── docs/                        # Architectuur- en ontwerpdocumentatie
├── plans/                       # Implementatieplannen en roadmaps
└── docker-compose.yml           # 5 services: db, api, pgadmin, ollama, frontend
```

---

## De `ims-proces/` map

Deze map bevat de **implementatiemethodologie**: hoe een organisatie stap voor stap van niets naar een operationeel IMS gaat. Denk aan:

- `CONTEXT.md` — het centrale design register (22 stappen, 4 fases, 18 AI-agenten)
- `blueprint-handboek.md` — sjabloon voor het IMS-handboek van een organisatie
- HTML-tools — interactieve roadmap, governance-simulator, register-tracker

De code (IMS-tooling) en de methodologie (ims-proces) zijn bewust gescheiden gehouden binnen dezelfde repo.

---

## Hoe werk je mee?

### Opstarten

```bash
# 1. Kopieer en vul het .env-bestand in
cp .env.example .env

# 2. Start de volledige stack
docker-compose up -d

# 3. Frontend lokaal draaien (development)
cd frontend && python -m reflex run
```

Toegangspunten:

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API (Swagger) | http://localhost:8000/docs |
| pgAdmin | http://localhost:5050 |
| Ollama | http://localhost:11434 |

### Na elke wijziging

Commit en push altijd direct na je wijziging:

```bash
git add <bestanden>
git commit -m "type: korte beschrijving"
git push origin main
```

Gebruik betekenisvolle prefixen: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`.

---

## Wat moet je weten voordat je begint?

### 1. Het datamodel is de kern

`backend/app/models/core_models.py` (~5000 regels) is het fundament. Begrijp de entiteiten die relevant zijn voor jouw domein voordat je iets bouwt. De modellen zijn leidend — de API volgt, de UI volgt.

### 2. Multi-tenancy zit overal

Elke query filtert op `tenant_id`. Dit is geen optie — het is een harde vereiste. Vergeet je het, introduceert je een data-lek tussen organisaties.

### 3. RBAC via scopes

Toegang werkt via `UserScopeRole`: een gebruiker heeft een rol binnen een specifieke scope. De vijf rollen:

| Rol | Niveau |
|-----|--------|
| Beheerder | Volledige toegang |
| Coordinator | Domein-coördinatie |
| Eigenaar | Scope-eigenaar |
| Medewerker | Operationele taken |
| Toezichthouder | Alleen-lezen, toezicht |

### 4. AI-agenten bijhouden

Er zijn 19 AI-agenten in `backend/app/agents/domains/`. Als je een feature toevoegt of wijzigt, check dan of de bijbehorende agent nog klopt. De agent moet de gebruiker accurate begeleiding kunnen geven bij de nieuwe functionaliteit.

### 5. EU data sovereignty

AI draait standaard lokaal (Ollama) of op EU-cloud (Mistral/Scaleway FR). Configureer **nooit** een US-gebaseerde AI-provider zonder expliciete juridische goedkeuring.

---

## Waar vind je meer?

| Document | Inhoud |
|----------|--------|
| `README.md` | Volledig platformoverzicht, alle features |
| `CLAUDE.md` | Werkafspraken voor AI-assisted development |
| `docs/ARCHITECTURE_PRINCIPLES.md` | Architectuurprincipes uitgelegd |
| `docs/COMPLETE_DESIGN_OVERVIEW.md` | Volledig systeemontwerp |
| `docs/IMS ROLES AND RESPONSIBILITIES.md` | Rolbeschrijvingen en drie-lijnen model |
| `ims-proces/CONTEXT.md` | Implementatiemethodologie (22 stappen) |

---

## Vragen?

Neem contact op met het ontwikkelteam. Welkom aan boord.

## Visuele identiteit

Voor AI-gegenereerde afbeeldingen (banners, iconen, presentatievisuals) zijn uitgewerkte prompts beschikbaar in:

`docs/IMS - Image Prompts.md` (of de gedeelde map van jouw organisatie)

7 prompts beschikbaar: Architectuur, Governance, De IMS-olifant, Dashboard UI, Hero Banner, Team & Bijdragers, Icoon/Logo.
