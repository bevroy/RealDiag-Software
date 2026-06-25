#!/usr/bin/env bash
#
# Restore a backup .sql.gz into a fresh Render Postgres database.
#
# Usage:
#   ./scripts/render_db_restore.sh <BACKUP_FILE.sql.gz> <NEW_EXTERNAL_CONNECTION_STRING>
#
# Example:
#   ./scripts/render_db_restore.sh \
#     backups/realdiag-database-20260503-224500.sql.gz \
#     "postgresql://user:pass@dpg-yyyy.virginia-postgres.render.com/realdiag_prod"
#
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <BACKUP_FILE.sql.gz> <NEW_EXTERNAL_CONNECTION_STRING>" >&2
  exit 1
fi

FILE="$1"
URL="$2"

if [[ ! -f "${FILE}" ]]; then
  echo "Backup file not found: ${FILE}" >&2
  exit 2
fi

if ! command -v psql >/dev/null 2>&1; then
  echo "psql not found. Install with:  sudo apt-get install -y postgresql-client" >&2
  exit 3
fi

echo ">> Restoring ${FILE} -> ${URL%%@*}@<host>"
gunzip -c "${FILE}" | psql --single-transaction --set ON_ERROR_STOP=on --dbname="${URL}"
echo ">> Restore complete."
