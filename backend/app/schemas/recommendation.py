from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class InteractionBase(BaseModel):
    user_id: Optional[UUID] = None
    product_id: Optional[UUID] = None
    session_id: Optional[UUID] = None
    event_type: str  # view, click, add_to_cart, purchase, wishlist, review
    event_value: Decimal = 1
    platform: Optional[str] = None  # web, ios, android, api
    device: Optional[Dict[str, Any]] = None


class InteractionCreate(InteractionBase):
    pass


class InteractionResponse(InteractionBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class SessionBase(BaseModel):
    user_id: Optional[UUID] = None
    context: Optional[Dict[str, Any]] = None


class SessionCreate(SessionBase):
    pass


class SessionResponse(SessionBase):
    session_id: UUID
    started_at: datetime
    ended_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ReasonFeatures(BaseModel):
    matched_tags: Optional[List[str]] = None
    cf_score: Optional[float] = None
    content_score: Optional[float] = None
    source: Optional[str] = None  # hybrid, content, collaborative


class RecommendationRequest(BaseModel):
    user_id: Optional[UUID] = None
    query: Optional[str] = None
    product_id: Optional[UUID] = None
    alpha: float = 0.6
    k: int = 10


class RecommendationResponse(BaseModel):
    product_id: UUID
    name: str
    price: Optional[Decimal] = None
    discount_percent: Optional[Decimal] = None
    image_url: Optional[str] = None
    hybrid_score: Optional[float] = None
    reason_features: Optional[ReasonFeatures] = None
    
    class Config:
        from_attributes = True


class RecommendationLogCreate(BaseModel):
    user_id: Optional[UUID] = None
    session_id: Optional[UUID] = None
    request_context: Optional[Dict[str, Any]] = None
    candidate_products: Optional[List[UUID]] = None

