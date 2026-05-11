# Security hardening checklist

> Checklist voor het productie-rijp en veilig draaien van het GRC-platform. Statussen per item: ✅ ingebouwd in het platform · 🛠️ moet je zelf doen · 💡 aanbevolen extra.
>
> Voor geautomatiseerde verificatie: `./scripts/security-check.sh https://grc.jouwdomein.nl`

---

## 1. Netwerk & toegang

| # | Item | Status | Toelichting |
|---|------|--------|-------------|
| 1.1 | Alleen Caddy bindt op publieke poorten (80/443) | ✅ | Zie `examples/caddy/docker-compose.prod.yml` — db/api/frontend ports zijn `!reset []` |
| 1.2 | Database (`5432`) niet bereikbaar vanaf het internet | ✅ | `docker-compose.yml` bindt op `127.0.0.1:5432` |
| 1.3 | Firewall sluit alle inkomende poorten behalve 80/443/22 | 🛠️ | UFW/iptables/cloud security group configureren |
| 1.4 | SSH alleen met public-key authenticatie | 🛠️ | `PasswordAuthentication no` in `sshd_config` |
| 1.5 | SSH alleen vanuit beheernetwerk of VPN | 💡 | IP-allowlist of WireGuard |
| 1.6 | Automatische OS-security-updates | 🛠️ | `unattended-upgrades` (Debian/Ubuntu) |
| 1.7 | Fail2ban op SSH | 💡 | Standaardpakket, jail.local met SSH-jail |

## 2. HTTPS & transport

| # | Item | Status | Toelichting |
|---|------|--------|-------------|
| 2.1 | HTTPS verplicht (HTTP → HTTPS redirect) | ✅ | Caddy doet automatisch HTTP-naar-HTTPS |
| 2.2 | TLS-certificaat automatisch vernieuwd | ✅ | Caddy + Let's Encrypt |
| 2.3 | HSTS-header met preload | ✅ | `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload` |
| 2.4 | `X-Content-Type-Options: nosniff` | ✅ | In `examples/caddy/Caddyfile` |
| 2.5 | `Referrer-Policy: strict-origin-when-cross-origin` | ✅ | In Caddyfile |
| 2.6 | `Permissions-Policy` beperkt browser-APIs | ✅ | Camera/microphone/geolocation uitgeschakeld |
| 2.7 | Server-header verwijderd | ✅ | `-Server` in Caddyfile |
| 2.8 | Content-Security-Policy (CSP) | 💡 | Niet meegeleverd — vergt tuning per Next.js setup |
| 2.9 | X-Forwarded-For correct geconfigureerd | 🛠️ | Uvicorn met `--forwarded-allow-ips`, zie deployment-caddy.md |

## 3. Authenticatie & autorisatie

| # | Item | Status | Toelichting |
|---|------|--------|-------------|
| 3.1 | JWT met HMAC-SHA256 ondertekening | ✅ | `JWT_ALGORITHM=HS256`, configureerbaar |
| 3.2 | `JWT_SECRET_KEY` ≥ 64 tekens, random | 🛠️ | Genereren met `openssl rand -hex 32` |
| 3.3 | Korte access-token TTL (15 min) | ✅ | `JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15` |
| 3.4 | RBAC met hiërarchische rollen (6 rollen) | ✅ | admin > strategisch_lid > tactisch_lid > discipline_eigenaar > lijnmanager > viewer |
| 3.5 | `/auth/dev-token` uit in productie | ✅ | Endpoint checkt `ENVIRONMENT != production` |
| 3.6 | `/docs` (Swagger) uit in productie | ✅ | `app.docs_url=None` als `ENVIRONMENT != development` |
| 3.7 | Rate limit op auth-endpoints | ✅ | Default `10/minute` per IP, configureerbaar |
| 3.8 | Wachtwoorden gehashed met bcrypt | ✅ | `passlib[bcrypt]` |
| 3.9 | Eerste-beheerder-wachtwoord direct gewijzigd | 🛠️ | `FIRST_ADMIN_PASSWORD` is tijdelijk — wissel bij eerste login |
| 3.10 | OIDC/SSO voor enterprise SSO | 💡 | Auth-laag is voorbereid, integratie nog niet meegeleverd |

## 4. Database & data-isolatie

| # | Item | Status | Toelichting |
|---|------|--------|-------------|
| 4.1 | Row Level Security op tenant-tabellen | ✅ | 21 tabellen, geactiveerd in migration `002_enable_rls.py` |
| 4.2 | `tenant_id` uit JWT, nooit uit user-input | ✅ | `set_tenant_context()` in `app/core/auth.py` |
| 4.3 | `POSTGRES_PASSWORD` ≥ 24 tekens, uniek | 🛠️ | Genereren met `openssl rand -base64 24` |
| 4.4 | Database in eigen Docker-volume | ✅ | `postgres_data` volume in `docker-compose.yml` |
| 4.5 | Append-only audit trail | ✅ | `ims_decisions`, `ims_document_versions` zonder UPDATE/DELETE |
| 4.6 | AI-aanroepen geaudit | ✅ | `ai_audit_logs` per call |
| 4.7 | Database-encryptie at rest | 💡 | Via volume-encryptie (LUKS, dm-crypt) of cloud-provider |
| 4.8 | Periodieke RLS-policy-verificatie | 💡 | Pytest tegen ims_test verifieert RLS — overweeg cron in productie |

## 5. Backups & recovery

| # | Item | Status | Toelichting |
|---|------|--------|-------------|
| 5.1 | Dagelijkse pg_dump met retentie | ✅ | `scripts/backup-postgres.sh` |
| 5.2 | Wekelijkse snapshot (langere horizon) | ✅ | Zondag-dump → weekly map |
| 5.3 | Backup-pipeline geautomatiseerd geverifieerd | ✅ | `scripts/test-backup-restore.sh` — maandelijks cron |
| 5.4 | Off-site backup-kopie | 💡 | rsync/rclone/restic naar externe locatie |
| 5.5 | Off-site backups encrypted | 💡 | `gpg --symmetric` of restic native |
| 5.6 | Restore minimaal halfjaarlijks getest | 🛠️ | Volg het ritueel uit `backup.md` |

## 6. Container & host hardening

| # | Item | Status | Toelichting |
|---|------|--------|-------------|
| 6.1 | `no-new-privileges` op alle containers | ✅ | `security_opt` in `docker-compose.yml` |
| 6.2 | Geheugen-limieten gezet | ✅ | `mem_limit: 512m` op db/api/frontend, `128m` op caddy |
| 6.3 | PID-limieten gezet | ✅ | `pids_limit: 100` op services |
| 6.4 | Containers draaien niet als root | 🛠️ | Vergt USER-directive in Dockerfile (uitbreiding) |
| 6.5 | Read-only root filesystem | 💡 | `read_only: true` met tmpfs voor mutables — vergt testen |
| 6.6 | Docker-daemon up-to-date | 🛠️ | Volg distro security updates |
| 6.7 | Geen Docker-socket gemount in containers | ✅ | Geen `/var/run/docker.sock` mounts in compose-files |

## 7. Rate limiting & DoS

| # | Item | Status | Toelichting |
|---|------|--------|-------------|
| 7.1 | Globaal rate limit per IP | ✅ | Default `100/minute`, configureerbaar |
| 7.2 | Strenger rate limit op auth-endpoints | ✅ | Default `10/minute` |
| 7.3 | `/health` exempt van rate limiting | ✅ | `@limiter.exempt` |
| 7.4 | Caddy rate limit op TCP-niveau (optioneel) | 💡 | Caddy heeft `rate_limit` module beschikbaar |

## 8. Secrets & configuratie

| # | Item | Status | Toelichting |
|---|------|--------|-------------|
| 8.1 | `.env` niet in version control | ✅ | `.env` in `.gitignore` |
| 8.2 | Geen defaults in productie (`changeme` etc.) | 🛠️ | Verifieer met `./scripts/security-check.sh` |
| 8.3 | `/health/details` lekt geen secrets | ✅ | Test in `test_health.py` verifieert dit |
| 8.4 | Logs filteren secrets uit | 🛠️ | Geen `print(token)` in code — code review |
| 8.5 | Secrets manager voor productie | 💡 | HashiCorp Vault, Bitwarden, of cloud KMS |

## 9. AI-laag

| # | Item | Status | Toelichting |
|---|------|--------|-------------|
| 9.1 | AI-provider configureerbaar (geen lock-in) | ✅ | `AI_API_BASE`, `AI_MODEL_NAME` via `.env` |
| 9.2 | EU-conforme AI-provider gebruikt | 🛠️ | Default `.env.example` wijst naar Mistral EU |
| 9.3 | AI-aanroepen geaudit (welke agent, welke tenant) | ✅ | `ai_audit_logs` tabel |
| 9.4 | AI-output gelabeld als concept | ✅ | UI-principe K14, `AI CONCEPT — verifieer handmatig` |
| 9.5 | Geen klantdata naar non-EU LLM zonder clearance | 🛠️ | Ontwerpprincipe, juridische verantwoordelijkheid blijft bij operator |

## 10. Logging & incident response

| # | Item | Status | Toelichting |
|---|------|--------|-------------|
| 10.1 | Structured JSON logging in productie | ✅ | `app/core/logging_config.py` actief bij `ENVIRONMENT=production` |
| 10.2 | Logs naar centrale aggregator | 🛠️ | Loki/ELK/CloudWatch — zie `monitoring.md` |
| 10.3 | Alerting op 5xx, 429-spikes, degraded health | 🛠️ | Drempels in `monitoring.md` |
| 10.4 | Incident response procedure | 🛠️ | Eigen procedure — `ims_incidents` tabel ondersteunt registratie |

---

## Geautomatiseerde verificatie

```bash
# Productie-deployment veilig?
./scripts/security-check.sh https://grc.jouwdomein.nl

# Werkt de pipeline (incl. backup + restore + smoke)?
./scripts/backup-postgres.sh
./scripts/test-backup-restore.sh
./scripts/smoke-test-deployment.sh https://grc.jouwdomein.nl
```

---

## Verantwoordelijkheidsverdeling

| Wie | Waar verantwoordelijk voor |
|-----|---------------------------|
| **Platform-team (open-source)** | ✅-items: code-level controls, defaults, geleverde scripts en docs |
| **IT-beheerder (deployment)** | 🛠️-items: server-hardening, secrets, firewall, backup-cron, monitoring-aansluiting |
| **Organisatie (governance)** | 💡-items waar bewuste investering nodig is: off-site backups, VPN-only beheer, secrets-vault, CSP |

Geen enkel platform kan al deze items in zijn eentje afdekken — security is gedeelde verantwoordelijkheid. Maar wat het platform *kan* uniformeren (defaults, helper-scripts, audit-trails) doet het.
