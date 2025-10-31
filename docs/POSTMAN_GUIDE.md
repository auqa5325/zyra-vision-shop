# Postman Quick Start Guide

Complete guide to testing the Zyra Vision Shop API with Postman.

## Table of Contents

1. [Installation](#installation)
2. [Import Collection](#import-collection)
3. [Setup Environment](#setup-environment)
4. [First Test](#first-test)
5. [Running Tests](#running-tests)
6. [Understanding the Collection](#understanding-the-collection)
7. [Troubleshooting](#troubleshooting)

---

## Installation

### Download Postman

1. Go to [https://www.postman.com/downloads/](https://www.postman.com/downloads/)
2. Download for your OS (Mac, Windows, Linux)
3. Install and open Postman

### Alternative: Use Postman Web

1. Go to [https://web.postman.co/](https://web.postman.co/)
2. Sign up or log in

---

## Import Collection

### Step 1: Start Postman

Open the Postman app.

### Step 2: Import Collection

1. Click **Import**
2. In the dialog:
   - Click **Upload Files**
   - Select `backend/tests/postman_collection.json`
   - Click **Import**
3. Import environment:
   - Click **Import** again
   - Upload `backend/tests/postman_environment.json`
   - Click **Import**

### Step 3: Verify Import

- In the left sidebar, confirm you see:
  - **Collections > Zyra Vision Shop - API Tests**
  - **Environments > Zyra Vision Shop - Local Environment**
- Expand the collection to view folders: Health & Status, Authentication, Products, etc.

---

## Setup Environment

### Select Environment

1. Open the **Environments** menu (top right) and select **Zyra Vision Shop - Local Environment**
2. Click the eye icon next to the environment name

### Configure Base URL

The `baseUrl` variable is preconfigured. Ensure your backend matches.

If your backend runs on a different port/host:

1. Open the **Environments** menu
2. Select **Zyra Vision Shop - Local Environment**
3. In **Variables**:
   - Find `baseUrl`
   - Set your backend URL (e.g., `http://localhost:8000`)
   - Save changes

---

## First Test

### Start the Backend Server

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Confirm it starts on `http://localhost:8000`.

### Test the Health Endpoint

1. In Postman, go to **Health & Status** > **Root Endpoint**
2. Click **Send**
3. Expected:
   ```json
   {
     "message": "Zyra AI Recommendation API",
     "version": "1.0.0",
     "status": "running",
     "docs": "/docs"
   }
   ```
4. Status: `200 OK`

---

## Running Tests

### Method 1: Individual Requests

Use folders in order:

#### 1. Health & Status

Test:
- Root Endpoint
- Health Check
- Metrics

#### 2. Authentication

#### 2a. Register

1. Open **Register User**
2. Click **Send**
3. Token script runs automatically
4. Open **Environments** and confirm `accessToken`, `refreshToken`, and `userId` are set

#### 2b. Login

1. Open **Login User**
2. Click **Send**
3. Confirm tokens are refreshed

#### 2c. Get Current User

1. Click **Send**
2. Verify your user profile

### Method 2: Run Entire Collection

1. Right‑click the collection
2. **Run collection**
3. Config:
   - Leave defaults
   - **Iterations**: 1
4. Click **Run Zyra Vision Shop...**
5. Wait for completion
6. Review the report:
   - Total requests
   - Pass/fail
   - Any errors

### Method 3: Run by Folder

- Right‑click the folder > **Run folder**

---

## Understanding the Collection

### Structure

```
Zyra Vision Shop - API Tests
├── Health & Status
│   ├── Root Endpoint
│   ├── Health Check
│   └── Metrics
├── Authentication
│   ├── Register User
│   ├── Login User
│   ├── Get Current User
│   ├── Refresh Token
│   └── Logout User
├── Products
│   ├── List Products
│   ├── Search Products
│   ├── Get Product by ID
│   ├── List Categories
│   ├── Get Category Hierarchy
│   └── Get Products by Category
├── Recommendations
│   ├── Get Top Pick
│   ├── Get Hybrid Recommendations
│   ├── Get Content Recommendations
│   ├── Get Collaborative Recommendations
│   ├── Get Personalized Recommendations
│   ├── Get Top Sellers
│   └── Get Product You May Also Like
├── Interactions
│   ├── Create Interaction (View)
│   ├── Get User Interactions
│   └── Test Interaction Endpoint
├── Reviews
│   ├── Create Review
│   ├── Get Product Reviews
│   ├── Get Product Rating Summary
│   └── Mark Review as Helpful
└── Users
    ├── Get User Profile
    ├── Get User Stats
    └── Update User Profile
```

### Automatic Token Management

Token scripts (e.g., in **Register User**) store tokens:

```javascript
if (pm.response.code === 201) {
    var jsonData = pm.response.json();
    pm.environment.set('accessToken', jsonData.access_token);
    pm.environment.set('refreshToken', jsonData.refresh_token);
}
```

After registration/login:
- `accessToken` is used for auth
- Tokens are refreshed as needed
- Logout clears tokens

### Environment Variables

| Variable | Description | Auto-Set? |
|----------|-------------|-----------|
| `baseUrl` | API base URL | No (manual) |
| `accessToken` | JWT access token | Yes |
| `refreshToken` | JWT refresh token | Yes |
| `userId` | Current user ID | Yes |
| `productId` | Product ID for tests | Yes |

---

## Step-by-Step Testing Workflow

### Complete User Flow

1. Run Authentication: Register or Login
2. Test Products: List/Search
3. Create an interaction: View a product
4. Get recommendations
5. Create a review (requires a product)
6. Check user stats
7. Logout

### Quick Test Sequence

#### 1. Register and Get Tokens

```
Authentication → Register User → Send
```

Confirm:
- Status: `201 Created`
- Variables contain `accessToken`, `refreshToken`, `userId`

#### 2. Get Product List

```
Products → List Products → Send
```

Confirm:
- Status: `200 OK`
- Array of products
- Set `productId` from the first product

#### 3. Search Products

```
Products → Search Products → Send
```

Confirm:
- Status: `200 OK`
- Search results array

#### 4. Get Recommendations

```
Recommendations → Get Hybrid Recommendations → Send
```

Confirm:
- Status: `200 OK`
- Array of recommendations

#### 5. Track Interaction

```
Interactions → Create Interaction (View) → Send
```

Confirm:
- Status: `200 OK`
- Interaction created

#### 6. Get User Stats

```
Users → Get User Stats → Send
```

Confirm:
- Status: `200 OK`
- User statistics

---

## Advanced Usage

### Manual Tests

1. Select a request
2. Edit params/headers/body as needed
3. Send
4. Use the Console for debugging

### Pre-request Scripts

- Set variables
- Generate random data
- Compute timestamps

### Test Scripts

Add validation:

```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has data", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('data');
});
```

### Save Responses

1. Click **Save Response**
2. Choose a name
3. Reuse in later requests

---

## Troubleshooting

### "Could not get any response"

- Backend running?
- Correct URL (`http://localhost:8000`)?
- Network access allowed?

Fix:
```bash
cd backend
python -m uvicorn app.main:app --reload
```

### "Unauthorized" (401)

- Expired or missing `accessToken`
- Corrupted environment

Fix:
- Re-run **Register User** or **Login User**
- Confirm `accessToken` is set

### "Not Found" (404)

- Wrong endpoint URL
- Backend routes changed

Fix:
- Check the backend route
- Open `/docs`

### Tests Fail in Collection Runner

- Start with **Health & Status**
- Ensure the backend is running
- Check the console for errors
- Use Runner settings: **Delay** 500 ms, **Iterations** 1

### Environment Variables Not Updating

- Confirm the correct environment is selected
- Verify the script runs

Fix:
- Manually set variables in the environment
- Re-import the collection/environment

### Collection Import Errors

- Valid JSON required
- Files aren’t corrupted

Fix:
- Re-download from the repo
- Use **Raw** import

---

## Tips

- Run tests in folder order
- Check the Console for errors
- Use **Health Check** first
- Keep the environment selected
- Review the Runner report
- Use a pre-request script for dynamic data
- Save examples

---

## What’s Next?

- [ ] Try all test cases
- [ ] Review `docs/TESTING.md`
- [ ] Customize tests for your needs
- [ ] Export collections for sharing
- [ ] Set up Newman for CLI

---

## Quick Reference

### Essential Commands

```
Select Environment → Zyra Vision Shop - Local Environment
Run Collection → Right-click collection → Run collection
View Variables → Environments → Zyra Vision Shop - Local Environment
View Console → View → Show Postman Console (Cmd/Ctrl + Alt + C)
```

### Status Code Meanings

- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Auth required
- `404 Not Found` - Resource not found
- `500 Server Error` - Backend error

---

## Need Help?

1. Check this guide
2. Review `docs/TESTING.md`
3. Inspect the Console
4. Try `/docs`
5. Create an issue

---

Happy Testing with Postman!

