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
