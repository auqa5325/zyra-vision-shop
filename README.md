# Zyra Vision Shop - Complete Project Overview

A modern e-commerce platform with AI-powered recommendations and chatbot integration.

## 📁 Project Directory Structure

```
zyra-vision-shop/
├── 📁 backend/                          # Python FastAPI Backend
│   ├── 📁 app/                          # Main Application Code
│   │   ├── 📁 __pycache__/              # Python Cache Files
│   │   ├── 📁 api/                      # API Endpoints (16 files)
│   │   │   ├── 📄 auth.py               # Authentication endpoints
│   │   │   ├── 📄 images.py             # Image handling endpoints
│   │   │   ├── 📄 interactions.py       # User interaction tracking
│   │   │   ├── 📄 products.py           # Product management endpoints
│   │   │   ├── 📄 recommendations.py    # ML recommendation endpoints
│   │   │   ├── 📄 reviews.py            # Review system endpoints
│   │   │   ├── 📄 schema.py             # Database schema endpoints
│   │   │   ├── 📄 session_interactions.py # Session tracking
│   │   │   ├── 📄 user_data.py          # User data management
│   │   │   ├── 📄 user_states.py        # User state management
│   │   │   └── 📄 users.py              # User management endpoints
│   │   ├── 📁 middleware/               # Custom Middleware
│   │   │   ├── 📄 __init__.py
│   │   │   └── 📄 auth.py               # JWT Authentication middleware
│   │   ├── 📁 ml/                       # Machine Learning Components
│   │   │   ├── 📄 __init__.py
│   │   │   └── 📄 model_loader.py       # ML model loading and management
│   │   ├── 📁 models/                   # SQLAlchemy Database Models (7 files)
│   │   │   ├── 📄 product.py            # Product and Category models
│   │   │   ├── 📄 user.py               # User model
│   │   │   ├── 📄 interaction.py        # User interaction models
│   │   │   ├── 📄 review.py             # Review system models
│   │   │   ├── 📄 session.py            # Session tracking models
│   │   │   ├── 📄 user_state.py         # User state models
│   │   │   └── 📄 recommendation.py     # Recommendation models
│   │   ├── 📁 schemas/                  # Pydantic Schemas (6 files)
│   │   │   ├── 📄 product.py           # Product validation schemas
│   │   │   ├── 📄 user.py              # User validation schemas
│   │   │   ├── 📄 auth.py              # Authentication schemas
│   │   │   ├── 📄 interaction.py       # Interaction schemas
│   │   │   ├── 📄 review.py            # Review schemas
│   │   │   └── 📄 recommendation.py    # Recommendation schemas
│   │   ├── 📁 services/                 # Business Logic Services (12 files)
│   │   │   ├── 📄 auth_service.py      # Authentication service
│   │   │   ├── 📄 content_based_service.py # Content-based recommendations
│   │   │   ├── 📄 collaborative.py      # Collaborative filtering
│   │   │   ├── 📄 hybrid_recommendation_service.py # Hybrid ML recommendations
│   │   │   ├── 📄 hybrid_storage.py    # AWS S3 + Local storage
│   │   │   ├── 📄 image_service.py     # Image processing
│   │   │   ├── 📄 interaction_service.py # User interaction tracking
│   │   │   ├── 📄 product_service.py   # Product management
│   │   │   ├── 📄 recommendation_service.py # Recommendation orchestration
│   │   │   ├── 📄 review_service.py    # Review management
│   │   │   ├── 📄 simple_session_logger.py # Session logging
│   │   │   └── 📄 user_service.py      # User management
│   │   ├── 📄 config.py                 # Application configuration
│   │   ├── 📄 database.py              # Database connection setup
│   │   └── 📄 main.py                  # FastAPI application entry point
│   ├── 📁 artifacts/                   # ML Models and Data
│   │   ├── 📄 als_mappings.json        # ALS model mappings
│   │   ├── 📄 als_mappings.npy          # ALS mappings numpy array
│   │   ├── 📄 faiss_products_binary.index # FAISS binary index
│   │   ├── 📄 faiss_products.index     # FAISS product index
│   │   ├── 📄 item_factors.npy         # ALS item factors
│   │   ├── 📄 model_info.json          # Model metadata
│   │   ├── 📄 product_embeddings.npy    # Product embeddings
│   │   ├── 📄 product_ids.npy          # Product ID mappings
│   │   ├── 📄 sentence_transformer_model/ # Sentence transformer model
│   │   └── 📄 user_factors.npy         # ALS user factors
│   ├── 📁 scripts/                     # Utility Scripts
│   │   ├── 📁 data-generation/          # Data generation scripts (13 files)
│   │   ├── 📁 ml/                      # ML training scripts (3 files)
│   │   ├── 📁 migration/               # Database migration scripts (3 files)
│   │   ├── 📁 monitoring/               # Monitoring scripts (4 files)
│   │   ├── 📄 build_faiss_index.py     # FAISS index builder
│   │   ├── 📄 create_user_state_tables.py # User state table creator
│   │   ├── 📄 fix_image_mapping.py     # Image mapping fixer
│   │   ├── 📄 init_db.py               # Database initializer
│   │   ├── 📄 restart_s3_migration.py  # S3 migration restarter
│   │   ├── 📄 setup_auth.py            # Authentication setup
│   │   └── 📄 sync_interactions_to_user_states.py # Data sync script
│   ├── 📁 tests/                       # Backend Tests
│   │   ├── 📄 conftest.py              # Test configuration
│   │   ├── 📄 test_auth.py             # Authentication tests
│   │   ├── 📄 test_images.py           # Image handling tests
│   │   ├── 📄 test_interactions.py     # Interaction tracking tests
│   │   ├── 📄 test_ml_services.py      # ML service tests
│   │   ├── 📄 test_products.py         # Product management tests
│   │   └── 📄 test_recommendations.py  # Recommendation system tests
│   ├── 📄 docker-compose.yml          # Docker Compose configuration
│   ├── 📄 Dockerfile                   # Docker container definition
│   ├── 📄 env.example                  # Environment variables template
│   ├── 📄 print_complete_schema.py     # Schema printer
│   ├── 📄 print_schemas.py             # Schema documentation
│   ├── 📄 pytest.ini                  # Pytest configuration
│   ├── 📄 README.md                    # Backend documentation
│   ├── 📄 requirements.txt             # Python dependencies
│   ├── 📄 run_tests.py                # Test runner
│   ├── 📄 sample_products.json        # Sample product data
│   └── 📄 setup.py                    # Package setup
├── 📁 src/                             # React Frontend
│   ├── 📁 components/                  # React Components
│   │   ├── 📁 ui/                      # shadcn/ui Components (50 files)
│   │   │   ├── 📄 accordion.tsx        # Accordion component
│   │   │   ├── 📄 alert-dialog.tsx     # Alert dialog component
│   │   │   ├── 📄 avatar.tsx           # Avatar component
│   │   │   ├── 📄 badge.tsx            # Badge component
│   │   │   ├── 📄 button.tsx           # Button component
│   │   │   ├── 📄 card.tsx             # Card component
│   │   │   ├── 📄 carousel.tsx         # Carousel component
│   │   │   ├── 📄 checkbox.tsx         # Checkbox component
│   │   │   ├── 📄 collapsible.tsx      # Collapsible component
│   │   │   ├── 📄 command.tsx          # Command component
│   │   │   ├── 📄 context-menu.tsx      # Context menu component
│   │   │   ├── 📄 dialog.tsx           # Dialog component
│   │   │   ├── 📄 dropdown-menu.tsx    # Dropdown menu component
│   │   │   ├── 📄 form.tsx              # Form component
│   │   │   ├── 📄 hover-card.tsx       # Hover card component
│   │   │   ├── 📄 input.tsx            # Input component
│   │   │   ├── 📄 label.tsx            # Label component
│   │   │   ├── 📄 menubar.tsx          # Menu bar component
│   │   │   ├── 📄 navigation-menu.tsx  # Navigation menu component
│   │   │   ├── 📄 popover.tsx          # Popover component
│   │   │   ├── 📄 progress.tsx         # Progress component
│   │   │   ├── 📄 radio-group.tsx      # Radio group component
│   │   │   ├── 📄 scroll-area.tsx      # Scroll area component
│   │   │   ├── 📄 select.tsx           # Select component
│   │   │   ├── 📄 separator.tsx        # Separator component
│   │   │   ├── 📄 sheet.tsx            # Sheet component
│   │   │   ├── 📄 slider.tsx           # Slider component
│   │   │   ├── 📄 switch.tsx           # Switch component
│   │   │   ├── 📄 table.tsx            # Table component
│   │   │   ├── 📄 tabs.tsx             # Tabs component
│   │   │   ├── 📄 textarea.tsx         # Textarea component
│   │   │   ├── 📄 toast.tsx            # Toast component
│   │   │   ├── 📄 toggle.tsx           # Toggle component
│   │   │   ├── 📄 tooltip.tsx          # Tooltip component
│   │   │   └── 📄 utils.ts             # UI utilities
│   │   ├── 📄 AuthModal.tsx            # Authentication modal
│   │   ├── 📄 AutocompleteSuggestions.tsx # Search autocomplete
│   │   ├── 📄 CategoryCard.tsx         # Category display card
│   │   ├── 📄 ChatBot.tsx              # AI chatbot component
│   │   ├── 📄 ErrorBoundary.tsx        # Error boundary wrapper
│   │   ├── 📄 FAQ.tsx                  # FAQ section
│   │   ├── 📄 FilterModal.tsx          # Product filter modal
│   │   ├── 📄 Footer.tsx               # Site footer
│   │   ├── 📄 Header.tsx               # Site header
│   │   ├── 📄 HeroCarousel.tsx          # Hero banner carousel
│   │   ├── 📄 LoginForm.tsx            # Login form component
│   │   ├── 📄 ProductCard.tsx          # Product display card
│   │   ├── 📄 ReviewSection.tsx        # Product reviews section
│   │   ├── 📄 SearchInput.tsx          # Search input component
│   │   ├── 📄 SortModal.tsx            # Product sorting modal
│   │   ├── 📄 SubcategorySection.tsx   # Subcategory display
│   │   ├── 📄 TopPicksCarousel.tsx     # Top picks carousel
│   │   └── 📄 TopRecommendation.tsx    # Top recommendation display
│   ├── 📁 contexts/                    # React Context Providers
│   │   └── 📄 AuthContext.tsx          # Authentication context
│   ├── 📁 hooks/                       # Custom React Hooks
│   │   ├── 📄 use-mobile.tsx          # Mobile detection hook
│   │   ├── 📄 use-toast.ts             # Toast notification hook
│   │   ├── 📄 useAuth.ts               # Authentication hook
│   │   ├── 📄 useCart.ts               # Shopping cart hook
│   │   ├── 📄 useProducts.ts           # Product data hook
│   │   ├── 📄 useProductsForCategories.ts # Category products hook
│   │   ├── 📄 useRecommendations.ts    # Recommendation hook
│   │   ├── 📄 useSearchSuggestions.ts  # Search suggestions hook
│   │   ├── 📄 useUserDataSync.ts       # User data sync hook
│   │   └── 📄 useWishlist.ts           # Wishlist hook
│   ├── 📁 pages/                       # Page Components
│   │   ├── 📄 CartPage.tsx             # Shopping cart page
│   │   ├── 📄 CategoryPage.tsx         # Category listing page
│   │   ├── 📄 Index.tsx                # Home page
│   │   ├── 📄 LoginPage.tsx            # Login page
│   │   ├── 📄 NotFound.tsx             # 404 error page
│   │   ├── 📄 ProductPage.tsx          # Product detail page
│   │   ├── 📄 ProfilePage.tsx          # User profile page
│   │   ├── 📄 SearchResults.tsx        # Search results page
│   │   ├── 📄 UserDashboard.tsx        # User dashboard
│   │   └── 📄 WishlistPage.tsx         # Wishlist page
│   ├── 📁 services/                    # API Service Layer (11 files)
│   │   ├── 📄 api.ts                   # Base API client
│   │   ├── 📄 authService.ts           # Authentication service
│   │   ├── 📄 cartService.ts           # Cart management service
│   │   ├── 📄 chatbotService.ts        # Chatbot integration service
│   │   ├── 📄 dualTrackingService.ts   # Dual tracking service
│   │   ├── 📄 interactionService.ts    # Interaction tracking service
│   │   ├── 📄 productService.ts        # Product management service
│   │   ├── 📄 recommendationService.ts # Recommendation service
│   │   ├── 📄 reviewService.ts         # Review management service
│   │   ├── 📄 userService.ts           # User management service
│   │   └── 📄 wishlistService.ts       # Wishlist service
│   ├── 📁 types/                       # TypeScript Type Definitions
│   │   ├── 📄 api.ts                   # API response types
│   │   └── 📄 product.ts               # Product-related types
│   ├── 📁 utils/                       # Utility Functions
│   │   └── 📄 authUtils.ts             # Authentication utilities
│   ├── 📁 assets/                      # Static Assets
│   │   ├── 📄 hero-deals.jpg           # Hero banner image
│   │   ├── 📄 hero-electronics.jpg     # Electronics hero image
│   │   └── 📄 hero-wearables.jpg       # Wearables hero image
│   ├── 📄 App.css                      # Global styles
│   ├── 📄 App.tsx                      # Main App component
│   ├── 📄 index.css                    # Base styles
│   ├── 📄 main.tsx                     # Application entry point
│   └── 📄 vite-env.d.ts                # Vite environment types
├── 📁 docs/                            # Documentation
│   ├── 📄 CHATBOT_INTEGRATION.md       # Chatbot integration guide
│   ├── 📄 ENVIRONMENT_SETUP.md        # Environment setup guide
│   ├── 📄 LOCAL_DEVELOPMENT.md        # Local development guide
│   ├── 📄 PERSONALIZED_HYBRID_RECOMMENDATION_SYSTEM.md # ML system docs
│   └── 📄 PRODUCT_GENERATION_SUMMARY.md # Product generation docs
├── 📁 public/                          # Public Static Assets
│   ├── 📄 favicon.ico                  # Site favicon
│   ├── 📄 placeholder.svg              # Placeholder image
│   └── 📄 robots.txt                   # SEO robots file
├── 📁 dist/                            # Built Frontend Assets
│   ├── 📁 assets/                      # Compiled assets
│   │   ├── 📄 hero-deals-C6aazFAW.jpg # Optimized hero images
│   │   ├── 📄 hero-electronics-DI_nAoCS.jpg
│   │   ├── 📄 hero-wearables-BL9iuEld.jpg
│   │   ├── 📄 index-DEPCUg95.js        # Compiled JavaScript
│   │   └── 📄 index-vGe6eUiI.css      # Compiled CSS
│   ├── 📄 favicon.ico
│   ├── 📄 index.html                   # Built HTML
│   ├── 📄 placeholder.svg
│   └── 📄 robots.txt
├── 📄 .gitignore                       # Git ignore rules
├── 📄 components.json                  # shadcn/ui configuration
├── 📄 DATABASE_SCHEMA.md              # Database schema documentation
├── 📄 eslint.config.js                 # ESLint configuration
├── 📄 index.html                       # Development HTML template
├── 📄 package.json                     # Node.js dependencies
├── 📄 package-lock.json               # Dependency lock file
├── 📄 postcss.config.js               # PostCSS configuration
├── 📄 README.md                        # Project documentation
├── 📄 STANDARDIZED_EVENT_TYPES.md     # Event tracking documentation
├── 📄 tailwind.config.ts              # Tailwind CSS configuration
├── 📄 tsconfig.app.json               # TypeScript app configuration
├── 📄 tsconfig.json                    # TypeScript configuration
├── 📄 tsconfig.node.json               # TypeScript node configuration
└── 📄 vite.config.ts                  # Vite build configuration
```

## 🚀 Key Features

- **🛍️ Modern E-commerce Interface**: React-based responsive design
- **🤖 AI-Powered Recommendations**: Hybrid ML recommendation system
- **💬 Integrated Chatbot**: Gemini AI-powered shopping assistant
- **🔍 Advanced Search**: Semantic search with FAISS vector similarity
- **📱 Responsive Design**: Mobile-first approach with Tailwind CSS
- **🔐 User Authentication**: JWT-based authentication system
- **📊 Analytics & Tracking**: Comprehensive user interaction tracking
- **☁️ Cloud Integration**: AWS S3 for image storage
- **🐳 Containerized**: Docker support for easy deployment

## 🛠️ Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **shadcn/ui** component library
- **React Query** for state management
- **React Router** for navigation
- **Lucide React** for icons

### Backend
- **Python 3.9+** with FastAPI
- **PostgreSQL** database
- **SQLAlchemy 2.0** ORM
- **Redis** for caching
- **JWT** authentication
- **AWS S3** for file storage
- **Docker** containerization

### Machine Learning
- **Sentence Transformers** for embeddings
- **FAISS** for vector similarity search
- **Implicit** for collaborative filtering
- **scikit-learn** for ML utilities
- **NumPy & Pandas** for data processing

## 📋 Important Code Snippets

### Backend - FastAPI Main Application

```python:backend/app/main.py
"""
FastAPI Main Application
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import time
import logging

from app.config import settings
from app.middleware import JWTAuthMiddleware
from app.api import (
    products_router,
    recommendations_router,
    interactions_router,
    users_router,
    reviews_router
)
from app.api.auth import router as auth_router
from app.api.images import router as images_router
from app.api.schema import router as schema_router
from app.api.user_data import router as user_data_router
from app.api.user_states import router as user_states_router
from app.api.session_interactions import router as session_interactions_router
from app.ml.model_loader import model_loader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Zyra AI Recommendation API",
    description="AI-powered hybrid recommendation system combining content-based and collaborative filtering",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
         "http://localhost:8001", 
        "http://localhost:8080", 
        "http://localhost:8081", 
        "http://localhost:8082",
        "http://127.0.0.1:8081",
        "http://127.0.0.1:8082",
        "http://localhost:3000",  # Common React dev port
        "http://localhost:5173",
        "http://3.110.143.60:8080",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add JWT authentication middleware
app.add_middleware(JWTAuthMiddleware)

@app.on_event("startup")
async def startup_event():
    """Load ML models on startup"""
    logger.info("Starting Zyra API...")
    
    # Temporarily disable model loading to test startup
    logger.info("✅ Skipping ML model loading for now")

@app.get("/", tags=["health"])
async def root():
    """Root endpoint"""
    return {
        "message": "Zyra AI Recommendation API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    try:
        # Check if models are loaded
        faiss_index = model_loader.get_faiss_index()
        sentence_transformer = model_loader.get_sentence_transformer()
        
        return {
            "status": "healthy",
            "models_loaded": True,
            "faiss_vectors": faiss_index.ntotal,
            "embedding_model": settings.embedding_model
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "models_loaded": False,
                "error": str(e)
            }
        )

# Include API routers
app.include_router(auth_router)
app.include_router(images_router)
app.include_router(schema_router)
app.include_router(session_interactions_router)
app.include_router(products_router)
app.include_router(recommendations_router)
app.include_router(interactions_router)
app.include_router(users_router)
app.include_router(user_data_router)
app.include_router(user_states_router)
app.include_router(reviews_router)
```

### Backend - Configuration Management

```python:backend/app/config.py
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database - Primary method (full connection string)
    database_url: Optional[str] = None
    
    # Database - Alternative method (individual components)
    db_host: Optional[str] = None
    db_port: Optional[int] = None
    db_name: Optional[str] = None
    db_user: Optional[str] = None
    db_password: Optional[str] = None
    
    # AWS (Optional - will use local storage if not provided)
    aws_region: str = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    s3_bucket_name: Optional[str] = None
    
    # Application Settings
    debug: bool = False
    environment: str = "development"
    
    # JWT Authentication
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # ML Models
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    faiss_index_path: str = "artifacts/faiss_products.index"
    embeddings_path: str = "artifacts/product_embeddings.npy"
    als_factors_path: str = "artifacts/item_factors.npy"
    
    # Recommendation
    default_alpha: float = 0.6
    default_top_k: int = 10
    
    # Gemini AI
    gemini_api_key: Optional[str] = None
    
    def get_database_url(self) -> str:
        """Get database URL, building from components if needed"""
        if self.database_url:
            return self.database_url
        
        # Build from individual components
        if all([self.db_host, self.db_port, self.db_name, self.db_user]):
            password_part = f":{self.db_password}" if self.db_password else ""
            return f"postgresql+psycopg2://{self.db_user}{password_part}@{self.db_host}:{self.db_port}/{self.db_name}"
        
        raise ValueError("Either DATABASE_URL or all individual DB components must be provided")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env

# Global settings instance
settings = Settings()
```

### Backend - Product Model

```python:backend/app/models/product.py
from sqlalchemy import Column, String, Boolean, DateTime, JSON, Integer, Numeric, ForeignKey, BigInteger, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid

class Category(Base):
    __tablename__ = "categories"
    
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.category_id"), nullable=True)
    
    # Relationships
    products = relationship("Product", back_populates="category")
    parent = relationship("Category", remote_side=[category_id])

class Product(Base):
    __tablename__ = "products"
    
    product_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku = Column(String, unique=True, nullable=True)
    name = Column(String, nullable=False)
    short_description = Column(String, nullable=True)
    long_description = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    price = Column(Numeric(10, 2), nullable=True)
    discount_percent = Column(Numeric(5, 2), nullable=True, default=0)
    currency = Column(String, default="INR")
    brand = Column(String, nullable=True)
    available = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    metadata_json = Column(JSON, nullable=True)
    
    # Relationships
    category = relationship("Category", back_populates="products")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="product")
    
    # New user state relationships
    cart_items = relationship("UserCart", back_populates="product", cascade="all, delete-orphan")
    wishlist_items = relationship("UserWishlist", back_populates="product", cascade="all, delete-orphan")
    purchase_history = relationship("PurchaseHistory", back_populates="product", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")

class ProductImage(Base):
    __tablename__ = "product_images"
    
    image_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    s3_key = Column(String, nullable=False)
    cdn_url = Column(String, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    format = Column(String, nullable=True)
    variant = Column(String, nullable=True)  # original, thumb, small, webp
    alt_text = Column(String, nullable=True)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="images")
```

### Backend - ML Model Loader

```python:backend/app/ml/model_loader.py
"""
ML Model Loader - Loads pre-trained models at startup
"""

import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import Optional, Dict, Any
from app.config import settings

class ModelLoader:
    """Singleton class to load and manage ML models"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.faiss_index: Optional[faiss.Index] = None
            self.product_ids: Optional[np.ndarray] = None
            self.sentence_transformer: Optional[SentenceTransformer] = None
            self.user_factors: Optional[np.ndarray] = None
            self.item_factors: Optional[np.ndarray] = None
            self.als_mappings: Optional[Dict[str, Any]] = None
            self._initialized = True
    
    def load_models(self):
        """Load all ML models and artifacts"""
        print("Loading ML models...")
        
        try:
            # Load FAISS index
            self._load_faiss_index()
            
            # Load Sentence Transformer
            self._load_sentence_transformer()
            
            # Load ALS factors
            self._load_als_factors()
            
            print("✅ All ML models loaded successfully!")
            
        except Exception as e:
            print(f"❌ Error loading ML models: {e}")
            raise
    
    def _load_faiss_index(self):
        """Load FAISS index and product IDs"""
        index_path = settings.faiss_index_path
        product_ids_path = "artifacts/product_ids.npy"
        
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"FAISS index not found: {index_path}")
        
        if not os.path.exists(product_ids_path):
            raise FileNotFoundError(f"Product IDs not found: {product_ids_path}")
        
        self.faiss_index = faiss.read_index(index_path)
        self.product_ids = np.load(product_ids_path, allow_pickle=True)
        
        print(f"✅ Loaded FAISS index with {self.faiss_index.ntotal} vectors")
    
    def _load_sentence_transformer(self):
        """Load Sentence Transformer model"""
        # Try to load locally stored model first
        local_model_path = "artifacts/sentence_transformer_model"
        
        if os.path.exists(local_model_path):
            self.sentence_transformer = SentenceTransformer(local_model_path)
            print(f"✅ Loaded local Sentence Transformer from {local_model_path}")
        else:
            # Fallback to downloading from Hugging Face
            self.sentence_transformer = SentenceTransformer(settings.embedding_model)
            print(f"✅ Loaded Sentence Transformer from Hugging Face: {settings.embedding_model}")
    
    def _load_als_factors(self):
        """Load ALS factors and mappings"""
        user_factors_path = "artifacts/user_factors.npy"
        item_factors_path = settings.als_factors_path
        mappings_path = "artifacts/als_mappings.json"
        
        if not os.path.exists(user_factors_path):
            raise FileNotFoundError(f"User factors not found: {user_factors_path}")
        
        if not os.path.exists(item_factors_path):
            raise FileNotFoundError(f"Item factors not found: {item_factors_path}")
        
        if not os.path.exists(mappings_path):
            raise FileNotFoundError(f"ALS mappings not found: {mappings_path}")
        
        self.user_factors = np.load(user_factors_path)
        self.item_factors = np.load(item_factors_path)
        
        # Load mappings from JSON
        import json
        with open(mappings_path, 'r') as f:
            self.als_mappings = json.load(f)
        
        print(f"✅ Loaded ALS factors: {self.user_factors.shape[0]} users, {self.item_factors.shape[0]} items")
    
    def get_faiss_index(self) -> faiss.Index:
        """Get FAISS index"""
        if self.faiss_index is None:
            raise RuntimeError("FAISS index not loaded")
        return self.faiss_index
    
    def get_product_ids(self) -> np.ndarray:
        """Get product IDs array"""
        if self.product_ids is None:
            raise RuntimeError("Product IDs not loaded")
        return self.product_ids
    
    def get_sentence_transformer(self) -> SentenceTransformer:
        """Get Sentence Transformer model"""
        if self.sentence_transformer is None:
            raise RuntimeError("Sentence Transformer not loaded")
        return self.sentence_transformer
    
    def get_als_factors(self) -> tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """Get ALS factors and mappings"""
        if self.user_factors is None or self.item_factors is None or self.als_mappings is None:
            raise RuntimeError("ALS factors not loaded")
        return self.user_factors, self.item_factors, self.als_mappings

# Global model loader instance
model_loader = ModelLoader()
```

### Frontend - Main App Component

```tsx:src/App.tsx
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { AuthProvider } from "@/contexts/AuthContext";
import Index from "./pages/Index";
import CategoryPage from "./pages/CategoryPage";
import ProductPage from "./pages/ProductPage";
import LoginPage from "./pages/LoginPage";
import ProfilePage from "./pages/ProfilePage";
import CartPage from "./pages/CartPage";
import WishlistPage from "./pages/WishlistPage";
import NotFound from "./pages/NotFound";
import SearchResults from "./pages/SearchResults";

const App = () => {
  return (
    <AuthProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter
          future={{
            v7_startTransition: true,
            v7_relativeSplatPath: true,
          }}
        >
          <ErrorBoundary>
            <Routes>
              <Route path="/" element={<Index />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/cart" element={<CartPage />} />
              <Route path="/wishlist" element={<WishlistPage />} />
              <Route path="/purchases" element={<ProfilePage />} />
              <Route path="/category/:categoryId" element={<CategoryPage />} />
              <Route path="/product/:productId" element={<ProductPage />} />
              <Route path="/search" element={<SearchResults />} />
              {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </ErrorBoundary>
        </BrowserRouter>
      </TooltipProvider>
    </AuthProvider>
  );
};

export default App;
```

### Frontend - Authentication Context

```tsx:src/contexts/AuthContext.tsx
import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { authService, User } from '@/services/authService';

interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
}

interface AuthContextType extends AuthState {
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    user: null,
    token: null,
    isLoading: false,
    error: null,
  });

  // Load stored auth state after component mounts
  useEffect(() => {
    const loadStoredAuth = () => {
      try {
        const storedToken = localStorage.getItem('accessToken');
        const storedUser = localStorage.getItem('user');
        
        if (storedToken && storedUser) {
          const user = JSON.parse(storedUser);
          setAuthState(prev => ({
            ...prev,
            isAuthenticated: true,
            user,
            token: storedToken,
          }));
        }
      } catch (error) {
        console.error('Failed to load stored auth state:', error);
        // Clear invalid data
        localStorage.removeItem('accessToken');
        localStorage.removeItem('user');
        localStorage.removeItem('refreshToken');
      }
    };

    loadStoredAuth();
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    setAuthState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const response = await authService.login({ username, password });
      
      // Get user info from authService (it already calls getCurrentUser)
      const user = authService.getCurrentUserSync();
      
      // Update state
      setAuthState({
        isAuthenticated: true,
        user,
        token: response.access_token,
        isLoading: false,
        error: null,
      });
      
      // Save to localStorage (authService already saves, but ensure consistency)
      localStorage.setItem('accessToken', response.access_token);
      localStorage.setItem('refreshToken', response.refresh_token);
      localStorage.setItem('user', JSON.stringify(user));
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Login failed';
      console.error('❌ [AUTH CONTEXT] Login failed:', errorMessage);
      setAuthState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
      throw err;
    }
  }, []);

  const logout = useCallback(async () => {
    setAuthState(prev => ({ ...prev, isLoading: true }));
    
    try {
      await authService.logout();
    } catch (error) {
      console.error('❌ [AUTH CONTEXT] Logout error:', error);
    } finally {
      // Clear state and storage regardless of API call success
      setAuthState({
        isAuthenticated: false,
        user: null,
        token: null,
        isLoading: false,
        error: null,
      });
      
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('user');
    }
  }, []);

  const value: AuthContextType = {
    ...authState,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    // During development/hot reload, sometimes context is undefined temporarily
    // Return a default context to prevent crashes
    if (process.env.NODE_ENV === 'development') {
      console.warn('useAuth called outside AuthProvider, returning default context');
      return {
        isAuthenticated: false,
        user: null,
        token: null,
        isLoading: false,
        error: null,
        login: async () => {},
        logout: async () => {}
      };
    }
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

### Frontend - Product Service

```typescript:src/services/productService.ts
/**
 * Product API service
 */

import apiClient from './api';
import { Product } from '../types/product';
import { CategoryHierarchy, Category } from '../types/api';

export interface ProductListParams {
  skip?: number;
  limit?: number;
  category_id?: number;
  min_price?: number;
  max_price?: number;
  available_only?: boolean;
}

export interface ProductImage {
  image_id: string;
  product_id: string;
  s3_key: string;
  cdn_url?: string;
  width?: number;
  height?: number;
  format?: string;
  variant?: string;
  alt_text?: string;
  is_primary: boolean;
  created_at: string;
}

export interface BackendProduct {
  product_id: string;
  sku?: string;
  name: string;
  short_description?: string;
  long_description?: string;
  category_id?: number;
  tags?: string[];
  price?: number | string; // Can be number or string from API
  discount_percent?: number | string; // Can be number or string from API
  currency: string;
  brand?: string;
  available: boolean;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
  images: ProductImage[];
  image_url?: string;
  rating?: number;
}

export interface ProductDetail extends BackendProduct {
  category?: Category;
}

class ProductService {
  private categoryCache: Map<number, string> = new Map();

  /**
   * Get list of products with optional filters
   */
  async getProducts(params: ProductListParams = {}): Promise<Product[]> {
    const backendProducts = await apiClient.get<BackendProduct[]>('/api/products/', params);
    return backendProducts.map(this.transformProduct);
  }

  /**
   * Get a single product by ID
   */
  async getProductById(id: string): Promise<Product> {
    const backendProduct = await apiClient.get<ProductDetail>(`/api/products/${id}`);
    return this.transformProduct(backendProduct);
  }

  /**
   * Get categories with hierarchical structure
   */
  async getCategoriesHierarchy(): Promise<CategoryHierarchy[]> {
    const hierarchy = await apiClient.get<CategoryHierarchy[]>('/api/products/categories/hierarchy');
    // Update category cache
    this.updateCategoryCache(hierarchy);
    return hierarchy;
  }

  /**
   * Get all categories
   */
  async getCategories(): Promise<Category[]> {
    const categories = await apiClient.get<Category[]>('/api/products/categories/');
    // Update category cache
    categories.forEach(cat => this.categoryCache.set(cat.category_id, cat.name));
    return categories;
  }

  /**
   * Search products by query
   */
  async searchProducts(query: string, k: number = 10): Promise<Product[]> {
    const backendProducts = await apiClient.get<BackendProduct[]>('/api/products/search', {
      q: query,
      k
    });
    return backendProducts.map(this.transformProduct);
  }

  /**
   * Get products by category (handles both parent and subcategories)
   */
  async getProductsByCategory(categoryId: number, params: Omit<ProductListParams, 'category_id'> = {}): Promise<Product[]> {
    const backendProducts = await apiClient.get<BackendProduct[]>(`/api/products/categories/${categoryId}/products`, params);
    return backendProducts.map(this.transformProduct);
  }

  /**
   * Update category cache from hierarchy data
   */
  private updateCategoryCache(hierarchy: CategoryHierarchy[]): void {
    hierarchy.forEach(category => {
      this.categoryCache.set(category.category_id, category.name);
      category.children.forEach(child => {
        this.categoryCache.set(child.category_id, child.name);
      });
    });
  }

  /**
   * Transform backend product to frontend Product format
   */
  private transformProduct = (backendProduct: BackendProduct | ProductDetail): Product => {
    // Get primary image URL
    let imageUrl = backendProduct.image_url;
    if (!imageUrl && backendProduct.images && backendProduct.images.length > 0) {
      const primaryImage = backendProduct.images.find(img => img.is_primary) || backendProduct.images[0];
      imageUrl = primaryImage.cdn_url || '';
    }

    // Use actual rating from database (defaults to 0 if no reviews)
    const rating = backendProduct.rating || 0;

    return {
      product_id: backendProduct.product_id,
      name: backendProduct.name,
      description: backendProduct.short_description || backendProduct.long_description || '',
      price: typeof backendProduct.price === 'string' ? parseFloat(backendProduct.price) : (backendProduct.price || 0),
      discount_percent: typeof backendProduct.discount_percent === 'string' ? parseFloat(backendProduct.discount_percent) : (backendProduct.discount_percent || 0),
      image_url: imageUrl || '/placeholder.svg',
      rating,
      category: this.getCategoryName(backendProduct.category_id),
      category_id: backendProduct.category_id,
      brand: backendProduct.brand,
      reason_features: {
        matched_tags: backendProduct.tags || [],
        cf_score: 0.8, // Mock collaborative filtering score
        content_score: 0.9, // Mock content-based score
      }
    };
  }

  /**
   * Get category name by ID using dynamic cache
   */
  private getCategoryName = (categoryId?: number): string => {
    return categoryId ? this.categoryCache.get(categoryId) || 'Other' : 'Other';
  }
}

export const productService = new ProductService();
export default productService;
```

### Frontend - Product Card Component

```tsx:src/components/ProductCard.tsx
import { Star, ShoppingCart, Info, Heart } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Product } from "@/types/product";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { DiscountPrice } from "@/components/ui/DiscountPrice";
import { interactionService } from "@/services/interactionService";
import { useCart } from "@/hooks/useCart";
import { useWishlist } from "@/hooks/useWishlist";
import { useAuth } from "@/contexts/AuthContext";
import { AuthModal } from "@/components/AuthModal";

interface ProductCardProps {
  product: Product;
}

export const ProductCard = ({ product }: ProductCardProps) => {
  const navigate = useNavigate();
  const { addToCart } = useCart();
  const { toggleWishlist, isInWishlist } = useWishlist();
  const { user } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authAction, setAuthAction] = useState<"cart" | "wishlist">("cart");
  
  const isWishlisted = isInWishlist(product.product_id);
  
  const renderStars = (rating: number) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;

    for (let i = 0; i < 5; i++) {
      if (i < fullStars) {
        stars.push(
          <Star key={i} className="h-4 w-4 fill-primary text-primary" />
        );
      } else if (i === fullStars && hasHalfStar) {
        stars.push(
          <Star key={i} className="h-4 w-4 fill-primary/50 text-primary" />
        );
      } else {
        stars.push(
          <Star key={i} className="h-4 w-4 text-muted-foreground" />
        );
      }
    }
    return stars;
  };

  const handleCardClick = () => {
    interactionService.trackClick(product.product_id);
    navigate(`/product/${product.product_id}`);
  };

  const handleAddToCart = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!user) {
      setAuthAction("cart");
      setShowAuthModal(true);
      return;
    }
    addToCart(product);
  };

  const handleWishlistToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!user) {
      setAuthAction("wishlist");
      setShowAuthModal(true);
      return;
    }
    toggleWishlist(product);
  };

  return (
    <div 
      className="group relative bg-card rounded-xl border overflow-hidden hover:shadow-card transition-all duration-300 hover:-translate-y-1 animate-fade-in-up cursor-pointer"
      onClick={handleCardClick}
    >
      {/* Product Image */}
      <div className="relative aspect-square overflow-hidden bg-muted">
        <img
          src={product.image_url}
          alt={product.name}
          className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
        />
        {product.reason_features && (
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <button className="absolute top-2 right-2 p-2 bg-background/80 backdrop-blur-sm rounded-full hover:bg-background transition-colors">
                  <Info className="h-4 w-4 text-primary" />
                </button>
              </TooltipTrigger>
              <TooltipContent side="left" className="max-w-xs">
                <p className="font-semibold mb-1">Why this?</p>
                {product.reason_features.matched_tags && (
                  <p className="text-xs text-muted-foreground">
                    Matches: {product.reason_features.matched_tags.join(", ")}
                  </p>
                )}
                {product.reason_features.cf_score && (
                  <p className="text-xs text-muted-foreground">
                    Recommendation score: {(product.reason_features.cf_score * 100).toFixed(0)}%
                  </p>
                )}
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        )}
        
        {/* Wishlist Button */}
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <button 
                className="absolute top-2 left-2 p-2 bg-background/80 backdrop-blur-sm rounded-full hover:bg-background transition-colors"
                onClick={handleWishlistToggle}
              >
                <Heart 
                  className={`h-4 w-4 transition-colors ${
                    isWishlisted 
                      ? "fill-red-500 text-red-500" 
                      : "text-muted-foreground hover:text-red-500"
                  }`} 
                />
              </button>
            </TooltipTrigger>
            <TooltipContent side="right">
              <p>{isWishlisted ? "Remove from wishlist" : "Add to wishlist"}</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>

      {/* Product Info */}
      <div className="p-4">
        <h3 className="font-semibold text-foreground mb-1 line-clamp-2 group-hover:text-primary transition-colors">
          {product.name}
        </h3>
        <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
          {product.description}
        </p>

        {/* Rating */}
        <div className="flex items-center gap-2 mb-3">
          <div className="flex gap-0.5">{renderStars(product.rating)}</div>
          <span className="text-sm text-muted-foreground">
            ({product.rating.toFixed(1)})
          </span>
        </div>

        {/* Price and CTA */}
        <div className="flex items-center justify-between">
          <DiscountPrice 
            price={product.price}
            discountPercent={product.discount_percent}
            size="2xl"
            layout="vertical"
            alignment="left"
            className="flex-1"
          />
          <Button 
            size="sm" 
            variant="gradient" 
            className="gap-2"
            onClick={handleAddToCart}
          >
            <ShoppingCart className="h-4 w-4" />
            Add
          </Button>
        </div>
      </div>
      
      <AuthModal 
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        action={authAction}
      />
    </div>
  );
};
```

### Frontend - ChatBot Component

```tsx:src/components/ChatBot.tsx
import { useState, useEffect } from "react";
import { MessageCircle, X, Send, RotateCcw, Loader2, ShoppingCart, Heart, ExternalLink, Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { DiscountPrice } from "@/components/ui/DiscountPrice";
import { chatbotService, ChatMessage, ProductSuggestion } from "@/services/chatbotService";
import { useAuth } from "@/hooks/useAuth";
import { useCart } from "@/hooks/useCart";
import { useWishlist } from "@/hooks/useWishlist";
import { productService } from "@/services/productService";
import { dualTrackingService } from "@/services/dualTrackingService";
import { useNavigate } from "react-router-dom";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  products?: ProductSuggestion[];
}

export const ChatBot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content: "Hi! I'm Zyra, your AI shopping assistant powered by Gemini. How can I help you find the perfect product today?",
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isHealthy, setIsHealthy] = useState(true);
  const [productDetails, setProductDetails] = useState<Record<string, any>>({});
  const [loadingProducts, setLoadingProducts] = useState<Set<string>>(new Set());
  
  const { user } = useAuth();
  const { addToCart } = useCart();
  const { addToWishlist } = useWishlist();
  const navigate = useNavigate();

  // Check chatbot health on component mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const healthy = await chatbotService.checkHealth();
        setIsHealthy(healthy);
        if (!healthy) {
          console.warn('⚠️ [CHATBOT] Service is not healthy');
        }
      } catch (error) {
        console.error('❌ [CHATBOT] Health check failed:', error);
        setIsHealthy(false);
      }
    };
    
    checkHealth();
  }, []);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: inputValue,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    try {
      // Convert messages to ChatMessage format
      const chatMessages: ChatMessage[] = [...messages, userMessage].map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      // Send to Gemini API
      const response = await chatbotService.sendMessage(chatMessages, user?.user_id);
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.message,
        products: response.products
      };
      
      setMessages((prev) => [...prev, aiMessage]);
      
      // Add suggestions if available
      if (response.suggestions && response.suggestions.length > 0) {
        const suggestionMessage: Message = {
          id: (Date.now() + 2).toString(),
          role: "assistant",
          content: `💡 Suggestions: ${response.suggestions.join(", ")}`,
        };
        setMessages((prev) => [...prev, suggestionMessage]);
      }
      
    } catch (error) {
      console.error('❌ [CHATBOT] Error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: chatbotService.getErrorMessage().content,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRestart = () => {
    setMessages([
      {
        id: "1",
        role: "assistant",
        content: chatbotService.getInitialMessage().content,
      },
    ]);
  };

  // Handle adding to cart
  const handleAddToCart = async (product: ProductSuggestion) => {
    try {
      const productDetails = await productService.getProductById(product.product_id);
      const result = await dualTrackingService.addToCart(productDetails, 1);
      
      if (result.success) {
        // Add success message to chat
        const successMessage: Message = {
          id: Date.now().toString(),
          role: "assistant",
          content: `✅ Added "${product.name}" to your cart!`,
        };
        setMessages(prev => [...prev, successMessage]);
      } else {
        throw new Error(result.message);
      }
    } catch (error) {
      console.error('Failed to add to cart:', error);
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: `❌ Failed to add "${product.name}" to cart. Please try again.`,
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  // Handle adding to wishlist
  const handleAddToWishlist = async (product: ProductSuggestion) => {
    try {
      const productDetails = await productService.getProductById(product.product_id);
      const result = await dualTrackingService.addToWishlist(productDetails);
      
      if (result.success) {
        // Add success message to chat
        const successMessage: Message = {
          id: Date.now().toString(),
          role: "assistant",
          content: `❤️ Added "${product.name}" to your wishlist!`,
        };
        setMessages(prev => [...prev, successMessage]);
      } else {
        throw new Error(result.message);
      }
    } catch (error) {
      console.error('Failed to add to wishlist:', error);
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: `❌ Failed to add "${product.name}" to wishlist. Please try again.`,
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  // Handle viewing product details
  const handleViewProduct = (productId: string) => {
    navigate(`/product/${productId}`);
    setIsOpen(false); // Close chatbot when navigating
  };

  return (
    <>
      {/* Floating Button */}
      <Button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-glow z-40"
        variant="gradient"
        size="icon"
      >
        <MessageCircle className="h-6 w-6" />
      </Button>

      {/* Chat Drawer */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 animate-fade-in"
            onClick={() => setIsOpen(false)}
          />

          {/* Drawer */}
          <div className="fixed top-0 right-0 h-full w-full md:w-96 bg-background border-l shadow-2xl z-50 flex flex-col animate-slide-in-right">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b bg-gradient-to-r from-primary/5 to-secondary/5">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                  <MessageCircle className="h-5 w-5 text-primary-foreground" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground">Zyra AI</h3>
                  <p className="text-xs text-muted-foreground">
                    Powered by Gemini {isHealthy ? "🟢" : "🔴"}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleRestart}
                  className="h-8 w-8"
                >
                  <RotateCcw className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setIsOpen(false)}
                  className="h-8 w-8"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Messages */}
            <ScrollArea className="flex-1 p-4">
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${
                      message.role === "user" ? "justify-end" : "justify-start"
                    } animate-fade-in`}
                  >
                    <div
                      className={`max-w-[80%] rounded-2xl px-4 py-2 ${
                        message.role === "user"
                          ? "bg-gradient-to-r from-primary to-secondary text-primary-foreground"
                          : "bg-muted text-foreground"
                      }`}
                    >
                      <p className="text-sm">{message.content}</p>
                      
                      {/* Product Suggestions */}
                      {message.products && message.products.length > 0 && (
                        <div className="mt-3 space-y-3">
                          <p className="text-xs font-medium text-muted-foreground">Recommended Products:</p>
                          {message.products.map((product) => {
                            const details = productDetails[product.product_id];
                            const isLoading = loadingProducts.has(product.product_id);
                            
                            return (
                              <Card key={product.product_id} className="bg-background/50 border-muted hover:border-primary/20 transition-colors">
                                <CardContent className="p-4">
                                  <div className="flex items-start gap-3">
                                    {product.image_url && (
                                      <img
                                        src={product.image_url}
                                        alt={product.name}
                                        className="w-16 h-16 rounded-lg object-cover flex-shrink-0"
                                      />
                                    )}
                                    <div className="flex-1 min-w-0">
                                      <div className="flex items-start justify-between gap-2">
                                        <div className="flex-1 min-w-0">
                                          <h4 className="text-sm font-medium truncate">{product.name}</h4>
                                          <div className="flex items-center gap-2 mt-1">
                                            <DiscountPrice 
                                              price={product.price}
                                              discountPercent={product.discount_percent}
                                              size="sm"
                                              layout="compact"
                                              alignment="left"
                                            />
                                            {details && (
                                              <div className="flex items-center gap-1">
                                                <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                                                <span className="text-xs text-muted-foreground">{details.rating?.toFixed(1) || '0.0'}</span>
                                              </div>
                                            )}
                                          </div>
                                          {details && (
                                            <div className="flex items-center gap-1 mt-1">
                                              <Badge variant="secondary" className="text-xs px-1 py-0">
                                                {details.category || 'General'}
                                              </Badge>
                                            </div>
                                          )}
                                          <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{product.reason}</p>
                                        </div>
                                        <div className="flex flex-col gap-1">
                                          <Button 
                                            size="sm" 
                                            variant="outline" 
                                            className="h-8 w-8 p-0 hover:bg-primary hover:text-primary-foreground"
                                            onClick={() => handleAddToCart(product)}
                                            disabled={isLoading}
                                          >
                                            <ShoppingCart className="h-4 w-4" />
                                          </Button>
                                          <Button 
                                            size="sm" 
                                            variant="outline" 
                                            className="h-8 w-8 p-0 hover:bg-red-500 hover:text-white"
                                            onClick={() => handleAddToWishlist(product)}
                                            disabled={isLoading}
                                          >
                                            <Heart className="h-4 w-4" />
                                          </Button>
                                          <Button 
                                            size="sm" 
                                            variant="outline" 
                                            className="h-8 w-8 p-0 hover:bg-blue-500 hover:text-white"
                                            onClick={() => handleViewProduct(product.product_id)}
                                          >
                                            <ExternalLink className="h-4 w-4" />
                                          </Button>
                                        </div>
                                      </div>
                                      {isLoading && (
                                        <div className="flex items-center gap-2 mt-2">
                                          <Loader2 className="h-3 w-3 animate-spin" />
                                          <span className="text-xs text-muted-foreground">Loading details...</span>
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                </CardContent>
                              </Card>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              {isLoading && (
                <div className="flex justify-start animate-fade-in">
                  <div className="max-w-[80%] rounded-2xl px-4 py-2 bg-muted text-foreground">
                    <div className="flex items-center gap-2">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <p className="text-sm">Zyra is thinking...</p>
                    </div>
                  </div>
                </div>
              )}
            </ScrollArea>

            {/* Input */}
            <div className="p-4 border-t bg-muted/30">
              <div className="flex gap-2">
                <Input
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
                  placeholder="Ask Zyra anything..."
                  className="flex-1 bg-background"
                  disabled={isLoading}
                />
                <Button
                  onClick={handleSendMessage}
                  variant="gradient"
                  size="icon"
                  className="shrink-0"
                  disabled={isLoading || !inputValue.trim()}
                >
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
              </div>
              <p className="text-xs text-muted-foreground mt-2 text-center">
                Powered by Gemini AI • Always learning
              </p>
            </div>
          </div>
        </>
      )}
    </>
  );
};
```

### Frontend - Custom Hooks

```typescript:src/hooks/useProducts.ts
/**
 * Custom hooks for product data fetching with React Query
 */

import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { Product, ProductListParams, SearchParams, CategoryHierarchy, Category } from '../types/api';
import { productService } from '../services/productService';

// Query keys
export const productKeys = {
  all: ['products'] as const,
  lists: () => [...productKeys.all, 'list'] as const,
  list: (params: ProductListParams) => [...productKeys.lists(), params] as const,
  details: () => [...productKeys.all, 'detail'] as const,
  detail: (id: string) => [...productKeys.details(), id] as const,
  categories: () => [...productKeys.all, 'categories'] as const,
  search: (params: SearchParams) => [...productKeys.all, 'search', params] as const,
};

/**
 * Hook to fetch products with optional filters
 */
export function useProducts(params: ProductListParams = {}): UseQueryResult<Product[], Error> {
  return useQuery({
    queryKey: productKeys.list(params),
    queryFn: () => productService.getProducts(params),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

/**
 * Hook to fetch a single product by ID
 */
export function useProduct(productId: string): UseQueryResult<Product, Error> {
  return useQuery({
    queryKey: productKeys.detail(productId),
    queryFn: () => productService.getProductById(productId),
    enabled: !!productId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to fetch categories with hierarchical structure
 */
export function useCategoriesHierarchy(): UseQueryResult<CategoryHierarchy[], Error> {
  return useQuery({
    queryKey: [...productKeys.categories(), 'hierarchy'],
    queryFn: () => productService.getCategoriesHierarchy(),
    staleTime: 10 * 60 * 1000, // 10 minutes - categories don't change often
  });
}

/**
 * Hook to fetch all categories
 */
export function useCategories(): UseQueryResult<Category[], Error> {
  return useQuery({
    queryKey: productKeys.categories(),
    queryFn: () => productService.getCategories(),
    staleTime: 10 * 60 * 1000, // 10 minutes - categories don't change often
  });
}

/**
 * Hook to search products
 */
export function useProductSearch(params: SearchParams): UseQueryResult<Product[], Error> {
  return useQuery({
    queryKey: productKeys.search(params),
    queryFn: () => productService.searchProducts(params.query, params.k),
    enabled: !!params.query && params.query.length > 0,
    staleTime: 1 * 60 * 1000, // 1 minute
  });
}

/**
 * Hook to fetch products by category
 */
export function useProductsByCategory(
  categoryId: number, 
  params: Omit<ProductListParams, 'category_id'> = {}
): UseQueryResult<Product[], Error> {
  return useQuery({
    queryKey: productKeys.list({ ...params, category_id: categoryId }),
    queryFn: () => productService.getProductsByCategory(categoryId, params),
    enabled: !!categoryId,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}
```

### Configuration Files

#### Package.json (Frontend Dependencies)

```json:package.json
{
  "name": "vite_react_shadcn_ts",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "build:dev": "vite build --mode development",
    "lint": "eslint .",
    "preview": "vite preview"
  },
  "dependencies": {
    "@hookform/resolvers": "^3.10.0",
    "@radix-ui/react-accordion": "^1.2.11",
    "@radix-ui/react-alert-dialog": "^1.1.14",
    "@radix-ui/react-aspect-ratio": "^1.1.7",
    "@radix-ui/react-avatar": "^1.1.10",
    "@radix-ui/react-checkbox": "^1.3.2",
    "@radix-ui/react-collapsible": "^1.1.11",
    "@radix-ui/react-context-menu": "^2.2.15",
    "@radix-ui/react-dialog": "^1.1.14",
    "@radix-ui/react-dropdown-menu": "^2.1.15",
    "@radix-ui/react-hover-card": "^1.1.14",
    "@radix-ui/react-label": "^2.1.7",
    "@radix-ui/react-menubar": "^1.1.15",
    "@radix-ui/react-navigation-menu": "^1.2.13",
    "@radix-ui/react-popover": "^1.1.14",
    "@radix-ui/react-progress": "^1.1.7",
    "@radix-ui/react-radio-group": "^1.3.7",
    "@radix-ui/react-scroll-area": "^1.2.9",
    "@radix-ui/react-select": "^2.2.5",
    "@radix-ui/react-separator": "^1.1.7",
    "@radix-ui/react-slider": "^1.3.5",
    "@radix-ui/react-slot": "^1.2.3",
    "@radix-ui/react-switch": "^1.2.5",
    "@radix-ui/react-tabs": "^1.1.12",
    "@radix-ui/react-toast": "^1.2.14",
    "@radix-ui/react-toggle": "^1.1.9",
    "@radix-ui/react-toggle-group": "^1.1.10",
    "@radix-ui/react-tooltip": "^1.2.7",
    "@tanstack/react-query": "^5.83.0",
    "axios": "^1.12.2",
    "class-variance-authority": "^0.7.1",
    "clsx": "^2.1.1",
    "cmdk": "^1.1.1",
    "date-fns": "^3.6.0",
    "embla-carousel-react": "^8.6.0",
    "input-otp": "^1.4.2",
    "lucide-react": "^0.462.0",
    "next-themes": "^0.3.0",
    "react": "^18.3.1",
    "react-day-picker": "^8.10.1",
    "react-dom": "^18.3.1",
    "react-hook-form": "^7.61.1",
    "react-resizable-panels": "^2.1.9",
    "react-router-dom": "^6.30.1",
    "recharts": "^2.15.4",
    "sonner": "^1.7.4",
    "tailwind-merge": "^2.6.0",
    "tailwindcss-animate": "^1.0.7",
    "vaul": "^0.9.9",
    "zod": "^3.25.76"
  },
  "devDependencies": {
    "@eslint/js": "^9.32.0",
    "@tailwindcss/typography": "^0.5.16",
    "@types/node": "^22.16.5",
    "@types/react": "^18.3.23",
    "@types/react-dom": "^18.3.7",
    "@vitejs/plugin-react-swc": "^3.11.0",
    "autoprefixer": "^10.4.21",
    "eslint": "^9.32.0",
    "eslint-plugin-react-hooks": "^5.2.0",
    "eslint-plugin-react-refresh": "^0.4.20",
    "globals": "^15.15.0",
    "lovable-tagger": "^1.1.11",
    "postcss": "^8.5.6",
    "tailwindcss": "^3.4.17",
    "typescript": "^5.8.3",
    "typescript-eslint": "^8.38.0",
    "vite": "^5.4.19"
  }
}
```

#### Requirements.txt (Backend Dependencies)

```txt:backend/requirements.txt
# Core FastAPI dependencies
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
alembic==1.13.1

# Data validation and settings
pydantic==2.5.3
pydantic-settings==2.1.0
python-dotenv==1.0.0

# Machine Learning
sentence-transformers==2.3.1
implicit==0.7.2
faiss-cpu==1.8.0
numpy==1.26.4
pandas==2.1.4
scikit-learn==1.4.0

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# AWS and HTTP
boto3==1.34.34
httpx==0.28.1
Pillow==10.2.0
google-generativeai>=0.3.0

# Data generation and testing
faker==22.6.0
pytest==7.4.4
pytest-asyncio==0.23.3
requests==2.32.3

# Additional utilities
python-dateutil>=2.8.2
PyJWT>=2.10.1
```

#### Docker Compose Configuration

```yaml:backend/docker-compose.yml
version: '3.8'

services:
  zyra-backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+psycopg2://zyra_user:password@db:5432/zyra_db
      - JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_REGION=us-east-1
      - S3_BUCKET_NAME=${S3_BUCKET_NAME}
      - DEBUG=true
    volumes:
      - ./artifacts:/app/artifacts
      - ./logs:/app/logs
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=zyra_db
      - POSTGRES_USER=zyra_user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

volumes:
  postgres_data:
```

#### Tailwind Configuration

```typescript:tailwind.config.ts
import type { Config } from "tailwindcss";

export default {
  darkMode: ["class"],
  content: ["./pages/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./app/**/*.{ts,tsx}", "./src/**/*.{ts,tsx}"],
  prefix: "",
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        sidebar: {
          DEFAULT: "hsl(var(--sidebar-background))",
          foreground: "hsl(var(--sidebar-foreground))",
          primary: "hsl(var(--sidebar-primary))",
          "primary-foreground": "hsl(var(--sidebar-primary-foreground))",
          accent: "hsl(var(--sidebar-accent))",
          "accent-foreground": "hsl(var(--sidebar-accent-foreground))",
          border: "hsl(var(--sidebar-border))",
          ring: "hsl(var(--sidebar-ring))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
        "fade-in": {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "fade-in-up": {
          "0%": { opacity: "0", transform: "translateY(20px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "scale-in": {
          "0%": { opacity: "0", transform: "scale(0.95)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
        "slide-in-right": {
          "0%": { transform: "translateX(100%)" },
          "100%": { transform: "translateX(0)" },
        },
        "slide-out-right": {
          "0%": { transform: "translateX(0)" },
          "100%": { transform: "translateX(100%)" },
        },
        "glow": {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.5" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "fade-in": "fade-in 0.5s ease-out",
        "fade-in-up": "fade-in-up 0.6s ease-out",
        "scale-in": "scale-in 0.3s ease-out",
        "slide-in-right": "slide-in-right 0.3s ease-out",
        "slide-out-right": "slide-out-right 0.3s ease-out",
        "glow": "glow 2s ease-in-out infinite",
      },
      boxShadow: {
        'glow': '0 0 30px hsl(var(--primary) / 0.3)',
        'card': '0 2px 8px hsl(var(--primary) / 0.08)',
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
} satisfies Config;
```

#### Vite Configuration

```typescript:vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8081,
  },
  plugins: [react(), mode === "development" && componentTagger()].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
```

### Backend - Database Configuration

```python:backend/app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Create database engine using the flexible URL method
engine = create_engine(
    settings.get_database_url(),
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.debug
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Frontend - API Client Service

```typescript:src/services/api.ts
/**
 * Base API configuration and utilities
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8005';

export interface ApiResponse<T> {
  data: T;
  message?: string;
  error?: string;
}

export interface ApiError {
  message: string;
  detail?: string;
  status?: number;
}

class ApiClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    // Get auth token from localStorage
    const accessToken = localStorage.getItem('accessToken');
    
    const defaultHeaders: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    
    // Add Authorization header if token exists
    if (accessToken) {
      defaultHeaders['Authorization'] = `Bearer ${accessToken}`;
    }

    const config: RequestInit = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    };

    try {
      // Add timeout to prevent hanging requests
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
      
      const response = await fetch(url, {
        ...config,
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.message || `HTTP ${response.status}`);
      }

      // Handle empty responses
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }
      
      return {} as T;
    } catch (error) {
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw new Error('API request failed: Request timeout');
        }
        throw new Error(`API request failed: ${error.message}`);
      }
      // Handle non-Error objects
      const errorMessage = typeof error === 'object' && error !== null 
        ? JSON.stringify(error) 
        : String(error);
      throw new Error(`API request failed: ${errorMessage}`);
    }
  }

  async get<T>(endpoint: string, params?: Record<string, any> | { params?: Record<string, any> }, options?: RequestInit): Promise<T> {
    const url = new URL(`${this.baseURL}${endpoint}`);
    
    // Handle both direct params and axios-style { params: {...} }
    const actualParams = params && 'params' in params ? params.params : params;
    
    if (actualParams) {
      Object.entries(actualParams).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          url.searchParams.append(key, String(value));
        }
      });
    }

    return this.request<T>(url.pathname + url.search, options);
  }

  async post<T>(endpoint: string, data?: any, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
      ...options,
    });
  }

  async put<T>(endpoint: string, data?: any, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
      ...options,
    });
  }

  async delete<T>(endpoint: string, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'DELETE',
      ...options,
    });
  }
}

export const apiClient = new ApiClient(API_BASE_URL);

export default apiClient;
```

### Backend - Product API Endpoints

```python:backend/app/api/products.py
"""
Product API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from decimal import Decimal

from app.database import get_db
from app.models import Product, Category, ProductImage
from app.schemas import (
    ProductResponse, ProductDetail, ProductSearch, 
    CategoryResponse, ProductImageResponse
)
from app.services import ContentBasedService
from sqlalchemy import func

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("/", response_model=List[ProductResponse])
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    min_price: Optional[Decimal] = None,
    max_price: Optional[Decimal] = None,
    available_only: bool = True,
    db: Session = Depends(get_db)
):
    """List products with pagination and filters"""
    query = db.query(Product)
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    if min_price:
        query = query.filter(Product.price >= min_price)
    
    if max_price:
        query = query.filter(Product.price <= max_price)
    
    if available_only:
        query = query.filter(Product.available == True)
    
    products = query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()
    
    # Add computed fields
    for product in products:
        # Set image_url from primary image
        primary_image = None
        for img in product.images:
            if img.is_primary:
                primary_image = img.cdn_url
                break
        if not primary_image and product.images:
            primary_image = product.images[0].cdn_url
        
        # Set computed fields
        product.image_url = primary_image
    
    return products


@router.get("/search", response_model=List[ProductResponse])
async def search_products(
    q: str = Query(..., min_length=1),
    k: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Search products using semantic similarity"""
    try:
        content_service = ContentBasedService()
        results = content_service.search_products(q, k=k)
        
        # Get product details
        product_ids = [result[0] for result in results]
        products = db.query(Product).filter(Product.product_id.in_(product_ids)).all()
        
        # Create mapping for ordering
        product_map = {p.product_id: p for p in products}
        ordered_products = [product_map[pid] for pid in product_ids if pid in product_map]
        
        return ordered_products
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/categories/hierarchy")
async def get_categories_hierarchy(db: Session = Depends(get_db)):
    """Get categories with hierarchical structure and product counts"""
    # Get all categories with product counts
    categories_with_counts = db.query(
        Category,
        func.count(Product.product_id).label('product_count')
    ).outerjoin(
        Product, Category.category_id == Product.category_id
    ).group_by(Category.category_id).all()
    
    # Build hierarchy
    hierarchy = []
    category_map = {}
    
    # First pass: create category objects
    for category, product_count in categories_with_counts:
        category_obj = {
            "category_id": category.category_id,
            "name": category.name,
            "slug": category.slug,
            "parent_id": category.parent_id,
            "product_count": product_count,
            "children": []
        }
        category_map[category.category_id] = category_obj
    
    # Second pass: build hierarchy
    for category_id, category_obj in category_map.items():
        if category_obj["parent_id"] is None:
            # This is a parent category
            hierarchy.append(category_obj)
        else:
            # This is a child category
            parent = category_map.get(category_obj["parent_id"])
            if parent:
                parent["children"].append(category_obj)
    
    # Third pass: calculate total product counts for parent categories
    for parent_category in hierarchy:
        if parent_category["children"]:
            # Sum up product counts from all children
            total_count = sum(child["product_count"] for child in parent_category["children"])
            parent_category["product_count"] = total_count
    
    return hierarchy
```

## 📊 Database Schema Overview

The project uses PostgreSQL with SQLAlchemy ORM. Key tables include:

- **users**: User accounts with authentication
- **products**: Product catalog with metadata
- **categories**: Hierarchical category structure
- **product_images**: Image storage with S3 integration
- **interactions**: User interaction tracking
- **user_cart**: Shopping cart items
- **user_wishlist**: Wishlist items
- **purchase_history**: Purchase records
- **reviews**: Product reviews and ratings
- **sessions**: User session tracking
- **recommendation_logs**: ML recommendation logs

For complete schema details, see [DATABASE_SCHEMA.md](../DATABASE_SCHEMA.md).

## 🔧 Development Setup

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### Frontend Setup

```bash
npm install
npm run dev
```

### Docker Setup

```bash
cd backend
docker-compose up -d
```

## 📚 Additional Documentation

- [Environment Setup Guide](docs/ENVIRONMENT_SETUP.md)
- [Local Development Guide](docs/LOCAL_DEVELOPMENT.md)
- [Chatbot Integration](docs/CHATBOT_INTEGRATION.md)
- [Recommendation System](docs/PERSONALIZED_HYBRID_RECOMMENDATION_SYSTEM.md)
- [Product Generation](docs/PRODUCT_GENERATION_SUMMARY.md)

## 🧪 Testing

### ✅ Test Suite Status: **100% ML Tests Passing**

- **[Complete Testing Guide](docs/TESTING.md)** - Comprehensive testing documentation
- **[Quick Start Testing](TEST_SETUP.md)** - Get started in 5 minutes
- **[Postman Quick Start](POSTMAN_QUICKSTART.md)** - API testing with Postman
- **[Postman Test Data](POSTMAN_TEST_DATA.md)** - Ready-to-use test values
- **[Postman Auth Help](POSTMAN_NO_AUTH_ERRORS.md)** - Fix 401 errors
- **[Postman Guide](docs/POSTMAN_GUIDE.md)** - Detailed Postman instructions
- **[Test Summary](TEST_SUMMARY.md)** - Overview of all tests
- **[Final Results](FINAL_TEST_RESULTS.md)** - Complete test results
- **[Test Complete](TEST_COMPLETE_SUMMARY.md)** - Success summary ✅

**Quick Test Commands:**
```bash
# Backend ML tests (✅ 13/13 passing)
cd backend && python3 -m pytest tests/test_ml_services.py -v

# Frontend E2E tests
npm run test:e2e:ui

# Postman: Import backend/tests/postman_collection.json
```

## 🎯 Key Architecture Decisions

1. **Hybrid Recommendation System**: Combines content-based filtering (FAISS) with collaborative filtering (ALS) for optimal recommendations
2. **Microservices Architecture**: Separated frontend and backend for scalability
3. **Type Safety**: TypeScript on frontend, type hints on backend
4. **Async Operations**: FastAPI async/await patterns for I/O operations
5. **State Management**: React Query for server state, Context API for global client state
6. **Cloud Storage**: Hybrid S3/local storage for flexible deployment

## 🚀 Deployment

The application is containerized with Docker and can be deployed to:
- AWS EC2/ECS
- Google Cloud Run
- Azure Container Instances
- Any container orchestration platform

## 📝 License

This project is licensed under the MIT License.

---

**Last Updated**: 2025
**Version**: 1.0.0