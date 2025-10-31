# Your First Postman Tests - Step by Step

You've imported the collection and environment variables are set up! Let's run your first tests.

## Your Current Setup ✅

- **Base URL**: `http://localhost:8005` ✓
- **Environment**: Zyra Vision Shop - Local Environment ✓
- **Backend**: Should be running on port 8005

## Let's Test! 🚀

### Step 1: Verify Backend is Running

Make sure your backend is running on port 8005:

```bash
# Check if backend is running
curl http://localhost:8005/

# If not running, start it:
cd backend
python -m uvicorn app.main:app --reload --port 8005
```

### Step 2: Run Health Check

1. In Postman, expand **"Zyra Vision Shop - API Tests"**
2. Expand **"Health & Status"** folder
3. Click **"Root Endpoint"**
4. Click **Send** (blue button, top right)

**Expected Result:**
```json
{
  "message": "Zyra AI Recommendation API",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs"
}
```

✅ **Status**: 200 OK

If this works, your connection is good!

---

### Step 3: Register a User (Get Tokens)

1. Go to **"Authentication"** folder
2. Click **"Register User"**
3. Click **Send**

**Expected Result:**
- Status: **201 Created**
- You'll see tokens in the response

**What Happens Automatically:**
- ✓ `accessToken` saved to environment
- ✓ `refreshToken` saved to environment  
- ✓ `userId` saved to environment

**Check Variables:**
- Click the "eye" icon (👁️) in the right sidebar
- Or go to Environments → Zyra Vision Shop - Local Environment
- You should now see values for `accessToken`, `refreshToken`, and `userId`

✅ **Status**: 201 Created

---

### Step 4: Get Your Profile

1. Go to **"Authentication"** folder
2. Click **"Get Current User"**
3. Click **Send**

This uses the `{{accessToken}}` automatically!

**Expected Result:**
```json
{
  "user_id": "...",
  "email": "test@example.com",
  "username": "testuser",
  ...
}
```

✅ **Status**: 200 OK

---

### Step 5: Get Products

1. Go to **"Products"** folder
2. Click **"List Products"**
3. Click **Send**

**Expected Result:**
- Array of products
- Each product has: `product_id`, `name`, `price`, etc.

✅ **Status**: 200 OK

---

### Step 6: Get a Product ID

After Step 5, you need to manually set the `productId` variable:

1. In the response, find a product
2. Copy its `product_id` (it looks like: `"47c506ff-ed15-47ba-af6e-4bd1ae7e27d6"`)
3. Go to **Environments** → **Zyra Vision Shop - Local Environment**
4. Find the `productId` variable
5. Paste the ID as the value
6. Click **Save**

---

### Step 7: Search Products

1. Go to **"Products"** folder
2. Click **"Search Products"**
3. Click **Send**

This searches for "laptop" by default.

**Expected Result:**
- Array of matching products

✅ **Status**: 200 OK

---

### Step 8: Get Recommendations

1. Go to **"Recommendations"** folder
2. Click **"Get Top Pick"**
3. Click **Send**

**Expected Result:**
- One recommended product with scores
- `hybrid_score`, `reason_features`, etc.

✅ **Status**: 200 OK

---

### Step 9: Track an Interaction

1. Go to **"Interactions"** folder
2. Click **"Create Interaction (View)"**
3. Update the request body to use your `{{productId}}`:
   - In the Body tab, you'll see JSON
   - Replace the `product_id` with your actual product ID
4. Click **Send**

**Expected Result:**
- Interaction created
- Status: 200 OK

✅ **Status**: 200 OK

---

### Step 10: Get User Stats

1. Go to **"Users"** folder
2. Click **"Get User Stats"**
3. Click **Send**

**Expected Result:**
```json
{
  "total_interactions": 1,
  "event_types": {"view": 1},
  "platforms": {"web": 1},
  "last_activity": "..."
}
```

✅ **Status**: 200 OK

---

## 🎉 Congratulations!

You've successfully:
- ✅ Connected to the API
- ✅ Registered a user
- ✅ Got tokens automatically
- ✅ Listed products
- ✅ Searched products
- ✅ Got recommendations
- ✅ Tracked interactions
- ✅ Viewed user stats

---

## Next: Run All Tests

### Run the Entire Collection

1. Right-click **"Zyra Vision Shop - API Tests"** (the collection name)
2. Select **"Run collection"**
3. You'll see the Collection Runner window
4. Click **"Run Zyra Vision Shop - API Tests"**
5. Watch all tests run automatically!

**What Happens:**
- All requests run in order
- Tests automatically pass/fail
- You'll see a report at the end

---

## Troubleshooting

### "Could not get response"

**Problem**: Backend not running

**Solution**:
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8005
```

### "401 Unauthorized"

**Problem**: Missing or expired token

**Solution**:
1. Go to **"Authentication"** → **"Register User"**
2. Click **Send**
3. This refreshes your tokens automatically

### "No products found"

**Problem**: Database is empty

**Solution**: You may need to populate your database with products. Check backend setup.

### Token not saving

**Problem**: Environment variables not updating

**Solution**:
1. Make sure the correct environment is selected (top right)
2. Manually set variables if needed
3. Check that `pm.environment.set()` is working in the test script

---

## Quick Reference

### Essential Variables
- `{{baseUrl}}` = http://localhost:8005
- `{{accessToken}}` = Your JWT token (auto-saved)
- `{{refreshToken}}` = Your refresh token (auto-saved)
- `{{userId}}` = Your user ID (auto-saved)
- `{{productId}}` = A product ID (set manually)

### Request Flow
1. Health checks don't need auth ✓
2. Register/Login gets tokens automatically ✓
3. Other requests use tokens automatically ✓

### View Variables
- Click the 👁️ "eye" icon in right sidebar
- Or go to: Environments → Zyra Vision Shop - Local Environment

---

## What's Next?

1. ✅ Run more individual tests
2. ✅ Try different endpoints
3. ✅ Create your own requests
4. ✅ Read: [Full Postman Guide](POSTMAN_GUIDE.md)
5. ✅ Explore: All test documentation

---

## Need Help?

- 📖 [Postman Quick Start](POSTMAN_QUICKSTART.md) - Simplified guide
- 📖 [Postman Guide](docs/POSTMAN_GUIDE.md) - Complete documentation
- 📖 [Testing Setup](TEST_SETUP.md) - All testing info
- 📖 [Test Summary](TEST_SUMMARY.md) - Overview

---

**Happy Testing! 🎉**

