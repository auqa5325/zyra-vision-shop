"""
Tests for products endpoints
"""

import pytest
from fastapi.testclient import TestClient


class TestProductsEndpoints:
    """Test products endpoints"""
    
    def test_create_product_success(self, client: TestClient, auth_headers, test_product_data):
        """Test successful product creation"""
        response = client.post("/api/products", json=test_product_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == test_product_data["name"]
        assert data["price"] == test_product_data["price"]
        assert "product_id" in data
    
    def test_create_product_no_auth(self, client: TestClient, test_product_data):
        """Test product creation without authentication"""
        response = client.post("/api/products", json=test_product_data)
        
        assert response.status_code == 401
    
    def test_create_product_invalid_data(self, client: TestClient, auth_headers):
        """Test product creation with invalid data"""
        invalid_data = {
            "name": "",  # Empty name should fail
            "price": -10  # Negative price should fail
        }
        
        response = client.post("/api/products", json=invalid_data, headers=auth_headers)
        
        assert response.status_code == 422
    
    def test_get_products_list(self, client: TestClient, auth_headers, sample_products):
        """Test getting products list"""
        response = client.get("/api/products", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= len(sample_products)
    
    def test_get_products_pagination(self, client: TestClient, auth_headers):
        """Test products pagination"""
        response = client.get("/api/products?skip=0&limit=2", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2
    
    def test_get_products_search(self, client: TestClient, auth_headers, sample_products):
        """Test products search"""
        response = client.get("/api/products?search=Test", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_product_by_id_success(self, client: TestClient, auth_headers, sample_products):
        """Test getting product by ID"""
        if sample_products:
            product_id = sample_products[0]["product_id"]
            response = client.get(f"/api/products/{product_id}", headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["product_id"] == product_id
    
    def test_get_product_by_id_not_found(self, client: TestClient, auth_headers):
        """Test getting non-existent product"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/products/{fake_id}", headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_update_product_success(self, client: TestClient, auth_headers, sample_products):
        """Test successful product update"""
        if sample_products:
            product_id = sample_products[0]["product_id"]
            update_data = {
                "name": "Updated Product Name",
                "price": 150.0
            }
            
            response = client.put(f"/api/products/{product_id}", json=update_data, headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == update_data["name"]
            assert data["price"] == update_data["price"]
    
    def test_update_product_not_found(self, client: TestClient, auth_headers):
        """Test updating non-existent product"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        update_data = {"name": "Updated Name"}
        
        response = client.put(f"/api/products/{fake_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_delete_product_success(self, client: TestClient, auth_headers, sample_products):
        """Test successful product deletion"""
        if sample_products:
            product_id = sample_products[0]["product_id"]
            response = client.delete(f"/api/products/{product_id}", headers=auth_headers)
            
            assert response.status_code == 204
    
    def test_delete_product_not_found(self, client: TestClient, auth_headers):
        """Test deleting non-existent product"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.delete(f"/api/products/{fake_id}", headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_get_product_categories(self, client: TestClient, auth_headers):
        """Test getting product categories"""
        response = client.get("/api/products/categories", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_create_category_success(self, client: TestClient, auth_headers):
        """Test successful category creation"""
        category_data = {
            "name": "Test Category",
            "slug": "test-category"
        }
        
        response = client.post("/api/products/categories", json=category_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == category_data["name"]
        assert data["slug"] == category_data["slug"]
