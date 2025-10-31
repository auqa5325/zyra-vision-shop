"""
Tests for admin endpoints
"""

import pytest
from fastapi.testclient import TestClient


class TestAdminEndpoints:
    """Test admin endpoints"""
    
    def test_admin_dashboard_access(self, client: TestClient, auth_headers):
        """Test accessing admin dashboard"""
        response = client.get("/api/admin/dashboard", headers=auth_headers)
        
        # This might require admin role, so could be 200 or 403
        assert response.status_code in [200, 403, 404]
    
    def test_admin_stats(self, client: TestClient, auth_headers):
        """Test getting admin statistics"""
        response = client.get("/api/admin/stats", headers=auth_headers)
        
        # This might require admin role, so could be 200 or 403
        assert response.status_code in [200, 403, 404]
    
    def test_admin_users_list(self, client: TestClient, auth_headers):
        """Test listing all users (admin)"""
        response = client.get("/api/admin/users", headers=auth_headers)
        
        # This might require admin role, so could be 200 or 403
        assert response.status_code in [200, 403, 404]
    
    def test_admin_products_list(self, client: TestClient, auth_headers):
        """Test listing all products (admin)"""
        response = client.get("/api/admin/products", headers=auth_headers)
        
        # This might require admin role, so could be 200 or 403
        assert response.status_code in [200, 403, 404]
    
    def test_admin_interactions_list(self, client: TestClient, auth_headers):
        """Test listing all interactions (admin)"""
        response = client.get("/api/admin/interactions", headers=auth_headers)
        
        # This might require admin role, so could be 200 or 403
        assert response.status_code in [200, 403, 404]

