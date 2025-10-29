"""
Dual tracking system: Interactions + User States
- Interactions: For ML model training (preserved)
- User States: For fast UI queries (optimized)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from uuid import UUID
import logging

from app.database import get_db
from app.models import UserWishlist, UserCart, PurchaseHistory, Product, Interaction

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/optimized", tags=["optimized"])

@router.get("/wishlist/{user_id}")
async def get_wishlist_optimized(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Get wishlist using optimized table - FAST"""
    try:
        items = db.query(UserWishlist).filter(UserWishlist.user_id == user_id).all()
        
        result = []
        for item in items:
            product = db.query(Product).filter(Product.product_id == item.product_id).first()
            if product:
                result.append({
                    "product_id": str(item.product_id),
                    "product_name": product.name,
                    "product_price": float(product.price) if product.price else 0,
                    "added_at": item.added_at.isoformat(),
                    "product_image": f"http://localhost:8005/api/images/proxy/{item.product_id}/1"
                })
        
        return {
            "items": result,
            "total_items": len(result),
            "source": "optimized_table"
        }
        
    except Exception as e:
        logger.error(f"Wishlist error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cart/{user_id}")
async def get_cart_optimized(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Get cart using optimized table - FAST"""
    try:
        items = db.query(UserCart).filter(UserCart.user_id == user_id).all()
        
        result = []
        total_price = 0
        total_items = 0
        
        for item in items:
            product = db.query(Product).filter(Product.product_id == item.product_id).first()
            if product:
                item_total = float(product.price) * item.quantity if product.price else 0
                total_price += item_total
                total_items += item.quantity
                
                result.append({
                    "product_id": str(item.product_id),
                    "product_name": product.name,
                    "product_price": float(product.price) if product.price else 0,
                    "quantity": item.quantity,
                    "item_total": item_total,
                    "added_at": item.added_at.isoformat(),
                    "product_image": f"http://localhost:8005/api/images/proxy/{item.product_id}/1"
                })
        
        return {
            "items": result,
            "total_items": total_items,
            "total_price": total_price,
            "source": "optimized_table"
        }
        
    except Exception as e:
        logger.error(f"Cart error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/purchases/{user_id}")
async def get_purchases_optimized(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Get purchases using optimized table - FAST"""
    try:
        items = db.query(PurchaseHistory).filter(
            PurchaseHistory.user_id == user_id
        ).order_by(desc(PurchaseHistory.purchased_at)).all()
        
        result = []
        total_spent = 0
        
        for item in items:
            product = db.query(Product).filter(Product.product_id == item.product_id).first()
            if product:
                total_spent += float(item.total_price) if item.total_price else 0
                
                result.append({
                    "product_id": str(item.product_id),
                    "product_name": product.name,
                    "quantity": item.quantity,
                    "unit_price": float(item.unit_price) if item.unit_price else 0,
                    "total_price": float(item.total_price) if item.total_price else 0,
                    "purchased_at": item.purchased_at.isoformat(),
                    "order_id": str(item.order_id) if item.order_id else None,
                    "payment_method": item.payment_method,
                    "product_image": f"http://localhost:8005/api/images/proxy/{item.product_id}/1"
                })
        
        return {
            "items": result,
            "total_items": len(result),
            "total_spent": total_spent,
            "source": "optimized_table"
        }
        
    except Exception as e:
        logger.error(f"Purchases error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add-to-cart/{user_id}/{product_id}")
async def add_to_cart_dual(
    user_id: UUID,
    product_id: UUID,
    quantity: int = 1,
    db: Session = Depends(get_db)
):
    """Add to cart with dual tracking: Interactions + User States"""
    try:
        # 1. Add to interactions table (for ML training)
        interaction = Interaction(
            user_id=user_id,
            product_id=product_id,
            event_type='add_to_cart',
            event_value=quantity,
            platform='web'
        )
        db.add(interaction)
        
        # 2. Update user cart table (for fast UI queries)
        existing_cart_item = db.query(UserCart).filter(
            UserCart.user_id == user_id,
            UserCart.product_id == product_id
        ).first()
        
        if existing_cart_item:
            existing_cart_item.quantity += quantity
        else:
            cart_item = UserCart(
                user_id=user_id,
                product_id=product_id,
                quantity=quantity
            )
            db.add(cart_item)
        
        db.commit()
        
        logger.info(f"✅ [DUAL TRACKING] Added to cart: user={user_id}, product={product_id}, qty={quantity}")
        return {
            "message": "Added to cart successfully",
            "tracking": "dual (interactions + user_states)"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Add to cart error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add-to-wishlist/{user_id}/{product_id}")
async def add_to_wishlist_dual(
    user_id: UUID,
    product_id: UUID,
    db: Session = Depends(get_db)
):
    """Add to wishlist with dual tracking: Interactions + User States"""
    try:
        # 1. Add to interactions table (for ML training)
        interaction = Interaction(
            user_id=user_id,
            product_id=product_id,
            event_type='wishlist',
            event_value=1,  # 1 = add, 0 = remove
            platform='web'
        )
        db.add(interaction)
        
        # 2. Update user wishlist table (for fast UI queries)
        existing_wishlist_item = db.query(UserWishlist).filter(
            UserWishlist.user_id == user_id,
            UserWishlist.product_id == product_id
        ).first()
        
        if not existing_wishlist_item:
            wishlist_item = UserWishlist(
                user_id=user_id,
                product_id=product_id
            )
            db.add(wishlist_item)
        
        db.commit()
        
        logger.info(f"✅ [DUAL TRACKING] Added to wishlist: user={user_id}, product={product_id}")
        return {
            "message": "Added to wishlist successfully",
            "tracking": "dual (interactions + user_states)"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Add to wishlist error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/interactions/{user_id}")
async def get_interactions_for_ml(
    user_id: UUID,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get interactions for ML model training - PRESERVED"""
    try:
        interactions = db.query(Interaction).filter(
            Interaction.user_id == user_id
        ).order_by(desc(Interaction.created_at)).limit(limit).all()
        
        result = []
        for interaction in interactions:
            result.append({
                "id": interaction.id,
                "user_id": str(interaction.user_id),
                "product_id": str(interaction.product_id),
                "event_type": interaction.event_type,
                "event_value": float(interaction.event_value) if interaction.event_value else 0,
                "platform": interaction.platform,
                "created_at": interaction.created_at.isoformat()
            })
        
        logger.info(f"📊 [ML TRAINING] Fetched {len(result)} interactions for user {user_id}")
        return {
            "interactions": result,
            "total_count": len(result),
            "source": "interactions_table",
            "purpose": "ml_model_training"
        }
        
    except Exception as e:
        logger.error(f"Interactions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

