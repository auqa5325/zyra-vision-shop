# Import all models to ensure they are registered with SQLAlchemy
from app.database import Base
from .user import User
from .product import Product, Category, ProductImage
from .interaction import Interaction, Session
from .embeddings import EmbeddingsMeta, RecommendationLog, ABTest, SystemAudit
from .user_states import UserCart, UserWishlist, PurchaseHistory, UserSessionState
from .review import Review, ReviewHelpfulVote

__all__ = [
    "Base",
    "User",
    "Product", 
    "Category",
    "ProductImage",
    "Interaction",
    "Session",
    "EmbeddingsMeta",
    "RecommendationLog",
    "ABTest",
    "SystemAudit",
    "UserCart",
    "UserWishlist", 
    "PurchaseHistory",
    "UserSessionState",
    "Review",
    "ReviewHelpfulVote"
]

