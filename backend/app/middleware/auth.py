"""
JWT Authentication Middleware
"""

from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
from app.config import settings
from app.services.auth_service import jwt_service


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """Middleware for JWT authentication"""
    
    def __init__(self, app):
        super().__init__(app)
        self.public_paths = {
            "/docs", 
            "/redoc", 
            "/openapi.json",
            "/health",
            "/",
            "/api/auth/login",
            "/api/auth/register",
            "/api/auth/refresh",
            "/api/auth/logout",  # Logout endpoint
            "/static/uploads",  # Local image serving
            "/api/images/proxy",  # Image proxy
            "/api/interactions/test",  # Test endpoint
            "/api/chatbot/health",  # Chatbot health check
            "/api/chatbot/chat"  # Chatbot chat endpoint
        }
        # Public path patterns (for endpoints that start with these)
        self.public_patterns = [
            "/api/products",
            "/api/recommendations",
            "/api/images",
            "/api/user-data",
            "/api/user-states"
        ]
    
    async def dispatch(self, request: Request, call_next):
        # Skip authentication for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Skip authentication for public paths
        if request.url.path in self.public_paths:
            return await call_next(request)
        
        # Skip authentication for public path patterns
        for pattern in self.public_patterns:
            if request.url.path.startswith(pattern):
                return await call_next(request)
        
        # Allow GET requests to /api/reviews without authentication (for viewing reviews)
        if request.method == "GET" and request.url.path.startswith("/api/reviews"):
            return await call_next(request)
        
        # Check for Authorization header
        authorization: str = request.headers.get("Authorization")
        
        if not authorization:
            raise HTTPException(
                status_code=401,
                detail="Authorization header required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=401,
                    detail="Invalid authentication scheme",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Verify token
            payload = jwt_service.verify_token(token, "access")
            
            # Add user info to request state
            request.state.user_id = payload.get("user_id") or payload.get("sub")
            request.state.user_email = payload.get("email")
            
        except ValueError:
            raise HTTPException(
                status_code=401,
                detail="Invalid authorization header format",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return await call_next(request)


class JWTSecurity(HTTPBearer):
    """JWT Security dependency for FastAPI"""
    
    def __init__(self):
        super().__init__()
    
    async def __call__(self, request: Request) -> dict:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        
        try:
            payload = jwt_service.verify_token(credentials.credentials, "access")
            return payload  # Return the decoded payload, not the token string
        except HTTPException:
            raise


# Global security instance
security = JWTSecurity()


def get_current_user_id(request: Request) -> str:
    """Get current user ID from request state"""
    return request.state.user_id


def get_current_user_email(request: Request) -> Optional[str]:
    """Get current user email from request state"""
    return getattr(request.state, 'user_email', None)
