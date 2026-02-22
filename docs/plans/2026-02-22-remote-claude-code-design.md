# Remote Claude Code — Design Document

**Datum:** 2026-02-22
**Status:** Goedgekeurd
**Server:** IMS (77.42.66.251, Hetzner CX22, 2 vCPU / 4 GB RAM / 40 GB NVMe)
**Domein:** code.agentportal.nl

## Doel

Een persistent, browser-toegankelijke Claude Code omgeving op de IMS server. VS Code als web-IDE, Claude Code CLI in persistent tmux-sessies, bereikbaar via `https://code.agentportal.nl`.

## Architectuur

```
Internet (HTTPS)
    |
Caddy (TLS auto-provisioning + reverse proxy)
    |
    +-- code.agentportal.nl --> code-server (:8080)
    |
code-server (VS Code in browser)
    |
    +-- Integrated Terminal
    |       +-- tmux sessie(s)
    |            +-- claude code (persistent)
    |
    +-- File Explorer --> /home/coder/projects/
    +-- Git integration (SSH key --> GitHub TREASON)
    +-- Extensions (GitLens, theme, etc.)

Filesystem:
    /home/coder/projects/
        +-- IMS/              (git clone, initieel)
        +-- (later meer repos via git clone)

Cross-server access:
    IMS server (77.42.66.251) --SSH--> webhostiq (46.225.18.83)
    (voor deploy-acties vanuit Claude Code)
```

## Componenten

### 1. Caddy (reverse proxy + TLS)

- Image: `caddy:2-alpine`
- Auto-TLS via Let's Encrypt voor `code.agentportal.nl`
- Reverse proxy naar code-server op poort 8080
- Security headers (HSTS, X-Content-Type-Options, X-Frame-Options)
- WebSocket support (vereist door code-server)

### 2. code-server (VS Code web)

- Custom Docker image op basis van `codercom/code-server:latest`
- Aangevuld met: Node.js 22, Claude Code CLI, tmux, git, ssh-client
- Wachtwoord-authenticatie (sterk wachtwoord, >20 chars)
- Persistent volumes voor config, extensions, en Claude Code settings

### 3. Claude Code CLI

- Geinstalleerd via `npm install -g @anthropic-ai/claude-code`
- Draait in tmux-sessies voor persistentie
- ANTHROPIC_API_KEY via environment variable
- Toegang tot project-repos via /home/coder/projects/

### 4. Git authenticatie

- Dedicated SSH deploy key voor GitHub (TREASON account)
- Key gemount als volume in de container
- Toegang tot alle repos op het TREASON account
- Optioneel: SSH key voor cross-server deploy naar webhostiq

## Docker Setup

### Dockerfile.code-server

```dockerfile
FROM codercom/code-server:latest

# System tools
RUN sudo apt-get update && sudo apt-get install -y \
    tmux git curl openssh-client jq \
    && sudo rm -rf /var/lib/apt/lists/*

# Node.js 22 LTS
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | sudo bash - \
    && sudo apt-get install -y nodejs \
    && sudo rm -rf /var/lib/apt/lists/*

# Claude Code CLI
RUN sudo npm install -g @anthropic-ai/claude-code

# Workspace
RUN mkdir -p /home/coder/projects

WORKDIR /home/coder/projects
```

### docker-compose.yml

```yaml
services:
  caddy:
    image: caddy:2-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
      - caddy_config:/config
    restart: unless-stopped
    depends_on:
      - code-server

  code-server:
    build:
      context: .
      dockerfile: Dockerfile.code-server
    environment:
      - PASSWORD=${CODE_SERVER_PASSWORD}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - /home/ims/projects:/home/coder/projects          # Git repos
      - cs-config:/home/coder/.config                     # VS Code settings
      - cs-local:/home/coder/.local/share/code-server     # Extensions
      - claude-config:/home/coder/.claude                  # Claude Code config
      - ${SSH_KEY_PATH}:/home/coder/.ssh/id_ed25519:ro    # GitHub SSH key
      - ./ssh-config:/home/coder/.ssh/config:ro            # SSH config
    restart: unless-stopped

volumes:
  caddy_data:
  caddy_config:
  cs-config:
  cs-local:
  claude-config:
```

### Caddyfile

```
code.agentportal.nl {
    reverse_proxy code-server:8080
    encode gzip

    header {
        Strict-Transport-Security "max-age=31536000;"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "SAMEORIGIN"
        Referrer-Policy "strict-origin-when-cross-origin"
    }
}
```

### .env

```env
CODE_SERVER_PASSWORD=<sterk-wachtwoord-20+-chars>
ANTHROPIC_API_KEY=<anthropic-api-key>
SSH_KEY_PATH=/home/ims/.ssh/id_github_deploy
```

## Beveiliging

| Laag | Mechanisme |
|------|------------|
| Transport | TLS 1.3 via Caddy (auto Let's Encrypt) |
| Authenticatie | code-server wachtwoord (>20 chars) |
| Netwerk | UFW: alleen poort 80, 443, 2222 open |
| OS | code-server draait als non-root user `coder` |
| SSH keys | Read-only mount, nooit in git |
| Fail2ban | Actief op SSH (poort 2222) |
| API key | Alleen als env var, nooit in bestanden |

## RAM Budget

| Component | Geschat RAM |
|-----------|-------------|
| OS + systemd | ~300 MB |
| IMS stack (API + DB + Frontend + PgAdmin) | ~800 MB |
| Caddy | ~30 MB |
| code-server | ~500-800 MB |
| Claude Code (in terminal) | ~50 MB |
| **Totaal** | **~1.7-2.0 GB** |
| **Vrij** | **~2.0-2.3 GB** |

Ollama staat geinstalleerd maar niet actief. Bij RAM-druk kan Ollama verwijderd worden.

## Workflow

### Dagelijks gebruik

1. Open `https://code.agentportal.nl` in browser
2. Log in met wachtwoord
3. VS Code opent met `/projects` workspace
4. Open terminal > `tmux new -s claude` (of `tmux attach -t claude`)
5. `cd IMS && claude` — Claude Code start
6. Werk, sluit browser wanneer je wilt
7. Kom later terug > terminal > `tmux attach -t claude` — precies waar je was

### Nieuwe repo toevoegen

```bash
cd /home/coder/projects
git clone git@github.com:TREASON/webhostiq.git
```

### Deploy naar webhostiq

```bash
ssh webhostiq@46.225.18.83 "cd /opt/mariskahouweling && git pull && docker compose up -d --build"
```

## DNS

Bij de registrar van agentportal.nl:

| Type | Naam | Waarde | TTL |
|------|------|--------|-----|
| A | `code` | `77.42.66.251` | 300 |

## Pre-installed VS Code Extensions

- GitLens (git blame, history)
- One Dark Pro (theme)
- Material Icon Theme (file icons)
- Remote containers support

## Overwogen alternatieven

| Aanpak | Reden afgewezen |
|--------|----------------|
| Claude Cowork op VPS | Vereist desktop OS + nested virtualization, Hetzner ondersteunt dit niet |
| ttyd (web terminal) | Te kaal, geen IDE-ervaring |
| SSH tunnel | Niet browser-native, vereist lokale setup |
| Bare metal (geen Docker) | Inconsistent met bestaande Docker-first infra |
