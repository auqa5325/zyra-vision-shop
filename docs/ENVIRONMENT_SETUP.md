# Zyra Backend Environment Setup Guide

## 🚀 Quick Start

```bash
# 1. Run setup script
python setup.py

# 2. Edit .env file with your values
# 3. Test connectivity
python scripts/test_connectivity.py

# 4. Initialize database
python scripts/init_db.py

# 5. Generate mock data
python scripts/generate_mock_data.py

# 6. Train ML models
python scripts/train_and_store_models.py

# 7. Start API
python app/main.py
```

## 📋 Required Environment Variables

Create a `.env` file with these variables:

### Database Configuration
```bash
# PostgreSQL Database (AWS RDS or local)
DATABASE_URL=postgresql+psycopg2://username:password@host:port/database_name

# Example for AWS RDS:
DATABASE_URL=postgresql+psycopg2://zyra_user:your_password@zyra-db.cluster-xyz.us-east-1.rds.amazonaws.com:5432/zyra_db

# Example for local PostgreSQL:
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/zyra_db
```

### JWT Authentication
```bash
# JWT Secret Key (generate a strong random key)
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production-minimum-32-characters

# JWT Configuration
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

### AWS Configuration (Optional - for S3 storage)
```bash
# AWS Credentials (optional - will use local storage if not provided)
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_REGION=us-east-1

# S3 Bucket for image storage (optional)
S3_BUCKET_NAME=zyra-product-images
```

**Note**: AWS credentials are now **optional**. If not provided, the system will automatically use local file storage instead of S3.

### Application Configuration
```bash
# Application Settings
DEBUG=true
ENVIRONMENT=development
```

### ML Model Configuration
```bash
# ML Models (these are defaults, can be changed)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
FAISS_INDEX_PATH=artifacts/faiss_products.index
EMBEDDINGS_PATH=artifacts/product_embeddings.npy
ALS_FACTORS_PATH=artifacts/item_factors.npy
DEFAULT_ALPHA=0.6
DEFAULT_TOP_K=10
```

## 🗄️ Database Setup

### Option 1: AWS RDS PostgreSQL

1. **Create RDS Instance**:
   - Engine: PostgreSQL
   - Instance class: db.t3.micro (free tier)
   - Storage: 20 GB
   - Database name: `zyra_db`
   - Username: `zyra_user`
   - Password: (generate strong password)

2. **Security Group**:
   - Allow inbound PostgreSQL (port 5432) from your IP
   - Or from EC2 security group if deploying on EC2

3. **Connection String**:
   ```bash
   DATABASE_URL=postgresql+psycopg2://zyra_user:password@zyra-db.cluster-xyz.us-east-1.rds.amazonaws.com:5432/zyra_db
   ```

### Option 2: Local PostgreSQL

1. **Install PostgreSQL**:
   ```bash
   # macOS
   brew install postgresql
   brew services start postgresql
   
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   sudo systemctl start postgresql
   ```

2. **Create Database**:
   ```sql
   sudo -u postgres psql
   CREATE DATABASE zyra_db;
   CREATE USER zyra_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE zyra_db TO zyra_user;
   \q
   ```

3. **Connection String**:
   ```bash
   DATABASE_URL=postgresql+psycopg2://zyra_user:password@localhost:5432/zyra_db
   ```

## 🪣 Storage Options

### Option 1: Local File Storage (Default - No AWS Required)

The system automatically uses local file storage if AWS credentials are not provided:

- **Upload Directory**: `uploads/products/`
- **Public URLs**: `http://localhost:8000/static/uploads/products/`
- **No AWS Account Required**
- **Perfect for Development**

### Option 2: AWS S3 Storage (Optional)

If you want to use AWS S3 for production:

### 1. Create S3 Bucket

```bash
# Using AWS CLI
aws s3 mb s3://zyra-product-images --region us-east-1

# Or using AWS Console
# - Go to S3 service
# - Create bucket
# - Name: zyra-product-images
# - Region: us-east-1
# - Block public access: Uncheck (for public image access)
```

### 2. Configure Bucket Policy

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::zyra-product-images/*"
        }
    ]
}
```

### 3. Create IAM User

1. **Create IAM User**:
   - Username: `zyra-backend-user`
   - Access type: Programmatic access

2. **Attach Policy**:
   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Effect": "Allow",
               "Action": [
                   "s3:GetObject",
                   "s3:PutObject",
                   "s3:DeleteObject",
                   "s3:ListBucket"
               ],
               "Resource": [
                   "arn:aws:s3:::zyra-product-images",
                   "arn:aws:s3:::zyra-product-images/*"
               ]
           }
       ]
   }
   ```

3. **Save Credentials**:
   - Access Key ID
   - Secret Access Key

## 🔧 Environment Setup Commands

### Generate JWT Secret Key
```bash
# Generate a secure random key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Test All Connections
```bash
python scripts/test_connectivity.py
```

### Initialize Database Schema
```bash
python scripts/init_db.py
```

### Generate Mock Data
```bash
python scripts/generate_mock_data.py
```

### Train ML Models (Local Storage)
```bash
python scripts/train_and_store_models.py
```

## 🚀 Production Environment

### Environment Variables for Production
```bash
# Production settings
DEBUG=false
ENVIRONMENT=production

# Strong JWT secret (use environment variable)
JWT_SECRET_KEY=${JWT_SECRET_KEY}

# Production database
DATABASE_URL=${DATABASE_URL}

# Production S3 bucket
S3_BUCKET_NAME=zyra-prod-images
```

### Docker Environment
```bash
# Build image
docker build -t zyra-backend .

# Run with environment file
docker run -p 8000:8000 --env-file .env zyra-backend
```

## 🧪 Testing Your Setup

### 1. Test Database Connection
```bash
python -c "
from app.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT 1'))
    print('✅ Database connection successful')
"
```

### 2. Test S3 Connection
```bash
python -c "
import boto3
from app.config import settings
s3 = boto3.client('s3', 
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.aws_region
)
s3.head_bucket(Bucket=settings.s3_bucket_name)
print('✅ S3 connection successful')
"
```

### 3. Test API Endpoints
```bash
# Start API
python app/main.py

# Test health endpoint
curl http://localhost:8000/health

# Test authentication
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123"}'
```

## 📊 Expected File Structure After Setup

```
backend/
├── .env                          # Your environment variables
├── artifacts/                    # ML models (created after training)
│   ├── faiss_products.index     # FAISS index
│   ├── product_embeddings.npy   # Product embeddings
│   ├── item_factors.npy         # ALS item factors
│   ├── user_factors.npy         # ALS user factors
│   ├── product_ids.npy          # Product ID mapping
│   ├── sentence_transformer_model/  # Local Sentence Transformer
│   ├── als_mappings.json        # ALS user/item mappings
│   └── model_info.json          # Model metadata
├── logs/                        # Application logs
└── data/                        # Data storage
    ├── embeddings/
    └── models/
```

## ⚠️ Troubleshooting

### Common Issues

1. **Database Connection Failed**:
   - Check DATABASE_URL format
   - Verify database is running
   - Check firewall/security group settings

2. **S3 Access Denied**:
   - Verify AWS credentials
   - Check bucket policy
   - Ensure IAM user has correct permissions

3. **JWT Token Errors**:
   - Ensure JWT_SECRET_KEY is set
   - Check token expiration settings

4. **Model Loading Failed**:
   - Run `python scripts/train_and_store_models.py`
   - Check artifacts directory exists

### Getting Help

1. Run connectivity test: `python scripts/test_connectivity.py`
2. Check logs in `logs/` directory
3. Verify all environment variables are set correctly
4. Ensure all dependencies are installed: `pip install -r requirements.txt`
