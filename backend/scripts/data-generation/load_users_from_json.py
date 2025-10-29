#!/usr/bin/env python3
"""
Load users from users.json and update database with password='password' (SHA256)
"""

import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models import User
from app.services.auth_service import jwt_service

# Read users.json
print("="*80)
print("Loading users from users.json...")
print("="*80)
print()

# Try multiple possible paths
possible_paths = [
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "users.json"),  # root/users.json
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "users.json"),  # backend/users.json
    "users.json",  # current directory
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json"),  # scripts/users.json
    "../users.json",  # relative to backend
]

json_path = None
for path in possible_paths:
    if os.path.exists(path):
        json_path = path
        break

if not json_path:
    print("❌ users.json not found. Tried:")
    for path in possible_paths:
        print(f"   - {path}")
    sys.exit(1)

print(f"📁 Found users.json at: {json_path}\n")

try:
    with open(json_path, 'r') as f:
        content = f.read()
    
    # Fix JSON formatting issues - remove malformed entries
    import re
    # Fix patterns like "Om",S" -> "Om",
    content = re.sub(r'",S"', '",', content)
    content = re.sub(r',Example"', ',"', content)
    content = re.sub(r',Methods"', ',"', content)
    # Fix missing quotes before commas
    content = re.sub(r'([a-zA-Z]),"', r'\1","', content)
    # Fix patterns like "Raman",Ramesh" -> "Raman","Ramesh"
    content = re.sub(r'"([^"]+)",([A-Z])', r'"\1","\2', content)
    
    # Parse JSON
    try:
        data = json.loads(content)
        usernames = data.get("usernames", [])
    except json.JSONDecodeError as e:
        print(f"⚠️  JSON parse error, trying manual extraction: {e}")
        # Fallback: extract usernames manually
        usernames = re.findall(r'"([A-Za-z]+)"', content)
        print(f"📋 Extracted {len(usernames)} usernames via regex")
    
    # Clean usernames (remove any extra characters, convert to lowercase)
    cleaned_usernames = []
    for username in usernames:
        if isinstance(username, str):
            # Clean up any formatting issues
            username = username.strip().lower()
            # Remove any trailing punctuation that might have been accidentally included
            username = username.rstrip(',')
            # Skip "usernames" which is the JSON key name
            if username and len(username) >= 2 and username != "usernames":
                cleaned_usernames.append(username)
    
    print(f"✅ Loaded {len(cleaned_usernames)} usernames from users.json")
    print(f"📋 Sample (first 10): {', '.join(cleaned_usernames[:10])}\n")
    
except Exception as e:
    print(f"❌ Error reading users.json: {e}")
    sys.exit(1)

# Update database
print("="*80)
print("Updating database...")
print("="*80)
print()

password_hash = jwt_service.get_password_hash("password")
print(f"🔐 Password hash (SHA256): {password_hash}\n", flush=True)

engine = create_engine(settings.get_database_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

created = 0
skipped = 0
errors = 0

with SessionLocal() as session:
    total = len(cleaned_usernames)
    
    for i, username in enumerate(cleaned_usernames, 1):
        try:
            # Check if exists
            existing = session.query(User).filter(User.username == username).first()
            if existing:
                skipped += 1
                if i % 50 == 0:
                    print(f"  [{i:3d}/{total}] Skipped (exists): {username} ... ({created} created, {skipped} skipped)", flush=True)
                continue
            
            # Create user
            user = User(
                username=username,
                password_hash=password_hash,
                is_anonymous=False,
                is_active=True
            )
            session.add(user)
            created += 1
            
            if i % 50 == 0:
                print(f"  [{i:3d}/{total}] Created: {username} ... ({created} created, {skipped} skipped)", flush=True)
            
            # Commit in batches
            if i % 100 == 0:
                session.commit()
                print(f"  💾 Committed batch ({i}/{total})", flush=True)
                
        except Exception as e:
            print(f"  ❌ Error creating '{username}': {e}", flush=True)
            errors += 1
            session.rollback()
            continue
    
    # Final commit
    session.commit()
    print(f"  💾 Final commit completed", flush=True)
    
    print()
    print("="*80)
    print("📊 SUMMARY")
    print("="*80)
    print(f"✅ Created: {created} users")
    print(f"⚠️  Skipped (already exist): {skipped} users")
    print(f"❌ Errors: {errors} users")
    print(f"📈 Total processed: {created + skipped + errors}/{total}")
    print("="*80)
    print()
    
    # Verification
    print("="*80)
    print("🔍 VERIFICATION")
    print("="*80)
    print()
    
    # Verify first 5 users
    for i, username in enumerate(cleaned_usernames[:5], 1):
        user = session.query(User).filter(User.username == username).first()
        if user:
            is_valid = jwt_service.verify_password("password", user.password_hash)
            status = "✅" if is_valid else "❌"
            print(f"  [{i}] Username: {user.username}")
            print(f"      Password 'password' matches: {is_valid} {status}")
            print(f"      User ID: {user.user_id}")
            print(f"      Created: {user.created_at}")
            print()
    
    # Count total users
    total_users = session.query(User).count()
    print(f"📊 Total users in database: {total_users}")
    print()

print("="*80)
print("✅ Process completed!")
print("="*80)

