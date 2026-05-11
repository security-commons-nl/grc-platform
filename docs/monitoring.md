# Monitoring & observability

> Voor systeembeheerders die het GRC-platform in productie willen volgen op gezondheid, performance en fouten.

---

## Health endpoints

Het platform biedt twee health endpoints, beide exempt van rate limiting.

### `GET /api/v1/health` — Basic

Voor load balancers, Kubernetes liveness probes, Caddy upstream-health checks. Snel, lichte query.

```json
{
  "status": "ok",
  "database": "connected"
}
```

HTTP 200 = alles werkt. Bij failure: HTTP 500 of timeout — load balancer kan deze instance uit pool halen.

### `GET /api/v1/health/details` — Verbose

Voor monitoring dashboards en alerting. Bevat **geen secrets** (alleen booleans en URLs zonder API-keys).

```json
{
  "status": "ok",
  "environment": "production",
  "database": {
    "connected": true,
    "latency_ms": 3
  },
  "ai_provider": {
    "configured": true,
    "base_url": "https://api.mistral.ai/v1",
    "model": "mistral-small-latest"
  },
  "observability": {
    "langfuse_configured": false
  },
  "rate_limit": {
    "enabled": true,
    "default": "100/minute",
    "auth": "10/minute"
  }
}
```

| Status | Betekenis |
|--------|-----------|
| `ok` | Database < 1000 ms en bereikbaar |
| `degraded` | Database > 1000 ms — werk wordt traag, alerting nodig |
| `unhealthy` | Database niet bereikbaar — incident |

---

## Structured logging

In productie (`ENVIRONMENT=production`) schrijft de API logs als JSON Lines naar stdout:

```json
{"ts":"2026-05-12T03:14:15+00:00","level":"INFO","logger":"app.api.v1.endpoints.risks","msg":"Created risk 7f2a..."}
```

Geschikt voor:
- **Loki** — `docker-compose.yml` aanvullen met promtail als sidecar
- **ELK / Opensearch** — Filebeat met JSON parser
- **CloudWatch / Datadog** — agent op de host, JSON parser ingeschakeld
- **Eenvoudig:** `docker compose logs api > grc-$(date +%F).log` + tooling naar keuze

In development blijft de output menselijk leesbaar (`HH:MM:SS LEVEL logger: message`).

**Demping van third-party loggers:** `uvicorn.access` en `sqlalchemy.engine` zijn op `WARNING` gezet om ruis te voorkomen. Pas aan in `backend/app/core/logging_config.py` als je access-logs of SQL-debug nodig hebt.

---

## Langfuse (AI-observability)

De `.env.example` bevat `LANGFUSE_SECRET_KEY`, `LANGFUSE_PUBLIC_KEY` en `LANGFUSE_HOST`. Vul deze in om LLM-calls naar Langfuse te streamen. Het platform rapporteert `observability.langfuse_configured: true` in `/health/details` zodra alle drie aanwezig zijn.

**Status:** configuratie ingebouwd, daadwerkelijke instrumentatie in `llm_client.py` is **placeholder** — zie [Issue tracker](https://github.com/security-commons-nl/grc-platform/issues) voor de stand. Tot dan: `AIAuditLog`-tabel in de database is de primaire AI-audit-trail.

Voor de meeste gemeenten is `AIAuditLog` voldoende; Langfuse voegt visualisatie, kosten-tracking en prompt-versioning toe als dat gewenst is.

---

## Prometheus metrics (optioneel)

Het platform schept zelf geen `/metrics` endpoint, maar `prometheus-fastapi-instrumentator` voegt dat eenvoudig toe:

```bash
pip install prometheus-fastapi-instrumentator
```

```python
# backend/app/main.py — toevoegen na app-creatie
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
```

Levert standaard: request count, latency histogram, response size — per route, per method, per status code. Direct te scrapen door Prometheus.

Niet meegeleverd omdat het een extra dependency is die niet elke deployment nodig heeft. Voor kleine gemeenten is `/health/details` + log-aggregatie voldoende.

---

## Alerting-suggesties

Drempelwaarden waar je op zou willen alerteren:

| Signal | Bron | Drempel |
|--------|------|---------|
| `/health/details.status == "degraded"` | HTTP poll | 3 opeenvolgende metingen |
| `/health/details.status == "unhealthy"` | HTTP poll | 1 meting |
| `/health/details.database.latency_ms > 500` | HTTP poll | gemiddeld over 5 minuten |
| HTTP 5xx ratio | reverse proxy logs of Prometheus | > 1% over 5 minuten |
| HTTP 429 spike | reverse proxy logs of Prometheus | meer dan baseline, mogelijk aanval |
| Backup ouder dan 30 uur | filesystem of cron-log | direct |
| Disk-vrije ruimte | host metrics | < 20% |

---

## Auditbaarheid (binnen het platform zelf)

Onafhankelijk van externe monitoring legt het platform zelf vast:

- **`ai_audit_logs`** — elke LLM-aanroep met model, tokens, agent, tenant
- **`ims_decisions`** — append-only besluitlog per tenant
- **`ims_document_versions`** — append-only documentgeschiedenis
- **`incident_timeline`** — chronologische incident-tijdlijn

Deze datapaden zijn doelbewust **niet** onderdeel van externe observability — ze zijn governance-evidence, niet operational metrics. Vermeng deze niet met monitoring-data; ze hebben andere retentievereisten en juridische status.

---

## Quickstart-checklist

Voor een nieuwe productie-deployment:

- [ ] `ENVIRONMENT=production` in `.env` (zet structured logging aan)
- [ ] Reverse proxy (Caddy) configureert toegang tot `/api/v1/health` voor uptime monitoring
- [ ] Externe uptime monitor pollt `/api/v1/health` elke 1–5 minuten
- [ ] Extern dashboard pollt `/api/v1/health/details` elke 1–5 minuten voor latency-tracking
- [ ] Logs worden minstens dagelijks naar een aggregator gestreamd of opgeslagen
- [ ] Alerting ingesteld op de drempels hierboven
- [ ] Backup-monitoring actief (zie [`backup.md`](backup.md))
