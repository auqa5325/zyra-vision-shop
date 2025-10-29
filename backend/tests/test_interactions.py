"""
Tests for interactions endpoints
"""

import pytest
from fastapi.testclient import TestClient


class TestInteractionsEndpoints:
    """Test interactions endpoints"""
    
    def test_record_interaction_success(self, client: TestClient, auth_headers, sample_products):
        """Test successful interaction recording"""
        if sample_products:
            product_id = sample_products[0]["product_id"]
            interaction_data = {
                "product_id": product_id,
                "event_type": "view",
                "event_value": 1
            }
            
            response = client.post("/api/interactions", json=interaction_data, headers=auth_headers)
            
            assert response.status_code == 201
            data = response.json()
            assert data["product_id"] == product_id
            assert data["event_type"] == "view"
    
    def test_record_interaction_no_auth(self, client: TestClient, sample_products):
        """Test interaction recording without authentication"""
        if sample_products:
            product_id = sample_products[0]["product_id"]
            interaction_data = {
                "product_id": product_id,
                "event_type": "view"
            }
            
            response = client.post("/api/interactions", json=interaction_data)
            
            assert response.status_code == 401
    
    def test_record_interaction_invalid_data(self, client: TestClient, auth_headers):
        """Test interaction recording with invalid data"""
        invalid_data = {
            "product_id": "invalid-uuid",
            "event_type": "invalid_event"
        }
        
        response = client.post("/api/interactions", json=invalid_data, headers=auth_headers)
        
        assert response.status_code == 422
    
    def test_record_interaction_nonexistent_product(self, client: TestClient, auth_headers):
        """Test interaction recording with non-existent product"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        interaction_data = {
            "product_id": fake_id,
            "event_type": "view"
        }
        
        response = client.post("/api/interactions", json=interaction_data, headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_get_user_interactions(self, client: TestClient, auth_headers, sample_products):
        """Test getting user interactions"""
        # Record some interactions first
        if sample_products:
            for i, product in enumerate(sample_products[:3]):
                interaction_data = {
                    "product_id": product["product_id"],
                    "event_type": "view",
                    "event_value": i + 1
                }
                client.post("/api/interactions", json=interaction_data, headers=auth_headers)
        
        response = client.get("/api/interactions", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_user_interactions_pagination(self, client: TestClient, auth_headers):
        """Test user interactions pagination"""
        params = {"skip": 0, "limit": 5}
        response = client.get("/api/interactions", params=params, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_user_interactions_filter_by_type(self, client: TestClient, auth_headers):
        """Test filtering interactions by event type"""
        params = {"event_type": "view"}
        response = client.get("/api/interactions", params=params, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_user_interactions_no_auth(self, client: TestClient):
        """Test getting interactions without authentication"""
        response = client.get("/api/interactions")
        
        assert response.status_code == 401
    
    def test_create_session_success(self, client: TestClient, auth_headers):
        """Test successful session creation"""
        session_data = {
            "context": {
                "page": "home",
                "device": "desktop"
            }
        }
        
        response = client.post("/api/interactions/sessions", json=session_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert "session_id" in data
    
    def test_create_session_no_auth(self, client: TestClient):
        """Test session creation without authentication"""
        session_data = {"context": {"page": "home"}}
        
        response = client.post("/api/interactions/sessions", json=session_data)
        
        assert response.status_code == 401
    
    def test_get_user_sessions(self, client: TestClient, auth_headers):
        """Test getting user sessions"""
        response = client.get("/api/interactions/sessions", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_end_session_success(self, client: TestClient, auth_headers):
        """Test ending a session"""
        # Create a session first
        session_data = {"context": {"page": "home"}}
        create_response = client.post("/api/interactions/sessions", json=session_data, headers=auth_headers)
        
        if create_response.status_code == 201:
            session_id = create_response.json()["session_id"]
            
            # End the session
            response = client.put(f"/api/interactions/sessions/{session_id}/end", headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["ended_at"] is not None
    
    def test_end_session_not_found(self, client: TestClient, auth_headers):
        """Test ending non-existent session"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.put(f"/api/interactions/sessions/{fake_id}/end", headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_record_multiple_interactions(self, client: TestClient, auth_headers, sample_products):
        """Test recording multiple interactions"""
        if sample_products:
            product_id = sample_products[0]["product_id"]
            
            # Record different types of interactions
            interactions = [
                {"product_id": product_id, "event_type": "view", "event_value": 1},
                {"product_id": product_id, "event_type": "click", "event_value": 1},
                {"product_id": product_id, "event_type": "add_to_cart", "event_value": 1}
            ]
            
            for interaction in interactions:
                response = client.post("/api/interactions", json=interaction, headers=auth_headers)
                assert response.status_code == 201
