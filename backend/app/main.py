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
from app.api.admin import router as admin_router
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


# Add CORS middleware

# Add JWT authentication middleware
app.add_middleware(JWTAuthMiddleware)

# Mount static files for local image storage
import os
if os.path.exists("uploads"):
    app.mount("/static/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header and CORS debugging"""
    start_time = time.time()
    
    # Log CORS-related information
    origin = request.headers.get("origin")
    if origin:
        logger.info(f"🌐 [CORS] Request from origin: {origin}")
    
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Add CORS headers for debugging
    if origin:
        response.headers["X-Requested-Origin"] = origin
    
    return response


@app.on_event("startup")
async def startup_event():
    """Load ML models on startup"""
    logger.info("Starting Zyra API...")
    
    # Load ML models on startup
    # Run in thread executor to avoid blocking the event loop during startup
    try:
        import asyncio
        logger.info("🔄 Loading ML models...")
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, model_loader.load_models)
        logger.info("✅ ML models loaded successfully")
    except Exception as e:
        logger.error(f"❌ Failed to load ML models: {e}")
        logger.warning("⚠️  API will continue but search/recommendations may not work")
        # Don't fail startup - allow API to run even if models fail to load


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Zyra API...")


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


@app.get("/metrics", tags=["health"])
async def get_metrics():
    """Get basic API metrics"""
    try:
        faiss_index = model_loader.get_faiss_index()
        
        return {
            "total_products": faiss_index.ntotal,
            "embedding_dimension": faiss_index.d,
            "model_info": {
                "embedding_model": settings.embedding_model,
                "faiss_index_type": "IndexFlatIP",
                "default_alpha": settings.default_alpha,
                "default_top_k": settings.default_top_k
            }
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get metrics: {str(e)}"}
        )


# Include API routers
app.include_router(auth_router)
app.include_router(images_router)
app.include_router(schema_router)
app.include_router(session_interactions_router)  # Session interaction tracking
app.include_router(products_router)
app.include_router(recommendations_router)  # Re-enabled
app.include_router(interactions_router)
app.include_router(users_router)
app.include_router(user_data_router)
app.include_router(user_states_router)
app.include_router(admin_router)
# app.include_router(debug_router)  # Temporarily disabled
# app.include_router(dual_tracking_router)  # Temporarily disabled
# app.include_router(simple_test_router)  # Temporarily disabled
# app.include_router(chatbot_router)  # Temporarily disabled - causing timeout
app.include_router(reviews_router)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    
    if settings.debug:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(exc),
                "path": str(request.url)
            }
        )
    else:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred"
            }
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
