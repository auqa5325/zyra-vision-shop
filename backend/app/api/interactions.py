"""
Simple Interaction API - Fast and reliable interaction tracking
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import logging
from datetime import datetime

from app.database import get_db
from app.models import Interaction
from app.schemas import InteractionCreate, InteractionResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/interactions", tags=["interactions"])

@router.post("/", response_model=InteractionResponse)
async def create_interaction(
    interaction: InteractionCreate,
    db: Session = Depends(get_db)
):
    """Log user interaction - Simple and fast"""
    try:
        logger.info(f"📝 [INTERACTION] Logging: {interaction.event_type} for user {interaction.user_id}")
        
        # Create interaction record
        db_interaction = Interaction(**interaction.model_dump())
        db.add(db_interaction)
        db.commit()
        db.refresh(db_interaction)
        
        logger.info(f"✅ [INTERACTION] Logged: {interaction.event_type} (ID: {db_interaction.id})")
        
        return InteractionResponse(
            id=db_interaction.id,
            user_id=db_interaction.user_id,
            product_id=db_interaction.product_id,
            session_id=db_interaction.session_id,
            event_type=db_interaction.event_type,
            event_value=db_interaction.event_value,
            platform=db_interaction.platform,
            device=db_interaction.device,
            created_at=db_interaction.created_at
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ [INTERACTION] Failed to log: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to log interaction: {str(e)}")

@router.get("/test")
async def test_endpoint():
    """Simple test endpoint"""
    logger.info("🧪 [TEST] Test endpoint called")
    return {"message": "Test endpoint working", "timestamp": datetime.now().isoformat()}

@router.get("/user/{user_id}")
async def get_user_interactions(
    user_id: UUID,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get user interactions - Simple and fast"""
    try:
        logger.info(f"📊 [INTERACTIONS] Fetching interactions for user {user_id}")
        
        # Simple query - get recent interactions
        interactions = db.query(Interaction).filter(
            Interaction.user_id == user_id
        ).order_by(
            Interaction.created_at.desc()
        ).limit(limit).all()
        
        result = []
        for interaction in interactions:
            result.append({
                "id": interaction.id,
                "user_id": str(interaction.user_id),
                "product_id": str(interaction.product_id),
                "event_type": interaction.event_type,
                "event_value": float(interaction.event_value) if interaction.event_value else 0,
                "platform": interaction.platform,
                "device": interaction.device,
                "created_at": interaction.created_at.isoformat()
            })
        
        logger.info(f"✅ [INTERACTIONS] Fetched {len(result)} interactions for user {user_id}")
        return result
        
    except Exception as e:
        logger.error(f"❌ [INTERACTIONS] Failed to fetch: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch interactions: {str(e)}")
