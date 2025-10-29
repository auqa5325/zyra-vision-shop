"""
AWS S3 service for image upload and management
"""

import boto3
import uuid
from typing import Optional, List, Dict, Any
from botocore.exceptions import ClientError
from app.config import settings


class S3Service:
    """AWS S3 service for image operations"""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key
        )
        self.bucket_name = settings.s3_bucket_name
    
    def upload_image(
        self, 
        file_content: bytes, 
        product_id: str, 
        variant: str = "original",
        content_type: str = "image/jpeg"
    ) -> Dict[str, Any]:
        """Upload image to S3"""
        try:
            # Generate unique filename
            file_extension = content_type.split('/')[-1]
            filename = f"{product_id}/{variant}_{uuid.uuid4().hex[:8]}.{file_extension}"
            s3_key = f"products/{filename}"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type
            )
            
            # Generate URL
            url = f"https://{self.bucket_name}.s3.{settings.aws_region}.amazonaws.com/{s3_key}"
            
            return {
                "s3_key": s3_key,
                "url": url,
                "bucket": self.bucket_name,
                "success": True
            }
            
        except ClientError as e:
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
        """Generate presigned URL for S3 object"""
        try:
            url = self.s3_client.generate_presigned_url(
                operation,
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None
    
    def delete_image(self, s3_key: str) -> bool:
        """Delete image from S3"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
        except ClientError as e:
            print(f"Error deleting image: {e}")
            return False
    
    def list_product_images(self, product_id: str) -> List[Dict[str, Any]]:
        """List all images for a product"""
        try:
            prefix = f"products/{product_id}/"
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            images = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    images.append({
                        "s3_key": obj['Key'],
                        "url": f"https://{self.bucket_name}.s3.{settings.aws_region}.amazonaws.com/{obj['Key']}",
                        "size": obj['Size'],
                        "last_modified": obj['LastModified']
                    })
            
            return images
            
        except ClientError as e:
            print(f"Error listing images: {e}")
            return []
    
    def get_image_url(self, s3_key: str) -> str:
        """Get public URL for S3 object"""
        return f"https://{self.bucket_name}.s3.{settings.aws_region}.amazonaws.com/{s3_key}"

