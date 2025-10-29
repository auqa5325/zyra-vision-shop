"""
Simple test endpoint to debug the issue
"""

from fastapi import APIRouter
from uuid import UUID

router = APIRouter(prefix="/api/test", tags=["test"])

@router.get("/simple/{user_id}")
async def simple_test(user_id: UUID):
    """Simple test endpoint"""
    return {
        "user_id": str(user_id),
        "message": "Simple test working!",
        "type": "success"
    }

@router.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy", "message": "API is working"}

