from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class CategoryBase(BaseModel):
    name: str
    slug: str
    parent_id: Optional[int] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    category_id: int
    
    class Config:
        from_attributes = True


class ProductImageBase(BaseModel):
    s3_key: str
    cdn_url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None
    variant: Optional[str] = None
    alt_text: Optional[str] = None
    is_primary: bool = False


class ProductImageCreate(ProductImageBase):
    product_id: UUID


class ProductImageResponse(ProductImageBase):
    image_id: UUID
    product_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    sku: Optional[str] = None
    name: str
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    category_id: Optional[int] = None
    tags: Optional[List[str]] = None
    price: Optional[Decimal] = None
    discount_percent: Optional[Decimal] = None
    currency: str = "INR"
    brand: Optional[str] = None
    available: bool = True
    metadata_json: Optional[Dict[str, Any]] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    category_id: Optional[int] = None
    tags: Optional[List[str]] = None
    price: Optional[Decimal] = None
    discount_percent: Optional[Decimal] = None
    currency: Optional[str] = None
    brand: Optional[str] = None
    available: Optional[bool] = None
    metadata_json: Optional[Dict[str, Any]] = None


class ProductResponse(ProductBase):
    product_id: UUID
    created_at: datetime
    updated_at: datetime
    images: List[ProductImageResponse] = []
    image_url: Optional[str] = None  # Computed from primary image
    rating: Optional[float] = None  # Computed rating (for backward compatibility)
    # Rating fields from database
    average_rating: Optional[float] = None  # Average rating from reviews table (converted to float)
    total_reviews: Optional[int] = None  # Total number of reviews
    rating_distribution: Optional[Dict[str, int]] = None  # {1: count, 2: count, ...}
    
    class Config:
        from_attributes = True


class ProductDetail(ProductResponse):
    category: Optional[CategoryResponse] = None


class ProductSearch(BaseModel):
    query: str
    category_id: Optional[int] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    tags: Optional[List[str]] = None
    available_only: bool = True

