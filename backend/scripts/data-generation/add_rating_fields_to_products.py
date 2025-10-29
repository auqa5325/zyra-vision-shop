#!/usr/bin/env python3
"""
Add rating fields to products table
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

def add_rating_fields():
    """Add rating fields to products table"""
    print("🔧 Adding rating fields to products table...")
    
    with SessionLocal() as session:
        try:
            # Add average_rating column
            session.execute(text("""
                ALTER TABLE products 
                ADD COLUMN IF NOT EXISTS average_rating NUMERIC(3,2) DEFAULT 0
            """))
            print("✅ Added average_rating column")
            
            # Add total_reviews column
            session.execute(text("""
                ALTER TABLE products 
                ADD COLUMN IF NOT EXISTS total_reviews INTEGER DEFAULT 0 NOT NULL
            """))
            print("✅ Added total_reviews column")
            
            # Add rating_distribution column
            session.execute(text("""
                ALTER TABLE products 
                ADD COLUMN IF NOT EXISTS rating_distribution JSON
            """))
            print("✅ Added rating_distribution column")
            
            session.commit()
            print("✅ All rating fields added successfully!")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error adding rating fields: {str(e)}")
            raise

def update_rating_data():
    """Update rating data for existing products based on reviews"""
    print("\n📊 Updating rating data for existing products...")
    
    with SessionLocal() as session:
        try:
            # Get all products
            products = session.execute(text("""
                SELECT product_id FROM products
            """)).fetchall()
            
            updated_count = 0
            for product_row in products:
                product_id = product_row.product_id
                
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
                            rating_distribution = :rating_distribution
                        WHERE product_id = :product_id
                    """), {
                        'product_id': product_id,
                        'average_rating': average_rating,
                        'total_reviews': total_reviews,
                        'rating_distribution': str(rating_distribution).replace("'", '"')
                    })
                    
                    updated_count += 1
                    
                    if updated_count % 100 == 0:
                        print(f"   Updated {updated_count} products...")
            
            session.commit()
            print(f"✅ Updated rating data for {updated_count} products")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error updating rating data: {str(e)}")
            raise

def verify_rating_fields():
    """Verify the rating fields were added correctly"""
    print("\n🔍 Verifying rating fields...")
    
    with SessionLocal() as session:
        try:
            # Check if columns exist
            columns = session.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'products' 
                AND column_name IN ('average_rating', 'total_reviews', 'rating_distribution')
                ORDER BY column_name
            """)).fetchall()
            
            print("📋 Rating fields in products table:")
            for col in columns:
                print(f"  - {col.column_name}: {col.data_type} (nullable: {col.is_nullable}, default: {col.column_default})")
            
            # Check sample data
            sample = session.execute(text("""
                SELECT 
                    product_id, 
                    name, 
                    average_rating, 
                    total_reviews,
                    rating_distribution
                FROM products 
                WHERE total_reviews > 0
                ORDER BY total_reviews DESC
                LIMIT 5
            """)).fetchall()
            
            if sample:
                print("\n📊 Sample products with ratings:")
                for row in sample:
                    print(f"  - {row.name[:30]}...")
                    print(f"    Rating: {row.average_rating}/5.0 ({row.total_reviews} reviews)")
                    print(f"    Distribution: {row.rating_distribution}")
            else:
                print("\n📊 No products with reviews found")
            
            # Get overall statistics
            stats = session.execute(text("""
                SELECT 
                    COUNT(*) as total_products,
                    COUNT(CASE WHEN total_reviews > 0 THEN 1 END) as products_with_reviews,
                    AVG(average_rating) as avg_rating_across_products,
                    MAX(total_reviews) as max_reviews
                FROM products
            """)).fetchone()
            
            print(f"\n📈 Overall statistics:")
            print(f"  - Total products: {stats.total_products}")
            print(f"  - Products with reviews: {stats.products_with_reviews}")
            print(f"  - Average rating across products: {float(stats.avg_rating_across_products or 0):.2f}")
            print(f"  - Max reviews for a product: {stats.max_reviews}")
            
        except Exception as e:
            print(f"❌ Error verifying rating fields: {str(e)}")

if __name__ == "__main__":
    add_rating_fields()
    update_rating_data()
    verify_rating_fields()
    print("\n✅ Rating fields migration completed!")
