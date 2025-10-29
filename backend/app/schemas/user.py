from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    profile: Optional[Dict[str, Any]] = None
    is_anonymous: bool = False


class UserCreate(UserBase):
    password: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    profile: Optional[Dict[str, Any]] = None
    last_seen_at: Optional[datetime] = None


class UserResponse(UserBase):
    user_id: UUID
    created_at: datetime
    last_seen_at: Optional[datetime] = None
    is_active: bool = True
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


class UserProfile(BaseModel):
    preferences: Optional[Dict[str, Any]] = None
    favorite_categories: Optional[list[str]] = None
    budget_range: Optional[Dict[str, float]] = None
    location: Optional[str] = None
