#!/usr/bin/env python3
"""
Generate products using Gemini 2.5 Flash API
Processes subcategories in parallel with rate limiting (1000 req/min)
Products focused on Indian market
"""

import os
import sys
import json
import random
import uuid
import time
import asyncio
from decimal import Decimal
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock, Semaphore

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import google.generativeai as genai
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models import Product, Category

# Rate limiting: 1000 requests per minute = ~16.67 requests per second
# Use semaphore to limit concurrent requests
MAX_CONCURRENT_REQUESTS = 15  # Keep below 16.67 to be safe
RATE_LIMIT_SEMAPHORE = Semaphore(MAX_CONCURRENT_REQUESTS)

# Progress tracking
progress_lock = Lock()
stats = {
    "total": 0,
    "completed": 0,
    "failed": 0,
    "start_time": None
}

# Configure Gemini
GEMINI_API_KEY = settings.gemini_api_key
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')


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


def generate_price_for_category(category_name: str) -> Decimal:
    """Generate realistic price for Indian market"""
    price_ranges = {
        "Fashion & Apparel": {"min": 299, "max": 50000},
        "Electronics & Gadgets": {"min": 500, "max": 200000},
        "Home & Kitchen": {"min": 199, "max": 50000},
        "Beauty & Personal Care": {"min": 99, "max": 5000},
        "Groceries & Daily Needs": {"min": 29, "max": 5000},
        "Sports & Lifestyle": {"min": 399, "max": 50000}
    }
    
    range_vals = price_ranges.get(category_name, {"min": 500, "max": 5000})
    price = random.randint(range_vals["min"], range_vals["max"])
    
    # Round to nearest 10 for most categories, or 100 for expensive items
    if price > 10000:
        price = round(price / 100) * 100
    else:
        price = round(price / 10) * 10
    
    return Decimal(str(price))


def generate_product_with_gemini(subcategory: Category, parent_category: Category, 
                                   product_num: int, total_in_subcat: int) -> Dict[str, Any]:
    """Generate a single product using Gemini API"""
    with RATE_LIMIT_SEMAPHORE:  # Rate limiting
        try:
            prompt = f"""Generate a realistic e-commerce product for Indian market in JSON format.

Category: {parent_category.name}
Subcategory: {subcategory.name}
Product Number: {product_num} of {total_in_subcat}

Requirements:
1. Product name should be in English, relevant to Indian market
2. Use popular Indian or international brands (e.g., Samsung, Nike, Prestige, Biba, Manyavar, etc.)
3. Price should be realistic for Indian market (₹{generate_price_for_category(parent_category.name).__str__()} range)
4. Descriptions should mention Indian context where appropriate
5. Tags should include brand name, category, and relevant keywords

Return ONLY valid JSON with these exact fields:
{{
  "name": "string (product name with brand)",
  "sku": "string (unique SKU code)",
  "brand": "string (brand name)",
  "short_description": "string (1 sentence, max 100 chars)",
  "long_description": "string (2-3 sentences, max 300 chars)",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "price": number (integer, in INR),
  "metadata": {{
    "color": "string (optional)",
    "weight": "string (optional, e.g., '500g')",
    "dimensions": "string (optional, e.g., '30x25x10cm')",
    "warranty": "string (optional, e.g., '1 year')"
  }}
}}

Important: Return ONLY the JSON object, no markdown, no code blocks, no explanations."""

            response = model.generate_content(prompt)
            
            # Parse JSON response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            product_data = json.loads(response_text)
            
            # Validate and set defaults
            product_data.setdefault("tags", [])
            product_data.setdefault("metadata", {})
            
            # Ensure price is set
            if "price" not in product_data:
                product_data["price"] = float(generate_price_for_category(parent_category.name))
            
            return {
                "success": True,
                "data": product_data
            }
            
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"JSON parse error: {str(e)}",
                "response": response_text if 'response_text' in locals() else "No response"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"API error: {str(e)}"
            }


def create_product_from_gemini_data(session, gemini_data: Dict, subcategory: Category, 
                                     parent_category: Category, product_num: int) -> Optional[Product]:
    """Create Product object from Gemini-generated data"""
    try:
        data = gemini_data["data"]
        
        # Generate unique SKU - always use our own format to ensure uniqueness
        parent_prefix = parent_category.name[:3].upper().replace(" ", "").replace("&", "").replace("-", "")
        subcat_prefix = subcategory.name[:3].upper().replace(" ", "").replace("(", "").replace(")", "").replace("/", "-").replace("-", "")
        sku = f"{parent_prefix}-{subcat_prefix}-{product_num:04d}"
        
        # Check if SKU already exists and make it unique if needed
        existing_sku_count = session.query(Product).filter(Product.sku == sku).count()
        if existing_sku_count > 0:
            # Add unique suffix
            sku = f"{sku}-{uuid.uuid4().hex[:6].upper()}"
        
        # Generate tags
        tags = data.get("tags", [])
        if not tags:
            tags = [
                data.get("brand", "").lower(),
                subcategory.name.lower().replace(" ", "-"),
                parent_category.name.lower().replace(" ", "-"),
            ]
        
        # Ensure tags are strings
        tags = [str(tag) for tag in tags if tag]
        
        product = Product(
            sku=sku,
            name=data.get("name", f"{subcategory.name} Product {product_num}"),
            short_description=data.get("short_description", ""),
            long_description=data.get("long_description", ""),
            category_id=subcategory.category_id,
            tags=tags[:10],  # Limit to 10 tags
            price=Decimal(str(int(data.get("price", 1000)))),
            currency="INR",
            brand=data.get("brand"),
            available=random.random() > 0.03,  # 97% available
            discount_percent=Decimal("0.0"),
            metadata_json=data.get("metadata", {}),
            # rating is 0.0 by default in schema
        )
        
        session.add(product)
        try:
            session.flush()  # Get product_id
        except Exception as e:
            session.rollback()
            # If still duplicate, try with UUID suffix
            if "sku" in str(e).lower() or "unique" in str(e).lower():
                product.sku = f"{product.sku}-{uuid.uuid4().hex[:8].upper()}"
                session.add(product)
                try:
                    session.flush()
                except Exception as e2:
                    session.rollback()
                    print(f"      ❌ Error creating product (duplicate SKU): {e2}")
                    return None
            else:
                print(f"      ❌ Error creating product: {e}")
                return None
        
        # Images not generated for now
        
        return product
        
    except Exception as e:
        session.rollback()
        print(f"      ❌ Error creating product: {e}")
        return None


def process_subcategory_products(session_factory, parent_category: Category, 
                                  subcategory: Category, product_count: int,
                                  subcat_index: int, total_subcats: int,
                                  start_from_product: int = 1):
    """Process all products for a subcategory"""
    session = session_factory()
    
    try:
        # Check existing products count
        existing_count = session.query(Product).filter(
            Product.category_id == subcategory.category_id
        ).count()
        
        if existing_count >= product_count:
            print(f"\n  [{subcat_index+1}/{total_subcats}] ⏭️  {subcategory.name}: Already has {existing_count} products, skipping...")
            with progress_lock:
                stats["completed"] += (product_count - existing_count)
            return existing_count, 0
        
        # Adjust start_from_product if we have existing products
        if start_from_product == 1 and existing_count > 0:
            start_from_product = existing_count + 1
        
        remaining_products = product_count - (start_from_product - 1)
        
        if remaining_products <= 0:
            print(f"\n  [{subcat_index+1}/{total_subcats}] ⏭️  {subcategory.name}: Already complete, skipping...")
            with progress_lock:
                stats["completed"] += product_count
            return product_count, 0
        
        print(f"\n  [{subcat_index+1}/{total_subcats}] 📋 {subcategory.name}: Generating {remaining_products} products (from product {start_from_product})...")
        
        # Use ThreadPoolExecutor for parallel API calls
        products_created = 0
        products_failed = 0
        
        with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_REQUESTS) as executor:
            # Submit all product generation tasks (starting from start_from_product)
            futures = {}
            for i in range(start_from_product, product_count + 1):
                future = executor.submit(
                    generate_product_with_gemini,
                    subcategory, parent_category, i, product_count
                )
                futures[future] = i
            
            # Process results as they complete
            for future in as_completed(futures):
                product_num = futures[future]
                
                try:
                    result = future.result()
                    
                    if result["success"]:
                        product = create_product_from_gemini_data(
                            session, result, subcategory, parent_category, product_num
                        )
                        
                        if product:
                            products_created += 1
                            with progress_lock:
                                stats["completed"] += 1
                            
                            # Update progress every 10 products or at end
                            total_in_subcat = products_created + existing_count
                            if products_created % 10 == 0 or products_created == remaining_products:
                                elapsed = time.time() - stats["start_time"]
                                rate = stats["completed"] / elapsed if elapsed > 0 else 0
                                remaining = stats["total"] - stats["completed"]
                                eta = remaining / rate if rate > 0 else 0
                                
                                print(f"      ⏳ {products_created}/{remaining_products} products | "
                                      f"Total: {stats['completed']}/{stats['total']} | "
                                      f"Rate: {rate:.1f}/s | ETA: {eta/60:.1f}m", end='\r', flush=True)
                        else:
                            products_failed += 1
                            with progress_lock:
                                stats["failed"] += 1
                    else:
                        products_failed += 1
                        with progress_lock:
                            stats["failed"] += 1
                        error_msg = result.get('error', 'Unknown error')
                        # Only print if not a timeout (to reduce noise)
                        if "504" not in str(error_msg) and "Deadline" not in str(error_msg):
                            print(f"      ⚠️  Product {product_num} failed: {error_msg}")
                
                except Exception as e:
                    products_failed += 1
                    with progress_lock:
                        stats["failed"] += 1
                    print(f"      ❌ Product {product_num} error: {e}")
        
        # Commit all products for this subcategory
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"      ❌ Error committing {subcategory.name}: {e}")
            raise
        
        print(f"      ✅ {subcategory.name}: {products_created} created, {products_failed} failed")
        
        return products_created, products_failed
        
    except Exception as e:
        session.rollback()
        print(f"      ❌ Error processing {subcategory.name}: {e}")
        return 0, product_count
    finally:
        session.close()


def generate_all_products(session_factory, json_data, category_map, start_from_product: int = 1):
    """Generate all products using Gemini API with parallel processing"""
    print("\n" + "="*80)
    print("🤖 GENERATING PRODUCTS WITH GEMINI 2.5 FLASH")
    if start_from_product > 1:
        print(f"🔄 RESUMING FROM PRODUCT {start_from_product}")
    print("="*80)
    
    # Count total products and check existing
    total_products = 0
    existing_products = 0
    subcategory_tasks = []
    
    for cat_data in json_data.get("categories", []):
        parent_category = category_map[cat_data["name"]]
        
        for subcat_data in cat_data.get("subcategories", []):
            product_count = subcat_data.get("product_count", 0)
            if product_count == 0:
                continue
            
            # Get subcategory from DB
            session = session_factory()
            try:
                subcategory = session.query(Category).filter(
                    Category.name == subcat_data["name"],
                    Category.parent_id == parent_category.category_id
                ).first()
                
                # Count existing products
                existing = session.query(Product).filter(
                    Product.category_id == subcategory.category_id
                ).count() if subcategory else 0
                existing_products += existing
                
                session.close()
            except:
                session.close()
                continue
            
            if subcategory:
                subcategory_tasks.append((parent_category, subcategory, product_count))
                total_products += product_count
    
    remaining_products = total_products - existing_products
    stats["total"] = total_products
    stats["completed"] = existing_products  # Start with existing count
    stats["start_time"] = time.time()
    
    print(f"\n📊 Total: {total_products} products across {len(subcategory_tasks)} subcategories")
    print(f"   Existing: {existing_products} products")
    print(f"   Remaining: {remaining_products} products")
    print(f"⚡ Parallel processing: {MAX_CONCURRENT_REQUESTS} concurrent API calls")
    print(f"⏱️  Estimated time: ~{remaining_products / 16.67 / 60:.1f} minutes")
    print()
    
    # Process subcategories in parallel (using ThreadPoolExecutor)
    total_created = 0
    total_failed = 0
    
    with ThreadPoolExecutor(max_workers=3) as executor:  # 3 subcategories at a time
        futures = []
        for idx, (parent_cat, subcat, count) in enumerate(subcategory_tasks):
            future = executor.submit(
                process_subcategory_products,
                session_factory, parent_cat, subcat, count, idx, len(subcategory_tasks),
                start_from_product
            )
            futures.append((future, subcat.name, count))
        
        # Wait for all subcategories to complete
        for future, subcat_name, count in futures:
            try:
                created, failed = future.result()
                total_created += created
                total_failed += failed
            except Exception as e:
                print(f"❌ Subcategory {subcat_name} failed: {e}")
                total_failed += count
    
    elapsed = time.time() - stats["start_time"]
    
    print("\n" + "="*80)
    print("✅ PRODUCT GENERATION COMPLETE")
    print("="*80)
    print(f"📊 Results:")
    print(f"   - Products created: {total_created}")
    print(f"   - Products failed: {total_failed}")
    print(f"   - Success rate: {(total_created/(total_created+total_failed)*100):.1f}%" if (total_created+total_failed) > 0 else "N/A")
    print(f"   - Time elapsed: {elapsed/60:.1f} minutes")
    print(f"   - Average rate: {total_created/elapsed:.1f} products/second" if elapsed > 0 else "N/A")
    
    return total_created


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate products using Gemini API')
    parser.add_argument('--start-from', type=int, default=1,
                        help='Start from product number (default: 1)')
    args = parser.parse_args()
    
    print("="*80)
    print("GEMINI PRODUCT GENERATOR")
    print("="*80)
    print()
    
    # Verify Gemini API key
    if not GEMINI_API_KEY:
        print("❌ Error: GEMINI_API_KEY not found in environment variables")
        return
    
    # Test Gemini connection
    print("🔗 Testing Gemini API connection...")
    try:
        test_response = model.generate_content("Say 'Hello' in one word")
        print(f"✅ Gemini API connected (using gemini-2.5-flash)")
    except Exception as e:
        print(f"❌ Gemini API connection failed: {e}")
        return
    
    # Find JSON file
    json_path = find_json_file()
    print(f"\n📄 Found products.json at: {json_path}")
    
    # Load JSON data
    json_data = load_json_data(json_path)
    
    # Database setup
    engine = create_engine(settings.get_database_url())
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    session = SessionLocal()
    
    try:
        # Create/update categories
        category_map = create_or_update_categories(session, json_data)
        
        # Generate products using Gemini
        total_created = generate_all_products(SessionLocal, json_data, category_map, 
                                             start_from_product=args.start_from)
        
        print(f"\n🎉 Total products in database: {total_created}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    main()

