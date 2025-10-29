#!/usr/bin/env python3
"""
Monitor Complete Generation Progress
"""

import os
import sys
import time
from datetime import datetime

# Add the parent directory to the path so we can import our app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.product import Product, ProductImage, Category
from app.config import settings

def monitor_complete_generation():
    """Monitor complete generation progress"""
    engine = create_engine(settings.get_database_url())
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    print("🔄 Complete Generation Monitor")
    print("=" * 50)
    
    target_products = 520
    last_product_count = 0
    last_image_count = 0
    start_time = time.time()
    
    while True:
        try:
            with SessionLocal() as session:
                current_products = session.query(Product).count()
                current_images = session.query(ProductImage).count()
                categories_count = session.query(Category).count()
                
                current_time = datetime.now().strftime("%H:%M:%S")
                
                # Calculate rates
                product_rate = current_products - last_product_count
                image_rate = current_images - last_image_count
                last_product_count = current_products
                last_image_count = current_images
                
                # Calculate progress
                product_progress = (current_products / target_products * 100) if target_products > 0 else 0
                image_progress = (current_images / current_products * 100) if current_products > 0 else 0
                
                # Phase detection
                if current_products < target_products:
                    phase = "📦 Product Generation"
                    eta_str = f"ETA: {((target_products - current_products) / max(product_rate, 1)) / 60:.1f}m" if product_rate > 0 else "ETA: Unknown"
                else:
                    phase = "🖼️ Image Generation"
                    remaining_images = current_products - current_images
                    eta_str = f"ETA: {(remaining_images / max(image_rate, 1)) / 60:.1f}m" if image_rate > 0 else "ETA: Unknown"
                
                print(f"[{current_time}] {phase}")
                print(f"   Products: {current_products}/{target_products} ({product_progress:.1f}%) | Rate: {product_rate}/min")
                print(f"   Images: {current_images}/{current_products} ({image_progress:.1f}%) | Rate: {image_rate}/min")
                print(f"   Categories: {categories_count} | {eta_str}")
                print()
                
                # Check if complete
                if current_products >= target_products and current_images >= current_products:
                    elapsed = time.time() - start_time
                    print("=" * 50)
                    print("🎉 Generation Complete!")
                    print(f"⏱️  Total time: {elapsed/60:.1f} minutes")
                    print(f"📦 Products: {current_products}")
                    print(f"🖼️ Images: {current_images}")
                    print(f"📁 Categories: {categories_count}")
                    break
            
            time.sleep(30)  # Update every 30 seconds
            
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    monitor_complete_generation()

