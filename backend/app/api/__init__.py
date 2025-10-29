# Import all API routers
from .products import router as products_router
from .recommendations import router as recommendations_router
from .interactions import router as interactions_router
from .users import router as users_router
from .reviews import router as reviews_router

__all__ = [
    "products_router",
    "recommendations_router", 
    "interactions_router",
    "users_router",
    "reviews_router"
]

