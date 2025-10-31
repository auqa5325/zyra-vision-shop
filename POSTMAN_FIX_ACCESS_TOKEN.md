# Fix "Invalid authorization header format" Error

If you're seeing this error on `/api/auth/me`, your `{{accessToken}}` is empty!

## 🐛 The Problem

```
"Invalid authorization header format"
Path: /api/auth/me
```

This happens when the `{{accessToken}}` variable is empty or not set.

## ✅ Quick Fix

### Step 1: Check Your Token

In Postman:

1. Click the **👁️ eye icon** (top right) - "View Variables"
2. Look at the `accessToken` row
3. Is it **empty**? Then you need to login!

### Step 2: Get a Token

Run this request:

1. Go to: **Authentication** → **Register User**
2. Click **Send**
3. **Status should be:** `201 Created`
4. **Response should have:** `access_token` and `refresh_token`

### Step 3: Verify Token Was Saved

Click the 👁️ eye icon again:

**Before Login:**
```
accessToken: ""  ← Empty!
```

**After Login:**
```
accessToken: "eyJhbGc..."  ← Long string!
```

### Step 4: Try Get Current User Again

Now run: **Authentication** → **Get Current User**

✅ Should work!

---

## 🔍 Detailed Steps

### 1️⃣ Run Register User

Request: `POST {{baseUrl}}/api/auth/register`

Body:
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "Test@123456",
  "profile": {
    "name": "Test User",
    "preferences": ["electronics", "books"]
  }
}
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2️⃣ Check Environment Variables

Click the **👁️ eye icon**:

You should see:
```
✅ accessToken: eyJhbGc... (has value)
✅ refreshToken: eyJhbGc... (has value)
✅ userId: 47c506ff-ed15-47ba-af6e-4bd1ae7e27d6 (has value)
```

### 3️⃣ Test Get Current User

Request: `GET {{baseUrl}}/api/auth/me`

**Should return:**
```json
{
  "user_id": "...",
  "email": "test@example.com",
  "username": "testuser",
  ...
}
```

---

## ⚠️ Troubleshooting

### Issue: Token Still Empty After Register

**Possible causes:**

1. **Wrong environment selected**
   - Top right dropdown
   - Should show: "Zyra Vision Shop - Local Environment"

2. **Test script didn't run**
   - Check collection has the correct test script
   - Script should contain: `pm.environment.set('accessToken', ...)`

3. **Collection not imported**
   - Re-import `postman_collection.json`

**Fix:**
```bash
# Re-import collection
1. Delete old collection
2. Import backend/tests/postman_collection.json again
3. Run Register User
```

### Issue: "Username already taken"

You registered before! Use **Login** instead:

1. Go to: **Authentication** → **Login User**
2. Body:
```json
{
  "username": "testuser",
  "password": "Test@123456"
}
```
3. Click **Send**

### Issue: Wrong Port

Your backend might be on a different port.

**Check:**
1. Look at `baseUrl` in environment variables
2. Should be: `http://localhost:8005`
3. Your backend should be running on port 8005

**Start backend:**
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8005
```

---

## 🎯 Quick Reference

### Check Token
```
Click: 👁️ (eye icon)
Look at: accessToken
Should have: Long string starting with "eyJ..."
Empty? = Problem! Need to login
```

### Get Token
```
Run: Authentication → Register User
Or: Authentication → Login User
Then: Click 👁️ eye icon → Token should appear!
```

### Test Token
```
Run: Authentication → Get Current User
If 200 OK: Token works! ✅
If 401: Token empty or invalid ❌
```

---

## 🔄 Complete Fix Workflow

```
1. Start backend: python -m uvicorn app.main:app --reload --port 8005
2. Open Postman
3. Import collection + environment ✅
4. Select environment: "Zyra Vision Shop - Local Environment"
5. Run: Authentication → Register User
6. Click 👁️ eye icon → Verify accessToken has value
7. Run: Authentication → Get Current User
8. Should work! ✅
```

---

## 📝 Manual Token (If Auto-Save Fails)

If tokens aren't auto-saving, manually set them:

1. Run Register/Login
2. Copy the `access_token` from response
3. Go to: Environments → Zyra Vision Shop - Local Environment
4. Find `accessToken` variable
5. Paste the token value
6. Click Save

---

## 🆘 Still Not Working?

1. **Restart Postman** - Sometimes caching issues
2. **Restart backend** - Fresh start
3. **Check environment selected** - Top right corner
4. **Verify collection imported** - Should see "Zyra Vision Shop - API Tests"
5. **Check backend running** - Should show "Application startup complete"
6. **Try different port** - Maybe backend on 8000, try that

---

## ✅ Success Indicators

You'll know it's working when:

1. ✅ Register returns `201 Created`
2. ✅ 👁️ eye icon shows `accessToken` with long value
3. ✅ Get Current User returns `200 OK` with user data
4. ✅ No more "Invalid authorization header format" errors

---

## 📚 See Also

- [Postman Quick Start](POSTMAN_QUICKSTART.md)
- [Postman Auth Help](POSTMAN_NO_AUTH_ERRORS.md)
- [Full Postman Guide](docs/POSTMAN_GUIDE.md)

---

**Remember: Always login first before accessing protected endpoints! 🔐**

