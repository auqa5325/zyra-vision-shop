#!/usr/bin/env python3
"""
Mock Data Generation Script for Zyra Backend
Generates realistic, usable data for all tables
"""

import os
import sys
import uuid
import random
import json
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any

# Add the parent directory to the path so we can import our app modules
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import *
from app.config import settings

# Initialize Faker
fake = Faker()

# Database setup
engine = create_engine(settings.get_database_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Category hierarchy
CATEGORIES = {
    "Electronics": {
        "Laptops": ["MacBook Pro", "Dell XPS", "HP Pavilion", "Lenovo ThinkPad", "ASUS ROG"],
        "Smartphones": ["iPhone", "Samsung Galaxy", "Google Pixel", "OnePlus", "Xiaomi"],
        "Headphones": ["Sony WH-1000XM5", "Bose QuietComfort", "AirPods Pro", "Sennheiser HD", "JBL"],
        "Cameras": ["Canon EOS", "Nikon D", "Sony Alpha", "Fujifilm X", "Panasonic Lumix"],
        "Smart Watches": ["Apple Watch", "Samsung Galaxy Watch", "Fitbit", "Garmin", "Amazfit"]
    },
    "Fashion": {
        "Men's Clothing": ["Nike", "Adidas", "Levi's", "Tommy Hilfiger", "Calvin Klein"],
        "Women's Clothing": ["Zara", "H&M", "Forever 21", "Mango", "Uniqlo"],
        "Footwear": ["Nike Air", "Adidas Ultraboost", "Converse", "Vans", "New Balance"],
        "Accessories": ["Ray-Ban", "Oakley", "Fossil", "Michael Kors", "Coach"]
    },
    "Fitness": {
        "Exercise Equipment": ["Bowflex", "NordicTrack", "Peloton", "Concept2", "TRX"],
        "Supplements": ["Optimum Nutrition", "Dymatize", "MuscleTech", "BSN", "Cellucor"],
        "Sportswear": ["Under Armour", "Lululemon", "Athleta", "Puma", "Reebok"],
        "Yoga": ["Manduka", "Liforme", "Jade Yoga", "Gaiam", "Yoga Design Lab"]
    },
    "Home & Living": {
        "Furniture": ["IKEA", "West Elm", "Crate & Barrel", "Pottery Barn", "Ashley"],
        "Kitchen": ["KitchenAid", "Cuisinart", "Ninja", "Instant Pot", "Vitamix"],
        "Decor": ["Anthropologie", "Urban Outfitters", "CB2", "Restoration Hardware", "Wayfair"],
        "Appliances": ["Samsung", "LG", "Whirlpool", "GE", "Bosch"]
    },
    "Books": {
        "Fiction": ["Penguin Random House", "HarperCollins", "Simon & Schuster", "Macmillan", "Hachette"],
        "Non-fiction": ["O'Reilly", "Wiley", "McGraw-Hill", "Addison-Wesley", "Manning"],
        "Educational": ["Pearson", "McGraw-Hill Education", "Cengage", "Wiley", "Sage"],
        "Comics": ["Marvel", "DC Comics", "Image Comics", "Dark Horse", "IDW"]
    }
}

# Price ranges by category
PRICE_RANGES = {
    "Electronics": {"min": 2000, "max": 150000},
    "Fashion": {"min": 500, "max": 25000},
    "Fitness": {"min": 800, "max": 50000},
    "Home & Living": {"min": 1000, "max": 100000},
    "Books": {"min": 200, "max": 5000}
}

# Event type distribution
# Based on: 500 users, 3000 products
# Per user: 3-4 wishlist, 5-6 purchases, 2-3 cart items
# Per product: 5-6 reviews
EVENT_DISTRIBUTION = {
    "view": 0.4749,      # 47.49% - ~45,000 events (90 views/user) - Product page views
    "click": 0.2902,     # 29.02% - ~27,500 events (55 clicks/user) - Product card clicks
    "review": 0.1741,    # 17.41% - ~16,500 events (5.5 reviews/product) - Product reviews
    "purchase": 0.0290,  # 2.90% - ~2,750 events (5.5 purchases/user) - Purchase completions
    "wishlist": 0.0185,  # 1.85% - ~1,750 events (3.5 wishlist/user) - Wishlist add/remove
    "add_to_cart": 0.0132 # 1.32% - ~1,250 events (2.5 cart/user) - Add to cart actions
}

# Platform distribution
PLATFORM_DISTRIBUTION = {
    "web": 0.70,
    "android": 0.20,
    "ios": 0.10
}


def create_categories(session):
    """Create category hierarchy"""
    print("Creating categories...")
    
    categories = {}
    
    # Create parent categories
    for parent_name in CATEGORIES.keys():
        parent_category = Category(
            name=parent_name,
            slug=parent_name.lower().replace(" ", "-").replace("&", "and")
        )
        session.add(parent_category)
        session.flush()  # Get the ID
        categories[parent_name] = parent_category
        
        # Create subcategories
        for sub_name, brands in CATEGORIES[parent_name].items():
            sub_category = Category(
                name=sub_name,
                slug=f"{parent_category.slug}-{sub_name.lower().replace(' ', '-').replace('&', 'and')}",
                parent_id=parent_category.category_id
            )
            session.add(sub_category)
            session.flush()
            categories[f"{parent_name}_{sub_name}"] = sub_category
    
    session.commit()
    print(f"Created {len(categories)} categories")
    return categories


def create_users(session, count=200):
    """Create realistic users"""
    print(f"Creating {count} users...")
    
    users = []
    
    # Create registered users (75%)
    for _ in range(int(count * 0.75)):
        user = User(
            email=fake.email(),
            profile={
                "name": fake.name(),
                "age": random.randint(18, 65),
                "location": fake.city(),
                "preferences": {
                    "favorite_categories": random.sample(list(CATEGORIES.keys()), random.randint(1, 3)),
                    "budget_range": {"min": random.randint(1000, 10000), "max": random.randint(20000, 100000)}
                }
            },
            is_anonymous=False,
            last_seen_at=fake.date_time_between(start_date="-30d", end_date="now")
        )
        session.add(user)
        users.append(user)
    
    # Create anonymous users (25%)
    for _ in range(int(count * 0.25)):
        user = User(
            email=None,
            profile={
                "session_data": {
                    "ip_address": fake.ipv4(),
                    "user_agent": fake.user_agent(),
                    "referrer": fake.url()
                }
            },
            is_anonymous=True,
            last_seen_at=fake.date_time_between(start_date="-7d", end_date="now")
        )
        session.add(user)
        users.append(user)
    
    session.commit()
    print(f"Created {len(users)} users")
    return users


def create_products(session, categories, count=500):
    """Create realistic products"""
    print(f"Creating {count} products...")
    
    products = []
    all_subcategories = [cat for cat in categories.values() if cat.parent_id is not None]
    
    for i in range(count):
        # Select random subcategory
        subcategory = random.choice(all_subcategories)
        parent_category = next(cat for cat in categories.values() if cat.category_id == subcategory.parent_id)
        
        # Get brands for this subcategory
        subcategory_key = f"{parent_category.name}_{subcategory.name}"
        brands = CATEGORIES[parent_category.name][subcategory.name]
        brand = random.choice(brands)
        
        # Generate product name
        product_name = f"{brand} {fake.word().title()} {subcategory.name.replace('s', '').replace('Men', 'Men\'s').replace('Women', 'Women\'s')}"
        
        # Generate realistic price
        price_range = PRICE_RANGES[parent_category.name]
        price = Decimal(str(random.randint(price_range["min"], price_range["max"])))
        
        # Generate discount (30% chance of having discount)
        discount_percent = Decimal("0.00")
        if random.random() < 0.3:  # 30% chance of discount
            discount_percent = Decimal(str(random.randint(5, 50)))  # 5% to 50% discount
        
        # Generate tags
        tags = [
            brand.lower(),
            subcategory.name.lower().replace(" ", "-"),
            parent_category.name.lower(),
            random.choice(["premium", "budget", "popular", "new", "bestseller"]),
            random.choice(["wireless", "bluetooth", "smart", "portable", "compact"])
        ]
        
        # Generate descriptions
        short_desc = f"High-quality {subcategory.name.lower()} from {brand}"
        long_desc = f"Experience the perfect blend of style and functionality with this {brand} {subcategory.name.lower()}. " \
                   f"Designed for modern lifestyles, this product offers exceptional performance and durability. " \
                   f"Perfect for {random.choice(['daily use', 'professional work', 'outdoor activities', 'home entertainment'])}. " \
                   f"Features include {random.choice(['advanced technology', 'premium materials', 'innovative design', 'user-friendly interface'])} " \
                   f"and comes with a comprehensive warranty."
        
        # Generate metadata
        metadata = {
            "brand": brand,
            "color": random.choice(["Black", "White", "Silver", "Blue", "Red", "Green"]),
            "weight": f"{random.randint(100, 5000)}g",
            "dimensions": f"{random.randint(10, 50)}x{random.randint(10, 50)}x{random.randint(5, 20)}cm",
            "warranty": f"{random.randint(1, 3)} years",
            "rating": round(random.uniform(3.5, 5.0), 1)
        }
        
        product = Product(
            sku=f"{parent_category.name[:3].upper()}-{subcategory.name[:3].upper()}-{i+1:03d}",
            name=product_name,
            short_description=short_desc,
            long_description=long_desc,
            category_id=subcategory.category_id,
            tags=tags,
            price=price,
            discount_percent=discount_percent,
            currency="INR",
            brand=brand,
            available=random.random() > 0.05,  # 95% available
            metadata=metadata
        )
        
        session.add(product)
        products.append(product)
    
    session.commit()
    print(f"Created {len(products)} products")
    return products


def create_product_images(session, products):
    """Create product images using Picsum"""
    print("Creating product images...")
    
    image_variants = [
        {"variant": "original", "width": 800, "height": 800},
        {"variant": "medium", "width": 400, "height": 400},
        {"variant": "thumb", "width": 200, "height": 200},
        {"variant": "small", "width": 150, "height": 150}
    ]
    
    for product in products:
        # Create 3-5 images per product
        num_images = random.randint(3, 5)
        
        for i in range(num_images):
            for variant in image_variants:
                image = ProductImage(
                    product_id=product.product_id,
                    s3_key=f"products/{product.product_id}/{variant['variant']}_{i+1}.jpg",
                    cdn_url=f"https://picsum.photos/seed/{product.product_id}_{i+1}/{variant['width']}/{variant['height']}",
                    width=variant["width"],
                    height=variant["height"],
                    format="jpg",
                    variant=variant["variant"],
                    alt_text=f"{product.name} - {variant['variant']} image {i+1}",
                    is_primary=(i == 0 and variant["variant"] == "medium")
                )
                session.add(image)
    
    session.commit()
    print("Created product images")


def create_sessions(session, users, count=1000):
    """Create user sessions"""
    print(f"Creating {count} sessions...")
    
    sessions = []
    
    for _ in range(count):
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
        session.add(session_obj)
        sessions.append(session_obj)
    
    session.commit()
    print(f"Created {len(sessions)} sessions")
    return sessions


def create_interactions(session, users, products, sessions, count=10000):
    """Create realistic user interactions"""
    print(f"Creating {count} interactions...")
    
    interactions = []
    
    # Create user preferences for more realistic interactions
    user_preferences = {}
    for user in users:
        if not user.is_anonymous and user.profile and "preferences" in user.profile:
            user_preferences[user.user_id] = user.profile["preferences"].get("favorite_categories", [])
    
    for _ in range(count):
        user = random.choice(users)
        product = random.choice(products)
        session_obj = random.choice(sessions)
        
        # Bias interactions based on user preferences (simplified)
        if user.user_id in user_preferences:
            preferred_categories = user_preferences[user.user_id]
            # Skip preference matching for now to avoid category lookup issues
            pass
        
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
        
        # Generate timestamp with peak hours bias (6-10 PM)
        hour = random.randint(6, 22)
        if 18 <= hour <= 22:  # Peak hours
            timestamp = fake.date_time_between(start_date="-90d", end_date="now")
        else:
            timestamp = fake.date_time_between(start_date="-90d", end_date="now")
        
        # Set event value based on event type
        if event_type == "purchase":
            # Purchase events should have event_value = 1 (quantity)
            event_value = Decimal("1.0")
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
            session_id=session_obj.session_id,
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
        
        session.add(interaction)
        interactions.append(interaction)
    
    session.commit()
    print(f"Created {len(interactions)} interactions")
    return interactions


def create_embeddings_meta(session, products):
    """Create embeddings metadata placeholder"""
    print("Creating embeddings metadata...")
    
    for i, product in enumerate(products):
        meta = EmbeddingsMeta(
            object_type="product",
            object_id=product.product_id,
            embedding_file="artifacts/product_embeddings.npy",
            vector_index=i,
            dim=384  # all-MiniLM-L6-v2 dimension
        )
        session.add(meta)
    
    session.commit()
    print("Created embeddings metadata")


def export_sample_data(products, output_file="sample_products.json"):
    """Export sample products to JSON for frontend testing"""
    print(f"Exporting sample data to {output_file}...")
    
    sample_products = []
    for product in products[:20]:  # First 20 products
        # Get primary image
        primary_image = None
        for img in product.images:
            if img.is_primary:
                primary_image = img.cdn_url
                break
        
        sample_products.append({
            "product_id": str(product.product_id),
            "name": product.name,
            "description": product.short_description,
            "price": float(product.price) if product.price else None,
            "image_url": primary_image,
            "rating": product.metadata.get("rating", 4.0) if product.metadata else 4.0,
            "category": product.category.name if product.category else None,
            "tags": product.tags or [],
            "brand": product.brand,
            "available": product.available
        })
    
    with open(output_file, "w") as f:
        json.dump(sample_products, f, indent=2)
    
    print(f"Exported {len(sample_products)} sample products")


def main():
    """Main function to generate all mock data"""
    print("Starting mock data generation...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    db_session = SessionLocal()
    
    try:
        # Generate data in order
        categories = create_categories(db_session)
        users = create_users(db_session)
        products = create_products(db_session, categories)
        create_product_images(db_session, products)
        sessions = create_sessions(db_session, users)
        interactions = create_interactions(db_session, users, products, sessions)
        create_embeddings_meta(db_session, products)
        
        # Export sample data
        export_sample_data(products)
        
        print("\n✅ Mock data generation completed successfully!")
        print(f"📊 Summary:")
        print(f"   - Categories: {len(categories)}")
        print(f"   - Users: {len(users)}")
        print(f"   - Products: {len(products)}")
        print(f"   - Sessions: {len(sessions)}")
        print(f"   - Interactions: {len(interactions)}")
        
    except Exception as e:
        print(f"❌ Error generating mock data: {e}")
        db_session.rollback()
        raise
    finally:
        db_session.close()


if __name__ == "__main__":
    main()

