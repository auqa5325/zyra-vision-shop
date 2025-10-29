"""
Hybrid Storage Service - Uses S3 if available, falls back to local storage
"""

from typing import Dict, Any, Optional, List
from app.config import settings
from app.services.s3_service import S3Service
from app.services.local_storage import LocalStorageService


class HybridStorageService:
    """Hybrid storage service that uses S3 if available, otherwise local storage"""
    
    def __init__(self):
        self.use_s3 = self._check_s3_availability()
        
        if self.use_s3:
            print("✅ Using AWS S3 for image storage")
            self.storage_service = S3Service()
        else:
            print("📁 Using local file storage for images")
            self.storage_service = LocalStorageService()
    
    def _check_s3_availability(self) -> bool:
        """Check if S3 is available and configured"""
        try:
            # Check if AWS credentials are provided
            if not settings.aws_access_key_id or not settings.aws_secret_access_key:
                return False
            
            # Check if bucket name is provided
            if not settings.s3_bucket_name:
                return False
            
            # Try to create S3 client (this will fail if credentials are invalid)
            import boto3
            s3_client = boto3.client(
                's3',
                region_name=settings.aws_region,
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key
            )
            
            # Try to access the bucket
            s3_client.head_bucket(Bucket=settings.s3_bucket_name)
            return True
            
        except Exception as e:
            print(f"⚠️  S3 not available, falling back to local storage: {e}")
            return False
    
    def upload_image(
        self, 
        file_content: bytes, 
        product_id: str, 
        variant: str = "original",
        content_type: str = "image/jpeg"
    ) -> Dict[str, Any]:
        """Upload image using available storage service"""
        return self.storage_service.upload_image(
            file_content, product_id, variant, content_type
        )
    
    def generate_presigned_url(
        self, 
        s3_key: str, 
        expiration: int = 3600,
        operation: str = "get_object"
    ) -> Optional[str]:
        """Generate URL using available storage service"""
        return self.storage_service.generate_presigned_url(
            s3_key, expiration, operation
        )
    
    def delete_image(self, s3_key: str) -> bool:
        """Delete image using available storage service"""
        return self.storage_service.delete_image(s3_key)
    
    def list_product_images(self, product_id: str) -> List[Dict[str, Any]]:
        """List product images using available storage service"""
        return self.storage_service.list_product_images(product_id)
    
    def get_image_url(self, s3_key: str) -> str:
        """Get image URL using available storage service"""
        return self.storage_service.get_image_url(s3_key)
    
    def get_storage_type(self) -> str:
        """Get the current storage type being used"""
        return "s3" if self.use_s3 else "local"
