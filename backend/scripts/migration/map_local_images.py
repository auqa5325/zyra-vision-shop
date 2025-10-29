#!/usr/bin/env python3
"""
Map local images to products and update database
"""

import os
import sys
import shutil
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.models import Product, ProductImage

# Database setup
engine = create_engine(settings.get_database_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_local_images():
    """Get all local images with their filenames"""
    local_images_dir = Path("local_images")
    if not local_images_dir.exists():
        print("❌ local_images directory not found")
        return []
    
    images = []
    for file_path in local_images_dir.glob("*.jpg"):
        images.append({
            'filename': file_path.name,
            'path': str(file_path),
            'product_name': file_path.stem.split('_')[0] if '_' in file_path.stem else file_path.stem
        })
    
    print(f"Found {len(images)} local images")
    return images

def find_matching_products(images, session):
    """Find products that match the image names"""
    matches = []
    
    for image in images:
        # Try to find product by name similarity
        product_name = image['product_name']
        
        # Query products with similar names
        result = session.execute(text("""
            SELECT product_id, name, sku
            FROM products 
            WHERE LOWER(name) LIKE LOWER(:pattern)
            OR LOWER(name) LIKE LOWER(:pattern2)
            OR LOWER(name) LIKE LOWER(:pattern3)
            LIMIT 1
        """), {
            'pattern': f'%{product_name}%',
            'pattern2': f'%{product_name.split()[0]}%' if ' ' in product_name else f'%{product_name}%',
            'pattern3': f'%{product_name.split()[-1]}%' if ' ' in product_name else f'%{product_name}%'
        })
        
        row = result.fetchone()
        if row:
            matches.append({
                'image': image,
                'product_id': row.product_id,
                'product_name': row.name,
                'sku': row.sku
            })
    
    return matches

def copy_image_to_uploads(image_path, product_id, filename):
    """Copy image to uploads directory structure"""
    uploads_dir = Path("uploads/products") / str(product_id)
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    dest_path = uploads_dir / filename
    
    try:
        shutil.copy2(image_path, dest_path)
        return str(dest_path)
    except Exception as e:
        print(f"❌ Error copying {image_path} to {dest_path}: {e}")
        return None

def update_product_images(matches, session):
    """Update product_images table with local images"""
    updated_count = 0
    
    for match in matches:
        image = match['image']
        product_id = match['product_id']
        
        # Copy image to uploads directory
        upload_path = copy_image_to_uploads(
            image['path'], 
            product_id, 
            image['filename']
        )
        
        if upload_path:
            # Check if product_image already exists
            existing = session.execute(text("""
                SELECT image_id FROM product_images 
                WHERE product_id = :product_id AND is_primary = true
            """), {'product_id': product_id}).fetchone()
            
            if existing:
                # Update existing record
                session.execute(text("""
                    UPDATE product_images 
                    SET s3_key = :s3_key, 
                        cdn_url = :cdn_url
                    WHERE product_id = :product_id AND is_primary = true
                """), {
                    'product_id': product_id,
                    's3_key': f"local_images/{image['filename']}",
                    'cdn_url': f"/Users/vijaygk/Documents/spm/zyra-vision-shop/backend/local_images/{image['filename']}"
                })
            else:
                # Insert new record
                session.execute(text("""
                    INSERT INTO product_images 
                    (product_id, s3_key, cdn_url, is_primary)
                    VALUES (:product_id, :s3_key, :cdn_url, true)
                """), {
                    'product_id': product_id,
                    's3_key': f"local_images/{image['filename']}",
                    'cdn_url': f"/Users/vijaygk/Documents/spm/zyra-vision-shop/backend/local_images/{image['filename']}"
                })
            
            updated_count += 1
            print(f"✅ Mapped: {image['product_name']} -> {match['product_name']}")
    
    session.commit()
    return updated_count

def main():
    """Main function"""
    print("🖼️  MAPPING LOCAL IMAGES TO PRODUCTS")
    print("=" * 50)
    
    # Get local images
    images = get_local_images()
    if not images:
        return
    
    # Find matching products
    with SessionLocal() as session:
        print("🔍 Finding product matches...")
        matches = find_matching_products(images, session)
        print(f"Found {len(matches)} matches out of {len(images)} images")
        
        if matches:
            print("\n📝 Updating database...")
            updated_count = update_product_images(matches, session)
            print(f"\n✅ Successfully mapped {updated_count} images to products")
            
            # Show some examples
            print("\n📋 Sample mappings:")
            for i, match in enumerate(matches[:5]):
                print(f"  {i+1}. {match['image']['product_name']} -> {match['product_name']}")
        else:
            print("❌ No matches found")
    
    print("\n🎉 Image mapping completed!")

if __name__ == "__main__":
    main()
