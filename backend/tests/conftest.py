"""
Test configuration and fixtures for Zyra backend
"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db, Base
from app.config import settings
from app.services.auth_service import jwt_service


# Test database URL (in-memory SQLite for testing)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the database dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = TestingSessionLocal()
    
    yield session
    
    # Clean up
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session) -> Generator[TestClient, None, None]:
    """Create a test client with database session"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_user_data():
    """Sample user data for testing"""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "profile": {
            "name": "Test User",
            "preferences": ["electronics", "books"]
        }
    }


@pytest.fixture
def test_product_data():
    """Sample product data for testing"""
    return {
        "name": "Test Product",
        "short_description": "A test product",
        "long_description": "This is a detailed description of the test product",
        "price": 99.99,
        "currency": "INR",
        "brand": "TestBrand",
        "tags": ["test", "sample"],
        "available": True
    }


@pytest.fixture
def auth_headers(client: TestClient, test_user_data):
    """Create authenticated headers for testing"""
    # Register user
    response = client.post("/api/auth/register", json=test_user_data)
    assert response.status_code == 201
    
    # Login user
    login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    }
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    
    token_data = response.json()
    access_token = token_data["access_token"]
    
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def sample_products(client: TestClient, auth_headers):
    """Create sample products for testing"""
    products = []
    
    for i in range(5):
        product_data = {
            "name": f"Test Product {i+1}",
            "short_description": f"Description for product {i+1}",
            "price": 100.0 + i * 10,
            "tags": [f"tag{i+1}", "electronics"],
            "available": True
        }
        
        response = client.post("/api/products", json=product_data, headers=auth_headers)
        if response.status_code == 201:
            products.append(response.json())
    
    return products
