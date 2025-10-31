# Backend Tests

This directory contains comprehensive tests for the Zyra Vision Shop backend API.

## Test Files

- `test_auth.py` - Authentication (register, login, logout, refresh token)
- `test_products.py` - Product CRUD operations and search
- `test_recommendations.py` - Recommendation algorithms (hybrid, collaborative, content-based)
- `test_interactions.py` - User interaction tracking
- `test_ml_services.py` - Machine learning services
- `test_users.py` - User management and profile
- `test_reviews.py` - Product reviews
- `test_admin.py` - Admin functionality
- `test_images.py` - Image uploads
- `test_schema.py` - Database schema

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

## Fixtures

Tests use fixtures from `conftest.py`:
- `client` - Test client for API requests
- `db_session` - Database session with auto-cleanup
- `test_user_data` - Sample user data
- `test_product_data` - Sample product data
- `auth_headers` - Authentication headers
- `sample_products` - Pre-created products

## Postman Collection

Also available: `postman_collection.json` for manual API testing.

Import both files in Postman:
- `postman_collection.json` - Test collection
- `postman_environment.json` - Environment variables

## Test Database

Tests use an in-memory SQLite database that is automatically created and cleaned up for each test.

