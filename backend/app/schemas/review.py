from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    title: Optional[str] = None
    comment: Optional[str] = None


class ReviewCreate(ReviewBase):
    product_id: UUID


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = None
    comment: Optional[str] = None


class ReviewResponse(ReviewBase):
    review_id: UUID
    user_id: UUID
    product_id: UUID
    verified_purchase: bool
    helpful_count: int
    is_approved: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ReviewWithUser(ReviewResponse):
    user: dict  # username, email (sanitized)
    product_name: Optional[str] = None


class ProductRatingSummary(BaseModel):
    average_rating: float
    total_reviews: int
    rating_distribution: dict  # {1: count, 2: count, ..., 5: count}
