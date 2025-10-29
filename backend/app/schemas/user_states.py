"""
Schemas for user state models - Cart, Wishlist, Purchase History
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from uuid import UUID


# Cart Schemas
class CartItemBase(BaseModel):
    product_id: UUID
    quantity: int = Field(ge=1, le=100)

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=0, le=100)

class CartItemResponse(CartItemBase):
    id: int
    user_id: UUID
    added_at: datetime
    updated_at: datetime
    
    # Product details
    product_name: str
    product_price: Decimal
    product_image: Optional[str] = None
    
    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total_items: int
    total_price: Decimal


# Wishlist Schemas
class WishlistItemBase(BaseModel):
    product_id: UUID

class WishlistItemCreate(WishlistItemBase):
    pass

class WishlistItemResponse(WishlistItemBase):
    id: int
    user_id: UUID
    added_at: datetime
    
    # Product details
    product_name: str
    product_price: Decimal
    product_image: Optional[str] = None
    
    class Config:
        from_attributes = True

class WishlistResponse(BaseModel):
    items: List[WishlistItemResponse]
    total_items: int


# Purchase History Schemas
class PurchaseItemBase(BaseModel):
    product_id: UUID
    quantity: int = Field(ge=1, le=100)
    unit_price: Decimal = Field(ge=0)
    total_price: Decimal = Field(ge=0)

class PurchaseItemCreate(PurchaseItemBase):
    order_id: Optional[UUID] = None
    payment_method: Optional[str] = None
    payment_status: str = "completed"

class PurchaseItemResponse(PurchaseItemBase):
    id: int
    user_id: UUID
    order_id: Optional[UUID]
    purchased_at: datetime
    payment_method: Optional[str]
    payment_status: str
    
    # Product details
    product_name: str
    product_image: Optional[str] = None
    
    class Config:
        from_attributes = True

class PurchaseHistoryResponse(BaseModel):
    items: List[PurchaseItemResponse]
    total_items: int
    total_spent: Decimal
    orders: int  # Number of unique orders


# Order Schemas
class OrderCreate(BaseModel):
    items: List[PurchaseItemCreate]
    payment_method: str = "credit_card"
    payment_status: str = "completed"

class OrderResponse(BaseModel):
    order_id: UUID
    user_id: UUID
    items: List[PurchaseItemResponse]
    total_amount: Decimal
    payment_method: str
    payment_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

