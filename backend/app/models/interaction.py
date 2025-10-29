from sqlalchemy import Column, String, DateTime, JSON, BigInteger, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid


class Interaction(Base):
    __tablename__ = "interactions"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.product_id"), nullable=True)
    session_id = Column(UUID(as_uuid=True), nullable=True)
    event_type = Column(String, nullable=False)  # view, click, add_to_cart, purchase, wishlist, review
    event_value = Column(Numeric, default=1)
    platform = Column(String, nullable=True)  # web, ios, android, api
    device = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="interactions")
    product = relationship("Product", back_populates="interactions")


class Session(Base):
    __tablename__ = "sessions"
    
    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    context = Column(JSON, nullable=True)  # cart, campaign, referrer
    
    # Relationships
    user = relationship("User", back_populates="sessions")

