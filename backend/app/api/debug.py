"""
Simple test endpoint to debug the user states API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from uuid import UUID
import logging

from app.database import get_db
from app.models import UserWishlist, Product

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/debug", tags=["debug"])

@router.get("/wishlist/{user_id}")
async def debug_wishlist(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Debug wishlist query"""
    try:
        wishlist_items = db.query(
            UserWishlist.id,
            UserWishlist.user_id,
            UserWishlist.product_id,
            UserWishlist.added_at,
            Product.name.label('product_name'),
            Product.price.label('product_price')
        ).join(
            Product, UserWishlist.product_id == Product.product_id
        ).filter(
            UserWishlist.user_id == user_id
        ).order_by(
            desc(UserWishlist.added_at)
        ).all()
        
        # Simple response without Pydantic models
        result = []
        for item in wishlist_items:
            result.append({
                "id": item.id,
                "user_id": str(item.user_id),
                "product_id": str(item.product_id),
                "added_at": item.added_at.isoformat(),
                "product_name": item.product_name,
                "product_price": float(item.product_price) if item.product_price else 0
            })
        
        return {
            "total_items": len(result),
            "items": result
        }
        
    except Exception as e:
        logger.error(f"Debug wishlist error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Debug error: {str(e)}")

