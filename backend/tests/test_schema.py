"""
Tests for schema endpoints
"""

import pytest
from fastapi.testclient import TestClient


class TestSchemaEndpoints:
    """Test schema endpoints"""
    
    def test_get_database_schema(self, client: TestClient):
        """Test getting database schema"""
        response = client.get("/api/schema")
        
        assert response.status_code == 200
        data = response.json()
        
        # Schema should contain tables
        assert isinstance(data, dict) or isinstance(data, list)
    
    def test_get_table_schema(self, client: TestClient):
        """Test getting specific table schema"""
        # Common table names to test
        test_tables = ["users", "products", "interactions", "categories"]
        
        for table_name in test_tables:
            response = client.get(f"/api/schema/{table_name}")
            
            # Table might not exist in test DB, so could be 200 or 404
            assert response.status_code in [200, 404]
            
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, dict) or isinstance(data, list)

