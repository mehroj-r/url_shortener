#!/usr/bin/env bash
# Dump the production database to $BACKUP_DIR and delete dumps older than $KEEP_DAYS days.
#
# Run on the host from the repository root, e.g. from cron:
#   0 3 * * * cd /path/to/url_shortener && ./scripts/backup.sh >> backups/backup.log 2>&1
#
# Restore with:
#   gunzip -c backups/<file>.sql.gz | docker compose -f docker-compose.prod.yml exec -T db \
#     sh -c 'psql -U "$POSTGRES_USER" "$POSTGRES_DB"'
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"
KEEP_DAYS="${KEEP_DAYS:-14}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"

mkdir -p "$BACKUP_DIR"
backup_file="$BACKUP_DIR/url_shortener_db_$(date +%Y%m%d_%H%M%S).sql.gz"

echo "Creating database backup..."
if ! docker compose -f "$COMPOSE_FILE" exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' \
    | gzip > "$backup_file.partial"; then
    rm -f "$backup_file.partial"
    echo "Backup failed" >&2
    exit 1
fi
mv "$backup_file.partial" "$backup_file"
echo "Backup created: $backup_file"

find "$BACKUP_DIR" -name 'url_shortener_db_*.sql.gz' -mtime +"$KEEP_DAYS" -delete
