"""
Tests for users endpoints
"""

import pytest
from fastapi.testclient import TestClient


class TestUsersEndpoints:
    """Test users endpoints"""
    
    def test_create_user_success(self, client: TestClient, test_user_data):
        """Test successful user creation"""
        response = client.post("/api/users/", json=test_user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert data["email"] == test_user_data["email"]
    
    def test_create_user_duplicate_email(self, client: TestClient, test_user_data):
        """Test user creation with duplicate email"""
        # Create first user
        client.post("/api/users/", json=test_user_data)
        
        # Try to create user with same email
        response = client.post("/api/users/", json=test_user_data)
        
        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()
    
    def test_get_user_success(self, client: TestClient, test_user_data):
        """Test getting user by ID"""
        # Create user first
        create_response = client.post("/api/users/", json=test_user_data)
        user_id = create_response.json()["user_id"]
        
        # Get user
        response = client.get(f"/api/users/{user_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user_id
        assert data["email"] == test_user_data["email"]
    
    def test_get_user_not_found(self, client: TestClient):
        """Test getting non-existent user"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/users/{fake_id}")
        
        assert response.status_code == 404
    
    def test_update_user_profile_success(self, client: TestClient, test_user_data):
        """Test successful user profile update"""
        # Create user first
        create_response = client.post("/api/users/", json=test_user_data)
        user_id = create_response.json()["user_id"]
        
        # Update profile
        update_data = {
            "name": "Updated User Name",
            "preferences": ["electronics", "books", "fashion"]
        }
        response = client.patch(f"/api/users/{user_id}/profile", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        # Verify profile was updated
        assert data["user_id"] == user_id
    
    def test_update_user_success(self, client: TestClient, test_user_data):
        """Test successful user update"""
        # Create user first
        create_response = client.post("/api/users/", json=test_user_data)
        user_id = create_response.json()["user_id"]
        
        # Update user
        update_data = {
            "email": "updated@example.com"
        }
        response = client.patch(f"/api/users/{user_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == update_data["email"]
    
    def test_update_user_duplicate_email(self, client: TestClient, test_user_data):
        """Test user update with duplicate email"""
        # Create two users
        user1 = client.post("/api/users/", json=test_user_data).json()
        
        user2_data = test_user_data.copy()
        user2_data["email"] = "user2@example.com"
        user2 = client.post("/api/users/", json=user2_data).json()
        
        # Try to update user2 with user1's email
        update_data = {"email": test_user_data["email"]}
        response = client.patch(f"/api/users/{user2['user_id']}", json=update_data)
        
        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()
    
    def test_get_user_stats_success(self, client: TestClient, test_user_data):
        """Test getting user statistics"""
        # Create user first
        create_response = client.post("/api/users/", json=test_user_data)
        user_id = create_response.json()["user_id"]
        
        # Get stats
        response = client.get(f"/api/users/{user_id}/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_interactions" in data
        assert "event_types" in data
        assert "platforms" in data
    
    def test_get_user_stats_not_found(self, client: TestClient):
        """Test getting stats for non-existent user"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/users/{fake_id}/stats")
        
        assert response.status_code == 404
    
    def test_create_anonymous_user(self, client: TestClient):
        """Test creating anonymous user"""
        anonymous_data = {
            "email": None,
            "is_anonymous": True,
            "profile": {}
        }
        
        response = client.post("/api/users/", json=anonymous_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_anonymous"] == True

