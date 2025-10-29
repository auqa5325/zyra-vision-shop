"""
Tests for recommendations endpoints
"""

import pytest
from fastapi.testclient import TestClient


class TestRecommendationsEndpoints:
    """Test recommendations endpoints"""
    
    def test_get_recommendations_success(self, client: TestClient, auth_headers, sample_products):
        """Test getting recommendations"""
        response = client.get("/api/recommendations", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should return recommendations even if empty
    
    def test_get_recommendations_with_params(self, client: TestClient, auth_headers):
        """Test getting recommendations with parameters"""
        params = {
            "top_k": 5,
            "alpha": 0.7
        }
        
        response = client.get("/api/recommendations", params=params, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_recommendations_no_auth(self, client: TestClient):
        """Test getting recommendations without authentication"""
        response = client.get("/api/recommendations")
        
        assert response.status_code == 401
    
    def test_get_recommendations_for_product(self, client: TestClient, auth_headers, sample_products):
        """Test getting recommendations for a specific product"""
        if sample_products:
            product_id = sample_products[0]["product_id"]
            response = client.get(f"/api/recommendations/product/{product_id}", headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_get_recommendations_for_product_not_found(self, client: TestClient, auth_headers):
        """Test getting recommendations for non-existent product"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/recommendations/product/{fake_id}", headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_get_recommendations_with_query(self, client: TestClient, auth_headers):
        """Test getting recommendations with search query"""
        params = {
            "query": "electronics",
            "top_k": 3
        }
        
        response = client.get("/api/recommendations/search", params=params, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_recommendations_empty_query(self, client: TestClient, auth_headers):
        """Test getting recommendations with empty query"""
        params = {"query": ""}
        
        response = client.get("/api/recommendations/search", params=params, headers=auth_headers)
        
        # Should handle empty query gracefully
        assert response.status_code in [200, 400]
    
    def test_get_recommendations_invalid_params(self, client: TestClient, auth_headers):
        """Test getting recommendations with invalid parameters"""
        params = {
            "top_k": -1,  # Invalid negative value
            "alpha": 2.0  # Invalid alpha > 1
        }
        
        response = client.get("/api/recommendations", params=params, headers=auth_headers)
        
        # Should handle invalid params gracefully
        assert response.status_code in [200, 422]
    
    def test_get_recommendations_trending(self, client: TestClient, auth_headers):
        """Test getting trending recommendations"""
        response = client.get("/api/recommendations/trending", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_recommendations_similar(self, client: TestClient, auth_headers, sample_products):
        """Test getting similar products"""
        if sample_products:
            product_id = sample_products[0]["product_id"]
            response = client.get(f"/api/recommendations/similar/{product_id}", headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_get_recommendations_collaborative(self, client: TestClient, auth_headers):
        """Test getting collaborative filtering recommendations"""
        response = client.get("/api/recommendations/collaborative", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_recommendations_content_based(self, client: TestClient, auth_headers):
        """Test getting content-based recommendations"""
        response = client.get("/api/recommendations/content-based", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
