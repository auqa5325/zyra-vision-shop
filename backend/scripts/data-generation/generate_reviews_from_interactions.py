#!/usr/bin/env python3
"""
Generate reviews for products based on interactions table using Gemini 2.5 Flash Lite
- Queries products from interactions table
- Generates reviews per product using Gemini JSON prompting
- Updates reviews table with generated reviews
- Runs at 4k RPM with parallel processing
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock, Semaphore
from dataclasses import dataclass
from uuid import UUID, uuid4

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import google.generativeai as genai
from sqlalchemy import create_engine, func, distinct
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.config import settings
from app.models import Interaction, Product, Review, User, Category

# Rate limiting: 4k RPM = 4000 requests/minute = ~66.67 requests/second
MAX_CONCURRENT_REQUESTS = 70  # Conservative limit to stay under 4k RPM
RATE_LIMIT_SEMAPHORE = Semaphore(MAX_CONCURRENT_REQUESTS)

# Progress tracking
progress_lock = Lock()
stats = {
    "total_products": 0,
    "products_processed": 0,
    "reviews_generated": 0,
    "reviews_created": 0,
    "failed": 0,
    "skipped": 0,
    "start_time": None
}

# Configure Gemini
GEMINI_API_KEY = settings.gemini_api_key
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")
genai.configure(api_key=GEMINI_API_KEY)

# Default Gemini model - user requested gemini-2.5-flash-lite for 4k RPM
# Note: Update this to "gemini-2.5-flash-lite" when available, or use --model flag
DEFAULT_GEMINI_MODEL = "gemini-2.0-flash-exp"  # Supports JSON mode, fallback option
PREFERRED_MODEL = "gemini-2.5-flash-lite"  # User requested model - try this first


@dataclass
class ProductReviewData:
    """Product data structure for review generation"""
    product_id: str
    name: str
    brand: Optional[str]
    short_description: Optional[str]
    long_description: Optional[str]
    category_name: Optional[str]
    price: Optional[float]
    discount_percent: Optional[float]
    user_ids: List[str]  # Users who interacted with this product


@dataclass
class GeneratedReview:
    """Generated review data structure"""
    product_id: str
    user_id: str
    rating: int
    title: Optional[str]
    comment: Optional[str]
    verified_purchase: bool


def load_products_with_interactions(session_factory, skip_existing: bool = True) -> List[ProductReviewData]:
    """Load products that have interactions and get user IDs who interacted"""
    print("\n📦 Loading products with interactions...")
    
    session = session_factory()
    products_data = []
    
    try:
        # Get distinct products that have interactions
        # Focus on products with purchase, add_to_cart, wishlist events
        product_ids_with_interactions = session.query(
            distinct(Interaction.product_id)
        ).filter(
            Interaction.product_id.isnot(None),
            Interaction.event_type.in_(['purchase', 'add_to_cart', 'wishlist', 'view'])
        ).all()
        
        product_ids = [pid[0] for pid in product_ids_with_interactions if pid[0]]
        
        if not product_ids:
            print("   ⚠️  No products with interactions found")
            return []
        
        print(f"   📊 Found {len(product_ids)} products with interactions")
        
        # Get existing reviews to skip products that already have reviews
        if skip_existing:
            products_with_reviews = set(
                str(pid[0]) for pid in session.query(distinct(Review.product_id)).all()
            )
        else:
            products_with_reviews = set()
        
        # Load category names
        categories = {
            cat.category_id: cat.name
            for cat in session.query(Category).all()
        }
        
        # Load products and their interactions
        products = session.query(Product).filter(
            Product.product_id.in_(product_ids)
        ).all()
        
        # Get user interactions per product
        for product in products:
            product_id_str = str(product.product_id)
            
            # Skip if already has reviews
            if skip_existing and product_id_str in products_with_reviews:
                with progress_lock:
                    stats["skipped"] += 1
                continue
            
            # Get users who interacted with this product (especially purchase/add_to_cart)
            user_interactions = session.query(
                distinct(Interaction.user_id)
            ).filter(
                Interaction.product_id == product.product_id,
                Interaction.user_id.isnot(None),
                Interaction.event_type.in_(['purchase', 'add_to_cart', 'wishlist', 'view'])
            ).limit(10).all()  # Limit to 10 users per product for review generation
            
            user_ids = [str(uid[0]) for uid in user_interactions if uid[0]]
            
            if not user_ids:
                continue
            
            # Get category name
            category_name = None
            if product.category_id and product.category_id in categories:
                category_name = categories[product.category_id]
            
            product_data = ProductReviewData(
                product_id=product_id_str,
                name=product.name,
                brand=product.brand,
                short_description=product.short_description,
                long_description=product.long_description,
                category_name=category_name,
                price=float(product.price) if product.price else None,
                discount_percent=float(product.discount_percent) if product.discount_percent else None,
                user_ids=user_ids
            )
            
            products_data.append(product_data)
        
        stats["total_products"] = len(products_data)
        print(f"   ✅ Loaded {len(products_data)} products for review generation")
        print(f"   ⏭️  Skipped {stats['skipped']} products (already have reviews)")
        
        return products_data
        
    finally:
        session.close()


def generate_reviews_for_product(product_data: ProductReviewData, model_name: str = None) -> List[GeneratedReview]:
    """Generate reviews for a product using Gemini API with JSON mode"""
    with RATE_LIMIT_SEMAPHORE:  # Rate limiting
        try:
            # Prepare product information for prompt
            product_info = {
                "name": product_data.name,
                "brand": product_data.brand or "Unknown",
                "category": product_data.category_name or "General",
                "description": (product_data.short_description or product_data.long_description or "")[:300],
                "price": product_data.price,
                "discount": product_data.discount_percent,
                "number_of_users": len(product_data.user_ids)
            }
            
            # Create JSON prompt for review generation
            price_str = f"₹{product_info['price']:.2f}" if product_info.get('price') else 'N/A'
            discount_str = f"{product_info['discount']}%" if product_info.get('discount') else "0%"
            
            prompt = f"""Generate realistic product reviews in JSON format for an e-commerce product.

Product Information:
- Name: {product_info['name']}
- Brand: {product_info['brand']}
- Category: {product_info['category']}
- Description: {product_info['description']}
- Price: {price_str}
- Discount: {discount_str}

Generate exactly {min(len(product_data.user_ids), 5)} unique product reviews. Each review should:
1. Have a rating between 1-5 stars (mostly 4-5 stars, some 3 stars, few 1-2 stars)
2. Have a brief title (5-10 words)
3. Have a detailed comment (2-4 sentences) in English or Hinglish
4. Sound natural and authentic - mention specific product features, usage experience, value for money
5. Some should mention verified purchase
6. Be appropriate for an Indian e-commerce platform

Return ONLY valid JSON array with this exact structure (no markdown, no code blocks):
[
  {{
    "rating": 5,
    "title": "Excellent product!",
    "comment": "Great quality and fast delivery. Highly recommend!",
    "verified_purchase": true
  }},
  {{
    "rating": 4,
    "title": "Good value for money",
    "comment": "Product works well. Minor issues but overall satisfied.",
    "verified_purchase": false
  }}
]

Generate reviews now:"""

            # Use Gemini for JSON generation with JSON mode
            model_to_use = model_name or DEFAULT_GEMINI_MODEL
            model = genai.GenerativeModel(
                model_to_use,
                generation_config={
                    "temperature": 0.8,
                    "response_mime_type": "application/json",
                }
            )
            
            response = model.generate_content(prompt)
            
            if not response or not response.text:
                print(f"      ❌ No response for {product_data.name}")
                return []
            
            # Parse JSON response
            try:
                reviews_json = json.loads(response.text)
                
                # Ensure it's a list
                if not isinstance(reviews_json, list):
                    reviews_json = [reviews_json]
                
                # Generate reviews for available users
                generated_reviews = []
                num_reviews = min(len(product_data.user_ids), len(reviews_json), 5)
                
                for i in range(num_reviews):
                    review_data = reviews_json[i] if i < len(reviews_json) else {
                        "rating": 4,
                        "title": f"Review for {product_data.name}",
                        "comment": "Good product.",
                        "verified_purchase": False
                    }
                    
                    # Validate and create review
                    rating = max(1, min(5, int(review_data.get("rating", 4))))
                    title = review_data.get("title", "").strip()[:200]
                    comment = review_data.get("comment", "").strip()[:2000]
                    verified = bool(review_data.get("verified_purchase", False))
                    
                    # Use a user_id from the list
                    user_id = product_data.user_ids[i % len(product_data.user_ids)]
                    
                    generated_review = GeneratedReview(
                        product_id=product_data.product_id,
                        user_id=user_id,
                        rating=rating,
                        title=title if title else None,
                        comment=comment if comment else None,
                        verified_purchase=verified
                    )
                    
                    generated_reviews.append(generated_review)
                
                return generated_reviews
                
            except json.JSONDecodeError as e:
                print(f"      ❌ JSON parse error for {product_data.name}: {e}")
                print(f"      Response: {response.text[:200]}")
                return []
            
        except Exception as e:
            print(f"      ❌ Generation error for {product_data.name}: {e}")
            return []


def generate_all_reviews(products_data: List[ProductReviewData], model_name: str = None) -> List[GeneratedReview]:
    """Generate reviews for all products with parallel processing"""
    
    if not products_data:
        print("\n✅ No products to process")
        return []
    
    print(f"\n⭐ Generating reviews for {len(products_data)} products...")
    print(f"⚡ Concurrent requests: {MAX_CONCURRENT_REQUESTS}")
    print(f"🚀 Model: {model_name or DEFAULT_GEMINI_MODEL}")
    
    stats["start_time"] = time.time()
    
    generated_reviews = []
    failed_products = []
    
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_REQUESTS) as executor:
        futures = {
            executor.submit(generate_reviews_for_product, product, model_name): product 
            for product in products_data
        }
        
        for future in as_completed(futures):
            product_data = futures[future]
            
            try:
                reviews = future.result()
                
                if reviews:
                    generated_reviews.extend(reviews)
                    with progress_lock:
                        stats["reviews_generated"] += len(reviews)
                        stats["products_processed"] += 1
                else:
                    failed_products.append(product_data)
                    with progress_lock:
                        stats["failed"] += 1
                
                # Update progress
                elapsed = time.time() - stats["start_time"]
                rate = stats["reviews_generated"] / elapsed if elapsed > 0 else 0
                remaining = stats["total_products"] - stats["products_processed"] - stats["failed"]
                eta = remaining / rate if rate > 0 else 0
                
                print(f"⏳ Processed: {stats['products_processed']}/{stats['total_products']} products | "
                      f"Reviews: {stats['reviews_generated']} | "
                      f"Failed: {stats['failed']} | "
                      f"Rate: {rate:.2f} reviews/s | ETA: {eta/60:.1f}m", end='\r', flush=True)
                
            except Exception as e:
                failed_products.append(product_data)
                with progress_lock:
                    stats["failed"] += 1
                print(f"      ❌ Error: {e}")
    
    print()  # New line after progress
    
    if failed_products:
        print(f"\n⚠️  {len(failed_products)} products failed to generate reviews")
    
    return generated_reviews


def update_reviews_table(session_factory, generated_reviews: List[GeneratedReview]):
    """Update reviews table with generated reviews"""
    print(f"\n💾 Updating reviews table with {len(generated_reviews)} reviews...")
    
    session = session_factory()
    
    try:
        created_count = 0
        skipped_count = 0
        
        for review in generated_reviews:
            try:
                product_id = UUID(review.product_id)
                user_id = UUID(review.user_id)
                
                # Check if review already exists
                existing_review = session.query(Review).filter(
                    Review.user_id == user_id,
                    Review.product_id == product_id
                ).first()
                
                if existing_review:
                    skipped_count += 1
                    continue
                
                # Create review
                db_review = Review(
                    product_id=product_id,
                    user_id=user_id,
                    rating=review.rating,
                    title=review.title,
                    comment=review.comment,
                    verified_purchase=review.verified_purchase,
                    is_approved=True
                )
                
                session.add(db_review)
                created_count += 1
                
                # Commit in batches of 100
                if created_count % 100 == 0:
                    session.commit()
                    print(f"   💾 Committed {created_count}/{len(generated_reviews)} reviews...", 
                          end='\r', flush=True)
                
            except Exception as e:
                session.rollback()
                print(f"      ❌ DB error for review: {e}")
                continue
        
        # Final commit
        session.commit()
        stats["reviews_created"] = created_count
        
        print(f"\n   ✅ Created {created_count} reviews in database")
        if skipped_count > 0:
            print(f"   ⏭️  Skipped {skipped_count} reviews (already exist)")
        
        # Update product ratings
        print("\n📊 Updating product ratings...")
        session.commit()
        
        # Refresh all affected products to update ratings
        updated_products = set(review.product_id for review in generated_reviews)
        for product_id in updated_products:
            try:
                avg_rating = session.query(func.avg(Review.rating)).filter(
                    Review.product_id == product_id,
                    Review.is_approved == True
                ).scalar()
                
                product = session.query(Product).filter(Product.product_id == product_id).first()
                if product:
                    if avg_rating:
                        product.rating = round(float(avg_rating), 1)
                    else:
                        product.rating = 0.0
            except Exception as e:
                print(f"      ⚠️  Could not update rating for product {product_id}: {e}")
        
        session.commit()
        print(f"   ✅ Updated ratings for {len(updated_products)} products")
        
    except Exception as e:
        session.rollback()
        print(f"\n   ❌ Database update error: {e}")
        raise
    finally:
        session.close()


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate reviews from interactions using Gemini')
    parser.add_argument('--regenerate', action='store_true',
                       help='Regenerate reviews for products that already have reviews')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of products to process (for testing)')
    parser.add_argument('--skip-db', action='store_true',
                       help='Skip database update (for testing)')
    parser.add_argument('--model', type=str, default=None,
                       help=f'Gemini model to use (default: tries gemini-2.5-flash-lite, falls back to {DEFAULT_GEMINI_MODEL})')
    
    args = parser.parse_args()
    
    # Determine model to use - try gemini-2.5-flash-lite first if not specified
    if args.model:
        model_to_use = args.model
    else:
        # Try the preferred model (gemini-2.5-flash-lite), fallback to default
        try:
            # Test if PREFERRED_MODEL exists
            test = genai.GenerativeModel(PREFERRED_MODEL)
            model_to_use = PREFERRED_MODEL
            print(f"   ✅ Using {PREFERRED_MODEL}")
        except Exception:
            model_to_use = DEFAULT_GEMINI_MODEL
            print(f"   ⚠️  {PREFERRED_MODEL} not available, using {DEFAULT_GEMINI_MODEL}")
            print(f"   💡 Use --model flag to specify a different model")
    
    print("="*80)
    print("⭐ GEMINI REVIEW GENERATION FROM INTERACTIONS")
    print("="*80)
    print()
    print(f"Model: {model_to_use}")
    print(f"Rate Limit: 4k RPM (~{MAX_CONCURRENT_REQUESTS} concurrent)")
    print(f"Skip Existing: {not args.regenerate}")
    print()
    
    # Database setup
    engine = create_engine(settings.get_database_url())
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    try:
        # Step 1: Load products with interactions
        products_data = load_products_with_interactions(
            SessionLocal, 
            skip_existing=not args.regenerate
        )
        
        if args.limit:
            products_data = products_data[:args.limit]
            stats["total_products"] = len(products_data)
            print(f"   ℹ️  Limited to {args.limit} products for testing")
        
        if not products_data:
            print("\n✅ No products to process")
            return
        
        # Step 2: Generate reviews
        generated_reviews = generate_all_reviews(products_data, model_name=model_to_use)
        
        if not generated_reviews:
            print("\n⚠️  No reviews were generated")
            return
        
        # Step 3: Update database (if not skipped)
        if not args.skip_db:
            update_reviews_table(SessionLocal, generated_reviews)
        else:
            print("\n⚠️  Skipping database update (--skip-db flag)")
        
        # Final summary
        elapsed = time.time() - stats["start_time"] if stats["start_time"] else 0
        
        print("\n" + "="*80)
        print("✅ REVIEW GENERATION COMPLETE")
        print("="*80)
        print(f"📊 Results:")
        print(f"   - Products processed: {stats['products_processed']}")
        print(f"   - Reviews generated: {stats['reviews_generated']}")
        print(f"   - Reviews created in DB: {stats['reviews_created']}")
        print(f"   - Skipped (already had reviews): {stats['skipped']}")
        print(f"   - Failed: {stats['failed']}")
        if stats['products_processed'] > 0:
            success_rate = (stats['products_processed'] / stats['total_products'] * 100)
            print(f"   - Success rate: {success_rate:.1f}%")
        if elapsed > 0:
            print(f"   - Time elapsed: {elapsed/60:.1f} minutes")
            print(f"   - Average rate: {stats['reviews_generated']/elapsed:.2f} reviews/second")
        print()
        
        # Verify final count
        final_session = SessionLocal()
        try:
            final_count = final_session.query(Review).count()
            products_with_reviews = final_session.query(Product.product_id)\
                .join(Review, Product.product_id == Review.product_id)\
                .distinct().count()
            total_products = final_session.query(Product).count()
            
            print(f"📊 Final Database Status:")
            print(f"   - Total reviews: {final_count}")
            print(f"   - Products with reviews: {products_with_reviews}/{total_products}")
        finally:
            final_session.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
