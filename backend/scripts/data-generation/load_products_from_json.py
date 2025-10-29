#!/usr/bin/env python3
"""
Load products from products.json and update database
Based on category structure and product counts in the JSON file
"""

import os
import sys
import json
import random
import uuid
from decimal import Decimal
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models import Product, Category, ProductImage

# Initialize Faker
fake = Faker()

# Price ranges by category (mapped from JSON categories)
PRICE_RANGES = {
    "Fashion & Apparel": {"min": 299, "max": 50000},
    "Electronics & Gadgets": {"min": 500, "max": 200000},
    "Home & Kitchen": {"min": 199, "max": 50000},
    "Beauty & Personal Care": {"min": 99, "max": 5000},
    "Groceries & Daily Needs": {"min": 29, "max": 5000},
    "Sports & Lifestyle": {"min": 399, "max": 50000}
}

# Brand names by category (common Indian/international brands)
BRANDS_BY_CATEGORY = {
    "Fashion & Apparel": {
        "Men's T-Shirts": ["Allen Solly", "Van Heusen", "Arrow", "US Polo", "Levis"],
        "Men's Ethnic Wear": ["Manyavar", "Fabindia", "Raymond", "Wrogn", "Aurelia"],
        "Women's Kurtas & Kurtis": ["Fabindia", "Biba", "W", "Libas", "Global Desi"],
        "Women's Sarees": ["Nalli", "Kanchipuram", "Biba", "Fabindia", "Soch"],
        "Kids Wear": ["H&M Kids", "GAP Kids", "Pantaloons", "Allen Solly Kids", "Carter's"],
        "Footwear (Men/Women)": ["Nike", "Adidas", "Puma", "Reebok", "Woodland"],
        "Bags & Wallets": ["Skybags", "American Tourister", "Wildcraft", "Zara", "H&M"],
        "Accessories (Belts, Caps)": ["Fossil", "Titan", "Fastrack", "Wildcraft", "Zara"],
        "Watches": ["Titan", "Fastrack", "Fossil", "Casio", "Timex"]
    },
    "Electronics & Gadgets": {
        "Smartphones": ["Samsung", "Apple", "OnePlus", "Xiaomi", "Realme"],
        "Mobile Accessories": ["Samsung", "Apple", "Boat", "OnePlus", "Amazon Basics"],
        "Laptops": ["HP", "Dell", "Lenovo", "Asus", "Apple"],
        "Smartwatches": ["Apple", "Samsung", "Fitbit", "Garmin", "Fossil"],
        "Earphones & Headphones": ["Boat", "JBL", "Sony", "Sennheiser", "AirPods"],
        "Smart TVs": ["Samsung", "LG", "Sony", "OnePlus", "Mi"],
        "Cameras & DSLRs": ["Canon", "Nikon", "Sony", "Fujifilm", "Panasonic"],
        "Computer Accessories": ["Logitech", "HP", "Dell", "Microsoft", "Razer"]
    },
    "Home & Kitchen": {
        "Cookware": ["Prestige", "Hawkins", "TTK", "Meyer", "Cello"],
        "Kitchen Appliances (Mixers, Grinders)": ["Prestige", "Bajaj", "Morphy Richards", "Havells", "Maharaja"],
        "Dinner Sets": ["Borosil", "Corelle", "Milton", "Nilkamal", "Cello"],
        "Home Decor": ["IKEA", "Fabindia", "Homescape", "Tupperware", "Zara Home"],
        "Bedsheets & Curtains": ["SPACES", "D'Decor", "Welspun", "Bombay Dyeing", "Home Centre"],
        "Furniture (Chairs, Tables)": ["IKEA", "Godrej", "Nilkamal", "Pepperfry", "HomeTown"],
        "Cleaning Supplies": ["Harpic", "Lizol", "Dettol", "Mr. Muscle", "Vim"],
        "Storage & Containers": ["Tupperware", "Tupperware", "Cello", "Milton", "Nilkamal"]
    },
    "Beauty & Personal Care": {
        "Skincare": ["Lakme", "Ponds", "L'Oreal", "Garnier", "Neutrogena"],
        "Hair Care": ["Sunsilk", "Pantene", "Dove", "Head & Shoulders", "L'Oreal"],
        "Makeup": ["Lakme", "Maybelline", "L'Oreal", "Colorbar", "Sugar"],
        "Fragrances": ["Axe", "Fogg", "Engage", "Wildstone", "Park Avenue"],
        "Health Supplements": ["Himalaya", "Dabur", "Havasu", "GNC", "MuscleBlaze"]
    },
    "Groceries & Daily Needs": {
        "Rice & Grains": ["Kohinoor", "India Gate", "Dawat", "Fortune", "Basmati"],
        "Masalas & Spices": ["Everest", "MDH", "Catch", "Aachi", "Ramdev"],
        "Snacks & Beverages": ["Lay's", "Kurkure", "Coca-Cola", "Pepsi", "Britannia"],
        "Oils & Ghee": ["Fortune", "Dhara", "Saffola", "Amul", "Patanjali"],
        "Household Essentials (Detergent, Cleaners)": ["Surf Excel", "Ariel", "Tide", "Vim", "Harpic"],
        "Personal Hygiene (Soap, Shampoo)": ["Dove", "Lux", "Pears", "Sunsilk", "Head & Shoulders"]
    },
    "Sports & Lifestyle": {
        "Fitness Equipment": ["Decathlon", "Kore", "PowerMax", "Fitkit", "REEBOK"],
        "Sportswear": ["Nike", "Adidas", "Puma", "Reebok", "Decathlon"],
        "Yoga Mats & Accessories": ["Decathlon", "Reebok", "Adidas", "Kore", "Curefit"],
        "Travel Bags": ["American Tourister", "Skybags", "Wildcraft", "Samsonite", "Skybags"],
        "Bicycles & Gear": ["Hero", "Avon", "Atlas", "BSA", "Firefox"],
        "Outdoor Games (Cricket, Badminton)": ["SG", "Yonex", "Cosco", "Nivia", "Slazenger"]
    }
}


def find_json_file():
    """Find products.json file"""
    current_dir = Path(__file__).parent.parent.parent
    possible_paths = [
        current_dir / "products.json",
        Path("products.json"),
        Path("../products.json"),
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    raise FileNotFoundError("Could not find products.json")


def load_json_data(json_path):
    """Load and parse products.json"""
    print(f"📖 Reading {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ Loaded JSON data")
    print(f"   - Categories: {len(data.get('categories', []))}")
    print(f"   - Total products to generate: {data.get('total_product_count', 0)}")
    return data


def create_or_update_categories(session, json_data):
    """Create or update category hierarchy"""
    print("\n📁 Creating/updating categories...")
    
    category_map = {}
    total_categories = 0
    
    for cat_data in json_data.get("categories", []):
        parent_name = cat_data["name"]
        
        # Create or get parent category
        parent_category = session.query(Category).filter(
            Category.name == parent_name,
            Category.parent_id == None
        ).first()
        
        if not parent_category:
            slug = parent_name.lower().replace(" ", "-").replace("&", "and")
            parent_category = Category(
                name=parent_name,
                slug=slug
            )
            session.add(parent_category)
            session.flush()
            print(f"   ✓ Created parent category: {parent_name}")
        else:
            print(f"   ✓ Found existing parent category: {parent_name}")
        
        category_map[parent_name] = parent_category
        total_categories += 1
        
        # Create or get subcategories
        for subcat_data in cat_data.get("subcategories", []):
            subcat_name = subcat_data["name"]
            
            subcategory = session.query(Category).filter(
                Category.name == subcat_name,
                Category.parent_id == parent_category.category_id
            ).first()
            
            if not subcategory:
                slug = f"{parent_category.slug}-{subcat_name.lower().replace(' ', '-').replace('(', '').replace(')', '').replace('/', '-')}"
                subcategory = Category(
                    name=subcat_name,
                    slug=slug,
                    parent_id=parent_category.category_id
                )
                session.add(subcategory)
                session.flush()
                print(f"     ✓ Created subcategory: {subcat_name}")
            else:
                print(f"     ✓ Found existing subcategory: {subcat_name}")
            
            total_categories += 1
    
    session.commit()
    print(f"\n✅ Created/updated {total_categories} categories")
    return category_map


def generate_product_name(brand, subcategory_name):
    """Generate a realistic product name"""
    # Clean subcategory name
    subcat_clean = subcategory_name.replace("Men's ", "").replace("Women's ", "").replace(" (Men/Women)", "")
    
    # Generate name variations
    templates = [
        f"{brand} {fake.word().title()} {subcat_clean}",
        f"{brand} {subcat_clean} {fake.word().title()}",
        f"{brand} Premium {subcat_clean}",
    ]
    
    return random.choice(templates)


def generate_products_for_subcategory(session, parent_category, subcategory, product_count, brands):
    """Generate products for a specific subcategory"""
    products = []
    
    price_range = PRICE_RANGES.get(parent_category.name, {"min": 500, "max": 5000})
    
    for i in range(product_count):
        brand = random.choice(brands) if brands else "Generic"
        
        # Generate product data
        product_name = generate_product_name(brand, subcategory.name)
        price = Decimal(str(random.randint(price_range["min"], price_range["max"])))
        
        # Generate SKU
        parent_prefix = parent_category.name[:3].upper().replace(" ", "")
        subcat_prefix = subcategory.name[:3].upper().replace(" ", "").replace("(", "").replace(")", "")
        sku = f"{parent_prefix}-{subcat_prefix}-{i+1:04d}"
        
        # Generate tags
        tags = [
            brand.lower(),
            subcategory.name.lower().replace(" ", "-").replace("(", "").replace(")", ""),
            parent_category.name.lower().replace(" ", "-"),
            random.choice(["premium", "bestseller", "new", "popular", "trending"]),
        ]
        
        # Generate descriptions
        short_desc = f"High-quality {subcategory.name.lower()} from {brand}"
        long_desc = (
            f"Experience the perfect blend of quality and style with this {brand} {subcategory.name.lower()}. "
            f"Designed for modern lifestyles, this product offers exceptional durability and performance. "
            f"Perfect for {random.choice(['daily use', 'special occasions', 'professional needs', 'casual wear'])}. "
            f"Made with {random.choice(['premium materials', 'high-quality materials', 'eco-friendly materials'])} "
            f"and backed by a comprehensive warranty."
        )
        
        # Generate metadata
        metadata = {
            "brand": brand,
            "color": random.choice(["Black", "White", "Blue", "Red", "Green", "Grey", "Brown", "Pink"]),
            "rating": round(random.uniform(3.8, 5.0), 1),
            "warranty": f"{random.randint(1, 2)} year" + ("s" if random.random() > 0.5 else ""),
        }
        
        # Add weight/dimensions for applicable categories
        if "Electronics" in parent_category.name or "Appliances" in subcategory.name:
            metadata["weight"] = f"{random.randint(200, 5000)}g"
            metadata["dimensions"] = f"{random.randint(10, 50)}x{random.randint(10, 50)}x{random.randint(5, 20)}cm"
        
        product = Product(
            sku=sku,
            name=product_name,
            short_description=short_desc,
            long_description=long_desc,
            category_id=subcategory.category_id,
            tags=tags,
            price=price,
            currency="INR",
            brand=brand,
            available=random.random() > 0.03,  # 97% available
            metadata_json=metadata
        )
        
        session.add(product)
        products.append(product)
    
    return products


def create_products(session, json_data, category_map):
    """Create all products based on JSON structure"""
    print("\n📦 Creating products...")
    
    all_products = []
    image_variants = [
        {"variant": "original", "width": 800, "height": 800},
        {"variant": "medium", "width": 400, "height": 400},
        {"variant": "thumb", "width": 200, "height": 200},
        {"variant": "small", "width": 150, "height": 150}
    ]
    
    for cat_data in json_data.get("categories", []):
        parent_category = category_map[cat_data["name"]]
        
        print(f"\n  📁 {parent_category.name}:")
        
        for subcat_data in cat_data.get("subcategories", []):
            product_count = subcat_data.get("product_count", 0)
            if product_count == 0:
                continue
            
            # Get subcategory from DB
            subcategory = session.query(Category).filter(
                Category.name == subcat_data["name"],
                Category.parent_id == parent_category.category_id
            ).first()
            
            if not subcategory:
                print(f"    ⚠️  Subcategory '{subcat_data['name']}' not found, skipping")
                continue
            
            # Get brands for this subcategory
            brands = BRANDS_BY_CATEGORY.get(parent_category.name, {}).get(subcat_data["name"], ["Generic"])
            
            print(f"    📋 {subcat_data['name']}: Generating {product_count} products...", end=" ", flush=True)
            
            # Generate products
            products = generate_products_for_subcategory(
                session, parent_category, subcategory, product_count, brands
            )
            
            all_products.extend(products)
            session.flush()  # Flush to get product IDs
            
            # Create images for products
            for product in products:
                num_images = random.randint(2, 4)
                for img_idx in range(num_images):
                    for variant in image_variants:
                        image = ProductImage(
                            product_id=product.product_id,
                            s3_key=f"products/{product.product_id}/{variant['variant']}_{img_idx+1}.jpg",
                            cdn_url=f"https://picsum.photos/seed/{product.product_id}_{img_idx+1}/{variant['width']}/{variant['height']}",
                            width=variant["width"],
                            height=variant["height"],
                            format="jpg",
                            variant=variant["variant"],
                            alt_text=f"{product.name} - {variant['variant']} image {img_idx+1}",
                            is_primary=(img_idx == 0 and variant["variant"] == "medium")
                        )
                        session.add(image)
            
            print(f"✅ ({len(products)} products + images created)")
    
    session.commit()
    print(f"\n✅ Created {len(all_products)} products with images")
    return all_products


def main():
    """Main function"""
    print("="*80)
    print("LOAD PRODUCTS FROM products.json")
    print("="*80)
    print()
    
    # Find JSON file
    json_path = find_json_file()
    print(f"📄 Found products.json at: {json_path}")
    
    # Load JSON data
    json_data = load_json_data(json_path)
    
    # Database setup
    engine = create_engine(settings.get_database_url())
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    session = SessionLocal()
    
    try:
        # Create/update categories
        category_map = create_or_update_categories(session, json_data)
        
        # Create products
        products = create_products(session, json_data, category_map)
        
        print("\n" + "="*80)
        print("✅ PRODUCT LOADING COMPLETE")
        print("="*80)
        print(f"📊 Summary:")
        print(f"   - Categories: {len(category_map)}")
        print(f"   - Products created: {len(products)}")
        print(f"   - Total expected: {json_data.get('total_product_count', 0)}")
        
        if len(products) < json_data.get('total_product_count', 0):
            print(f"   ⚠️  Note: Some subcategories may have had product_count=0")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()

