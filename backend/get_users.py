#!/usr/bin/env python3
"""
Script to get users directly from database
"""
import logging
from sqlalchemy import create_engine, text
from app.config import settings

# Suppress logging
logging.basicConfig(level=logging.CRITICAL)
logging.getLogger('sqlalchemy').setLevel(logging.CRITICAL)

# Create engine
engine = create_engine(
    settings.get_database_url(),
    echo=False
)

# Query users directly
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT user_id, username, email, created_at, is_anonymous, is_active
        FROM users
        LIMIT 5
    """))
    
    print("\n" + "="*80)
    print("5 USERS FROM DATABASE")
    print("="*80 + "\n")
    
    for row in result:
        print(f"User ID:  {row.user_id}")
        print(f"Username: {row.username}")
        print(f"Email:    {row.email or 'N/A'}")
        print(f"Created:  {row.created_at}")
        print(f"Anonymous: {row.is_anonymous}")
        print(f"Active:   {row.is_active}")
        print("-" * 80)
    
    print()




