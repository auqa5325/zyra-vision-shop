#!/usr/bin/env python3
"""
Migration script to upload all local images to S3 and update database URLs
"""

import os
import sys
import uuid
from pathlib import Path
from typing import List, Dict, Any
from sqlalchemy.orm import Session

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.product import ProductImage
from app.services.hybrid_storage import HybridStorageService
from app.config import settings


class LocalToS3Migrator:
    """Migrates local images to S3 and updates database URLs"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.storage_service = HybridStorageService()
        self.uploads_dir = Path("uploads/products")
        self.stats = {
            'total_images': 0,
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }
    
    def get_local_images(self) -> List[ProductImage]:
        """Get all images that are currently using local URLs"""
        return self.db.query(ProductImage).filter(
            ProductImage.cdn_url.like('http://localhost%')
        ).all()
    
    def extract_local_file_path(self, image: ProductImage) -> Path:
        """Extract the local file path from the S3 key"""
        # S3 key format: local_images/filename.jpg
        # Local path format: uploads/products/product_id/filename.jpg
        
        filename = image.s3_key.replace('local_images/', '')
        
        # Try to find the file in the uploads directory
        # Look for files matching the filename pattern
        for product_dir in self.uploads_dir.iterdir():
            if product_dir.is_dir():
                for file_path in product_dir.iterdir():
                    if file_path.is_file() and file_path.name == filename:
                        return file_path
        
        # If not found, try to construct path from product_id
        product_id = str(image.product_id)
        potential_path = self.uploads_dir / product_id / filename
        if potential_path.exists():
            return potential_path
            
        return None
    
    def upload_image_to_s3(self, image: ProductImage, local_file_path: Path) -> Dict[str, Any]:
        """Upload a single image to S3"""
        try:
            # Read the file
            with open(local_file_path, 'rb') as f:
                file_content = f.read()
            
            # Determine content type
            content_type = f"image/{local_file_path.suffix[1:].lower()}"
            if content_type == "image/jpg":
                content_type = "image/jpeg"
            
            # Upload to S3
            result = self.storage_service.upload_image(
                file_content=file_content,
                product_id=str(image.product_id),
                variant=image.variant or "original",
                content_type=content_type
            )
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_database_url(self, image: ProductImage, s3_result: Dict[str, Any]):
        """Update the database with new S3 URL"""
        try:
            image.s3_key = s3_result["s3_key"]
            image.cdn_url = s3_result["url"]
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e
    
    def migrate_image(self, image: ProductImage) -> bool:
        """Migrate a single image from local to S3"""
        try:
            # Find the local file
            local_file_path = self.extract_local_file_path(image)
            if not local_file_path or not local_file_path.exists():
                self.stats['skipped'] += 1
                self.stats['errors'].append(f"File not found for image {image.image_id}: {image.s3_key}")
                return False
            
            # Upload to S3
            s3_result = self.upload_image_to_s3(image, local_file_path)
            if not s3_result.get("success"):
                self.stats['failed'] += 1
                self.stats['errors'].append(f"Upload failed for image {image.image_id}: {s3_result.get('error')}")
                return False
            
            # Update database
            self.update_database_url(image, s3_result)
            
            self.stats['successful'] += 1
            return True
            
        except Exception as e:
            self.stats['failed'] += 1
            self.stats['errors'].append(f"Migration failed for image {image.image_id}: {str(e)}")
            return False
    
    def run_migration(self, dry_run: bool = False, limit: int = None):
        """Run the complete migration"""
        print("🚀 Starting Local to S3 Migration")
        print(f"📁 Uploads directory: {self.uploads_dir.absolute()}")
        print(f"🪣 S3 Bucket: {settings.s3_bucket_name}")
        print(f"🌍 AWS Region: {settings.aws_region}")
        
        if dry_run:
            print("🔍 DRY RUN MODE - No actual changes will be made")
        
        # Get all local images
        local_images = self.get_local_images()
        self.stats['total_images'] = len(local_images)
        
        if limit:
            local_images = local_images[:limit]
            print(f"📊 Processing {len(local_images)} images (limited to {limit})")
        else:
            print(f"📊 Found {len(local_images)} images to migrate")
        
        if not local_images:
            print("✅ No local images found to migrate")
            return
        
        # Process each image
        for i, image in enumerate(local_images, 1):
            print(f"\n📸 Processing image {i}/{len(local_images)}: {image.image_id}")
            print(f"   Current URL: {image.cdn_url}")
            print(f"   S3 Key: {image.s3_key}")
            
            if dry_run:
                # In dry run, just check if file exists
                local_file_path = self.extract_local_file_path(image)
                if local_file_path and local_file_path.exists():
                    print(f"   ✅ File found: {local_file_path}")
                    self.stats['successful'] += 1
                else:
                    print(f"   ❌ File not found")
                    self.stats['failed'] += 1
            else:
                success = self.migrate_image(image)
                if success:
                    print(f"   ✅ Successfully migrated to S3")
                else:
                    print(f"   ❌ Migration failed")
            
            self.stats['processed'] += 1
            
            # Progress update every 10 images
            if i % 10 == 0:
                print(f"\n📈 Progress: {i}/{len(local_images)} processed")
                print(f"   ✅ Successful: {self.stats['successful']}")
                print(f"   ❌ Failed: {self.stats['failed']}")
                print(f"   ⏭️  Skipped: {self.stats['skipped']}")
        
        # Final statistics
        print(f"\n🎉 Migration completed!")
        print(f"📊 Final Statistics:")
        print(f"   Total images: {self.stats['total_images']}")
        print(f"   Processed: {self.stats['processed']}")
        print(f"   Successful: {self.stats['successful']}")
        print(f"   Failed: {self.stats['failed']}")
        print(f"   Skipped: {self.stats['skipped']}")
        
        if self.stats['errors']:
            print(f"\n❌ Errors encountered:")
            for error in self.stats['errors'][:10]:  # Show first 10 errors
                print(f"   - {error}")
            if len(self.stats['errors']) > 10:
                print(f"   ... and {len(self.stats['errors']) - 10} more errors")
    
    def cleanup(self):
        """Clean up resources"""
        self.db.close()


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate local images to S3')
    parser.add_argument('--dry-run', action='store_true', help='Run in dry-run mode (no actual changes)')
    parser.add_argument('--limit', type=int, help='Limit number of images to process (for testing)')
    
    args = parser.parse_args()
    
    migrator = LocalToS3Migrator()
    try:
        migrator.run_migration(dry_run=args.dry_run, limit=args.limit)
    finally:
        migrator.cleanup()


if __name__ == "__main__":
    main()
