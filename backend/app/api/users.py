"""
User API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.models import User, Interaction
from app.schemas import UserCreate, UserResponse, UserUpdate, UserProfile

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """Create new user"""
    try:
        # Check if email already exists
        if user.email:
            existing_user = db.query(User).filter(User.email == user.email).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already registered")
        
        db_user = User(
            email=user.email,
            profile=user.profile,
            is_anonymous=user.is_anonymous
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Get user profile"""
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.patch("/{user_id}/profile", response_model=UserResponse)
async def update_user_profile(
    user_id: UUID,
    profile_update: UserProfile,
    db: Session = Depends(get_db)
):
    """Update user profile and preferences"""
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        # Update profile
        if user.profile is None:
            user.profile = {}
        
        user.profile.update(profile_update.dict(exclude_unset=True))
        user.last_seen_at = datetime.utcnow()
        
        db.commit()
        db.refresh(user)
        
        return user
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """Update user information"""
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        # Check email uniqueness if updating email
        if user_update.email and user_update.email != user.email:
            existing_user = db.query(User).filter(User.email == user_update.email).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already registered")
        
        # Update fields
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")


@router.get("/{user_id}/stats")
async def get_user_stats(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Get user interaction statistics"""
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get interaction counts
    from app.models import Interaction
    interactions = db.query(Interaction).filter(Interaction.user_id == user_id).all()
    
    stats = {
        "total_interactions": len(interactions),
        "event_types": {},
        "platforms": {},
        "last_activity": None
    }
    
    if interactions:
        # Count by event type
        for interaction in interactions:
            event_type = interaction.event_type
            stats["event_types"][event_type] = stats["event_types"].get(event_type, 0) + 1
            
            # Count by platform
            platform = interaction.platform or "unknown"
            stats["platforms"][platform] = stats["platforms"].get(platform, 0) + 1
        
        # Get last activity
        latest_interaction = max(interactions, key=lambda x: x.created_at)
        stats["last_activity"] = latest_interaction.created_at
    
    return stats


@router.get("/{user_id}/stats")
async def get_user_stats(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Get user interaction statistics"""
    try:
        # Get total interactions count
        total_interactions = db.query(func.count(Interaction.id)).filter(
            Interaction.user_id == user_id
        ).scalar() or 0
        
        # Get event type distribution
        event_types = db.query(
            Interaction.event_type,
            func.count(Interaction.id).label('count')
        ).filter(
            Interaction.user_id == user_id
        ).group_by(Interaction.event_type).all()
        
        event_type_stats = {event_type: count for event_type, count in event_types}
        
        # Get platform distribution
        platforms = db.query(
            Interaction.platform,
            func.count(Interaction.id).label('count')
        ).filter(
            Interaction.user_id == user_id
        ).group_by(Interaction.platform).all()
        
        platform_stats = {platform: count for platform, count in platforms}
        
        # Get last activity
        last_interaction = db.query(Interaction.created_at).filter(
            Interaction.user_id == user_id
        ).order_by(desc(Interaction.created_at)).first()
        
        last_activity = last_interaction.created_at.isoformat() if last_interaction else None
        
        stats = {
            "total_interactions": total_interactions,
            "event_types": event_type_stats,
            "platforms": platform_stats,
            "last_activity": last_activity
        }
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user stats: {str(e)}")

