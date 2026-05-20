# Deployment-handleiding voor IT-beheerders

> Stap-voor-stap-gids om het GRC-platform productie-rijp te draaien bij een gemeente of publieke organisatie. Gericht op IT-beheerders met basiskennis van Linux en Docker.
>
> Verwante documenten: [`configuratie.md`](configuratie.md) · [`deployment-caddy.md`](deployment-caddy.md) · [`backup.md`](backup.md) · [`monitoring.md`](monitoring.md)

---

## In één oogopslag

1. **Voorbereiden** — server, DNS, firewall
2. **Installeren** — repo clonen, `.env` invullen, containers starten
3. **Initialiseren** — migraties, eerste beheerder, normenkaders
4. **Verifiëren** — smoke-test, security headers
5. **Onderhouden** — backup-cron, monitoring, updates

Verwachte tijd: **half tot heel werkdag** voor een ervaren beheerder, langer bij eerste keer.

---

## Fase 1 — Voorbereiden

### 1.1 Server

| Vereiste | Minimaal | Aanbevolen |
|----------|----------|------------|
| OS | Ubuntu 22.04 LTS of Debian 12 | Ubuntu 24.04 LTS |
| CPU | 2 vCPU | 4 vCPU |
| Geheugen | 4 GB RAM | 8 GB RAM |
| Schijf | 20 GB SSD | 50 GB SSD |
| Docker | 24.0+ met Compose plugin v2 | 28.0+ |

### 1.2 DNS

Wijs één van deze configuraties aan naar je server-IP:

- **Variant A (één domein):** `grc.jouwdomein.nl` → IP
- **Variant B (subdomeinen):** `grc.jouwdomein.nl` + `api.grc.jouwdomein.nl` → IP

Wacht tot DNS-propagatie afgerond is (verifieer met `dig grc.jouwdomein.nl`) voor je verder gaat. Zonder werkende DNS kan Let's Encrypt geen certificaat uitgeven.

### 1.3 Firewall

Open vanuit het internet alleen:

- **TCP 80** — voor Let's Encrypt ACME HTTP-01 challenge en HTTP → HTTPS redirect
- **TCP 443** — voor HTTPS
- **UDP 443** — voor HTTP/3 (optioneel maar aanbevolen)
- **TCP 22** — SSH alleen vanuit beheernetwerken, idealiter met key-only auth

Niet open: 5432 (PostgreSQL), 8000 (API), 3000 (frontend). Die zijn alleen intern bereikbaar.

### 1.4 Voorbereidende installatie

```bash
# Op een verse Ubuntu server
sudo apt update && sudo apt install -y git docker.io docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker $USER  # log opnieuw in voor groep-wijziging
```

---

## Fase 2 — Installeren

### 2.1 Repo klonen

```bash
sudo mkdir -p /opt && sudo chown $USER /opt
cd /opt
git clone https://github.com/security-commons-nl/grc-platform.git
cd grc-platform
```

### 2.2 `.env` aanmaken

```bash
cp .env.example .env
```

Verplichte aanpassingen — alle waarden moeten gewijzigd zijn voor productie:

```env
# Database — kies een sterk uniek wachtwoord
POSTGRES_PASSWORD=<openssl rand -base64 24>

# JWT — minimaal 64 tekens
JWT_SECRET_KEY=<openssl rand -hex 32>

# Environment — schakelt /docs en /auth/dev-token uit
ENVIRONMENT=production

# CORS — vul in het frontend-domein
ALLOWED_ORIGINS=https://grc.jouwdomein.nl

# Rate limiting — defaults zijn meestal goed
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT=100/minute
RATE_LIMIT_AUTH=10/minute

# AI — voor EU-conforme deployment (Mistral)
AI_API_BASE=https://api.mistral.ai/v1
AI_API_KEY=<mistral-api-key>
AI_MODEL_NAME=mistral-small-latest
AI_EMBEDDING_MODEL=mistral-embed
```

Houd de `.env` **uit version control** en bewaar een kopie veilig (password manager, encrypted backup).

### 2.3 Reverse proxy configureren

Volg [`deployment-caddy.md`](deployment-caddy.md): kies Variant A of B, kopieer het Caddyfile-voorbeeld uit `examples/caddy/`, vervang het domein.

### 2.4 Stack starten

```bash
docker compose -f docker-compose.yml -f examples/caddy/docker-compose.prod.yml up -d --build
```

Eerste keer duurt 3–5 minuten (containers bouwen + Let's Encrypt certificaat ophalen).

Verifieer dat alles draait:

```bash
docker compose ps
# verwacht: db, api, frontend, caddy — allemaal Up
```

### 2.4 Production-modus (aanbevolen voor liveomgeving)

`docker-compose.yml` start de frontend in Next.js-dev-modus (Turbopack, hot-reload, hoog geheugengebruik). Voor een productiedeployment naast bestaande sites is er **`docker-compose.prod.yml`** in de repo:

- Frontend wordt gebouwd via `frontend/Dockerfile.prod` (multi-stage `next build` + `next start`) — geheugen ~80 MB i.p.v. >1 GB
- Container-namen: `grc-db`, `grc-api`, `grc-frontend` (zodat ze niet botsen met andere stacks op dezelfde host)
- Ports: API op `127.0.0.1:8010`, frontend op `127.0.0.1:3010` (niet 8000/3000) — bedoeld om achter een gedeelde reverse-proxy te draaien
- Health-checks op alle drie containers met `depends_on: condition: service_healthy`
- Eigen volume `grc_postgres_data` (geen botsing met dev-volume)

Gebruik:

```bash
sudo docker compose -f docker-compose.prod.yml build
sudo docker compose -f docker-compose.prod.yml up -d
sleep 10
sudo docker exec grc-api alembic upgrade head
```

`NEXT_PUBLIC_API_URL` wordt tijdens de build geïnlined; pas de build-arg in `docker-compose.prod.yml` aan op je eigen domein (default: `https://liviq.nl/api/v1` — verander dit naar je eigen URL vóór de build).

---

## Fase 3 — Initialiseren

### 3.1 Database-migraties

```bash
docker compose exec api alembic upgrade head
```

17 migraties draaien, in volgorde:
1. **001** — Initiële schema (35 tabellen, 67 indexen)
2. **002** — Row Level Security policies op 21 tenant-tabellen + speciale policy voor `ims_knowledge_chunks`
3. **003–008** — Seed reference data (IMS-stappen, normenkaders, step-output-definities, agent-conversaties)
4. **010** — AI-systemenregister (M4)
5. **011** — NIST AI RMF 1.0 als zesde normenkader
6. **012–013** — AI Conformity Assessment + HITL-checkpoints (M4)
7. **014–015** — Financiële range + Monte Carlo simulatie-historie (M5)
8. **016** — Custom-attributes JSONB + `ims_custom_field_definitions` (RFC 0001)
9. **017** — Organizational units met parent-self-FK (RFC 0002)

Eindstand: **41 tabellen, 27 RLS-policies**.

### 3.2 Eerste beheerder

Standaard wordt een `admin@example.com` beheerder aangemaakt. Wijzig direct het e-mailadres en wachtwoord via de UI bij eerste login, of vooraf via SQL als je dat liever scriptbaar doet.

### 3.3 Organisatie aanmaken

In de UI: **Beheer → Organisaties → Nieuwe organisatie** — vul de naam van jullie gemeente in. Voeg gebruikers en rollen toe (zie [`gebruik.md`](gebruik.md) voor de rolverdeling).

---

## Fase 4 — Verifiëren

### 4.1 Geautomatiseerde smoke-test

```bash
./scripts/smoke-test-deployment.sh https://grc.jouwdomein.nl
```

Controleert HTTPS, security headers, dat `/api/docs` en `/auth/dev-token` uit staan in productie, dat `/health` en `/health/details` antwoorden.

Exit-code 0 = alles in orde. Bij fouten: zie output voor welke check faalde.

### 4.2 Handmatige checks

- Inloggen via `https://grc.jouwdomein.nl/login` werkt
- `https://grc.jouwdomein.nl/api/v1/health/details` toont `"status": "ok"`, `"environment": "production"`
- Browser-console heeft geen CORS-errors
- Een nieuwe risk aanmaken slaagt en is na refresh nog zichtbaar

---

## Fase 5 — Onderhouden

### 5.1 Backups automatiseren

```bash
crontab -e
```

Voeg toe:

```cron
# Dagelijks 03:00 — backup met retentie (7 daily + 4 weekly)
0 3 * * * /opt/grc-platform/scripts/backup-postgres.sh >> /var/log/grc-backup.log 2>&1

# Wekelijks maandag 04:00 — verifieer backup/restore pipeline
0 4 * * 1 /opt/grc-platform/scripts/test-backup-restore.sh >> /var/log/grc-backup-test.log 2>&1
```

Volledige strategie: [`backup.md`](backup.md). Off-site backups: zie de relevante sectie aldaar.

### 5.2 Monitoring

Stel een externe uptime-monitor in die polled:
- `GET /api/v1/health` elke 1–5 minuten (basic)
- `GET /api/v1/health/details` elke 1–5 minuten (latency, status)

Alerting-drempels en log-aggregatie: [`monitoring.md`](monitoring.md).

### 5.3 Updates

Bij een nieuwe release:

```bash
cd /opt/grc-platform
git fetch origin
git log --oneline HEAD..origin/main   # bekijk wat er verandert

# Maak eerst een handmatige backup
./scripts/backup-postgres.sh

# Pull en herstart
git pull
docker compose -f docker-compose.yml -f examples/caddy/docker-compose.prod.yml up -d --build
docker compose exec api alembic upgrade head

# Verifieer
./scripts/smoke-test-deployment.sh https://grc.jouwdomein.nl
```

**Roll-back bij problemen:**

```bash
git checkout <vorige-commit-hash>
docker compose up -d --build
./scripts/restore-postgres.sh backups/daily/grc-<timestamp>.sql.gz
docker compose exec api alembic upgrade head
```

---

## Common pitfalls

| Symptoom | Oorzaak | Oplossing |
|----------|---------|-----------|
| Caddy: `tls handshake error: no certificate available` | DNS niet correct of poort 80 dicht | `dig <domein>` + `nc -zv <domein> 80` |
| Browser: CORS-error in console | `ALLOWED_ORIGINS` in `.env` mist het frontend-domein, of staat zonder `https://` | corrigeer `.env`, `docker compose restart api` |
| `/api/docs` is bereikbaar in productie | `ENVIRONMENT` staat nog op `development` | zet `ENVIRONMENT=production`, `docker compose restart api` |
| Login werkt niet, `403` | Geen seed-data of admin niet aangemaakt | check `docker compose exec api alembic current` — moet `head` zijn |
| Backup-script: "POSTGRES_USER not set" | `.env` ontbreekt of staat op verkeerde locatie | zet `ENV_FILE=/pad/naar/.env` of run uit repo-root |
| API geeft 429 vanaf één client (bv. integratie) | Rate limit te streng voor die use case | verhoog `RATE_LIMIT_DEFAULT` in `.env` of overweeg agent-token met aparte limiet |
| Disk vol door backups | Retentie te ruim of dump te groot | pas `BACKUP_DAILY_RETENTION` aan, of off-site backup naar NAS |

---

## Hardening — extra stappen voor strikte omgevingen

- **SSH:** disable password-auth, alleen public-key
- **Unattended-upgrades:** automatische security updates voor Ubuntu/Debian
- **Fail2ban:** rate-limiting op SSH-niveau
- **AppArmor/SELinux:** profiel voor Docker-daemon
- **Audit logging:** systemd-journald output streamen naar een log-aggregator
- **Backup-encryptie:** off-site backups met `gpg --symmetric` of restic
- **VPN-only beheer:** sta SSH alleen toe vanuit een VPN-netwerk

Een uitgebreidere checklist staat in [`security-hardening.md`](security-hardening.md) (10 categorieën met statussen ✅ ingebouwd / 🛠️ zelf doen / 💡 aanbevolen extra) + geautomatiseerd verifieerbaar via `./scripts/security-check.sh`.

---

## Hulp nodig?

- Logs: `docker compose logs --tail 200 <service>` waarbij service ∈ {api, frontend, caddy, db}
- Architectuur-vragen: [`architectuur.md`](architectuur.md)
- GitHub issues: <https://github.com/security-commons-nl/grc-platform/issues>
- Discussions: <https://github.com/security-commons-nl/grc-platform/discussions>
