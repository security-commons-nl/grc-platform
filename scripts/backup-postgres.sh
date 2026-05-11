#!/usr/bin/env bash
#
# PostgreSQL backup-script voor het GRC-platform.
#
# Maakt een gzipte pg_dump van de actieve database en past retentie toe:
#   - Bewaar de laatste BACKUP_DAILY_RETENTION dagelijkse dumps (default: 7)
#   - Bewaar de laatste BACKUP_WEEKLY_RETENTION wekelijkse dumps (default: 4)
#
# Een dump op zondag wordt automatisch een wekelijkse dump.
#
# Gebruik:
#   ./scripts/backup-postgres.sh
#
# Cron-voorbeeld (dagelijks om 03:00):
#   0 3 * * * /opt/grc-platform/scripts/backup-postgres.sh >> /var/log/grc-backup.log 2>&1
#
# Exit codes:
#   0  Backup succesvol
#   1  pg_dump faalde
#   2  Configuratie-probleem (.env ontbreekt, etc.)

set -euo pipefail

# Configuratie — overschrijf via environment of via .env naast dit script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

BACKUP_DIR="${BACKUP_DIR:-${REPO_ROOT}/backups}"
BACKUP_DAILY_RETENTION="${BACKUP_DAILY_RETENTION:-7}"
BACKUP_WEEKLY_RETENTION="${BACKUP_WEEKLY_RETENTION:-4}"
COMPOSE_FILE="${COMPOSE_FILE:-${REPO_ROOT}/docker-compose.yml}"
DB_SERVICE="${DB_SERVICE:-db}"

# Lees database-credentials uit .env
ENV_FILE="${ENV_FILE:-${REPO_ROOT}/.env}"
if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: .env file not found at ${ENV_FILE}" >&2
  exit 2
fi
# shellcheck disable=SC1090
set -a; source "$ENV_FILE"; set +a

POSTGRES_USER="${POSTGRES_USER:?POSTGRES_USER not set in .env}"
POSTGRES_DB="${POSTGRES_DB:?POSTGRES_DB not set in .env}"

mkdir -p "${BACKUP_DIR}/daily" "${BACKUP_DIR}/weekly"

timestamp=$(date +%Y%m%d-%H%M%S)
dow=$(date +%u)  # 1=Monday .. 7=Sunday
daily_file="${BACKUP_DIR}/daily/grc-${timestamp}.sql.gz"

echo "[$(date -Iseconds)] Starting backup of database '${POSTGRES_DB}'..."

# Run pg_dump in the db container, stream via gzip to the host
if ! docker compose -f "${COMPOSE_FILE}" exec -T "${DB_SERVICE}" \
       pg_dump -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" --no-owner --no-privileges \
     | gzip > "${daily_file}"; then
  echo "ERROR: pg_dump failed" >&2
  rm -f "${daily_file}"
  exit 1
fi

size=$(du -h "${daily_file}" | cut -f1)
echo "[$(date -Iseconds)] Daily backup written: ${daily_file} (${size})"

# Promoteer naar wekelijks op zondag
if [ "$dow" = "7" ]; then
  weekly_file="${BACKUP_DIR}/weekly/grc-${timestamp}.sql.gz"
  cp "${daily_file}" "${weekly_file}"
  echo "[$(date -Iseconds)] Weekly snapshot: ${weekly_file}"
fi

# Retentie — verwijder oude bestanden
find "${BACKUP_DIR}/daily" -name 'grc-*.sql.gz' -type f | sort | head -n -"${BACKUP_DAILY_RETENTION}" | xargs -r rm -v
find "${BACKUP_DIR}/weekly" -name 'grc-*.sql.gz' -type f | sort | head -n -"${BACKUP_WEEKLY_RETENTION}" | xargs -r rm -v

# Verifieer dat de dump niet leeg is
min_size_bytes=1024
actual_size=$(stat -c '%s' "${daily_file}" 2>/dev/null || stat -f '%z' "${daily_file}")
if [ "${actual_size}" -lt "${min_size_bytes}" ]; then
  echo "ERROR: Backup file is suspiciously small (${actual_size} bytes < ${min_size_bytes})" >&2
  exit 1
fi

echo "[$(date -Iseconds)] Backup complete."
