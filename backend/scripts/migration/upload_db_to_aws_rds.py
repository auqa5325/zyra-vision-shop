#!/usr/bin/env python3
"""
Script to upload local zyra_db to AWS RDS PostgreSQL
"""
import sys
import subprocess
import os
from pathlib import Path
from datetime import datetime

def create_backup():
    """Create a backup of the local database"""
    print("Creating backup of local database...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_zyra_db_{timestamp}.sql"
    
    # Local database credentials
    db_name = "zyra_db"
    
    # Create pg_dump command
    # Note: This assumes pg_dump is installed on the system
    cmd = [
        "pg_dump",
        "-h", "localhost",
        "-p", "5432",
        "-U", "vijaygk",
        "-d", db_name,
        "-F", "c",  # Custom format (compressed)
        "-f", backup_file
    ]
    
    # Set PGPASSWORD environment variable
    env = os.environ.copy()
    env['PGPASSWORD'] = 'Crestora2025'
    
    try:
        result = subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
        print(f"✓ Backup created: {backup_file}")
        return backup_file
    except subprocess.CalledProcessError as e:
        print(f"✗ Error creating backup: {e.stderr}")
        return None
    except FileNotFoundError:
        print("✗ Error: pg_dump not found. Please install PostgreSQL client tools.")
        return None

def upload_to_rds(backup_file, rds_config):
    """
    Upload backup to AWS RDS PostgreSQL
    
    Args:
        backup_file: Path to the backup file
        rds_config: Dictionary with RDS connection details
    """
    print(f"\nUploading to AWS RDS...")
    print(f"RDS Endpoint: {rds_config['host']}")
    print(f"Database: {rds_config['database']}")
    
    # First, restore the schema
    cmd_restore = [
        "pg_restore",
        "-h", rds_config['host'],
        "-p", str(rds_config['port']),
        "-U", rds_config['user'],
        "-d", rds_config['database'],
        "--clean",  # Clean before restoring
        "--if-exists",
        "--verbose",
        backup_file
    ]
    
    env = os.environ.copy()
    env['PGPASSWORD'] = rds_config['password']
    
    try:
        result = subprocess.run(cmd_restore, env=env, check=True, capture_output=True, text=True)
        print(f"✓ Database uploaded successfully to RDS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error uploading to RDS: {e.stderr}")
        return False
    except FileNotFoundError:
        print("✗ Error: pg_restore not found. Please install PostgreSQL client tools.")
        return False

def main():
    """Main function"""
    print("="*60)
    print("AWS RDS Database Migration Script")
    print("="*60 + "\n")
    
    # Get RDS configuration from environment or user input
    print("Enter AWS RDS PostgreSQL connection details:")
    rds_config = {
        'host': input("RDS Endpoint (e.g., mydb.123456.us-east-1.rds.amazonaws.com): ").strip(),
        'port': input("Port (default 5432): ").strip() or "5432",
        'user': input("Username: ").strip(),
        'password': input("Password: ").strip(),
        'database': input("Database name: ").strip()
    }
    
    # Validate inputs
    if not all([rds_config['host'], rds_config['user'], rds_config['password'], rds_config['database']]):
        print("\n✗ Error: All fields are required")
        sys.exit(1)
    
    # Create backup
    backup_file = create_backup()
    if not backup_file:
        print("\n✗ Failed to create backup. Aborting.")
        sys.exit(1)
    
    # Confirm before uploading
    print(f"\n⚠️  WARNING: This will overwrite the database at {rds_config['host']}")
    confirm = input("Continue? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Aborted.")
        sys.exit(0)
    
    # Upload to RDS
    success = upload_to_rds(backup_file, rds_config)
    
    if success:
        print("\n" + "="*60)
        print("✓ Migration completed successfully!")
        print("="*60)
        print(f"\nBackup file: {backup_file}")
        print(f"RDS Endpoint: {rds_config['host']}")
        print("\nYou can now update your .env file with the RDS connection string:")
        print(f"DATABASE_URL=postgresql+psycopg2://{rds_config['user']}:{rds_config['password']}@{rds_config['host']}:{rds_config['port']}/{rds_config['database']}")
    else:
        print("\n✗ Migration failed. Please check the errors above.")

if __name__ == "__main__":
    main()

