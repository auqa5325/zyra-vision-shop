# Testing Guide for Zyra Vision Shop

This document provides comprehensive information about running tests for both the frontend and backend of the Zyra Vision Shop application.

## Table of Contents

1. [Backend Testing](#backend-testing)
   - [Unit Tests with Pytest](#unit-tests-with-pytest)
   - [Postman API Testing](#postman-api-testing)
2. [Frontend Testing](#frontend-testing)
   - [E2E Tests with Playwright](#e2e-tests-with-playwright)
3. [Running All Tests](#running-all-tests)
4. [CI/CD Integration](#cicd-integration)

---

## Backend Testing

### Unit Tests with Pytest

Backend tests are located in `backend/tests/` and use pytest with asyncio support.

#### Setup

```bash
cd backend
pip install -r requirements.txt
```

#### Running Tests

**Run all tests:**
```bash
pytest
```

**Run with coverage:**
```bash
pytest --cov=app --cov-report=html
```

**Run specific test file:**
```bash
pytest tests/test_auth.py
```

**Run specific test class:**
```bash
pytest tests/test_auth.py::TestAuthEndpoints
```

**Run specific test method:**
```bash
pytest tests/test_auth.py::TestAuthEndpoints::test_register_user_success
```

**Run with verbose output:**
```bash
pytest -v
```

**Run with output capture disabled:**
```bash
pytest -s
```

#### Test Files

- `test_auth.py` - Authentication endpoints (register, login, logout, refresh)
- `test_products.py` - Product CRUD operations
- `test_recommendations.py` - Recommendation algorithms
- `test_interactions.py` - User interaction tracking
- `test_ml_services.py` - Machine learning services
- `test_users.py` - User management
- `test_reviews.py` - Product reviews
- `test_admin.py` - Admin functionality
- `test_images.py` - Image uploads
- `test_schema.py` - Database schema

#### Test Configuration

The test configuration is in `backend/pytest.ini` and uses an in-memory SQLite database for isolated testing.

---

### Postman API Testing

We provide a comprehensive Postman collection for manual API testing and exploration.

#### Importing the Collection

1. Open Postman
2. Click **Import**
3. Select `backend/tests/postman_collection.json`
4. Select `backend/tests/postman_environment.json` (for environment variables)

#### Running the Collection

1. Set the environment variables:
   - `baseUrl`: API base URL (default: `http://localhost:8000`)
   
2. Start the backend server:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

3. Run the collection in order:
   - **Health & Status** - Verify API is running
   - **Authentication** - Register/login to get tokens
   - **Products** - Test product endpoints
   - **Recommendations** - Test recommendation endpoints
   - **Interactions** - Test interaction tracking
   - **Reviews** - Test review endpoints
   - **Users** - Test user management

#### Postman Test Scripts

The collection includes automatic test scripts that:
- Extract tokens from responses
- Store user/product IDs in environment variables
- Validate response codes and data
- Test token refresh workflows

#### Environment Variables

The collection uses these environment variables:
- `accessToken` - JWT access token
- `refreshToken` - JWT refresh token
- `userId` - Current user ID
- `productId` - Product ID for testing

---

## Frontend Testing

### E2E Tests with Playwright

Frontend E2E tests are located in `e2e/` and use Playwright for browser automation.

#### Setup

```bash
npm install
npx playwright install
```

#### Running Tests

**Run all tests:**
```bash
npm run test:e2e
```

**Run with UI mode (interactive):**
```bash
npm run test:e2e:ui
```

**Run in headed mode (see browser):**
```bash
npm run test:e2e:headed
```

**Run specific test file:**
```bash
npx playwright test e2e/home.spec.ts
```

**Run tests in specific browser:**
```bash
npx playwright test --project=chromium
```

**Run with codegen (record new tests):**
```bash
npx playwright codegen http://localhost:5173
```

#### Test Files

- `home.spec.ts` - Homepage and authentication tests
- `product-search.spec.ts` - Product search, navigation, cart, and wishlist
- `responsive.spec.ts` - Responsive design and accessibility tests

#### Configuration

Configuration is in `playwright.config.ts`:
- Base URL: `http://localhost:5173`
- Parallel execution enabled
- Automatic screenshot on failure
- Tests on Chrome, Firefox, Safari, and mobile browsers

#### Before Running Tests

1. Start the frontend dev server:
   ```bash
   npm run dev
   ```

2. Ensure the backend API is running:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

---

## Running All Tests

### Backend Tests

```bash
cd backend
pytest --cov=app --cov-report=html
open htmlcov/index.html  # View coverage report
```

### Frontend Tests

```bash
npm run test:e2e
npx playwright show-report  # View test report
```

### Full Test Suite

Create a script `test-all.sh`:

```bash
#!/bin/bash
set -e

echo "Running backend tests..."
cd backend
pytest --cov=app --cov-report=html

echo "Running frontend tests..."
cd ..
npm run test:e2e

echo "All tests passed!"
```

---

## CI/CD Integration

### GitHub Actions Example

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: npm ci
      - name: Install Playwright
        run: npx playwright install --with-deps
      - name: Run tests
        run: npm run test:e2e
      - uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
```

---

## Best Practices

### Writing Backend Tests

1. **Use fixtures** from `conftest.py` for common test setup
2. **Test edge cases** including validation errors, not found, unauthorized
3. **Use descriptive names** that explain what is being tested
4. **Keep tests isolated** - each test should be independent
5. **Clean up after tests** - use database fixtures that auto-clean

### Writing Frontend Tests

1. **Use data-testid** attributes for stable selectors
2. **Wait for async operations** - use `page.waitForTimeout()` and `waitForSelector()`
3. **Test user flows** from a user's perspective
4. **Handle flaky tests** with retries and proper waiting
5. **Test accessibility** with keyboard navigation and screen readers

### Test Coverage Goals

- **Backend**: Aim for >80% code coverage
- **Frontend**: Aim for >70% code coverage
- **Critical paths**: 100% coverage (auth, payments, data processing)

---

## Troubleshooting

### Backend Tests Fail

1. **Database issues**: Ensure test database is accessible
2. **Missing dependencies**: Run `pip install -r requirements.txt`
3. **Port conflicts**: Change test configuration port numbers
4. **ML models not loaded**: Some tests may skip if models aren't available

### Frontend Tests Fail

1. **Port conflicts**: Ensure port 5173 is available
2. **Timeout issues**: Increase timeout in `playwright.config.ts`
3. **Element not found**: Check selectors match current UI
4. **Flaky tests**: Add `page.waitForSelector()` before interactions

### Postman Tests Fail

1. **Server not running**: Ensure backend is running on correct port
2. **Environment variables**: Check `baseUrl` is correct
3. **Expired tokens**: Re-run authentication requests
4. **Missing data**: Ensure test data exists in database

---

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Playwright Documentation](https://playwright.dev/)
- [Postman Documentation](https://learning.postman.com/)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)

---

## Test Coverage Reports

After running tests with coverage, view reports:

**Backend:**
```bash
cd backend
open htmlcov/index.html
```

**Frontend:**
```bash
npx playwright show-report
```

---

## Contributing

When adding new features:

1. **Write tests first** (TDD approach recommended)
2. **Ensure all tests pass** before submitting PR
3. **Update this documentation** if adding new test types
4. **Keep test execution time under 5 minutes** for fast feedback

---

## Questions or Issues?

For testing-related questions or issues:
1. Check this documentation first
2. Review existing test examples
3. Ask in team chat or create an issue
4. Contribute improvements back to the documentation

