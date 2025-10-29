"""
Local File Storage Service (Alternative to S3)
"""

import os
import uuid
import shutil
from typing import Optional, List, Dict, Any
from pathlib import Path
from app.config import settings


class LocalStorageService:
    """Local file storage service for image operations"""
    
    def __init__(self):
        self.base_path = Path("uploads")
        self.products_path = self.base_path / "products"
        self.base_url = "http://localhost:8000/static/uploads"
        
        # Create directories if they don't exist
        self.products_path.mkdir(parents=True, exist_ok=True)
    
    def upload_image(
        self, 
        file_content: bytes, 
        product_id: str, 
        variant: str = "original",
        content_type: str = "image/jpeg"
    ) -> Dict[str, Any]:
        """Upload image to local storage"""
        try:
            # Generate unique filename
            file_extension = content_type.split('/')[-1]
            filename = f"{variant}_{uuid.uuid4().hex[:8]}.{file_extension}"
            
            # Create product directory
            product_dir = self.products_path / product_id
            product_dir.mkdir(exist_ok=True)
            
            # Save file
            file_path = product_dir / filename
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # Generate URL
            relative_path = f"products/{product_id}/{filename}"
            url = f"{self.base_url}/{relative_path}"
            
            return {
                "s3_key": relative_path,  # Keep same format for compatibility
                "url": url,
                "bucket": "local-storage",
                "local_path": str(file_path),
                "success": True
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }
    
    def generate_presigned_url(
        self, 
        s3_key: str, 
        expiration: int = 3600,
        operation: str = "get_object"
    ) -> Optional[str]:
        """Generate URL for local file (no expiration needed)"""
        try:
            # Convert s3_key to local URL
            url = f"{self.base_url}/{s3_key}"
            return url
        except Exception as e:
            print(f"Error generating URL: {e}")
            return None
    
    def delete_image(self, s3_key: str) -> bool:
        """Delete image from local storage"""
        try:
            file_path = self.base_path / s3_key
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting image: {e}")
            return False
    
    def list_product_images(self, product_id: str) -> List[Dict[str, Any]]:
        """List all images for a product"""
        try:
            product_dir = self.products_path / product_id
            images = []
            
            if product_dir.exists():
                for file_path in product_dir.iterdir():
                    if file_path.is_file():
                        relative_path = f"products/{product_id}/{file_path.name}"
                        images.append({
                            "s3_key": relative_path,
                            "url": f"{self.base_url}/{relative_path}",
                            "size": file_path.stat().st_size,
                            "last_modified": file_path.stat().st_mtime
                        })
            
            return images
            
        except Exception as e:
            print(f"Error listing images: {e}")
            return []
    
    def get_image_url(self, s3_key: str) -> str:
        """Get public URL for local file"""
        return f"{self.base_url}/{s3_key}"
    
    def cleanup_old_files(self, days_old: int = 30):
        """Clean up old files (optional maintenance)"""
        try:
            import time
            current_time = time.time()
            cutoff_time = current_time - (days_old * 24 * 60 * 60)
            
            for file_path in self.base_path.rglob("*"):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    print(f"Deleted old file: {file_path}")
                    
        except Exception as e:
            print(f"Error during cleanup: {e}")
