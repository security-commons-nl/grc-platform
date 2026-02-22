# Remote Claude Code on IMS Server — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Deploy a persistent, browser-accessible Claude Code environment on the IMS server (77.42.66.251) via code-server + Caddy, reachable at `https://code.agentportal.nl`.

**Architecture:** code-server (VS Code web) runs in Docker alongside Caddy for TLS termination. Claude Code CLI is pre-installed in the code-server container. tmux provides persistent sessions. SSH deploy key enables GitHub repo access.

**Tech Stack:** Docker, code-server, Caddy 2, Node.js 22, Claude Code CLI, tmux, SSH

**Design doc:** `docs/plans/2026-02-22-remote-claude-code-design.md`

---

## Task 1: Create the code-server Docker stack (local files)

**Files:**
- Create: `code-server/Dockerfile.code-server`
- Create: `code-server/docker-compose.yml`
- Create: `code-server/Caddyfile`
- Create: `code-server/.env.example`
- Create: `code-server/ssh-config`
- Create: `code-server/settings.json` (VS Code defaults)

**Step 1: Create the directory structure**

```bash
mkdir -p code-server
```

**Step 2: Create the Dockerfile**

Create `code-server/Dockerfile.code-server`:

```dockerfile
FROM codercom/code-server:latest

# System tools
RUN sudo apt-get update && sudo apt-get install -y \
    tmux git curl openssh-client jq htop \
    && sudo rm -rf /var/lib/apt/lists/*

# Node.js 22 LTS (required for Claude Code)
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | sudo bash - \
    && sudo apt-get install -y nodejs \
    && sudo rm -rf /var/lib/apt/lists/*

# Claude Code CLI
RUN sudo npm install -g @anthropic-ai/claude-code

# Git config defaults (overridden by env vars at runtime)
RUN git config --global init.defaultBranch main

# Workspace directory
RUN mkdir -p /home/coder/projects

# SSH directory with correct permissions
RUN mkdir -p /home/coder/.ssh && chmod 700 /home/coder/.ssh

WORKDIR /home/coder/projects
```

**Step 3: Create docker-compose.yml**

Create `code-server/docker-compose.yml`:

```yaml
services:
  caddy:
    image: caddy:2-alpine
    container_name: agent-caddy
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
    networks:
      - agent-net

  code-server:
    build:
      context: .
      dockerfile: Dockerfile.code-server
    container_name: agent-code-server
    environment:
      - PASSWORD=${CODE_SERVER_PASSWORD}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GIT_AUTHOR_NAME=${GIT_AUTHOR_NAME:-Claude Code}
      - GIT_AUTHOR_EMAIL=${GIT_AUTHOR_EMAIL:-claude@agentportal.nl}
      - GIT_COMMITTER_NAME=${GIT_AUTHOR_NAME:-Claude Code}
      - GIT_COMMITTER_EMAIL=${GIT_AUTHOR_EMAIL:-claude@agentportal.nl}
    volumes:
      # Project files (host directory)
      - /home/ims/projects:/home/coder/projects
      # Persistent config
      - cs-config:/home/coder/.config
      - cs-extensions:/home/coder/.local/share/code-server
      - claude-config:/home/coder/.claude
      # SSH keys (read-only)
      - /home/ims/.ssh/id_github_deploy:/home/coder/.ssh/id_ed25519:ro
      - ./ssh-config:/home/coder/.ssh/config:ro
      # VS Code settings
      - ./settings.json:/home/coder/.local/share/code-server/User/settings.json:ro
    restart: unless-stopped
    networks:
      - agent-net

networks:
  agent-net:
    driver: bridge

volumes:
  caddy_data:
  caddy_config:
  cs-config:
  cs-extensions:
  claude-config:
```

**Step 4: Create the Caddyfile**

Create `code-server/Caddyfile`:

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

**Step 5: Create .env.example**

Create `code-server/.env.example`:

```env
# code-server password (min 20 characters, complex)
CODE_SERVER_PASSWORD=

# Anthropic API key for Claude Code
ANTHROPIC_API_KEY=

# Git identity for commits
GIT_AUTHOR_NAME=Your Name
GIT_AUTHOR_EMAIL=your@email.com
```

**Step 6: Create SSH config**

Create `code-server/ssh-config`:

```
# GitHub
Host github.com
    HostName github.com
    User git
    IdentityFile /home/coder/.ssh/id_ed25519
    StrictHostKeyChecking accept-new

# webhostiq VPS (for deployments)
Host webhostiq
    HostName 46.225.18.83
    User webhostiq
    IdentityFile /home/coder/.ssh/id_ed25519
    StrictHostKeyChecking accept-new
```

**Step 7: Create VS Code default settings**

Create `code-server/settings.json`:

```json
{
    "workbench.colorTheme": "One Dark Pro",
    "editor.fontSize": 15,
    "editor.fontFamily": "'Fira Code', 'Droid Sans Mono', monospace",
    "editor.minimap.enabled": false,
    "editor.wordWrap": "on",
    "terminal.integrated.fontSize": 14,
    "terminal.integrated.defaultProfile.linux": "tmux",
    "terminal.integrated.profiles.linux": {
        "tmux": {
            "path": "/usr/bin/tmux",
            "args": ["new-session", "-A", "-s", "main"]
        },
        "bash": {
            "path": "/bin/bash"
        }
    },
    "files.autoSave": "afterDelay",
    "files.autoSaveDelay": 1000,
    "git.autofetch": true,
    "git.confirmSync": false,
    "extensions.autoUpdate": true
}
```

**Step 8: Commit**

```bash
git add code-server/
git commit -m "feat: add code-server Docker stack for remote Claude Code

Includes Caddy reverse proxy, code-server with Claude Code CLI,
tmux for persistent sessions, and SSH config for GitHub access.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 2: Create the deploy script

**Files:**
- Create: `code-server/deploy.ps1`

**Step 1: Create the PowerShell deploy script**

Create `code-server/deploy.ps1`:

```powershell
# Deploy code-server stack to IMS server
# Usage: .\deploy.ps1

$SERVER = "ims@77.42.66.251"
$SSH_PORT = "2222"
$REMOTE_DIR = "/opt/code-server"
$SSH_CMD = "ssh -p $SSH_PORT $SERVER"
$SCP_CMD = "scp -P $SSH_PORT"

Write-Host "=== Deploying code-server to IMS server ===" -ForegroundColor Cyan

# 1. Create remote directory
Write-Host "`n[1/5] Creating remote directory..." -ForegroundColor Yellow
Invoke-Expression "$SSH_CMD 'sudo mkdir -p $REMOTE_DIR && sudo chown ims:ims $REMOTE_DIR'"

# 2. Copy files
Write-Host "[2/5] Copying files..." -ForegroundColor Yellow
$files = @(
    "Dockerfile.code-server",
    "docker-compose.yml",
    "Caddyfile",
    "ssh-config",
    "settings.json"
)
foreach ($file in $files) {
    Invoke-Expression "$SCP_CMD $file ${SERVER}:${REMOTE_DIR}/"
}

# 3. Copy .env (secrets)
Write-Host "[3/5] Copying .env..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Invoke-Expression "$SCP_CMD .env ${SERVER}:${REMOTE_DIR}/"
} else {
    Write-Host "  WARNING: .env not found! Copy .env.example and fill in values." -ForegroundColor Red
}

# 4. Create projects directory
Write-Host "[4/5] Creating projects directory..." -ForegroundColor Yellow
Invoke-Expression "$SSH_CMD 'mkdir -p /home/ims/projects'"

# 5. Build and start
Write-Host "[5/5] Building and starting containers..." -ForegroundColor Yellow
Invoke-Expression "$SSH_CMD 'cd $REMOTE_DIR && docker compose up -d --build'"

Write-Host "`n=== Deploy complete ===" -ForegroundColor Green
Write-Host "Access: https://code.agentportal.nl" -ForegroundColor Cyan
Write-Host "(Make sure DNS A record for code.agentportal.nl points to 77.42.66.251)" -ForegroundColor Gray
```

**Step 2: Commit**

```bash
git add code-server/deploy.ps1
git commit -m "feat: add deploy script for code-server stack

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 3: Generate SSH deploy key for GitHub

This task runs on your **local machine** (Windows).

**Step 1: Generate a dedicated SSH key**

```powershell
ssh-keygen -t ed25519 -C "code-server-deploy@agentportal.nl" -f "$env:USERPROFILE\.ssh\id_github_deploy" -N ""
```

**Step 2: Copy the public key to the IMS server**

```powershell
scp -P 2222 "$env:USERPROFILE\.ssh\id_github_deploy" ims@77.42.66.251:/home/ims/.ssh/id_github_deploy
scp -P 2222 "$env:USERPROFILE\.ssh\id_github_deploy.pub" ims@77.42.66.251:/home/ims/.ssh/id_github_deploy.pub
ssh -p 2222 ims@77.42.66.251 "chmod 600 /home/ims/.ssh/id_github_deploy"
```

**Step 3: Add the public key to GitHub**

```powershell
# Display the public key
Get-Content "$env:USERPROFILE\.ssh\id_github_deploy.pub"
```

Go to https://github.com/settings/keys > "New SSH key"
- Title: `code-server IMS`
- Key type: Authentication key
- Paste the public key

**Step 4: Test SSH connection from IMS server**

```bash
ssh -p 2222 ims@77.42.66.251 "ssh -i /home/ims/.ssh/id_github_deploy -T git@github.com"
```

Expected: `Hi TREASON! You've successfully authenticated...`

---

## Task 4: Configure DNS

**Step 1: Add DNS record**

At your domain registrar for `agentportal.nl`, add:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | `code` | `77.42.66.251` | 300 |

**Step 2: Verify DNS propagation**

```powershell
nslookup code.agentportal.nl
```

Expected: resolves to `77.42.66.251`

Note: DNS can take 5-60 minutes to propagate. Caddy will retry TLS provisioning automatically.

---

## Task 5: Create .env with secrets and deploy

**Step 1: Create the .env file**

```powershell
cd code-server
Copy-Item .env.example .env
```

Edit `.env` and fill in:
- `CODE_SERVER_PASSWORD`: generate with `openssl rand -base64 24`
- `ANTHROPIC_API_KEY`: your Anthropic API key
- `GIT_AUTHOR_NAME`: your name
- `GIT_AUTHOR_EMAIL`: your email

**Step 2: Deploy to server**

```powershell
.\deploy.ps1
```

**Step 3: Verify containers are running**

```powershell
ssh -p 2222 ims@77.42.66.251 "cd /opt/code-server && docker compose ps"
```

Expected: both `agent-caddy` and `agent-code-server` showing as `Up`.

**Step 4: Check Caddy logs for TLS**

```powershell
ssh -p 2222 ims@77.42.66.251 "cd /opt/code-server && docker compose logs caddy --tail=20"
```

Expected: successful certificate provisioning for `code.agentportal.nl`.

---

## Task 6: Verify and initial setup

**Step 1: Open in browser**

Navigate to `https://code.agentportal.nl`

Expected: code-server login page. Enter your password.

**Step 2: Verify VS Code loads**

Expected: VS Code interface with `/home/coder/projects` as workspace. Dark theme, file explorer on left.

**Step 3: Clone IMS repo**

Open terminal in VS Code (should auto-attach to tmux):

```bash
cd /home/coder/projects
git clone git@github.com:TREASON/IMS.git
```

Expected: successful clone using the deploy SSH key.

**Step 4: Start Claude Code**

```bash
cd IMS
claude
```

Expected: Claude Code starts, can read files, execute commands.

**Step 5: Test persistence**

1. Start a Claude Code session in tmux
2. Close the browser tab
3. Wait 30 seconds
4. Reopen `https://code.agentportal.nl`
5. Open terminal — should reconnect to the existing tmux session

Expected: Claude Code session is still running with full history.

**Step 6: Install VS Code extensions**

In code-server, open Extensions panel (Ctrl+Shift+X) and install:
- GitLens
- One Dark Pro (theme, if not auto-applied)
- Material Icon Theme

---

## Task 7: Verify no conflict with existing IMS services

**Step 1: Check IMS services still work**

```bash
ssh -p 2222 ims@77.42.66.251 "cd /opt/IMS && docker compose ps"
```

Expected: all IMS services (db, api, frontend, pgadmin, ollama) still running.

**Step 2: Check port conflicts**

```bash
ssh -p 2222 ims@77.42.66.251 "sudo ss -tlnp | grep -E ':(80|443|8001|3000|5432|5050)'"
```

Expected:
- Ports 80, 443: Caddy (agent-caddy)
- Port 8001: IMS API (127.0.0.1 only)
- Port 3000: IMS frontend (127.0.0.1 only)
- Port 5432: PostgreSQL (127.0.0.1 only)
- Port 5050: pgAdmin (127.0.0.1 only)

No conflicts because IMS binds to 127.0.0.1, Caddy binds to 0.0.0.0.

**Step 3: Check memory usage**

```bash
ssh -p 2222 ims@77.42.66.251 "free -h"
```

Expected: at least 1 GB free after all services running.

**Step 4: Commit verification notes**

```bash
git add -A
git commit -m "chore: verify code-server deployment, no conflicts with IMS

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Optional: Task 8: Cross-server deploy to webhostiq

Only if needed — enables Claude Code to deploy sites on the webhostiq VPS.

**Step 1: Copy SSH key to webhostiq**

From the IMS server:

```bash
ssh-copy-id -i /home/ims/.ssh/id_github_deploy -p 22 webhostiq@46.225.18.83
```

Or manually append the public key to webhostiq's `~/.ssh/authorized_keys`.

**Step 2: Test connection**

From inside the code-server container:

```bash
ssh webhostiq "echo 'Connected to webhostiq'"
```

Expected: `Connected to webhostiq`

**Step 3: Test a deploy command**

```bash
ssh webhostiq "cd /opt/mariskahouweling && git status"
```

Expected: shows git status of the mariskahouweling site on the webhostiq server.
