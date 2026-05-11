#!/usr/bin/env bash
#
# End-to-end backup/restore test.
#
# Dit script verifieert dat de backup-/restore-pipeline werkt door:
#   1. Een backup van de live database te maken
#   2. Een test-database aan te maken
#   3. De backup in de test-database te restoren
#   4. Tabellen en rijen te vergelijken
#   5. De test-database op te ruimen
#
# Bedoeld voor:
#   - Periodiek (kwartaalbasis) draaien om disaster-recovery te bevestigen
#   - In CI als integration test (toekomstige uitbreiding)
#
# Gebruik:
#   ./scripts/test-backup-restore.sh
#
# Exit code: 0 als alle assertions slagen.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

COMPOSE_FILE="${COMPOSE_FILE:-${REPO_ROOT}/docker-compose.yml}"
DB_SERVICE="${DB_SERVICE:-db}"
ENV_FILE="${ENV_FILE:-${REPO_ROOT}/.env}"

# shellcheck disable=SC1090
set -a; source "$ENV_FILE"; set +a

POSTGRES_USER="${POSTGRES_USER:?}"
POSTGRES_DB="${POSTGRES_DB:?}"
RESTORE_DB="ims_restore_test"

cleanup() {
  echo "[cleanup] Dropping ${RESTORE_DB}..."
  docker compose -f "${COMPOSE_FILE}" exec -T "${DB_SERVICE}" \
    psql -U "${POSTGRES_USER}" -d postgres -c "DROP DATABASE IF EXISTS ${RESTORE_DB};" || true
  rm -f /tmp/grc-backup-test.sql.gz
}
trap cleanup EXIT

echo "[1/5] Creating backup..."
docker compose -f "${COMPOSE_FILE}" exec -T "${DB_SERVICE}" \
  pg_dump -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" --no-owner --no-privileges \
  | gzip > /tmp/grc-backup-test.sql.gz

backup_size=$(stat -c '%s' /tmp/grc-backup-test.sql.gz 2>/dev/null || stat -f '%z' /tmp/grc-backup-test.sql.gz)
echo "       Backup size: ${backup_size} bytes"

if [ "${backup_size}" -lt 1024 ]; then
  echo "FAIL: Backup is suspiciously small"
  exit 1
fi

echo "[2/5] Creating restore database '${RESTORE_DB}'..."
docker compose -f "${COMPOSE_FILE}" exec -T "${DB_SERVICE}" \
  psql -U "${POSTGRES_USER}" -d postgres -c "CREATE DATABASE ${RESTORE_DB};"
docker compose -f "${COMPOSE_FILE}" exec -T "${DB_SERVICE}" \
  psql -U "${POSTGRES_USER}" -d "${RESTORE_DB}" -c "CREATE EXTENSION IF NOT EXISTS vector;"

echo "[3/5] Restoring backup into ${RESTORE_DB}..."
gunzip -c /tmp/grc-backup-test.sql.gz | docker compose -f "${COMPOSE_FILE}" exec -T "${DB_SERVICE}" \
  psql -U "${POSTGRES_USER}" -d "${RESTORE_DB}" --quiet > /dev/null

echo "[4/5] Comparing table counts..."

count_tables() {
  docker compose -f "${COMPOSE_FILE}" exec -T "${DB_SERVICE}" \
    psql -U "${POSTGRES_USER}" -d "$1" -tAc \
    "SELECT count(*) FROM information_schema.tables WHERE table_schema='public';"
}

original_tables=$(count_tables "${POSTGRES_DB}")
restored_tables=$(count_tables "${RESTORE_DB}")

echo "       Original tables: ${original_tables}"
echo "       Restored tables: ${restored_tables}"

if [ "${original_tables}" != "${restored_tables}" ]; then
  echo "FAIL: Table count mismatch (${original_tables} vs ${restored_tables})"
  exit 1
fi

echo "[5/5] Comparing row counts in key tables..."

compare_rows() {
  local table="$1"
  local orig
  local rest
  orig=$(docker compose -f "${COMPOSE_FILE}" exec -T "${DB_SERVICE}" \
    psql -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -tAc "SELECT count(*) FROM ${table};" 2>/dev/null || echo "0")
  rest=$(docker compose -f "${COMPOSE_FILE}" exec -T "${DB_SERVICE}" \
    psql -U "${POSTGRES_USER}" -d "${RESTORE_DB}" -tAc "SELECT count(*) FROM ${table};" 2>/dev/null || echo "0")
  if [ "${orig}" != "${rest}" ]; then
    echo "       FAIL ${table}: ${orig} vs ${rest}"
    return 1
  fi
  echo "       PASS ${table}: ${orig} rows"
  return 0
}

failures=0
for table in tenants users roles ims_steps ims_standards ims_risks ims_controls; do
  compare_rows "${table}" || failures=$((failures + 1))
done

echo ""
if [ "${failures}" -gt 0 ]; then
  echo "RESULT: ${failures} table(s) mismatched"
  exit 1
fi

echo "RESULT: Backup/restore pipeline verified — all table and row counts match."
