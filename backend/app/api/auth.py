"""
Authentication API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID

from app.database import get_db
from app.models import User
from app.schemas import (
    UserCreate, UserLogin, UserResponse, 
    TokenResponse, TokenRefresh
)
from app.services.auth_service import jwt_service
from app.services.simple_session_logger import session_logger
from app.middleware.auth import JWTSecurity

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=TokenResponse)
async def register(
    user_data: UserCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    try:
        # Check if username already exists
        if user_data.username:
            existing_user = db.query(User).filter(User.username == user_data.username).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        # Hash password if provided
        password_hash = None
        if user_data.password:
            password_hash = jwt_service.get_password_hash(user_data.password)
        
        # Create user
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=password_hash,
            profile=user_data.profile,
            is_anonymous=user_data.is_anonymous,
            is_active=True
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Create session for new user
        session_id = session_logger.create_session(
            db=db,
            user_id=str(db_user.user_id),
            request=request
        )
        
        # Create tokens
        token_data = {"sub": str(db_user.user_id), "user_id": str(db_user.user_id), "session_id": session_id}
        if db_user.username:
            token_data["username"] = db_user.username
        if db_user.email:
            token_data["email"] = db_user.email
        
        tokens = jwt_service.create_token_pair(token_data)
        
        return TokenResponse(**tokens)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """Login user with username and password"""
    try:
        # Find user by username
        user = db.query(User).filter(
            User.username == login_data.username,
            User.is_active == True
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        if not user.password_hash or not jwt_service.verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Update last seen
        user.last_seen_at = datetime.utcnow()
        db.commit()
        
        # Create session for successful login
        session_id = session_logger.create_session(
            db=db,
            user_id=str(user.user_id),
            request=request
        )
        
        # Create tokens
        token_data = {"user_id": str(user.user_id), "username": user.username, "session_id": session_id}
        if user.email:
            token_data["email"] = user.email
        tokens = jwt_service.create_token_pair(token_data)
        
        return TokenResponse(**tokens)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    try:
        # Verify refresh token
        payload = jwt_service.verify_token(refresh_data.refresh_token, "refresh")
        
        # Get user
        user_id = payload.get("sub")
        user = db.query(User).filter(
            User.user_id == UUID(user_id),
            User.is_active == True
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create new tokens
        token_data = {"sub": str(user.user_id), "user_id": str(user.user_id)}
        
        # Preserve session_id from the original token if available
        session_id = payload.get("session_id")
        if session_id:
            token_data["session_id"] = session_id
        
        if user.username:
            token_data["username"] = user.username
        if user.email:
            token_data["email"] = user.email
        
        tokens = jwt_service.create_token_pair(token_data)
        
        return TokenResponse(**tokens)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )


@router.post("/logout")
async def logout(
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTSecurity())
):
    """Logout user and end session"""
    try:
        # Get user_id from JWT token payload
        user_id = current_user.get("user_id") or current_user.get("sub")
        session_id = current_user.get("session_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: user_id not found"
            )
        
        # End the session
        session_ended = session_logger.end_session(
            db=db,
            user_id=str(user_id),
            session_id=session_id,
            request=request
        )
        
        if session_ended:
            return {"message": "Successfully logged out", "session_ended": True}
        else:
            return {"message": "Successfully logged out", "session_ended": False, "warning": "No active session found"}
        
    except HTTPException:
        raise
    except Exception as e:
        # Don't fail logout even if session logging fails
        return {"message": "Successfully logged out", "warning": f"Session logging failed: {str(e)}"}


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get current user profile"""
    user_id = request.state.user_id
    user = db.query(User).filter(User.user_id == UUID(user_id)).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


