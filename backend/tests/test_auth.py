"""
Tests for authentication endpoints
"""

import pytest
from fastapi.testclient import TestClient


class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_register_user_success(self, client: TestClient, test_user_data):
        """Test successful user registration"""
        response = client.post("/api/auth/register", json=test_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "user_id" in data
        assert data["email"] == test_user_data["email"]
        assert "password" not in data  # Password should not be returned
    
    def test_register_user_duplicate_email(self, client: TestClient, test_user_data):
        """Test registration with duplicate email"""
        # Register first user
        client.post("/api/auth/register", json=test_user_data)
        
        # Try to register with same email
        response = client.post("/api/auth/register", json=test_user_data)
        
        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()
    
    def test_register_user_invalid_email(self, client: TestClient):
        """Test registration with invalid email"""
        invalid_data = {
            "email": "invalid-email",
            "password": "password123"
        }
        
        response = client.post("/api/auth/register", json=invalid_data)
        
        assert response.status_code == 422
    
    def test_login_success(self, client: TestClient, test_user_data):
        """Test successful login"""
        # Register user first
        client.post("/api/auth/register", json=test_user_data)
        
        # Login
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client: TestClient, test_user_data):
        """Test login with invalid credentials"""
        # Register user first
        client.post("/api/auth/register", json=test_user_data)
        
        # Try to login with wrong password
        login_data = {
            "email": test_user_data["email"],
            "password": "wrongpassword"
        }
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with non-existent user"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
    
    def test_refresh_token_success(self, client: TestClient, test_user_data):
        """Test successful token refresh"""
        # Register and login user
        client.post("/api/auth/register", json=test_user_data)
        
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        login_response = client.post("/api/auth/login", json=login_data)
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh token
        refresh_data = {"refresh_token": refresh_token}
        response = client.post("/api/auth/refresh", json=refresh_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_refresh_token_invalid(self, client: TestClient):
        """Test refresh with invalid token"""
        refresh_data = {"refresh_token": "invalid_token"}
        response = client.post("/api/auth/refresh", json=refresh_data)
        
        assert response.status_code == 401
    
    def test_get_current_user_success(self, client: TestClient, auth_headers):
        """Test getting current user with valid token"""
        response = client.get("/api/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "email" in data
    
    def test_get_current_user_no_token(self, client: TestClient):
        """Test getting current user without token"""
        response = client.get("/api/auth/me")
        
        assert response.status_code == 401
    
    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test getting current user with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/auth/me", headers=headers)
        
        assert response.status_code == 401
