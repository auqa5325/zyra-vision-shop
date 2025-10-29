#!/usr/bin/env python3
"""
Migration script to add discount_percent column to products table
"""

import os
import sys

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import text
from app.database import engine
from app.config import settings


def add_discount_percent_column():
    """Add discount_percent column to products table"""
    print("Adding discount_percent column to products table...")
    
    try:
        with engine.connect() as conn:
            # Check if column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='products' AND column_name='discount_percent'
            """))
            
            if result.fetchone():
                print("✅ discount_percent column already exists!")
                return
            
            # Add the column
            conn.execute(text("""
                ALTER TABLE products 
                ADD COLUMN discount_percent NUMERIC(5,2) DEFAULT 0
            """))
            
            conn.commit()
            print("✅ discount_percent column added successfully!")
            
    except Exception as e:
        print(f"❌ Error adding discount_percent column: {e}")
        raise


if __name__ == "__main__":
    add_discount_percent_column()
