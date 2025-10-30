#!/usr/bin/env python3
"""
Script to list all database tables and their record counts
"""
import sys
from sqlalchemy import inspect, text, create_engine
from app.config import settings

# Create a new engine without echo for clean output
clean_engine = create_engine(
    settings.get_database_url(),
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False
)

def get_database_info():
    """Print database name and all tables with record counts"""
    
    # Get database name from connection string
    db_url = settings.get_database_url()
    if "postgresql" in db_url:
        # Extract database name from connection string
        # Format: postgresql://user:pass@host:port/dbname
        db_name = db_url.split('/')[-1].split('?')[0]
        print(f"\n{'='*60}")
        print(f"Database Name: {db_name}")
        print(f"{'='*60}\n")
    else:
        print(f"\n{'='*60}")
        print(f"Database Type: {db_url.split('://')[0]}")
        print(f"{'='*60}\n")
    
    # Create inspector
    inspector = inspect(clean_engine)
    
    # Get all table names
    tables = inspector.get_table_names()
    
    print(f"Total Tables: {len(tables)}\n")
    print(f"{'Table Name':<30} {'Record Count':>15}")
    print("-" * 50)
    
    # Get record count for each table using text() for proper SQL execution
    for table_name in sorted(tables):
        try:
            with clean_engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()
                print(f"{table_name:<30} {count:>15,}")
        except Exception as e:
            print(f"{table_name:<30} Error: {str(e)[:50]}")
    
    print("-" * 50)
    print("\nComplete Table List:\n")
    
    for i, table in enumerate(sorted(tables), 1):
        print(f"{i:2d}. {table}")
    
    print(f"\n{'='*60}\n")

if __name__ == "__main__":
    try:
        get_database_info()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)




