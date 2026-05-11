#!/usr/bin/env bash
#
# PostgreSQL restore-script voor het GRC-platform.
#
# WAARSCHUWING: dit overschrijft de huidige database. Maak eerst een
# backup van de huidige staat als die nog waardevolle data bevat.
#
# Gebruik:
#   ./scripts/restore-postgres.sh <backup-file.sql.gz>
#
# Voorbeeld:
#   ./scripts/restore-postgres.sh backups/daily/grc-20260512-030000.sql.gz

set -euo pipefail

BACKUP_FILE="${1:-}"
if [ -z "$BACKUP_FILE" ] || [ ! -f "$BACKUP_FILE" ]; then
  echo "Usage: $0 <backup-file.sql.gz>" >&2
  echo "Backup file not found: ${BACKUP_FILE}" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

COMPOSE_FILE="${COMPOSE_FILE:-${REPO_ROOT}/docker-compose.yml}"
DB_SERVICE="${DB_SERVICE:-db}"
ENV_FILE="${ENV_FILE:-${REPO_ROOT}/.env}"

# shellcheck disable=SC1090
set -a; source "$ENV_FILE"; set +a

POSTGRES_USER="${POSTGRES_USER:?POSTGRES_USER not set in .env}"
POSTGRES_DB="${POSTGRES_DB:?POSTGRES_DB not set in .env}"

echo "WARNING: This will DROP and recreate database '${POSTGRES_DB}'."
echo "         All current data will be lost."
read -p "Type the database name '${POSTGRES_DB}' to confirm: " confirm
if [ "${confirm}" != "${POSTGRES_DB}" ]; then
  echo "Aborted."
  exit 1
fi

echo "[$(date -Iseconds)] Dropping and recreating database..."
docker compose -f "${COMPOSE_FILE}" exec -T "${DB_SERVICE}" \
  psql -U "${POSTGRES_USER}" -d postgres -c "DROP DATABASE IF EXISTS ${POSTGRES_DB};"
docker compose -f "${COMPOSE_FILE}" exec -T "${DB_SERVICE}" \
  psql -U "${POSTGRES_USER}" -d postgres -c "CREATE DATABASE ${POSTGRES_DB};"
docker compose -f "${COMPOSE_FILE}" exec -T "${DB_SERVICE}" \
  psql -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -c "CREATE EXTENSION IF NOT EXISTS vector;"

echo "[$(date -Iseconds)] Restoring from ${BACKUP_FILE}..."
gunzip -c "${BACKUP_FILE}" | docker compose -f "${COMPOSE_FILE}" exec -T "${DB_SERVICE}" \
  psql -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" --quiet

echo "[$(date -Iseconds)] Restore complete."
echo ""
echo "Next steps:"
echo "  1. Verify schema: docker compose exec api alembic current"
echo "  2. Apply any newer migrations: docker compose exec api alembic upgrade head"
echo "  3. Restart api: docker compose restart api"
