#!/usr/bin/env bash
#
# Security-check voor een productie-deployment.
#
# Verifieert zoveel mogelijk items uit docs/security-hardening.md
# geautomatiseerd. Combineert lokale checks (.env, docker-compose.yml)
# met remote checks (security headers, prod-flags).
#
# Gebruik:
#   ./scripts/security-check.sh [https://deployment-url]
#
# Met URL: ook remote checks. Zonder URL: alleen lokale checks.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

URL="${1:-}"
URL="${URL%/}"

failures=0
warnings=0
checks=0

pass() { checks=$((checks + 1)); echo "  ✓ $1"; }
fail() { checks=$((checks + 1)); failures=$((failures + 1)); echo "  ✗ FAIL  $1"; }
warn() { checks=$((checks + 1)); warnings=$((warnings + 1)); echo "  ⚠ WARN  $1"; }

echo "=========================================="
echo "GRC-platform security check"
echo "Repo: ${REPO_ROOT}"
[ -n "$URL" ] && echo "Remote: ${URL}"
echo "=========================================="
echo ""

# ----- 1. .env hygiene -----
echo "[1] .env file hygiene"
ENV_FILE="${REPO_ROOT}/.env"

if [ ! -f "$ENV_FILE" ]; then
  fail ".env not found at ${ENV_FILE}"
else
  pass ".env exists"

  if grep -qE '^POSTGRES_PASSWORD=changeme' "$ENV_FILE"; then
    fail "POSTGRES_PASSWORD still has default value 'changeme'"
  else
    pass "POSTGRES_PASSWORD is not the default"
  fi

  if grep -qE '^JWT_SECRET_KEY=changeme' "$ENV_FILE"; then
    fail "JWT_SECRET_KEY still has default value 'changeme'"
  else
    pass "JWT_SECRET_KEY is not the default"
  fi

  # Lengte JWT_SECRET_KEY moet minimaal 32 zijn (~64 hex)
  jwt_len=$(grep -E '^JWT_SECRET_KEY=' "$ENV_FILE" | cut -d= -f2- | tr -d '"' | tr -d "'" | wc -c)
  if [ "$jwt_len" -lt 32 ]; then
    fail "JWT_SECRET_KEY too short (${jwt_len} chars, minimum 32)"
  else
    pass "JWT_SECRET_KEY length OK (${jwt_len} chars)"
  fi

  if grep -qE '^ENVIRONMENT=production' "$ENV_FILE"; then
    pass "ENVIRONMENT=production"
  else
    fail "ENVIRONMENT is not set to 'production'"
  fi

  if grep -qE '^ALLOWED_ORIGINS=http://localhost' "$ENV_FILE"; then
    fail "ALLOWED_ORIGINS still has localhost — replace with production domain"
  elif grep -qE '^ALLOWED_ORIGINS=https?://' "$ENV_FILE"; then
    pass "ALLOWED_ORIGINS configured for non-localhost"
  else
    warn "ALLOWED_ORIGINS unclear in .env"
  fi

  if grep -qE '^RATE_LIMIT_ENABLED=true' "$ENV_FILE"; then
    pass "RATE_LIMIT_ENABLED=true"
  else
    warn "RATE_LIMIT_ENABLED is not explicitly true"
  fi

  if grep -qE '^AI_API_BASE=https://openrouter\.ai' "$ENV_FILE"; then
    warn "AI_API_BASE points to OpenRouter (US) — consider EU-hosted alternative for GDPR"
  fi
fi
echo ""

# ----- 2. docker-compose hardening -----
echo "[2] docker-compose hardening"
COMPOSE="${REPO_ROOT}/docker-compose.yml"

if [ -f "$COMPOSE" ]; then
  if grep -q "no-new-privileges:true" "$COMPOSE"; then
    pass "security_opt: no-new-privileges set"
  else
    fail "security_opt: no-new-privileges missing in docker-compose.yml"
  fi

  if grep -q "mem_limit:" "$COMPOSE"; then
    pass "mem_limit configured"
  else
    warn "mem_limit not configured — containers can OOM the host"
  fi

  if grep -q "pids_limit:" "$COMPOSE"; then
    pass "pids_limit configured"
  else
    warn "pids_limit not configured"
  fi

  if grep -qE '"127\.0\.0\.1:5432:5432"' "$COMPOSE"; then
    pass "Database bound to 127.0.0.1 only"
  elif grep -qE '"5432:5432"' "$COMPOSE"; then
    fail "Database port bound to 0.0.0.0 — restrict to 127.0.0.1"
  fi
else
  fail "docker-compose.yml not found"
fi
echo ""

# ----- 3. .gitignore -----
echo "[3] .gitignore"
GITIGNORE="${REPO_ROOT}/.gitignore"
if [ -f "$GITIGNORE" ]; then
  if grep -qE '^\.env$' "$GITIGNORE"; then
    pass ".env in .gitignore"
  else
    fail ".env NOT in .gitignore — risk of committing secrets"
  fi
fi
echo ""

# ----- 4. Remote checks (optional) -----
if [ -n "$URL" ]; then
  echo "[4] Remote deployment checks"

  if ! curl -sfI "$URL/" > /dev/null; then
    fail "${URL} not reachable over HTTPS"
  else
    pass "HTTPS reachable"

    # Security headers
    headers=$(curl -sI "$URL/")
    for header in "strict-transport-security" "x-content-type-options" "referrer-policy"; do
      if echo "$headers" | grep -qi "^${header}:"; then
        pass "Header present: ${header}"
      else
        fail "Header missing: ${header}"
      fi
    done

    # /docs uit
    docs_status=$(curl -s -o /dev/null -w "%{http_code}" "${URL}/api/docs")
    if [ "$docs_status" = "404" ] || [ "$docs_status" = "401" ]; then
      pass "/api/docs disabled (HTTP ${docs_status})"
    else
      fail "/api/docs returned HTTP ${docs_status} — Swagger should be off in production"
    fi

    # /auth/dev-token uit
    devtoken_status=$(curl -s -o /dev/null -w "%{http_code}" -X POST "${URL}/api/v1/auth/dev-token" \
      -H "Content-Type: application/json" -d '{}')
    if [ "$devtoken_status" = "403" ] || [ "$devtoken_status" = "404" ] || [ "$devtoken_status" = "405" ] || [ "$devtoken_status" = "422" ]; then
      # 422 = pydantic rejects body before reaching env check — also acceptable
      if [ "$devtoken_status" = "422" ]; then
        warn "/auth/dev-token returns 422 (validation) — ENVIRONMENT check happens after validation"
      else
        pass "/auth/dev-token disabled (HTTP ${devtoken_status})"
      fi
    else
      fail "/auth/dev-token returned HTTP ${devtoken_status} — should be 403 in production"
    fi

    # /health/details — verify environment + rate limit
    details=$(curl -sf "${URL}/api/v1/health/details" || echo "")
    if [ -n "$details" ]; then
      if echo "$details" | grep -q '"environment":"production"'; then
        pass "/health/details reports environment=production"
      else
        fail "/health/details environment is not 'production'"
      fi
      if echo "$details" | grep -q '"enabled":true'; then
        pass "/health/details reports rate_limit.enabled=true"
      else
        warn "/health/details: rate limit not enabled"
      fi
    else
      warn "/health/details not reachable"
    fi
  fi
  echo ""
else
  echo "[4] Remote checks skipped (no URL provided)"
  echo ""
fi

echo "=========================================="
echo "Result: ${checks} checks, ${failures} failed, ${warnings} warnings"
echo "=========================================="

if [ "$failures" -gt 0 ]; then
  exit 1
fi
if [ "$warnings" -gt 0 ]; then
  exit 0  # warnings non-fatal
fi
