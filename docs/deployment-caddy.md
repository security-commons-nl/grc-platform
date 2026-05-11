# Deployment achter Caddy reverse proxy

> Voor systeembeheerders die het platform productie-rijp willen draaien achter een HTTPS-reverse proxy. Caddy is aanbevolen vanwege automatische certificaatverlenging via Let's Encrypt en zero-config security defaults.
>
> Voor algemene configuratie: zie [`configuratie.md`](configuratie.md). Voor architectuur: zie [`architectuur.md`](architectuur.md).

---

## Architectuur

```
                ┌──────────────────────────────────────┐
                │           Internet (poort 443)        │
                └────────────────┬─────────────────────┘
                                 │ HTTPS
                                 ▼
                ┌──────────────────────────────────────┐
                │              Caddy                    │
                │  - TLS-terminatie (Let's Encrypt)     │
                │  - HTTP→HTTPS redirect (poort 80)     │
                │  - Security headers                   │
                │  - Reverse proxy + gzip               │
                └────────────────┬─────────────────────┘
                                 │ HTTP (intern Docker-netwerk)
                ┌────────────────┴─────────────────────┐
                ▼                                       ▼
        ┌──────────────┐                       ┌──────────────┐
        │  frontend    │                       │     api      │
        │ Next.js:3000 │                       │ FastAPI:8000 │
        └──────────────┘                       └──────┬───────┘
                                                      │
                                               ┌──────▼───────┐
                                               │      db      │
                                               │ Postgres:5432│
                                               └──────────────┘
```

Alleen Caddy bindt op publieke poorten (80/443). Frontend, API en database zijn alleen bereikbaar binnen het Docker-netwerk.

---

## Pre-flight: aanpassingen in `.env`

Voor productie moeten minimaal de volgende waarden gezet zijn:

```env
ENVIRONMENT=production
ALLOWED_ORIGINS=https://grc.jouwdomein.nl
JWT_SECRET_KEY=<64+ willekeurige tekens — gebruik `openssl rand -hex 32`>
POSTGRES_PASSWORD=<sterk uniek wachtwoord>
FIRST_ADMIN_PASSWORD=<tijdelijk, direct wijzigen na eerste login>
```

`ENVIRONMENT=production` schakelt automatisch het volgende uit:
- `/docs` (Swagger UI op de API) — geen public API-documentatie
- `/auth/dev-token` endpoint — geen ongeauthenticeerde tokens
- SQL query-echo in de logs — geen leaking van queries

`ALLOWED_ORIGINS` is een comma-separated lijst. Voor één domein volstaat één entry; voor subdomein-deployment (zie hieronder) komt alleen het frontend-domein hier.

---

## Variant A — Eén domein (aanbevolen voor kleine deployments)

Alles onder één domein, API onder `/api`. Eenvoudigst qua DNS en CORS.

### Caddyfile

```caddy
grc.jouwdomein.nl {
    encode gzip

    # Security headers
    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
        X-Content-Type-Options "nosniff"
        Referrer-Policy "strict-origin-when-cross-origin"
        Permissions-Policy "camera=(), microphone=(), geolocation=()"
        -Server
    }

    # API requests
    handle /api/* {
        reverse_proxy api:8000
    }

    # Frontend (alles overig)
    handle {
        reverse_proxy frontend:3000
    }
}
```

### .env aanvulling

```env
ALLOWED_ORIGINS=https://grc.jouwdomein.nl
```

Bij deze variant maakt de frontend API-calls naar dezelfde origin (`/api/*`), dus CORS is technisch niet eens nodig — maar `ALLOWED_ORIGINS` moet wel correct staan voor het geval frontend en API ooit gesplitst worden.

---

## Variant B — Twee subdomeinen

Frontend op één subdomein, API op een ander. Beter scheidbaar, geschikter voor grotere deployments.

### Caddyfile

```caddy
(security_headers) {
    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
        X-Content-Type-Options "nosniff"
        Referrer-Policy "strict-origin-when-cross-origin"
        Permissions-Policy "camera=(), microphone=(), geolocation=()"
        -Server
    }
}

grc.jouwdomein.nl {
    encode gzip
    import security_headers
    reverse_proxy frontend:3000
}

api.grc.jouwdomein.nl {
    encode gzip
    import security_headers
    reverse_proxy api:8000
}
```

### .env aanvulling

```env
ALLOWED_ORIGINS=https://grc.jouwdomein.nl
```

CORS wordt hier wél actief — de frontend op `grc.jouwdomein.nl` moet expliciet toegestaan zijn om de API op `api.grc.jouwdomein.nl` te benaderen.

---

## Docker Compose voor productie

Maak een `docker-compose.prod.yml` naast de bestaande `docker-compose.yml`:

```yaml
services:
  caddy:
    image: caddy:2-alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
      - "443:443/udp"   # HTTP/3
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
      - caddy_config:/config
    depends_on:
      - api
      - frontend
    security_opt:
      - no-new-privileges:true

  # Override port bindings — services zijn alleen via Caddy bereikbaar
  api:
    ports: !reset []

  frontend:
    ports: !reset []

volumes:
  caddy_data:
  caddy_config:
```

### Starten

```bash
# Eerste keer: bouwen + opstarten
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Database-migraties (zoals normaal)
docker-compose exec api alembic upgrade head

# Logs volgen
docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f caddy
```

Caddy haalt bij de eerste request automatisch een Let's Encrypt-certificaat op. Dit vereist dat:

1. DNS-records (A of AAAA) wijzen naar de server
2. Poorten 80 en 443 publiek bereikbaar zijn (firewall / port-forward / cloud security group)
3. Het domein in de Caddyfile een geldig FQDN is

---

## Verifiëren

```bash
# TLS-versies en cipher
curl -vI https://grc.jouwdomein.nl 2>&1 | grep -E "(SSL|TLS|HTTP/)"

# Security headers controleren
curl -sI https://grc.jouwdomein.nl | grep -E "(Strict-Transport|X-Content|Referrer|Permissions)"

# API health
curl https://grc.jouwdomein.nl/api/v1/health
# of bij Variant B:
curl https://api.grc.jouwdomein.nl/api/v1/health

# Bevestig dat /docs uit staat
curl -i https://grc.jouwdomein.nl/api/docs
# verwacht: 404 Not Found
```

---

## Security headers — wat Caddy doet

| Header | Waarde | Doel |
|--------|--------|------|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains; preload` | Browser dwingt HTTPS af voor 1 jaar |
| `X-Content-Type-Options` | `nosniff` | Voorkomt MIME-sniffing aanvallen |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Lekt geen URLs naar externe sites |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=()` | Disablet ongebruikte browser-APIs |
| `-Server` | *(verwijderd)* | Verbergt server-versie |

Niet meegenomen (overweging vereist per deployment):
- **Content-Security-Policy** — Next.js heeft inline scripts; CSP moet per deployment getuned worden. Begin met `Content-Security-Policy-Report-Only` in een test-omgeving.
- **X-Frame-Options** — overschaduwd door CSP `frame-ancestors`. Voeg toe (`DENY`) als je geen CSP hebt.

---

## Troubleshooting

**Caddy logt `tls handshake error: no certificate available`**
DNS wijst nog niet naar de server, of poort 80 is niet open (Let's Encrypt heeft poort 80 nodig voor ACME HTTP-01 challenge). Check met `dig grc.jouwdomein.nl` en `nc -zv jouwdomein.nl 80`.

**Frontend toont CORS-error in browser console**
`ALLOWED_ORIGINS` in `.env` mist het frontend-domein, of staat met `http://` in plaats van `https://`. Restart de api-container na `.env`-wijziging: `docker-compose restart api`.

**Caddy is bereikbaar maar `/api/*` geeft 502 Bad Gateway**
API-container is niet opgestart of niet bereikbaar binnen het Docker-netwerk. Check: `docker-compose ps` en `docker-compose logs api`.

**Certificaat wordt elke 60 dagen niet vernieuwd**
Caddy doet dit automatisch. Als het misgaat: check of de Caddy-container blijft draaien (`docker-compose ps caddy`) en kijk in de Caddy-logs (`docker-compose logs caddy | grep -i renew`).

---

## Onderhoud

- **Certificaten:** Caddy vernieuwt automatisch ~30 dagen vóór verloop. Geen handmatige actie nodig.
- **Caddy-updates:** `docker-compose pull caddy && docker-compose up -d caddy` — Caddy is stateless behalve `caddy_data` (certificaten) en `caddy_config`.
- **Logs:** standaard naar stdout van de container. Voor persistente logs: voeg een log-directive toe in de Caddyfile (`log { output file /var/log/caddy/access.log }`) en mount een log-volume.
- **Caddyfile aanpassen:** edit het bestand en herlaad zonder downtime met `docker-compose exec caddy caddy reload --config /etc/caddy/Caddyfile`.

---

## Voorbeeldbestanden

Volledige voorbeelden staan in [`examples/caddy/`](../examples/caddy/):
- `Caddyfile` — Variant A (single domain) ready-to-use
- `docker-compose.prod.yml` — productie-compose-overlay
