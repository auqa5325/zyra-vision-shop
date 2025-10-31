# Postman Quick Start - 5 Minutes

## Step 1: Open Postman

Download: [postman.com/downloads](https://www.postman.com/downloads)

## Step 2: Import Collection

1. Click **Import** button (top left)
2. Select **Upload Files**
3. Choose:
   - `backend/tests/postman_collection.json`
   - `backend/tests/postman_environment.json`
4. Click **Import**

## Step 3: Select Environment

Top right corner:
- Click dropdown (shows "No Environment")
- Select **"Zyra Vision Shop - Local Environment"**

## Step 4: Start Backend

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Wait for: `Application startup complete`

## Step 5: Run First Test

1. Expand collection: **Zyra Vision Shop - API Tests**
2. Go to folder: **Health & Status**
3. Click: **Root Endpoint**
4. Click: **Send** button (blue, top right)

✅ You should see: `"status": "running"`

## Step 6: Register User

1. Go to: **Authentication** folder
2. Click: **Register User**
3. Click: **Send**

✅ Tokens automatically saved! Check **Environment** variables.

## Step 7: Get Products

1. Go to: **Products** folder
2. Click: **List Products**
3. Click: **Send**

✅ You should see product list!

## Step 8: Run All Tests

1. Right-click **"Zyra Vision Shop - API Tests"** (collection name)
2. Select **"Run collection"**
3. Click **Run Zyra Vision Shop...**

✅ Watch all tests run automatically!

---

## That's It! 🎉

You've successfully:
- ✅ Imported collection
- ✅ Connected to API
- ✅ Run your first tests
- ✅ Used automatic token management

## Test Data & Examples

📄 **[POSTMAN_TEST_DATA.md](POSTMAN_TEST_DATA.md)** - All test values ready to copy!

Includes:
- ✅ Login credentials
- ✅ Product examples
- ✅ Interaction data
- ✅ Review templates
- ✅ Search queries
- ✅ Quick copy-paste values

## Next Steps

- Try different API endpoints
- See full guide: `docs/POSTMAN_GUIDE.md`
- Explore recommendation endpoints
- Copy test data: `POSTMAN_TEST_DATA.md`

## Common Issues

**"401 Unauthorized" errors** ⚠️
→ **You need to login first!** See: [POSTMAN_NO_AUTH_ERRORS.md](POSTMAN_NO_AUTH_ERRORS.md)
→ Quick fix: Run "Register User" or "Login User" to get tokens

**"Could not get response"**
→ Backend not running! Start it with `python -m uvicorn app.main:app --reload --port 8005`

**Can't find files**
→ Make sure you're in the project root directory

---

For detailed instructions, see: **`docs/POSTMAN_GUIDE.md`**

