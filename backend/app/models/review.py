from sqlalchemy import Column, String, DateTime, JSON, BigInteger, ForeignKey, Integer, Text, Boolean, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid


class Review(Base):
    __tablename__ = "reviews"
    
    review_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    title = Column(String, nullable=True)
    comment = Column(Text, nullable=True)
    verified_purchase = Column(Boolean, default=False, nullable=False)
    helpful_count = Column(Integer, default=0, nullable=False)
    is_approved = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")
    
    __table_args__ = (
        {'extend_existing': True}
    )
    
    def update_product_rating(self, db_session):
        """Update product rating when review is created/updated/deleted"""
        from app.models import Product
        avg_rating = db_session.query(func.avg(Review.rating)).filter(
            Review.product_id == self.product_id,
            Review.is_approved == True
        ).scalar()
        
        product = db_session.query(Product).filter(Product.product_id == self.product_id).first()
        if product:
            if avg_rating:
                product.rating = round(float(avg_rating), 1)
            else:
                product.rating = 0.0
            db_session.commit()


class ReviewHelpfulVote(Base):
    __tablename__ = "review_helpful_votes"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    review_id = Column(UUID(as_uuid=True), ForeignKey("reviews.review_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Unique constraint - one user can only vote once per review
    __table_args__ = (
        UniqueConstraint('review_id', 'user_id', name='unique_review_user_vote'),
        {'extend_existing': True}
    )
