#!/usr/bin/env python3
"""
Update product ratings when reviews are added/updated
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings

# Database setup
engine = create_engine(settings.get_database_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def update_product_ratings(product_id: str):
    """Update rating fields for a specific product"""
    with SessionLocal() as session:
        try:
            # Calculate rating statistics from reviews table
            rating_stats = session.execute(text("""
                SELECT 
                    COUNT(*) as total_reviews,
                    AVG(rating) as average_rating,
                    COUNT(CASE WHEN rating = 1 THEN 1 END) as rating_1,
                    COUNT(CASE WHEN rating = 2 THEN 1 END) as rating_2,
                    COUNT(CASE WHEN rating = 3 THEN 1 END) as rating_3,
                    COUNT(CASE WHEN rating = 4 THEN 1 END) as rating_4,
                    COUNT(CASE WHEN rating = 5 THEN 1 END) as rating_5
                FROM reviews 
                WHERE product_id = :product_id
            """), {'product_id': product_id}).fetchone()
            
            if rating_stats:
                total_reviews = rating_stats.total_reviews or 0
                average_rating = float(rating_stats.average_rating) if rating_stats.average_rating else 0.0
                
                # Create rating distribution JSON
                rating_distribution = {
                    "1": int(rating_stats.rating_1 or 0),
                    "2": int(rating_stats.rating_2 or 0),
                    "3": int(rating_stats.rating_3 or 0),
                    "4": int(rating_stats.rating_4 or 0),
                    "5": int(rating_stats.rating_5 or 0)
                }
                
                # Update product with rating data
                session.execute(text("""
                    UPDATE products 
                    SET 
                        average_rating = :average_rating,
                        total_reviews = :total_reviews,
                        rating_distribution = :rating_distribution,
                        updated_at = NOW()
                    WHERE product_id = :product_id
                """), {
                    'product_id': product_id,
                    'average_rating': average_rating,
                    'total_reviews': total_reviews,
                    'rating_distribution': str(rating_distribution).replace("'", '"')
                })
                
                session.commit()
                print(f"✅ Updated ratings for product {product_id}: {average_rating:.2f}/5.0 ({total_reviews} reviews)")
                return True
            else:
                print(f"⚠️  No reviews found for product {product_id}")
                return False
                
        except Exception as e:
            session.rollback()
            print(f"❌ Error updating ratings for product {product_id}: {str(e)}")
            return False

def update_all_product_ratings():
    """Update rating fields for all products"""
    print("🔄 Updating ratings for all products...")
    
    with SessionLocal() as session:
        try:
            # Get all products
            products = session.execute(text("""
                SELECT product_id FROM products
            """)).fetchall()
            
            updated_count = 0
            for product_row in products:
                product_id = product_row.product_id
                if update_product_ratings(str(product_id)):
                    updated_count += 1
                
                if updated_count % 100 == 0:
                    print(f"   Updated {updated_count} products...")
            
            print(f"✅ Updated ratings for {updated_count} products")
            
        except Exception as e:
            print(f"❌ Error updating all product ratings: {str(e)}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Update product ratings')
    parser.add_argument('--product-id', type=str, help='Update ratings for specific product ID')
    parser.add_argument('--all', action='store_true', help='Update ratings for all products')
    
    args = parser.parse_args()
    
    if args.product_id:
        update_product_ratings(args.product_id)
    elif args.all:
        update_all_product_ratings()
    else:
        print("Please specify --product-id <id> or --all")
