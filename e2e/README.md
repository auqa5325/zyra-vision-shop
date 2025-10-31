# Frontend E2E Tests

End-to-end tests using Playwright for the Zyra Vision Shop frontend.

## Test Files

- `home.spec.ts` - Homepage, navigation, and authentication tests
- `product-search.spec.ts` - Product search, navigation, cart, and wishlist
- `responsive.spec.ts` - Responsive design and accessibility

## Prerequisites

```bash
npm install
npx playwright install
```

## Running Tests

```bash
# Run all tests
npm run test:e2e

# Run with UI mode (interactive)
npm run test:e2e:ui

# Run in headed mode (see browser)
npm run test:e2e:headed

# Run specific test file
npx playwright test e2e/home.spec.ts

# Run in specific browser
npx playwright test --project=chromium
```

## Configuration

See `playwright.config.ts` for:
- Supported browsers (Chrome, Firefox, Safari, mobile)
- Base URL configuration
- Retry and timeout settings
- Screenshot and video recording

## Before Running

1. Start the frontend dev server:
   ```bash
   npm run dev
   ```

2. Ensure the backend API is running:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

## Test Reports

View test reports:
```bash
npx playwright show-report
```

## Codegen

Record new tests interactively:
```bash
npx playwright codegen http://localhost:5173
```

