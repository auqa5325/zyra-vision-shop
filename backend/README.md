# Backend API

FastAPI-based backend for Zyra Vision Shop with AI-powered recommendations.

## Features

- 🚀 FastAPI with async support
- 🤖 ML-powered recommendation engine
- 💬 Chatbot integration
- 🔐 JWT authentication
- 📊 User interaction tracking
- 🖼️ Image generation and management
- 📈 Analytics and insights

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/refresh` - Refresh token

### Products
- `GET /products` - Get products with filtering
- `GET /products/{id}` - Get product details
- `POST /products` - Create product (admin)

### Recommendations
- `GET /recommendations` - Get personalized recommendations
- `GET /recommendations/hybrid` - Get hybrid recommendations

### Chatbot
- `POST /chatbot/message` - Send message to chatbot

### User Data
- `GET /user-data` - Get user data
- `POST /user-data` - Update user data

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp env.example .env
# Edit .env with your configuration
```

3. Initialize database:
```bash
python scripts/init_db.py
```

4. Train ML models:
```bash
python scripts/train_and_store_models.py
```

5. Run the server:
```bash
python -m uvicorn app.main:app --reload
```

## Development

- Run tests: `python run_tests.py`
- Generate sample data: `python scripts/generate_mock_data.py`
- Monitor logs: `tail -f backend.log`

## Architecture

- **FastAPI**: Web framework
- **PostgreSQL**: Primary database
- **Redis**: Caching and sessions
- **ML Models**: Collaborative filtering + content-based
- **AWS S3**: Image storage
- **Celery**: Background tasks (optional)
