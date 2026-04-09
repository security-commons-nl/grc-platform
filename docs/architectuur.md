# GRC-platform — Architectuur

> Voor contributors die begrijpen willen hoe het platform is opgebouwd en waarom.

---

## Vierlaagse architectuur

```
Laag 1: MODEL (Data)       — PostgreSQL 16 + SQLAlchemy 2.0
Laag 2: API   (Logica)     — FastAPI + JWT + RBAC + RLS
Laag 3: TOOLS (UI)         — Next.js 15
Laag 4: AI    (Agents/RAG) — OpenAI-compatible client (OpenRouter / Ollama / EU-hosted)
```

Het principe: **logica zit in de API, niet in de UI**. De frontend is een dunne glasplaat. Dit maakt alternatieve clients (CLI, integraties, andere UI's) mogelijk zonder de businesslogica te dupliceren.

---

## Database (Laag 1)

**Multi-tenant via Row Level Security**

Elke tabel die tenantdata bevat heeft een `tenant_id`-kolom. PostgreSQL RLS-policies zorgen dat queries automatisch gefilterd worden op de actieve tenant — afgedwongen op databaseniveau, niet alleen in applicatiecode.

Dit betekent: zelfs als er een bug in de API zit die de tenant_id niet meestuurt, levert de database geen data terug.

**Structuur**

| Module | Tabellen |
|--------|----------|
| Auth / tenants | `tenants`, `users`, `roles`, `user_roles` |
| GRC-engine | `risks`, `controls`, `risk_controls`, `assessments`, `findings` |
| Evidence | `evidence_items`, `control_evidence` |
| Incidenten | `incidents`, `incident_timeline` |
| Normen | `frameworks`, `framework_controls`, `control_mappings` |
| IMS-inrichting | `ims_steps`, `step_responses`, `setup_progress` |

**Migraties**

Alembic beheert het schema. Er zijn drie basismigraties:
1. `schema` — alle tabellen aanmaken
2. `rls` — Row Level Security policies instellen
3. `seed` — basis-normenkaders en rollen laden

Nieuwe migraties aanmaken: `docker-compose exec api alembic revision --autogenerate -m "beschrijving"`

---

## API (Laag 2)

**FastAPI + async SQLAlchemy**

Alle endpoints zijn asynchroon. De API volgt REST-conventies: `GET /risks`, `POST /risks`, `PATCH /risks/{id}`, etc.

**Authenticatie**

JWT (HS256). De token bevat `user_id`, `tenant_id` en `role`. Elke request die tenantdata raakt, haalt `tenant_id` uit de token en zet die als RLS-context op de databaseverbinding.

```python
# Zie backend/app/core/auth.py
async def set_tenant_context(db: AsyncSession, tenant_id: str):
    # tenant_id komt uit een geverifieerde JWT — nooit direct uit user input
    await db.execute(text("SET app.current_tenant = :tid"), {"tid": tenant_id})
```

**RBAC**

Rollen worden gecontroleerd via dependency injection. Elke endpoint declareert welke rollen toegang hebben:

```python
@router.post("/risks", dependencies=[Depends(require_role("ciso", "admin"))])
```

**Router-structuur**

```
backend/app/api/v1/endpoints/
├── auth.py         # login, token refresh
├── risks.py        # risicobeheer
├── controls.py     # maatregelen
├── assessments.py  # audits
├── evidence.py     # bewijsbeheer
├── incidents.py    # incidentregistratie
├── frameworks.py   # normenkaders
├── ims_setup.py    # inrichtingswizard stappen
├── users.py        # gebruikersbeheer
└── tenants.py      # organisatiebeheer (admin only)
```

---

## Frontend (Laag 3)

**Next.js 15 + TypeScript + TailwindCSS v4**

De frontend bevat geen businesslogica. Alle validatie en berekeningen zitten in de API. De UI fetcht data, toont die, en stuurt mutaties naar de API.

**Route-structuur**

```
frontend/src/app/
├── (auth)/login/           # Inlogscherm
├── inrichten/              # IMS-wizard (22 stappen)
│   └── stap/[nummer]/
├── beheer/                 # Dagelijks GRC-gebruik
│   ├── risicos/
│   ├── controls/
│   ├── assessments/
│   ├── incidenten/
│   └── bewijs/
└── admin/                  # Platformbeheer (admin-rol)
    ├── gebruikers/
    └── organisaties/
```

**State management**

SWR voor server-state (data fetching + caching). React Context voor auth-state (user, tenant, token). Geen Redux of andere global state library.

---

## AI (Laag 4)

De AI-laag bestaat uit domeinagenten, een RAG-pipeline en een configureerbare LLM-client. AI is altijd adviserend: het platform genereert concepten en suggesties, maar beslissingen worden altijd door mensen genomen.

### LLM-client

`backend/app/services/llm_client.py` — OpenAI-compatible interface. Configureerbaar via `.env`:

| Variabele | Standaard | Beschrijving |
|-----------|-----------|--------------|
| `AI_API_BASE` | `https://openrouter.ai/api/v1` | API-endpoint (OpenRouter, Ollama, Mistral EU, etc.) |
| `AI_API_KEY` | — | API-sleutel |
| `AI_MODEL_NAME` | `mistralai/mistral-small-latest` | Taalmodel |
| `AI_EMBEDDING_MODEL` | `openai/text-embedding-3-small` | Embedding-model voor RAG |

De standaardconfiguratie gebruikt OpenRouter. Voor EU-conforme deployments: zie [configuratie.md](configuratie.md).

### Domeinagenten

Per IMS-inrichtingsstap is er een gespecialiseerde agent. Elke agent:

1. Laadt normatieve context via RAG (zie onder)
2. Voert een gesprek met de gebruiker om de stap in te vullen
3. Genereert concept-documenten op basis van het gesprek (JSON, gelabeld als `AI CONCEPT — verifieer handmatig`)
4. Schrijft elke LLM-aanroep weg naar `AIAuditLog`

| Agent | Verantwoordelijkheid |
|-------|---------------------|
| `commitment_agent` | Bestuurlijk draagvlak en mandatering |
| `context_agent` | Organisatiecontext en scope |
| `scope_agent` | Toepassingsgebied IMS |
| `governance_agent` | Governance-structuur (SIMS/TIMS) |
| `gap_agent` | Gap-analyse t.o.v. normenkaders |
| `register_agent` | Registers (risico's, assets, verwerkingen) |
| `controls_agent` | Maatregelen en controls |

### RAG-pipeline

`backend/app/services/rag/` — semantisch zoeken via pgvector cosine similarity.

Twee kennislagen:
- **Normatief** (`tenant_id IS NULL`) — gedeelde normteksten: BIO 2.0, ISO 27001, ISO 27701, ISO 22301, AVG
- **Organisatie** (tenant-scoped) — organisatiespecifieke documenten en eerder opgeleverde stap-outputs

Bij elke agent-aanroep worden de top-3 meest relevante kennisfragmenten meegestuurd als context aan het model.

### Auditbaarheid AI

Elke LLM-aanroep wordt vastgelegd in `AIAuditLog`:
- Welke agent, welke stap, welke tenant
- Model-naam, prompt-tokens, completion-tokens
- Gekoppeld aan het gegenereerde `AgentMessage`

Optioneel: Langfuse-integratie voor volledige observability (`LANGFUSE_SECRET_KEY`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_HOST` in `.env`).

---

## Tests

105 backend-tests in `backend/tests/`. Opgebouwd met `pytest` + `httpx` async.

Tests draaien altijd tegen een echte PostgreSQL-testdatabase (geen mocks). Dit voorkomt divergentie tussen test- en productiegedrag.

```bash
docker-compose exec api pytest --tb=short          # alle tests
docker-compose exec api pytest tests/test_risks.py  # één module
```

---

## Auditbaarheid by design

Elke beslissing en datamutatie in het platform is traceerbaar. Dit is geen feature maar een ontwerpvereiste — governance-tooling die zichzelf niet kan verantwoorden, is geen governance-tooling.

Concreet in het datamodel:

| Tabel | Wat het vastlegt |
|-------|-----------------|
| `assessments` + `findings` | Auditbevindingen per control, inclusief wie wat wanneer heeft vastgesteld |
| `evidence_items` | Bewijsstukken gekoppeld aan controls, met vervaldatum |
| `incidents` + `incident_timeline` | Tijdlijn van beveiligingsincidenten stap voor stap |
| `step_responses` | Elke inrichtingsstap die een organisatie heeft doorlopen |
| `risk_controls` | Welke controls aan welke risico's zijn gekoppeld, en wanneer |

Alle tabellen hebben `created_at` en `updated_at` timestamps. Mutaties worden niet overschreven maar als nieuwe records toegevoegd waar de context dat vereist (bijv. `incident_timeline`).

---

## Designkeuzes

**Waarom FastAPI?** Asynchroon, type-safe via Pydantic, automatische OpenAPI-docs. Geschikt voor een team dat ook Python kent voor datawerk en scripting.

**Waarom Next.js en niet een SPA-framework?** Server-side rendering maakt het eenvoudiger om auth-state consistent te houden. De inrichtingswizard heeft veel server-rond-trips; SSR reduceert de waargenomen laadtijd.

**Waarom een configureerbare AI-provider?** De LLM-client is bewust provider-agnostisch. De standaardconfiguratie gebruikt OpenRouter (breed model-aanbod, snelste manier om te starten). Voor productie-deployments bij publieke organisaties zijn EU-conforme alternatieven aan te raden: [Mistral EU API](https://mistral.ai) (GDPR-compliant, EU-gehost) of Ollama lokaal. Geen vendor lock-in — alleen `AI_API_BASE` en `AI_MODEL_NAME` hoeven te wijzigen.

**Waarom geen ORM-abstractie bovenop SQLAlchemy?** De RLS-implementatie vereist directe controle over databasesessies en transacties. Een extra ORM-laag zou dat bemoeilijken.
