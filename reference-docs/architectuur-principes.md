# IMS — Architectuurprincipes

*Vastgesteld: 2026-03-19*
*Van toepassing op: het volledige IMS-platform (inrichtingsmodus + beheermodus)*

---

## Context

IMS is een **gemeentelijk intern platform**, gebouwd door en voor ambtenaren van Gemeente Leiden en de Leidse Regio. Het is geen commercieel SaaS-product. Eigendom ligt bij Gemeente Leiden.

Het platform ondersteunt het inrichten en beheren van een Integrated Management System (ISMS/PIMS/BCMS) conform ISO 27001, ISO 27701, ISO 22301 en BIO 2.0.

---

## 1. Governance-principes

### 1.1 AI bereidt voor, de mens beslist
AI is altijd adviserend. Geen enkel door AI gegenereerd document, beoordeling of besluit wordt zonder expliciete menselijke goedkeuring vastgesteld. De stap `concept → in review → vastgesteld` is voor alle AI-output verplicht — zonder uitzondering.

### 1.2 Auditbaarheid by design
Elke datamutatie, accordering en AI-interactie is traceerbaar. Audit trails zijn geen afterthought maar ontwerpvereiste. Het besluitlog is immutable — besluiten worden nooit overschreven, alleen aangevuld.

### 1.3 EU-datasouvereiniteit
Gemeentelijke data en AI-verwerking blijven binnen de EU. Geen afhankelijkheid van niet-EU cloud providers voor kritieke verwerkingen. Standaard AI-model: Mistral via Scaleway (FR). Lokale Ollama als toekomstige fallback.

### 1.4 Proportionaliteit
Governance-maatregelen zijn proportioneel aan het risico. Niet elk onderdeel vereist hetzelfde toezicht. Mandatering is rol-gebaseerd: normale accordering door TIMS-lid, restrisico-acceptatie door IMS Stuurgroep.

### 1.5 Transparantie
AI-output is altijd herleidbaar. Geen black-box besluitvorming. Onzekerheid in AI-gegenereerde content wordt expliciet gemarkeerd ("gebaseerd op documentextractie — verifieer handmatig").

### 1.6 Database is altijd leidend
Documenten (handboek, SoA, auditrapportages) zijn gegenereerde views van structurele data. Nooit omgekeerd. Exports zijn momentopnamen met tijdstempel — bewijs, niet bron. Geen bestandsopslag voor documentinhoud.

---

## 2. Technische principes

### 2.1 Infra-agnostisch
Het platform draait op elke containerized omgeving — een VPS (Hetzner, OVH), Azure Container Apps, of on-premise Docker. Geen vendor lock-in op infrastructuurniveau. Alle configuratie via omgevingsvariabelen (`.env`).

### 2.2 Eenvoud boven complexiteit
Kies de simpelste oplossing die werkt. Voeg complexiteit alleen toe wanneer het aantoonbaar nodig is. Monoliet met modulaire structuur — geen microservices tenzij de schaal dat vereist.

### 2.3 Security in lagen (defense in depth)
Beveiliging is geen enkele maatregel maar een gelaagde architectuur. Elke laag compenseert mogelijk falen van andere lagen. Zie sectie 5 (Security baseline).

### 2.4 Least privilege
Toegang tot data en systemen is minimaal. AI-agents krijgen alleen de rechten die ze nodig hebben. Database-gebruikers hebben per-module minimale rechten. API-endpoints valideren rol bij elke aanroep.

### 2.5 Infrastructure as Code
Alle infrastructuur is reproduceerbaar via `docker-compose.yml` en `.env`. Handmatige configuratie op de server is een uitzondering, niet de norm. Elke omgeving (dev/staging/prod) is reproduceerbaar vanuit dezelfde bestanden.

### 2.6 Observability is verplicht
Alle AI-gebruik wordt gelogd (Langfuse of equivalent). Uptime monitoring op alle publieke endpoints. Zonder monitoring ontdek je problemen pas als gebruikers klagen.

### 2.7 Verifieer, vertrouw niet op defaults
Beveiligingsinstellingen worden altijd expliciet geconfigureerd en geverifieerd. Defaults zijn onbetrouwbaar — ze variëren per OS-versie en package-versie.

---

## 3. Tech stack

Gebaseerd op bewezen keuzes uit productie-omgevingen voor de Nederlandse publieke sector.

| Laag | Keuze | Reden |
|------|-------|-------|
| **Backend** | FastAPI + Python 3.12 | Snel, async-native, goede OpenAPI-docs |
| **Database** | PostgreSQL 16 + pgvector | Één DB voor relationele data én RAG-embeddings |
| **ORM** | SQLAlchemy 2.0 async + Alembic | Bewezen, type-safe, migraties versioneerd |
| **Frontend** | Next.js App Router + TypeScript + TailwindCSS | Route groups per module, gedeelde auth/context |
| **Auth** | JWT (RS256) via eigen auth-module of Keycloak OIDC | Multi-tenant, rol-gebaseerd |
| **AI-gateway** | Model-agnostisch via OpenRouter of directe provider API | Wisselen van provider zonder agent-code aan te passen |
| **AI-observability** | Langfuse (self-hosted of cloud) | Tracing, kosten, kwaliteitsevaluatie |
| **Reverse proxy** | Caddy | Automatische TLS, security headers, rate limiting |
| **Containers** | Docker Compose | Dev en productie gelijk, infra-agnostisch |
| **Async taken** | Celery + Redis (optioneel in v1) | Alleen inzetten als async background jobs nodig zijn |
| **Object storage** | MinIO of Azure Blob (configureerbaar) | Zelfgehoste S3-compatibele opslag |

**Niet in v1:** Kubernetes, message brokers (Kafka/RabbitMQ), aparte vector-database (pgvector is voldoende).

---

## 4. Datamodel-principes

### 4.1 Module-prefixed tabellen
Alle IMS-specifieke tabellen krijgen een prefix:

```
Platform-breed (gedeeld):
  users, organisations, tenant_config, ai_audit_logs

IMS-specifiek:
  ims_standards, ims_requirements, ims_requirement_mappings
  ims_steps, ims_step_executions, ims_decisions
  ims_risks, ims_controls, ims_assessments, ims_evidence
  ims_documents, ims_document_versions
  ims_scores_setup, ims_scores_grc
```

### 4.2 Multi-tenant via tenant_id
Elke rij in IMS-tabellen heeft een `tenant_id`. Queries filteren altijd op `tenant_id` — geen uitzonderingen. Cross-tenant data alleen via de `visibility`-laag (privé/regionaal).

### 4.3 Normversioning
Standards hebben een `version`-veld en een `superseded_by`-verwijzing. RequirementMappings verwijzen naar een specifieke normversie. Historische scores blijven gekoppeld aan de norm waarop ze zijn gebaseerd.

### 4.4 Immutability voor audit-kritieke data
Besluitlog-entries, accorderingen en vastgestelde documentversies worden nooit overschreven. Correcties krijgen een nieuw record met verwijzing naar het origineel.

### 4.5 Twee-scores-model
```
ims_scores_setup:   inrichtingsscore per tenant per domein (0-100%)
                    gebaseerd op stap-afronding + jaarlijkse herbevestiging

ims_scores_grc:     GRC-score per tenant per domein (0-100%)
                    data-gedreven, berekend op basis van actuele GRC-activiteit
                    start op 0% bij aanvang beheermodus
```

---

## 5. Agent-architectuur

### 5.1 Kennis in RAG-store, niet in agent-prompts
Agents bevatten geen embedded domeinkennis. Kennis zit in de RAG-store (pgvector). Bij normwijziging: RAG-store bijwerken → alle agents profiteren automatisch.

**RAG-store twee lagen:**
```
Normatieve laag (platform-breed, gedeeld):
  BIO 2.0, ISO 27001, ISO 27701, ISO 22301, AVG-tekst
  normenmapping, handboek-blueprint

Organisatielaag (per tenant):
  organisatiecontextdocument, vastgestelde besluiten
  handboek-versies, gemeente-specifieke beleidsdocumenten
  → nooit cross-tenant
```

### 5.2 6-8 domain agents + 1 orchestrator
Geen 1-op-1 agent per stap. Domein-agents zijn breed inzetbaar:

| Agent | Domeinen |
|-------|---------|
| Governance-agent | Stappen 1, 3, 4, governance-documenten |
| ISMS-agent | BIO 2.0, ISO 27001, stap 5, 6, 9, 10, 11 |
| PIMS-agent | AVG, ISO 27701, privacy-tracks alle stappen |
| BCMS-agent | ISO 22301, BIA, BCP, stap 9, 10, 13 |
| Risk-agent | Risicoanalyse, behandeling, risicoregister |
| Compliance-agent | Gap-analyse, normenmapping, SoA |
| Reporting-agent | Auditrapportages, management review, dashboards |
| Normenkader-agent | Nieuwe frameworks inladen en opsplitsen |

Orchestrator routeert op basis van stap-context naar de juiste domain agent.

### 5.3 Agentic normenkader-workflow
Nieuwe normen worden niet door een developer ingeladen. Een 2e-lijnsrol (CISO, FG) uploadt een document of URL → normenkader-agent splitst op in `Standard` + `Requirement`-entries → menselijke review → activatie.

### 5.4 Human-in-the-loop altijd verplicht
AI genereert altijd een concept. Een mens maakt altijd de overgang naar `vastgesteld`. Geldt voor: handboek-secties, gap-analyse, normenkader-entries, risicobeoordelingen, SoA-scores, auditrapportages.

### 5.5 ROCKTOC-formaat voor agent-specs
Elke agent wordt gespecificeerd via:
```
ROL               — wie is de agent?
DOEL              — wat bereikt hij?
CONTEXT           — welke data heeft hij toegang tot?
TOOLS             — welke tools mag hij aanroepen?
TAKEN             — concrete taakbeschrijving
OPERATING GUIDELINES — gedragsregels
CONSTRAINTS       — wat mag hij niet?
OUTPUT            — verwachte outputformaat
ACCEPTATIECRITERIA — wanneer is de output goed?
```

---

## 6. Security baseline

*Gebaseerd op LIVIQ SECURE-ARCHITECTURE-BASELINE.md (productie-gevalideerd, maart 2026)*

### Tier 1 — Verplicht bij eerste deployment

| # | Maatregel | Rationale |
|---|-----------|-----------|
| 1.1 | SSH uitsluitend via VPN (Tailscale/Headscale) | Elimineert brute-force aanvalsvlak op poort 22 |
| 1.2 | UFW default deny incoming (alleen 80, 443) | Elke open poort is een aanvalsvlak |
| 1.3 | SSH-configuratie expliciet hardenen (`PermitRootLogin no`, `PasswordAuthentication no`) | Defaults zijn onbetrouwbaar — altijd expliciet instellen |
| 1.4 | Caddy op host-netwerk | Zodat rate limiting en IP-logging werken op echt client-IP |
| 1.5 | Container-poorten alleen op loopback (`127.0.0.1:xxxx`) | Voorkomt dat Caddy wordt omzeild |
| 1.6 | Container-hardening (`no-new-privileges`, `seccomp`, `cap_drop ALL`, `mem_limit`, `pids_limit`) | Beperkt blast radius bij gecompromitteerde container |
| 1.7 | `restart: unless-stopped` op alle containers | Voorkomt dat platform offline blijft na reboot |
| 1.8 | `.env`-bestanden `chmod 600` | Voorkomt leesbare secrets voor andere gebruikers |
| 1.9 | Security headers in Caddy (`X-Content-Type-Options`, `X-Frame-Options`, `HSTS`, `Referrer-Policy`) | Bescherming tegen clickjacking, MIME-sniffing |

### Tier 2 — Binnen eerste week

- Fail2ban voor SSH-bescherming (extra laag achter VPN)
- CrowdSec voor HTTP threat intelligence
- Docker egress firewall (DOCKER-USER chain — whitelist uitgaand verkeer)
- Docker socket proxy (nooit directe socket-mount in containers)
- Rate limiting op API- en AI-endpoints (voorkomt kostbare LLM-misbruik)

### Tier 3 — Defense-in-depth

- Host Intrusion Detection (AIDE, rkhunter)
- Observability stack (Uptime Kuma, Grafana Alloy → Loki)
- Container image scanning (Trivy) in CI/CD
- Gepinde image-versies (nooit `:latest`)
- Admin-interfaces alleen via VPN

### Gemeente-specifiek (aanvullend op SaaS-baseline)

- PostgreSQL: `scram-sha-256` authenticatie, bind op loopback, aparte DB-user per module
- Redis: `requirepass`, bind op loopback, `rename-command FLUSHALL ""`
- Admin-console (PGAdmin, monitoring) alleen via VPN-IP
- Audit logging conform BIO 2.0 en AVG art. 30

---

## 7. Deployment

### 7.1 Omgevingen

```
Development:   docker-compose up -d (lokaal)
Staging:       VPS of Azure Container Apps (identiek aan productie)
Productie:     VPS of Azure (geconfigureerd via .env)
```

### 7.2 Configuratie via omgevingsvariabelen

```env
# Database
POSTGRES_SERVER=...
POSTGRES_USER=...
POSTGRES_PASSWORD=...
POSTGRES_DB=ims

# AI
AI_API_BASE=https://api.scaleway.ai/v1      # Mistral via Scaleway
AI_MODEL_NAME=mistral-small-latest
AI_FALLBACK_BASE=http://localhost:11434/v1  # Ollama (toekomstig)

# Auth
JWT_SECRET=...
JWT_ALGORITHM=RS256

# Observability
LANGFUSE_SECRET_KEY=...
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_HOST=...

# Tenant
DEFAULT_TENANT_ID=leiden
```

### 7.3 Azure vs. VPS

| Criterium | VPS (Hetzner/OVH) | Azure Container Apps |
|-----------|-------------------|---------------------|
| Kosten | €20-80/maand | Variabel (hoger bij scale) |
| Controle | Volledig | Beperkt op infra-niveau |
| Compliance | EU-gehost (DE/FR) | EU-regio beschikbaar |
| Beheer | Handmatig hardening | Managed security |
| Leiden-voorkeur | Waarschijnlijk VPS v1 | Mogelijk later |

Het platform is zo gebouwd dat wisselen tussen beide geen code-wijzigingen vereist.

---

## 8. Niet in scope (bewuste keuzes)

| Wat | Waarom niet |
|-----|------------|
| Kubernetes | Niet nodig voor deze schaal — Docker Compose volstaat |
| Microservices | Monoliet met modules is simpeler te bouwen en te beheren |
| Aparte vector-database | pgvector in PostgreSQL is voldoende |
| Real-time sync met TopDesk/ServiceNow | Platform beheert governance, niet operationele events |
| Eigen auth (wachtwoord + 2FA bouwen) | Gebruik bestaande auth-patronen of Keycloak |
| Automatisch lerende agents | Te vroeg, te complex — handmatige prompt-verbetering in v1 |

---

## 9. RBAC — Permissiematrix

### Rolhiërarchie

```
admin
  └── sims_lid          (SIMS = strategisch niveau — restrisico/beleidsafwijking)
        └── tims_lid    (TIMS = tactisch niveau — normaal accorderen)
              └── discipline_eigenaar  (operationeel, eigen domein)
                    └── lijnmanager   (eigen processen)
                          └── viewer  (read-only)
```

Hogere rol erft alle rechten van lagere rol. `admin` is platformbeheerder (technisch), niet inhoudelijk.

### Permissiematrix per resource

| Resource | viewer | lijnmanager | discipline_eigenaar | tims_lid | sims_lid | admin |
|----------|--------|-------------|---------------------|----------|----------|-------|
| Stap-executions lezen | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Stap-executions bijwerken | ❌ | eigen proces | eigen domein | ✅ | ✅ | ✅ |
| Besluit aanmaken (normaal) | ❌ | ❌ | ✅ groen | ✅ | ✅ | ✅ |
| Besluit aanmaken (restrisico) | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| Besluit aanmaken (beleidsafwijking) | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| Risico's lezen | ✅ | eigen | eigen domein | ✅ | ✅ | ✅ |
| Risico's aanmaken/bewerken | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| Controls lezen | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Controls aanmaken/bewerken | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| Assessments aanmaken | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| Evidence toevoegen | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Verbeteracties aanmaken | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Documenten lezen (privé) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Documenten vaststellen | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| Normenkader beheren | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| Users beheren | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Scores inzien | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**Domeinscoping:** `tims_lid` en `discipline_eigenaar` met `domain=ISMS` zien alleen ISMS-resources. De API filtert altijd op zowel `tenant_id` als `domain` (indien gevuld op de rol).

**Escalatieladder risico-accordering:**
- Groen (score 1–4): `discipline_eigenaar`
- Geel (5–9): `tims_lid`
- Oranje (10–14): `sims_lid`
- Rood (15–25): `sims_lid` + expliciete notatie in besluitlog

### Regionale rollen

| Rol | Wat mag het |
|-----|-------------|
| `regionaal_toezichthouder` | Cross-tenant READ op regionaal-gepubliceerde documenten en scores. Nooit schrijven. |
| `regionaal_viewer` | Idem, maar alleen documenten — geen scores of besluitlog. |

### API-afdwinging

Elke endpoint valideert in deze volgorde:
1. JWT geldig en niet verlopen
2. `tenant_id` uit JWT matcht resource-tenant (geen cross-tenant leaks)
3. Gebruiker heeft vereiste rol (via `user_tenant_roles`)
4. Domeinfilter toegepast indien rol domein-specifiek is
5. Bij schrijfoperaties: escalatieladder gecontroleerd (applicatielogica, niet DB)

Nooit rechten hardcoden per endpoint — gebruik een centrale `require_role()`-dependency in FastAPI.

---

## 10. API Security — Implementatiechecklist

### Authenticatie & autorisatie

| # | Vereiste | Implementatie |
|---|----------|---------------|
| A1 | JWT RS256, expiry 15 min | `python-jose` + RS256 keypair in `.env` |
| A2 | Refresh token, expiry 7 dagen, httpOnly cookie | Aparte `/auth/refresh`-endpoint |
| A3 | Token revocation bij uitloggen | Blacklist in Redis (korte TTL) |
| A4 | `tenant_id` in JWT-claims | Middleware extraheert en valideert bij elke request |
| A5 | RBAC-check via centrale dependency | `Depends(require_role("tims_lid"))` in FastAPI |

### Rate limiting (via Caddy)

| Endpoint-categorie | Limiet |
|-------------------|--------|
| Algemene API | 200 req/min per IP |
| Auth-endpoints (`/auth/login`, `/auth/refresh`) | 10 req/min per IP |
| AI-endpoints (`/agents/*`) | 20 req/min per gebruiker |
| Export-endpoints (PDF/Word generatie) | 5 req/min per gebruiker |

AI-endpoints krijgen een aparte, strengere limiet — één LLM-call kost 10–100× meer dan een DB-query.

### Input & output

- Alle input gevalideerd via Pydantic-modellen (FastAPI doet dit automatisch)
- Geen stack traces in productie-errors — `debug=False` in FastAPI, generieke 500-response
- CORS: alleen de frontend-origin toegestaan (`ALLOWED_ORIGINS` in `.env`)
- SQL-injectie: SQLAlchemy ORM met parameterized queries — nooit raw SQL met f-strings

### Secrets & configuratie

- Alle secrets via `.env` — nooit in code of git
- `.env` chmod 600 op server
- Aparte DB-user per module met minimale rechten (principe 2.4)
- AI API-key nooit in logs of error-responses

### Bouwinstructies

```python
# FastAPI — centrale RBAC-dependency
from fastapi import Depends, HTTPException, status

def require_role(*roles):
    def dependency(current_user = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        # tenant_id check is altijd al gedaan in get_current_user
        return current_user
    return dependency

# Gebruik:
@router.post("/decisions/")
async def create_decision(
    user = Depends(require_role("tims_lid", "sims_lid", "admin"))
):
    ...
```

---

*Bronnen: LIVIQ PRINCIPLES.md, LIVIQ BEST_PRACTICES_REPOS.md, LIVIQ SECURE-ARCHITECTURE-BASELINE.md (productie-gevalideerd maart 2026) + IMS-proces CONTEXT.md K1-K15 + skills: database-schema-design, access-control-rbac, api-security-hardening*
