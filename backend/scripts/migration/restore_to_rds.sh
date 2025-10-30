#!/bin/bash

# Script to restore database backup to AWS RDS
# Usage: ./restore_to_rds.sh <backup_file>

set -e

# Add Homebrew paths for PostgreSQL tools
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup_file>"
    echo "Example: $0 backup_zyra_db_20251030_052729.sql"
    exit 1
fi

BACKUP_FILE=$1

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file '$BACKUP_FILE' not found"
    exit 1
fi

echo "=========================================="
echo "AWS RDS Database Restore"
echo "=========================================="
echo ""

echo "Enter AWS RDS PostgreSQL connection details:"
read -p "RDS Endpoint: " RDS_HOST
read -p "RDS Port (default 5432): " RDS_PORT
RDS_PORT=${RDS_PORT:-5432}
read -p "RDS Username: " RDS_USER
read -sp "RDS Password: " RDS_PASSWORD
echo ""
read -p "RDS Database Name: " RDS_DATABASE

# Validate inputs
if [ -z "$RDS_HOST" ] || [ -z "$RDS_USER" ] || [ -z "$RDS_PASSWORD" ] || [ -z "$RDS_DATABASE" ]; then
    echo "Error: All fields are required"
    exit 1
fi

echo ""
echo "⚠️  WARNING: This will overwrite the database at $RDS_HOST"
read -p "Continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "Restoring to AWS RDS..."

export PGPASSWORD="$RDS_PASSWORD"

if pg_restore -h "$RDS_HOST" \
    -p "$RDS_PORT" \
    -U "$RDS_USER" \
    -d "$RDS_DATABASE" \
    --clean \
    --if-exists \
    --verbose \
    "$BACKUP_FILE"; then
    echo "✓ Database restored successfully to RDS"
    echo ""
    echo "Update your .env file with:"
    echo "DATABASE_URL=postgresql+psycopg2://$RDS_USER:$RDS_PASSWORD@$RDS_HOST:$RDS_PORT/$RDS_DATABASE"
else
    echo "✗ Error restoring to RDS"
    unset PGPASSWORD
    exit 1
fi

unset PGPASSWORD

