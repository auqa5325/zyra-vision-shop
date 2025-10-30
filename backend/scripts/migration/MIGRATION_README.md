# Database Migration to AWS RDS

This directory contains scripts to migrate your local `zyra_db` to AWS RDS PostgreSQL.

## Prerequisites

1. **PostgreSQL client tools installed**:
   - `pg_dump` - for creating database backups
   - `pg_restore` - for restoring database backups
   
   Install on macOS:
   ```bash
   brew install postgresql
   ```
   
   Install on Ubuntu/Debian:
   ```bash
   sudo apt-get install postgresql-client
   ```

2. **AWS RDS PostgreSQL instance created**:
   - Create an RDS instance in AWS Console
   - Note down: Endpoint, Port, Username, Password, Database Name
   - Security group must allow connections from your IP

3. **Network access**:
   - Ensure your local machine can connect to the RDS instance
   - Test connection: `psql -h <RDS_ENDPOINT> -U <USERNAME> -d <DATABASE>`

## Method 1: Using Python Script (Recommended)

```bash
cd backend/scripts/migration
python3 upload_db_to_aws_rds.py
```

This script will:
1. Create a backup of your local database
2. Prompt for RDS connection details
3. Upload the backup to RDS

## Method 2: Using Shell Script

```bash
cd backend/scripts/migration
./migrate_to_aws_rds.sh
```

## What Gets Migrated

All data from these 16 tables:
- ab_tests
- categories (48 records)
- embeddings_meta (3,352 records)
- interactions (47,321 records)
- product_images (3,517 records)
- products (3,448 records)
- purchase_history (1,421 records)
- recommendation_logs
- review_helpful_votes
- reviews (16,015 records)
- sessions (2,635 records)
- system_audit
- user_cart (652 records)
- user_session_states
- user_wishlist (798 records)
- users (529 records)

**Total:** ~80,165 records

## After Migration

1. **Update your `.env` file**:
   ```env
   # Comment out local database
   # DATABASE_URL=postgresql+psycopg2://vijaygk:Crestora2025@localhost:5432/zyra_db
   
   # Use RDS database
   DATABASE_URL=postgresql+psycopg2://username:password@your-rds-endpoint.region.rds.amazonaws.com:5432/zyra_db
   ```

2. **Test the connection**:
   ```bash
   cd backend
   python3 list_tables.py
   ```

3. **Keep the backup file** for safety

## Troubleshooting

### Connection Issues

If you can't connect to RDS:
1. Check security group allows your IP
2. Verify endpoint is correct
3. Check username and password
4. Ensure RDS instance is publicly accessible (if needed)

### Restore Issues

If restore fails:
1. Ensure the target database exists
2. Check user has proper permissions
3. Try creating tables first using SQLAlchemy migrations
4. Check RDS storage limits

### Performance

For large databases:
- Consider using RDS Multi-AZ for better performance
- Monitor I/O credits for t2/t3 instances
- Consider db.r5 instances for production

## Security Notes

⚠️ **Important**: 
- Backup files contain sensitive data
- Don't commit backup files to git
- Use secure passwords for RDS
- Enable SSL/TLS for RDS connections
- Consider using AWS Secrets Manager for credentials

## Rollback

To rollback to local database:
```bash
# In your .env file, switch back to local
DATABASE_URL=postgresql+psycopg2://vijaygk:Crestora2025@localhost:5432/zyra_db
```

Then restart your application.

