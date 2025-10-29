#!/usr/bin/env python3
"""
Generate interactions for existing users and products in the database
"""

import os
import sys
import random
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from faker import Faker
from app.database import SessionLocal
from app.models import Interaction, Session, User, Product
from app.config import settings

# Initialize Faker
fake = Faker()

# Event type distribution
EVENT_DISTRIBUTION = {
    "view": 0.4749,      # 47.49% - Product page views
    "click": 0.2902,     # 29.02% - Product card clicks
    "review": 0.1741,    # 17.41% - Product reviews
    "purchase": 0.0290,  # 2.90% - Purchase completions
    "wishlist": 0.0185,  # 1.85% - Wishlist add/remove
    "add_to_cart": 0.0132 # 1.32% - Add to cart actions
}

# Platform distribution
PLATFORM_DISTRIBUTION = {
    "web": 0.70,
    "android": 0.20,
    "ios": 0.10
}


def get_or_create_sessions(db_session, users, count=1000):
    """Get existing sessions or create new ones"""
    print(f"Checking/creating {count} sessions...")
    
    # Get existing sessions
    existing_sessions = db_session.query(Session).all()
    sessions = list(existing_sessions)
    
    # Create additional sessions if needed
    if len(sessions) < count:
        needed = count - len(sessions)
        print(f"Creating {needed} additional sessions...")
        
        for _ in range(needed):
            user = random.choice(users)
            session_obj = Session(
                user_id=user.user_id,
                started_at=fake.date_time_between(start_date="-90d", end_date="now"),
                context={
                    "referrer": random.choice([fake.url(), "direct", "google", "facebook", "instagram"]),
                    "campaign": random.choice(["summer_sale", "new_arrivals", "black_friday", None]),
                    "device_type": random.choice(["desktop", "mobile", "tablet"])
                }
            )
            db_session.add(session_obj)
            sessions.append(session_obj)
        
        db_session.commit()
    
    print(f"Using {len(sessions)} sessions")
    return sessions


def create_interactions(db_session, users, products, sessions, count=10000):
    """Create realistic user interactions for existing users and products"""
    print(f"Creating {count} interactions...")
    
    if not users:
        print("❌ No users found in database!")
        return []
    
    if not products:
        print("❌ No products found in database!")
        return []
    
    if not sessions:
        print("⚠️  No sessions available, creating some...")
        sessions = get_or_create_sessions(db_session, users, min(count // 10, 1000))
    
    interactions = []
    
    # Create user preferences for more realistic interactions
    user_preferences = {}
    for user in users:
        if not user.is_anonymous and user.profile and isinstance(user.profile, dict) and "preferences" in user.profile:
            prefs = user.profile.get("preferences", {})
            if isinstance(prefs, dict):
                user_preferences[user.user_id] = prefs.get("favorite_categories", [])
    
    # Batch insert for better performance
    batch_size = 1000
    for batch_num in range(0, count, batch_size):
        batch_count = min(batch_size, count - batch_num)
        batch_interactions = []
        
        for _ in range(batch_count):
            user = random.choice(users)
            product = random.choice(products)
            session_obj = random.choice(sessions) if sessions else None
            
            # Select event type based on distribution
            event_type = random.choices(
                list(EVENT_DISTRIBUTION.keys()),
                weights=list(EVENT_DISTRIBUTION.values())
            )[0]
            
            # Select platform
            platform = random.choices(
                list(PLATFORM_DISTRIBUTION.keys()),
                weights=list(PLATFORM_DISTRIBUTION.values())
            )[0]
            
            # Generate timestamp
            timestamp = fake.date_time_between(start_date="-90d", end_date="now")
            
            # Set event value based on event type
            if event_type == "purchase":
                # Use actual product price for purchases
                event_value = Decimal(str(product.price)) if product.price else Decimal("1.0")
            elif event_type == "wishlist":
                # Wishlist events can be add (1) or remove (0)
                event_value = Decimal("1.0") if random.random() > 0.1 else Decimal("0.0")
            elif event_type == "review":
                # Review events: rating value from 1 to 5
                event_value = Decimal(str(random.randint(1, 5)))
            else:
                event_value = Decimal("1.0")
            
            interaction = Interaction(
                user_id=user.user_id,
                product_id=product.product_id,
                session_id=session_obj.session_id if session_obj else None,
                event_type=event_type,
                event_value=event_value,
                platform=platform,
                device={
                    "user_agent": fake.user_agent(),
                    "screen_resolution": random.choice(["1920x1080", "1366x768", "375x667", "414x896"]),
                    "os": random.choice(["Windows", "macOS", "iOS", "Android"])
                },
                created_at=timestamp
            )
            
            batch_interactions.append(interaction)
        
        # Bulk insert the batch
        db_session.bulk_save_objects(batch_interactions)
        db_session.commit()
        interactions.extend(batch_interactions)
        
        print(f"  Created batch {batch_num // batch_size + 1}: {len(batch_interactions)} interactions")
    
    print(f"✅ Created {len(interactions)} interactions")
    return interactions


def main():
    """Main function to generate interactions for existing data"""
    print("=" * 80)
    print("Generating Interactions for Existing Users and Products")
    print("=" * 80)
    
    db_session = SessionLocal()
    
    try:
        # Load existing users
        users = db_session.query(User).all()
        print(f"\n📊 Found {len(users)} users in database")
        
        if not users:
            print("❌ No users found. Please create users first.")
            return
        
        # Load existing products (only available ones)
        products = db_session.query(Product).filter(Product.available == True).all()
        print(f"📦 Found {len(products)} available products in database")
        
        if not products:
            print("❌ No products found. Please create products first.")
            return
        
        # Get or create sessions
        sessions = get_or_create_sessions(db_session, users, count=min(len(users) * 5, 5000))
        
        # Calculate appropriate interaction count
        # Aim for ~90 interactions per user (similar to original distribution)
        interaction_count = len(users) * 90
        if interaction_count < 1000:
            interaction_count = 1000  # Minimum
        if interaction_count > 100000:
            interaction_count = 100000  # Maximum
        
        print(f"\n🎯 Generating {interaction_count} interactions...")
        print(f"   - Users: {len(users)}")
        print(f"   - Products: {len(products)}")
        print(f"   - Sessions: {len(sessions)}")
        
        # Check existing interactions count
        existing_count = db_session.query(Interaction).count()
        print(f"\n📈 Existing interactions: {existing_count}")
        
        # Generate interactions
        interactions = create_interactions(db_session, users, products, sessions, count=interaction_count)
        
        # Final count
        final_count = db_session.query(Interaction).count()
        
        print("\n" + "=" * 80)
        print("✅ Interaction generation completed!")
        print("=" * 80)
        print(f"📊 Summary:")
        print(f"   - Total interactions in DB: {final_count}")
        print(f"   - New interactions created: {len(interactions)}")
        print(f"   - Users: {len(users)}")
        print(f"   - Products: {len(products)}")
        print(f"   - Sessions: {len(sessions)}")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error generating interactions: {e}")
        import traceback
        traceback.print_exc()
        db_session.rollback()
        raise
    finally:
        db_session.close()


if __name__ == "__main__":
    main()

