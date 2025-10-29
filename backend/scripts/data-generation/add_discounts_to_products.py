#!/usr/bin/env python3
"""
Add discounts to existing products
"""

import sys
import os
import random
from decimal import Decimal
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings

# Database setup
engine = create_engine(settings.get_database_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def add_discounts_to_products():
    """Add discounts to existing products"""
    print("🛍️ Adding discounts to existing products...")
    
    with SessionLocal() as session:
        try:
            # Get all products without discounts
            products = session.execute(text("""
                SELECT product_id, name, price, category_id
                FROM products 
                WHERE discount_percent = 0 OR discount_percent IS NULL
                ORDER BY RANDOM()
            """)).fetchall()
            
            print(f"Found {len(products)} products without discounts")
            
            updated_count = 0
            for product in products:
                product_id = product.product_id
                price = float(product.price) if product.price else 0
                
                # 30% chance of getting a discount
                if random.random() < 0.3:
                    # Higher discount for higher prices
                    if price > 50000:
                        discount_percent = random.randint(10, 30)  # 10-30% for expensive items
                    elif price > 20000:
                        discount_percent = random.randint(15, 40)  # 15-40% for mid-range items
                    else:
                        discount_percent = random.randint(20, 50)  # 20-50% for cheaper items
                    
                    # Update product with discount
                    session.execute(text("""
                        UPDATE products 
                        SET discount_percent = :discount_percent
                        WHERE product_id = :product_id
                    """), {
                        'product_id': product_id,
                        'discount_percent': discount_percent
                    })
                    
                    updated_count += 1
                    
                    if updated_count % 100 == 0:
                        print(f"   Updated {updated_count} products...")
            
            session.commit()
            print(f"✅ Added discounts to {updated_count} products")
            
            # Verify the results
            result = session.execute(text("""
                SELECT 
                    COUNT(*) as total_products,
                    COUNT(CASE WHEN discount_percent > 0 THEN 1 END) as products_with_discount,
                    MIN(discount_percent) as min_discount,
                    MAX(discount_percent) as max_discount,
                    AVG(discount_percent) as avg_discount
                FROM products
            """)).fetchone()
            
            print(f"\n📊 Updated Discount Statistics:")
            print(f"  Total products: {result.total_products}")
            print(f"  Products with discount: {result.products_with_discount}")
            print(f"  Min discount: {result.min_discount}%")
            print(f"  Max discount: {result.max_discount}%")
            print(f"  Avg discount: {float(result.avg_discount or 0):.2f}%")
            
            # Show some examples
            examples = session.execute(text("""
                SELECT name, price, discount_percent
                FROM products 
                WHERE discount_percent > 0
                ORDER BY discount_percent DESC
                LIMIT 5
            """)).fetchall()
            
            print(f"\n📋 Examples with discounts:")
            for name, price, discount in examples:
                discounted_price = float(price) * (1 - float(discount) / 100)
                print(f"  - {name[:40]}...")
                print(f"    Original: ₹{price}, Discount: {discount}%, Final: ₹{discounted_price:.0f}")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error adding discounts: {str(e)}")
            raise

if __name__ == "__main__":
    add_discounts_to_products()
