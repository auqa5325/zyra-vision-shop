"""
User model with password support for JWT authentication
"""

import uuid
from sqlalchemy import Column, String, DateTime, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=True)
    email = Column(String, nullable=True)
    password_hash = Column(String, nullable=True)  # For registered users
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_seen_at = Column(DateTime(timezone=True), nullable=True)
    profile = Column(JSON, nullable=True)
    is_anonymous = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Relationships
    interactions = relationship("Interaction", back_populates="user")
    sessions = relationship("Session", back_populates="user")
    recommendation_logs = relationship("RecommendationLog", back_populates="user")
    ab_tests = relationship("ABTest", back_populates="user")
    
    # New user state relationships
    cart_items = relationship("UserCart", back_populates="user", cascade="all, delete-orphan")
    wishlist_items = relationship("UserWishlist", back_populates="user", cascade="all, delete-orphan")
    purchase_history = relationship("PurchaseHistory", back_populates="user", cascade="all, delete-orphan")
    session_states = relationship("UserSessionState", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
