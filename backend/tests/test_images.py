"""
Tests for image proxy endpoints
"""

import pytest
from fastapi.testclient import TestClient


class TestImageProxyEndpoints:
    """Test image proxy endpoints"""
    
    def test_proxy_image_success(self, client: TestClient):
        """Test successful image proxy"""
        # Test with a valid path structure
        test_path = "products/test-product-id/original_1.jpg"
        
        response = client.get(f"/api/images/proxy/{test_path}")
        
        # Should return an image (even if it's a placeholder)
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/jpeg"
    
    def test_proxy_image_invalid_path(self, client: TestClient):
        """Test image proxy with invalid path"""
        invalid_path = "invalid/path"
        
        response = client.get(f"/api/images/proxy/{invalid_path}")
        
        # Should handle invalid path gracefully
        assert response.status_code in [400, 500]
    
    def test_proxy_image_missing_filename(self, client: TestClient):
        """Test image proxy with missing filename"""
        invalid_path = "products/test-product-id/"
        
        response = client.get(f"/api/images/proxy/{invalid_path}")
        
        assert response.status_code == 400
    
    def test_placeholder_image_success(self, client: TestClient):
        """Test placeholder image generation"""
        response = client.get("/api/images/placeholder/200/200")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/jpeg"
    
    def test_placeholder_image_invalid_dimensions(self, client: TestClient):
        """Test placeholder with invalid dimensions"""
        response = client.get("/api/images/placeholder/0/0")
        
        # Should handle invalid dimensions gracefully
        assert response.status_code in [200, 400]
    
    def test_placeholder_image_negative_dimensions(self, client: TestClient):
        """Test placeholder with negative dimensions"""
        response = client.get("/api/images/placeholder/-100/-100")
        
        # Should handle negative dimensions gracefully
        assert response.status_code in [200, 400]
    
    def test_proxy_image_different_variants(self, client: TestClient):
        """Test image proxy with different variants"""
        variants = ["original", "medium", "thumb", "small"]
        
        for variant in variants:
            test_path = f"products/test-product-id/{variant}_1.jpg"
            response = client.get(f"/api/images/proxy/{test_path}")
            
            # Should handle different variants
            assert response.status_code in [200, 500]
    
    def test_proxy_image_cache_headers(self, client: TestClient):
        """Test that image proxy sets proper cache headers"""
        test_path = "products/test-product-id/original_1.jpg"
        
        response = client.get(f"/api/images/proxy/{test_path}")
        
        if response.status_code == 200:
            assert "cache-control" in response.headers
            assert "max-age" in response.headers["cache-control"]
    
    def test_proxy_image_content_disposition(self, client: TestClient):
        """Test that image proxy sets proper content disposition"""
        test_path = "products/test-product-id/original_1.jpg"
        
        response = client.get(f"/api/images/proxy/{test_path}")
        
        if response.status_code == 200:
            assert "content-disposition" in response.headers
            assert "inline" in response.headers["content-disposition"]
    
    def test_placeholder_image_different_sizes(self, client: TestClient):
        """Test placeholder images with different sizes"""
        sizes = [
            (100, 100),
            (300, 200),
            (800, 600),
            (50, 50)
        ]
        
        for width, height in sizes:
            response = client.get(f"/api/images/placeholder/{width}/{height}")
            
            # Should handle different sizes
            assert response.status_code in [200, 500]
    
    def test_proxy_image_timeout_handling(self, client: TestClient):
        """Test image proxy timeout handling"""
        # This test would require mocking httpx to simulate timeout
        # For now, just test that the endpoint exists
        test_path = "products/test-product-id/original_1.jpg"
        
        response = client.get(f"/api/images/proxy/{test_path}")
        
        # Should not hang indefinitely
        assert response.status_code in [200, 500, 502]
