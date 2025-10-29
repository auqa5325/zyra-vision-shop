# Local Development Setup (No AWS Required)

## 🚀 Quick Start - Local Development

This guide shows how to run the Zyra backend with **local file storage** (no AWS required).

### 1. Environment Setup

Create a `.env` file with minimal configuration:

**Option 1: Full Connection String (Recommended)**
```bash
# Required - Database
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/zyra_db

# Required - JWT Authentication
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-minimum-32-characters

# Optional - Leave empty for local storage
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
S3_BUCKET_NAME=

# API Settings
DEBUG=true
ENVIRONMENT=development
```

**Option 2: Individual Database Components**
```bash
# Required - Database (individual components)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=zyra_db
DB_USER=postgres
DB_PASSWORD=your_password

# Required - JWT Authentication
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-minimum-32-characters

# Optional - Leave empty for local storage
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
S3_BUCKET_NAME=

# API Settings
DEBUG=true
ENVIRONMENT=development
```

### 2. Database Setup (Local PostgreSQL)

```bash
# Install PostgreSQL (macOS)
brew install postgresql
brew services start postgresql

# Create database
createdb zyra_db
```

### 3. Run Setup Commands

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Test connectivity (will use local storage)
python scripts/test_connectivity.py

# 3. Initialize database
python scripts/init_db.py

# 4. Generate mock data
python scripts/generate_mock_data.py

# 5. Train ML models
python scripts/train_and_store_models.py

# 6. Start API
python app/main.py
```

### 4. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Register user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123"}'

# Get recommendations
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/recommendations/hybrid?k=5"
```

## 📁 Local Storage Structure

```
backend/
├── uploads/                    # Local image storage
│   └── products/
│       └── {product_id}/
│           ├── original_abc123.jpg
│           └── thumbnail_def456.jpg
├── artifacts/                  # ML models
│   ├── faiss_products.index
│   ├── product_embeddings.npy
│   └── sentence_transformer_model/
└── logs/                       # Application logs
```

## 🌐 Image URLs

Images uploaded locally will be accessible at:
- **URL Format**: `http://localhost:8000/static/uploads/products/{product_id}/{filename}`
- **Example**: `http://localhost:8000/static/uploads/products/123e4567-e89b-12d3-a456-426614174000/original_abc123.jpg`

## 🔄 Switching to S3 Later

When you're ready to use S3 in production:

1. Add AWS credentials to `.env`:
   ```bash
   AWS_ACCESS_KEY_ID=your-key
   AWS_SECRET_ACCESS_KEY=your-secret
   S3_BUCKET_NAME=your-bucket
   ```

2. Restart the API - it will automatically detect S3 and switch over

## ✅ What Works Without AWS

- ✅ **All recommendation engines** (content-based, collaborative, hybrid)
- ✅ **User authentication** (JWT)
- ✅ **Product management** (CRUD operations)
- ✅ **Image uploads** (stored locally)
- ✅ **Search functionality** (semantic search)
- ✅ **User interactions** (tracking, analytics)
- ✅ **Mock data generation**

## 🚀 Production Deployment

For production, you can still use local storage or switch to S3:

### Option 1: Continue with Local Storage
- Images stored on server filesystem
- Use reverse proxy (nginx) to serve static files
- Backup uploads directory regularly

### Option 2: Switch to S3
- Add AWS credentials to production environment
- Images automatically migrate to S3
- Better scalability and CDN integration

## 🛠️ Troubleshooting

### Images Not Loading
- Check if `uploads/` directory exists
- Verify FastAPI static file mounting
- Check file permissions

### Storage Service Issues
- Run `python scripts/test_connectivity.py`
- Check logs for storage service initialization
- Verify directory creation permissions

This setup gives you a fully functional recommendation API without any AWS dependencies!
