#!/bin/bash

# Simple script to create a backup of the local database
# This backup can then be uploaded to AWS RDS manually or via psql

set -e

# Add Homebrew paths for PostgreSQL tools
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

echo "=========================================="
echo "Database Backup Script"
echo "=========================================="
echo ""

LOCAL_DB_HOST="localhost"
LOCAL_DB_PORT="5432"
LOCAL_DB_NAME="zyra_db"
LOCAL_DB_USER="vijaygk"
LOCAL_DB_PASSWORD="Crestora2025"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="backup_zyra_db_${TIMESTAMP}.sql"

echo "Creating backup of local database..."
echo "Database: $LOCAL_DB_NAME"
echo ""

export PGPASSWORD="$LOCAL_DB_PASSWORD"

# Create backup
if pg_dump -h "$LOCAL_DB_HOST" \
    -p "$LOCAL_DB_PORT" \
    -U "$LOCAL_DB_USER" \
    -d "$LOCAL_DB_NAME" \
    -F c \
    -f "$BACKUP_FILE"; then
    echo "✓ Backup created: $BACKUP_FILE"
    echo ""
    echo "To restore to AWS RDS, run:"
    echo "pg_restore -h <RDS_ENDPOINT> -U <USERNAME> -d <DATABASE> --clean --if-exists $BACKUP_FILE"
else
    echo "✗ Error creating backup"
    exit 1
fi

unset PGPASSWORD

