# Avoiding 401 Errors in Postman

If you're seeing 401 errors, you haven't logged in yet! Here's how to fix it:

## 🚨 The Problem

401 errors mean:
- **"Authorization header required"** = No token provided
- **"Could not validate credentials"** = Invalid/expired token

These are **normal** if you haven't logged in yet!

---

## ✅ The Solution: Login First!

### Step 1: Register or Login

You need to get tokens first. Run this request:

**Go to:** `Authentication` → `Register User`

**Or:** `Authentication` → `Login User`

**Send the request!**

### Step 2: Check That Tokens Are Saved

After Login/Register succeeds:

1. Click the **👁️ eye icon** in the right sidebar (View Variables)
2. You should see:
   - ✓ `accessToken` has a long string value
   - ✓ `refreshToken` has a long string value  
   - ✓ `userId` has a UUID value

**If tokens are empty:** Re-run Register/Login

### Step 3: Now Try Other Requests

Once tokens are saved, all other requests should work!

---

## 🎯 Correct Order to Run Tests

```
1. Health & Status → Root Endpoint ✅ (no auth needed)
2. Health & Status → Health Check ✅ (no auth needed)
3. Authentication → Register User ⚠️ RUN THIS FIRST!
4. Now ALL other requests will work with tokens ✓
```

---

## 🔧 Quick Fix: Re-Authenticate

If you're getting 401 errors:

### Option 1: Run Register Again

1. Go to **Authentication** → **Register User**
2. Click **Send**
3. Tokens will refresh automatically
4. Try your request again

### Option 2: Run Login

If you already registered:

1. Go to **Authentication** → **Login User**  
2. Click **Send**
3. Tokens will refresh automatically

---

## 📋 Which Endpoints Need Auth?

### ✅ NO Auth Required (Always Work)

These work without logging in:
- `GET /` (Root)
- `GET /health`
- `GET /metrics`
- `GET /api/products/` (List products)
- `GET /api/products/search`
- `GET /api/products/{id}`
- `GET /api/products/categories/`

### 🔒 Auth Required (Need Login First)

These need `{{accessToken}}`:
- `GET /api/auth/me`
- `POST /api/interactions/`
- `POST /api/reviews`
- `GET /api/users/{id}/stats`
- `PATCH /api/users/{id}/profile`
- Most recommendation endpoints
- All user-specific data

---

## 🧪 Test If Your Token Works

After logging in, try this test:

1. Go to **Authentication** → **Get Current User**
2. Click **Send**
3. You should get your user profile back
4. ✅ Status: **200 OK**

If this works, your token is good! 🎉

---

## 🐛 Common Auth Mistakes

### Mistake 1: Running Protected Endpoints First

```
❌ Don't do this:
1. List Products → Works (no auth)
2. Create Interaction → 401 ERROR! (needs auth)
3. Register User → Too late!

✅ Do this instead:
1. Register User → Get tokens
2. List Products → Works
3. Create Interaction → Works with tokens!
```

### Mistake 2: Wrong Environment Selected

Check the top-right corner shows:
- **"Zyra Vision Shop - Local Environment"** ✓

If it says "No Environment", select the correct one!

### Mistake 3: Empty Token Value

Check your variables:
- Click the 👁️ eye icon
- Look at `accessToken`
- If it's empty (""), re-run Register/Login

### Mistake 4: Token Expired

Tokens expire after some time. Just:
1. Run **Login User** again
2. Tokens refresh automatically
3. Keep testing!

---

## 📖 Step-by-Step: First Time User

Follow these steps in order:

### 1. Start Backend

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8005
```

### 2. Open Postman

- Import collection ✅
- Select environment ✅
- Make sure baseUrl is `http://localhost:8005` ✓

### 3. Test Connection (No Auth)

```
Request: GET /
Expected: 200 OK with "status": "running"
```

### 4. Register User (GET AUTH)

```
Request: POST /api/auth/register
Body: Use values from POSTMAN_TEST_DATA.md
Expected: 201 Created with tokens
Check: Variables should auto-populate ✓
```

### 5. Verify Token Works

```
Request: GET /api/auth/me
Expected: 200 OK with your user data
```

### 6. Now You Can Test Everything!

All requests should work now because you have a token ✓

---

## 💡 Pro Tips

1. **Always start with Register/Login** in a new session
2. **Check variables** using the 👁️ icon to verify tokens
3. **Re-run Login** if something stops working
4. **Don't worry about 401s** on the first try - just login!
5. **Collection Runner**: Login runs automatically before other tests

---

## 🎯 Summary

**TL;DR:**

1. 🔐 **Login first** → `Authentication` → `Register User`
2. ✓ **Check tokens** → Click 👁️ eye icon, verify `accessToken` has value
3. ✅ **Test freely** → All other requests now work!

**The 401 errors you saw are normal - you just need to authenticate first!**

---

## 🆘 Still Having Issues?

1. **Re-import** the collection and environment
2. **Restart** your backend server
3. **Check** you're on the right environment
4. **Verify** port 8005 matches your backend
5. **See** [Full Guide](docs/POSTMAN_GUIDE.md) for details

---

**Remember: Auth first, everything else second! 🚀**

