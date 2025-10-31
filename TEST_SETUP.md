# Quick Test Setup Guide

This is a quick reference guide for running tests in the Zyra Vision Shop project.

## Quick Start

### Backend Tests (Pytest)

```bash
# Navigate to backend
cd backend

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Frontend Tests (Playwright)

```bash
# Install dependencies
npm install

# Install Playwright browsers
npx playwright install

# Run tests
npm run test:e2e

# Run with UI (recommended for first time)
npm run test:e2e:ui

# View test report
npx playwright show-report
```

### Postman API Tests

**Quick Setup (5 minutes):**
1. Import `backend/tests/postman_collection.json` in Postman
2. Import `backend/tests/postman_environment.json` 
3. Select environment: "Zyra Vision Shop - Local Environment"
4. Start backend: `cd backend && python -m uvicorn app.main:app --reload`
5. Run "Health & Status" → "Root Endpoint"
6. Run "Authentication" → "Register User" (gets tokens automatically)

**See:** `POSTMAN_QUICKSTART.md` for step-by-step guide

**Detailed:** `docs/POSTMAN_GUIDE.md` for complete instructions

## Prerequisites Checklist

- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] PostgreSQL running (for backend)
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] Playwright browsers installed

## Running All Tests

```bash
# Terminal 1: Start backend
cd backend
python -m uvicorn app.main:app --reload

# Terminal 2: Start frontend
npm run dev

# Terminal 3: Run backend tests
cd backend
pytest --cov=app

# Terminal 4: Run frontend tests
npm run test:e2e
```

## Common Issues

### Backend Tests

**Issue**: Database connection error
**Solution**: Ensure PostgreSQL is running and DATABASE_URL is set correctly

**Issue**: ML models not found
**Solution**: Tests will skip ML-related tests if models aren't available

**Issue**: Import errors
**Solution**: Ensure you're in the `backend` directory when running pytest

### Frontend Tests

**Issue**: Port 5173 already in use
**Solution**: Kill existing vite process or change port in vite.config.ts

**Issue**: Tests timeout
**Solution**: Increase timeout in playwright.config.ts

**Issue**: Browser not found
**Solution**: Run `npx playwright install`

## Test Files Overview

### Backend Tests (`backend/tests/`)
- `test_auth.py` - Authentication flows
- `test_products.py` - Product operations
- `test_recommendations.py` - ML recommendations
- `test_interactions.py` - User tracking
- `test_users.py` - User management
- `test_reviews.py` - Product reviews
- `test_admin.py` - Admin features
- `test_images.py` - Image uploads
- `test_schema.py` - Database schema

### Frontend Tests (`e2e/`)
- `home.spec.ts` - Homepage and navigation
- `product-search.spec.ts` - Search and shopping flows
- `responsive.spec.ts` - Responsive design and accessibility

### Postman Tests
- `postman_collection.json` - API test collection
- `postman_environment.json` - Environment variables

## Getting Help

See [docs/TESTING.md](docs/TESTING.md) for detailed documentation.

## Quick Commands Reference

```bash
# Backend
pytest                    # Run all tests
pytest -v                # Verbose output
pytest tests/test_auth.py # Specific file
pytest -s                # Show print statements

# Frontend  
npm run test:e2e         # Run all tests
npm run test:e2e:ui      # Interactive UI
npx playwright test --project=chromium  # One browser
npx playwright codegen   # Record new test

# Coverage
pytest --cov=app --cov-report=html
# Then open htmlcov/index.html
```

## Next Steps

1. ✅ Run backend tests: `pytest`
2. ✅ Run frontend tests: `npm run test:e2e`
3. ✅ Import Postman collection
4. ✅ Read full testing guide: [docs/TESTING.md](docs/TESTING.md)
5. ✅ View coverage reports
6. ✅ Contribute more tests!

