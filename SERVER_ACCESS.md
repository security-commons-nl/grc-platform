# Server Access — IMS

## Connection

- **Public IP**: `77.42.66.251`
- **SSH Port**: `2222`
- **Username**: `ims` (sudo, NOPASSWD)
- **SSH Key Path**: `C:\Users\shgst\.ssh\id_ims`

> **Note:** Root login is uitgeschakeld. Gebruik user `ims` met sudo.

## Connect

```powershell
ssh ims-admin
```

## Useful Commands

```powershell
# Uptime
ssh hetzner-ims uptime

# Firewall
ssh hetzner-ims "sudo ufw status verbose"

# Fail2ban
ssh hetzner-ims "sudo fail2ban-client status sshd"

# Docker services
ssh hetzner-ims "cd /opt/IMS && docker compose ps"

# App logs
ssh hetzner-ims "cd /opt/IMS && docker compose logs --tail=50 -f ims-api"

# Database shell
ssh hetzner-ims "docker exec -it ims-db psql -U postgres -d ims"

# Apply RLS policies
ssh hetzner-ims "cd /opt/IMS && cat backend/enable_rls.sql | docker exec -i ims-db psql -U postgres -d ims"

# Deploy
ssh hetzner-ims "cd /opt/IMS && git pull origin main && docker compose up -d --build"
```

## Hetzner Cloud API

- **Base URL**: `https://api.hetzner.cloud/v1`
- **API Key**: opgeslagen in `.env` als `HETZNER_API_KEY`
- **Docs**: https://docs.hetzner.cloud/

```powershell
# Voorbeelden (vanuit lokale machine)

# Server info
curl -s -H "Authorization: Bearer $env:HETZNER_API_KEY" https://api.hetzner.cloud/v1/servers | jq

# Server status
curl -s -H "Authorization: Bearer $env:HETZNER_API_KEY" https://api.hetzner.cloud/v1/servers | jq '.servers[] | {name, status, public_net}'

# Reboot
curl -s -X POST -H "Authorization: Bearer $env:HETZNER_API_KEY" https://api.hetzner.cloud/v1/servers/{server-id}/actions/reboot
```

> **Let op:** API key staat in `.env` (git-ignored). Nooit in dit bestand of in git.

---

## Team Access

| User | SSH Command | Doel |
|------|------------|------|
| `ims` (admin) | `ssh ims-admin` | Volledige servertoegang (sudo) |
| `vasilis` | `ssh -p 2222 vasilis@77.42.66.251` | Deployment & git push |

### vasilis (Vasilis Theocharis)

- **Email**: vasilistheocharis@outlook.com
- **SSH Key**: `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPqAPJ5gto4CfVw05idmn1ilFBGugTZ8HWdkXGKIehdv`
- **Aangemaakt**: 2026-02-13
- **Shell**: `/bin/bash`

```bash
# Vasilis verbindt met:
ssh -p 2222 vasilis@77.42.66.251
```

---

## Server Specs

| Component | Detail |
|-----------|--------|
| **Provider** | Hetzner |
| **Plan** | CX22 (2 vCPU, 4 GB RAM, 40 GB NVMe) |
| **OS** | Ubuntu 24.04 LTS |
| **Location** | *(nog invullen)* |

## Security Hardening

- [x] Non-root user `ims` with sudo (NOPASSWD) + SSH key
- [x] `PermitRootLogin no`
- [x] `PasswordAuthentication no`
- [x] `PubkeyAuthentication yes`
- [x] SSH poort gewijzigd naar `2222`
- [x] UFW: default deny, allow 2222/tcp, 80, 443
- [x] Fail2ban active (sshd jail, port 2222, banaction=ufw, ignoreip=188.90.139.89)
- [x] Docker installeren
- [ ] Tailscale VPN *(optioneel, overweeg voor fase 2)*

## Port Forwards (via `ims-admin`)

| Service | Local Port | Access |
|---------|-----------|--------|
| IMS API | `8001` | http://localhost:8001/docs |
| PostgreSQL | `5432` | `psql -h localhost -p 5432 -U postgres ims` |
| PgAdmin | `5050` | http://localhost:5050 |
| Ollama | `11434` | AI model inference |

## Docker Services

| Service | Container | Port |
|---------|-----------|------|
| Backend API | `ims-api` | `8001` |
| PostgreSQL + pgvector | `ims-db` | `5432` |
| Frontend (Reflex) | `ims-frontend` | `3000` |
| PgAdmin | `ims-pgadmin` | `5050` |
| Ollama | `ims-ollama` | `11434` |
