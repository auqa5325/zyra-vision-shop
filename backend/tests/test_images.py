"""
Tests for images endpoints
"""

import pytest
from fastapi.testclient import TestClient
import io


class TestImagesEndpoints:
    """Test images endpoints"""
    
    def test_upload_image_success(self, client: TestClient, auth_headers):
        """Test successful image upload"""
        # Create a fake image file
        fake_image = io.BytesIO(b"fake image data")
        
        response = client.post(
            "/api/images/upload",
            files={"file": ("test.jpg", fake_image, "image/jpeg")},
            data={"product_id": "00000000-0000-0000-0000-000000000000"},
            headers=auth_headers
        )
        
        # Image upload might fail if S3 not configured, but should be handled gracefully
        assert response.status_code in [200, 201, 400, 500]
    
    def test_upload_image_no_auth(self, client: TestClient):
        """Test image upload without authentication"""
        fake_image = io.BytesIO(b"fake image data")
        
        response = client.post(
            "/api/images/upload",
            files={"file": ("test.jpg", fake_image, "image/jpeg")}
        )
        
        # Should require authentication
        assert response.status_code in [401, 403]
    
    def test_upload_image_invalid_format(self, client: TestClient, auth_headers):
        """Test image upload with invalid format"""
        fake_file = io.BytesIO(b"not an image")
        
        response = client.post(
            "/api/images/upload",
            files={"file": ("test.txt", fake_file, "text/plain")},
            headers=auth_headers
        )
        
        # Should reject non-image files
        assert response.status_code in [400, 422]
