#!/usr/bin/env bash
#
# Smoke-test voor een productie-deployment achter Caddy.
#
# Verifieert:
#   - HTTPS bereikbaarheid
#   - Security headers (HSTS, X-Content-Type-Options, Referrer-Policy)
#   - /api/docs (Swagger) staat uit (ENVIRONMENT=production)
#   - /api/v1/auth/dev-token staat uit (ENVIRONMENT=production)
#   - /api/v1/health is bereikbaar
#
# Gebruik:
#   ./scripts/smoke-test-deployment.sh https://grc.jouwdomein.nl
#
# Exit code: 0 als alles slaagt, 1 als één of meer checks falen.

set -euo pipefail

URL="${1:-}"
if [ -z "$URL" ]; then
  echo "Usage: $0 <https://your-deployment-url>" >&2
  exit 2
fi

# Strip trailing slash
URL="${URL%/}"

failures=0
checks=0

pass() {
  checks=$((checks + 1))
  echo "  PASS  $1"
}

fail() {
  checks=$((checks + 1))
  failures=$((failures + 1))
  echo "  FAIL  $1"
}

check_header() {
  local header="$1"
  local pattern="$2"
  local value
  value=$(curl -sI "$URL/" | grep -i "^${header}:" | tr -d '\r' || true)
  if [ -z "$value" ]; then
    fail "header '${header}' is missing"
  elif ! echo "$value" | grep -qi "$pattern"; then
    fail "header '${header}' does not match '${pattern}': ${value}"
  else
    pass "${value}"
  fi
}

check_status() {
  local path="$1"
  local expected="$2"
  local method="${3:-GET}"
  local actual
  actual=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "${URL}${path}")
  if [ "$actual" = "$expected" ]; then
    pass "${method} ${path} -> ${actual}"
  else
    fail "${method} ${path} returned ${actual}, expected ${expected}"
  fi
}

check_status_in() {
  local path="$1"
  shift
  local expected_codes=("$@")
  local method="GET"
  local actual
  actual=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "${URL}${path}")
  for code in "${expected_codes[@]}"; do
    if [ "$actual" = "$code" ]; then
      pass "${method} ${path} -> ${actual}"
      return
    fi
  done
  fail "${method} ${path} returned ${actual}, expected one of: ${expected_codes[*]}"
}

echo "Smoke-testing ${URL}"
echo ""

echo "[1] TLS reachability"
if curl -sfI "$URL/" > /dev/null; then
  pass "HTTPS bereikbaar"
else
  fail "HTTPS niet bereikbaar — controleer DNS, firewall, Caddy-status"
  echo ""
  echo "Stopping early — niets te testen als HTTPS niet werkt."
  exit 1
fi
echo ""

echo "[2] Security headers"
check_header "strict-transport-security" "max-age"
check_header "x-content-type-options" "nosniff"
check_header "referrer-policy" "strict-origin"
echo ""

echo "[3] Production hardening (ENVIRONMENT=production)"
# /api/docs moet 404 zijn in productie (Swagger UI staat uit)
check_status_in "/api/docs" "404" "401" "403"
# /api/v1/auth/dev-token moet niet werken in productie
check_status_in "/api/v1/auth/dev-token" "403" "404" "405"
echo ""

echo "[4] Health endpoints"
check_status "/api/v1/health" "200"
check_status "/api/v1/health/details" "200"
echo ""

echo "Result: ${checks} checks, ${failures} failure(s)."
if [ "$failures" -gt 0 ]; then
  exit 1
fi
