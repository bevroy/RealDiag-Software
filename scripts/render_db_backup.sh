#!/usr/bin/env bash
#
# Backup a Render Postgres database to a local .sql file.
#
# Usage:
#   ./scripts/render_db_backup.sh <NAME> <EXTERNAL_CONNECTION_STRING>
#
# Example:
#   ./scripts/render_db_backup.sh realdiag-database \
#     "postgresql://user:pass@dpg-xxxx.ohio-postgres.render.com/realdiag_prod"
#
# How to get the connection string:
#   Render Dashboard -> click the database -> "Connect" tab ->
#   copy the "External Database URL".
#
# Output:
#   backups/<NAME>-YYYYMMDD-HHMMSS.sql.gz
#
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <NAME> <EXTERNAL_CONNECTION_STRING>" >&2
  exit 1
fi

NAME="$1"
URL="$2"
TS="$(date -u +%Y%m%d-%H%M%S)"
OUT_DIR="backups"
OUT_FILE="${OUT_DIR}/${NAME}-${TS}.sql.gz"

mkdir -p "${OUT_DIR}"

if ! command -v pg_dump >/dev/null 2>&1; then
  echo "pg_dump not found. Install with:  sudo apt-get install -y postgresql-client" >&2
  exit 2
fi

echo ">> Dumping ${NAME} -> ${OUT_FILE}"
# --no-owner / --no-privileges keeps the dump portable across Render db users.
pg_dump \
  --no-owner \
  --no-privileges \
  --format=plain \
  --dbname="${URL}" \
  | gzip -9 > "${OUT_FILE}"

SIZE="$(du -h "${OUT_FILE}" | cut -f1)"
echo ">> Done. ${OUT_FILE} (${SIZE})"
