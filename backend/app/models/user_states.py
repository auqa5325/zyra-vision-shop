"""
Separate tables for user states - Cart, Wishlist, Purchase History
This is more efficient than scanning interactions table
"""

from sqlalchemy import Column, String, DateTime, JSON, BigInteger, ForeignKey, Numeric, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid


class UserCart(Base):
    """User's current cart items"""
    __tablename__ = "user_cart"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.product_id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    added_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")
    
    # Unique constraint to prevent duplicate cart entries
    __table_args__ = (
        {'extend_existing': True}
    )


class UserWishlist(Base):
    """User's wishlist items"""
    __tablename__ = "user_wishlist"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.product_id"), nullable=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="wishlist_items")
    product = relationship("Product", back_populates="wishlist_items")
    
    # Unique constraint to prevent duplicate wishlist entries
    __table_args__ = (
        {'extend_existing': True}
    )


class PurchaseHistory(Base):
    """User's purchase history"""
    __tablename__ = "purchase_history"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.product_id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    order_id = Column(UUID(as_uuid=True), nullable=True)  # For grouping multiple items in one order
    purchased_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    payment_method = Column(String, nullable=True)  # credit_card, paypal, etc.
    payment_status = Column(String, nullable=True, default='completed')  # pending, completed, failed, refunded
    
    # Relationships
    user = relationship("User", back_populates="purchase_history")
    product = relationship("Product", back_populates="purchase_history")


class UserSessionState(Base):
    """User session tracking - renamed to avoid conflict with existing Session model"""
    __tablename__ = "user_session_states"
    
    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    platform = Column(String, nullable=True)  # web, ios, android
    device_info = Column(JSON, nullable=True)
    context = Column(JSON, nullable=True)  # cart, campaign, referrer
    
    # Relationships
    user = relationship("User", back_populates="session_states")
