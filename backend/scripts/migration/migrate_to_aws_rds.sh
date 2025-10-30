#!/bin/bash

# Script to migrate local zyra_db to AWS RDS PostgreSQL
# This script uses pg_dump and pg_restore

set -e  # Exit on error

echo "=========================================="
echo "AWS RDS Database Migration"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
LOCAL_DB_HOST="localhost"
LOCAL_DB_PORT="5432"
LOCAL_DB_NAME="zyra_db"
LOCAL_DB_USER="vijaygk"
LOCAL_DB_PASSWORD="Crestora2025"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="backup_zyra_db_${TIMESTAMP}.sql"

# Get RDS configuration
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
    echo -e "${RED}Error: All fields are required${NC}"
    exit 1
fi

echo ""
echo "Creating backup of local database..."

# Export password for pg_dump
export PGPASSWORD="$LOCAL_DB_PASSWORD"

# Create backup
if pg_dump -h "$LOCAL_DB_HOST" \
    -p "$LOCAL_DB_PORT" \
    -U "$LOCAL_DB_USER" \
    -d "$LOCAL_DB_NAME" \
    -F c \
    -f "$BACKUP_FILE"; then
    echo -e "${GREEN}✓ Backup created: $BACKUP_FILE${NC}"
else
    echo -e "${RED}✗ Error creating backup${NC}"
    exit 1
fi

# Unset local password
unset PGPASSWORD

echo ""
echo -e "${YELLOW}⚠️  WARNING: This will overwrite the database at $RDS_HOST${NC}"
read -p "Continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "Uploading to AWS RDS..."

# Export password for pg_restore
export PGPASSWORD="$RDS_PASSWORD"

# Restore to RDS
if pg_restore -h "$RDS_HOST" \
    -p "$RDS_PORT" \
    -U "$RDS_USER" \
    -d "$RDS_DATABASE" \
    --clean \
    --if-exists \
    --verbose \
    "$BACKUP_FILE"; then
    echo -e "${GREEN}✓ Database uploaded successfully to RDS${NC}"
else
    echo -e "${RED}✗ Error uploading to RDS${NC}"
    unset PGPASSWORD
    exit 1
fi

# Unset RDS password
unset PGPASSWORD

echo ""
echo "=========================================="
echo -e "${GREEN}✓ Migration completed successfully!${NC}"
echo "=========================================="
echo ""
echo "Backup file: $BACKUP_FILE"
echo "RDS Endpoint: $RDS_HOST"
echo ""
echo "Update your .env file with:"
echo "DATABASE_URL=postgresql+psycopg2://$RDS_USER:$RDS_PASSWORD@$RDS_HOST:$RDS_PORT/$RDS_DATABASE"




