# GRC-platform — Configuratie

> Voor systeembeheerders en IT-teams die het platform installeren en aanpassen aan hun omgeving.

---

## Omgevingsvariabelen

Kopieer `.env.example` naar `.env` en pas aan:

```bash
cp .env.example .env
```

### Verplicht aanpassen

| Variabele | Beschrijving | Voorbeeld |
|-----------|--------------|-----------|
| `POSTGRES_PASSWORD` | Wachtwoord voor de PostgreSQL-database | Een sterk, uniek wachtwoord |
| `SECRET_KEY` | JWT-signeringssleutel | 64+ willekeurige tekens |
| `FIRST_ADMIN_EMAIL` | E-mailadres eerste beheerder | `beheer@jouworganisatie.nl` |
| `FIRST_ADMIN_PASSWORD` | Wachtwoord eerste beheerder | Tijdelijk, direct wijzigen na eerste login |

### AI (optioneel)

| Variabele | Standaard | Beschrijving |
|-----------|-----------|--------------|
| `AI_API_BASE` | `https://openrouter.ai/api/v1` | API-endpoint van de LLM-provider |
| `AI_API_KEY` | — | API-sleutel van de LLM-provider |
| `AI_MODEL_NAME` | `mistralai/mistral-small-latest` | Taalmodel |
| `AI_EMBEDDING_MODEL` | `openai/text-embedding-3-small` | Embedding-model voor RAG |
| `AI_MAX_TOKENS` | `4096` | Maximum tokens per LLM-aanroep |
| `AI_TEMPERATURE` | `0.3` | Creativiteit van het model (0 = deterministisch) |
| `LANGFUSE_SECRET_KEY` | — | Langfuse observability (optioneel) |
| `LANGFUSE_PUBLIC_KEY` | — | Langfuse observability (optioneel) |
| `LANGFUSE_HOST` | — | Langfuse host URL (optioneel) |

**EU-conforme AI-configuratie**

De standaardconfiguratie gebruikt OpenRouter (Amerikaans). Voor productie bij publieke organisaties zijn twee EU-conforme alternatieven beschikbaar:

*Optie A: Mistral EU API (aanbevolen voor productie)*
```env
AI_API_BASE=https://api.mistral.ai/v1
AI_API_KEY=<jouw-mistral-api-key>
AI_MODEL_NAME=mistral-small-latest
AI_EMBEDDING_MODEL=mistral-embed
```

*Optie B: Ollama lokaal (volledig air-gapped)*
```env
AI_API_BASE=http://localhost:11434/v1
AI_API_KEY=ollama
AI_MODEL_NAME=mistral
AI_EMBEDDING_MODEL=nomic-embed-text
```
| `CORS_ORIGINS` | `http://localhost:3000` | Toegestane frontend-origins |
| `LOG_LEVEL` | `INFO` | Logging-niveau (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

---

## Docker Compose

Het platform bestaat uit drie containers:

| Container | Image | Poort |
|-----------|-------|-------|
| `db` | PostgreSQL 16 | 5432 (intern) |
| `api` | FastAPI (Python 3.12) | 8000 |
| `frontend` | Next.js 15 | 3000 |

### Starten

```bash
docker-compose up -d --build
```

### Database initialiseren (eerste keer)

```bash
docker-compose exec api alembic upgrade head
```

Dit voert drie migraties uit: schema aanmaken, RLS instellen, en seed-data laden (normenkaders, standaardrollen, eerste beheerdersaccount).

### Stoppen

```bash
docker-compose down           # containers stoppen (data blijft)
docker-compose down -v        # containers + volumes verwijderen (data weg)
```

---

## Eerste beheerdersaccount

Na `alembic upgrade head` is er een beheerdersaccount aangemaakt met de gegevens uit `FIRST_ADMIN_EMAIL` en `FIRST_ADMIN_PASSWORD`.

Wijzig het wachtwoord direct na de eerste login via **Profiel → Wachtwoord wijzigen**.

---

## Meerdere organisaties (multi-tenant)

Het platform ondersteunt meerdere organisaties vanuit één installatie. Nieuwe organisaties aanmaken:

1. Log in als platformbeheerder
2. Ga naar **Beheer → Organisaties → Nieuwe organisatie**
3. Vul de naam en een beheerder-e-mailadres in
4. De nieuwe tenant krijgt een uitnodigingsmail (als e-mail geconfigureerd is)

---

## Rate limiting

Het platform past rate limiting toe per client-IP. Drie environment-variabelen sturen dit gedrag:

| Variabele | Standaard | Beschrijving |
|-----------|-----------|--------------|
| `RATE_LIMIT_ENABLED` | `true` | Schakel rate limiting volledig uit (bv. tijdens debugsessies in development). |
| `RATE_LIMIT_DEFAULT` | `100/minute` | Globaal limit voor alle endpoints zonder specifiek limit. |
| `RATE_LIMIT_AUTH` | `10/minute` | Strenger limit op `/api/v1/auth/dev-token` en `/api/v1/auth/agent-token`. |

Het `/api/v1/health` endpoint is uitgesloten van rate limiting zodat load balancers en monitoring het onbeperkt kunnen aanroepen.

**Achter Caddy of een andere reverse proxy:** zorg dat Uvicorn met `--forwarded-allow-ips` draait of dat Starlette's `ProxyHeadersMiddleware` actief is, zodat `X-Forwarded-For` correct doorkomt en rate limits per echte client-IP worden toegepast (niet per proxy-IP). Zie [`deployment-caddy.md`](deployment-caddy.md).

**Storage:** standaard in-memory — geschikt voor single-instance deployments. Voor load-balanced deployments met meerdere API-instances is een gedeelde store (Redis) nodig; dit kan later geconfigureerd worden via `SLOWAPI_STORAGE_URI`.

---

## HTTPS

In productie moet het platform achter een reverse proxy draaien die HTTPS afhandelt. Aanbevolen: **Caddy** (automatische certificaatverlenging via Let's Encrypt, zero-config security defaults).

Volledige deployment-instructies inclusief Caddyfile-voorbeelden, productie-`docker-compose.prod.yml`, security headers en troubleshooting staan in [`deployment-caddy.md`](deployment-caddy.md). Werkende voorbeeldbestanden in [`examples/caddy/`](../examples/caddy/).

Minimaal vereiste `.env`-wijzigingen voor productie:

```env
ENVIRONMENT=production
ALLOWED_ORIGINS=https://grc.jouwdomein.nl
```

`ENVIRONMENT=production` schakelt automatisch `/docs` (Swagger UI) en `/auth/dev-token` uit.

---

## Backups

De PostgreSQL-data staat in een Docker-volume (`grc_postgres_data`). Back-up strategie:

```bash
# Dagelijkse dump
docker-compose exec db pg_dump -U postgres ims > backup-$(date +%Y%m%d).sql

# Herstellen
docker-compose exec -T db psql -U postgres ims < backup-20260401.sql
```

Automatiseer dit via cron of een backuptool. Bewaar minimaal 7 dagelijkse en 4 wekelijkse backups.

---

## Normenkaders aanpassen

Het platform laadt standaard vijf normenkaders (BIO 2.0, ISO 27001, ISO 27701, ISO 22301, AVG) via seed-data. Nieuwe normen toevoegen:

1. Maak een nieuwe Alembic-migratie aan
2. Voeg `frameworks`- en `framework_controls`-records toe
3. Draai `alembic upgrade head`

Zie `backend/alembic/versions/003_seed.py` voor het formaat van bestaande normenkaders.
