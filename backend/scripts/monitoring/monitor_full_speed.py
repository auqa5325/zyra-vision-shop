#!/usr/bin/env python3
"""
Monitor Full Speed Image Generation Progress
Shows real-time progress with 499 RPM optimization
"""

import os
import sys
import time
from datetime import datetime
from sqlalchemy import create_engine, func, distinct
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the path so we can import our app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.product import Product, ProductImage
from app.config import settings

# Database setup
engine = create_engine(settings.get_database_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def print_status(message: str, level: int = 0):
    """Print status message with indentation and timestamp"""
    indent = "  " * level
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {indent}{message}")

def monitor_progress():
    """Monitor image generation progress with 499 RPM optimization"""
    print_status("📊 FULL SPEED IMAGE GENERATION MONITOR (499 RPM)", 0)
    print_status("=" * 60, 0)
    
    start_time = time.time()
    last_count = 0
    
    while True:
        try:
            with SessionLocal() as session:
                total_products = session.query(Product).count()
                total_images = session.query(ProductImage).count()
                products_with_images = session.query(func.count(distinct(ProductImage.product_id))).scalar()
                products_without_images = total_products - products_with_images
                
                # Calculate progress
                progress = (products_with_images / total_products) * 100 if total_products > 0 else 0
                
                # Calculate rate
                current_time = time.time()
                elapsed = current_time - start_time
                rate = (products_with_images - last_count) / 10 if elapsed > 0 else 0  # Rate per 10 seconds
                
                # Calculate ETA
                if rate > 0 and products_without_images > 0:
                    eta_seconds = products_without_images / rate
                    eta_minutes = eta_seconds / 60
                else:
                    eta_minutes = 0
                
                # Clear screen and show progress
                os.system('clear' if os.name == 'posix' else 'cls')
                
                print_status("📊 FULL SPEED IMAGE GENERATION MONITOR (499 RPM)", 0)
                print_status("=" * 60, 0)
                print_status(f"Total Products: {total_products}", 1)
                print_status(f"Products with Images: {products_with_images}", 1)
                print_status(f"Products Remaining: {products_without_images}", 1)
                print_status(f"Progress: {progress:.1f}%", 1)
                print_status(f"Rate: {rate:.1f} images/10sec", 1)
                print_status(f"ETA: {eta_minutes:.1f} minutes", 1)
                print_status(f"Elapsed: {elapsed/60:.1f} minutes", 1)
                
                # Progress bar
                bar_length = 50
                filled_length = int(bar_length * progress / 100)
                bar = '█' * filled_length + '░' * (bar_length - filled_length)
                print_status(f"Progress: [{bar}] {progress:.1f}%", 1)
                
                # Show recent images
                if products_with_images > 0:
                    recent_images = session.query(ProductImage).order_by(ProductImage.created_at.desc()).limit(3).all()
                    print_status("Recent Images:", 1)
                    for img in recent_images:
                        print_status(f"  • {img.s3_key}", 2)
                
                if products_without_images == 0:
                    print_status("🎉 ALL IMAGES GENERATED SUCCESSFULLY!", 1)
                    break
                
                last_count = products_with_images
                
        except Exception as e:
            print_status(f"❌ Error monitoring progress: {str(e)}", 1)
        
        time.sleep(10)  # Update every 10 seconds

if __name__ == "__main__":
    try:
        monitor_progress()
    except KeyboardInterrupt:
        print_status("\\n👋 Monitoring stopped by user", 0)

