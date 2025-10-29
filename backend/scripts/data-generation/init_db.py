#!/usr/bin/env python3
"""
Initialize database schema
"""

import os
import sys

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine, Base
from app.config import settings


def init_database():
    """Initialize database schema"""
    print("Initializing database schema...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database schema created successfully!")
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection test successful!")
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise


if __name__ == "__main__":
    init_database()

