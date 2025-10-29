#!/usr/bin/env python3
"""
Clear all tables in the database and recreate the schema
"""

import os
import sys

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, inspect
from app.database import engine, Base
from app.config import settings
# Import all models to ensure they are registered with SQLAlchemy
from app.models import (
    User, Product, Category, ProductImage,
    Interaction, Session,
    EmbeddingsMeta, RecommendationLog, ABTest, SystemAudit,
    UserCart, UserWishlist, PurchaseHistory, UserSessionState,
    Review, ReviewHelpfulVote
)


def clear_database():
    """Drop all tables and recreate the schema"""
    print("🗑️  Clearing all tables from database...")
    
    try:
        # Get inspector to check tables
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if existing_tables:
            print(f"Found {len(existing_tables)} tables:")
            for table in existing_tables:
                print(f"  - {table}")
            
            # Drop all tables
            print("\nDropping all tables...")
            Base.metadata.drop_all(bind=engine)
            print("✅ All tables dropped successfully!")
        else:
            print("ℹ️  No tables found in the database.")
        
        # Recreate all tables
        print("\n🔄 Recreating database schema...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database schema recreated successfully!")
        
        # Verify tables were created
        inspector = inspect(engine)
        new_tables = inspector.get_table_names()
        print(f"\n✅ Database reset complete! {len(new_tables)} tables created:")
        for table in sorted(new_tables):
            print(f"  - {table}")
            
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Clear all tables in the database')
    parser.add_argument('--yes', '-y', action='store_true', 
                       help='Skip confirmation prompt')
    args = parser.parse_args()
    
    # Confirm before proceeding (unless --yes flag is used)
    if not args.yes:
        print("=" * 60)
        print("⚠️  WARNING: This will DELETE ALL DATA in the database!")
        print("=" * 60)
        response = input("\nType 'yes' to proceed: ")
        
        if response.lower() != 'yes':
            print("❌ Operation cancelled.")
            sys.exit(1)
    
    clear_database()

