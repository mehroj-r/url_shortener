#!/bin/sh

# Database backup script
BACKUP_DIR="/app/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/url_shortener_db_$DATE.sql"

mkdir -p $BACKUP_DIR

echo "Creating database backup..."
docker-compose exec db pg_dump -U postgres url_shortener_db > $BACKUP_FILE

echo "Backup created: $
