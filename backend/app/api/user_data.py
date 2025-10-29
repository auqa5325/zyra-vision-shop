"""
Simple User Data API - Fast and reliable endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
from uuid import UUID
import logging

from app.database import get_db
from app.models import Interaction, Product
from app.models.product import ProductImage
from app.models.user_states import UserWishlist, UserCart, PurchaseHistory

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/user-data", tags=["user-data"])

@router.get("/cart/{user_id}")
async def get_user_cart(user_id: UUID, db: Session = Depends(get_db)):
    """Get user's cart from dedicated user_cart table"""
    try:
        # Get cart items from dedicated table
        cart_items = db.query(
            UserCart.product_id,
            UserCart.quantity,
            UserCart.added_at,
            Product.name,
            Product.price,
            Product.discount_percent
        ).join(Product, UserCart.product_id == Product.product_id).filter(
            UserCart.user_id == user_id
        ).order_by(desc(UserCart.added_at)).all()
        
        result = []
        for item in cart_items:
            # Get the primary image URL from the database
            primary_image = db.query(ProductImage).filter(
                ProductImage.product_id == item.product_id,
                ProductImage.is_primary == True
            ).first()
            
            image_url = None
            if primary_image and primary_image.cdn_url:
                # Use S3 URL if available, otherwise construct proxy URL
                if primary_image.cdn_url.startswith('http'):
                    image_url = primary_image.cdn_url
                else:
                    image_url = f"http://localhost:8005{primary_image.cdn_url}"
            else:
                # Fallback to proxy URL
                image_url = f"http://localhost:8005/api/images/proxy/{item.product_id}/1"
            
            result.append({
                "product_id": str(item.product_id),
                "name": item.name,
                "price": float(item.price) if item.price else 0,
                "discount_percent": float(item.discount_percent) if item.discount_percent else 0,
                "quantity": item.quantity,
                "last_added": item.added_at.isoformat(),
                "image_url": image_url
            })
        
        logger.info(f"🛒 [CART] Fetched {len(result)} items for user {user_id}")
        return result
        
    except Exception as e:
        logger.error(f"❌ [CART] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch cart: {str(e)}")

@router.get("/wishlist/{user_id}")
async def get_user_wishlist(user_id: UUID, db: Session = Depends(get_db)):
    """Get user's wishlist from dedicated user_wishlist table"""
    try:
        # Get wishlist items from dedicated table
        wishlist_items = db.query(
            UserWishlist.product_id,
            UserWishlist.added_at,
            Product.name,
            Product.price,
            Product.discount_percent
        ).join(Product, UserWishlist.product_id == Product.product_id).filter(
            UserWishlist.user_id == user_id
        ).order_by(desc(UserWishlist.added_at)).all()
        
        result = []
        for item in wishlist_items:
            # Get the primary image URL from the database
            primary_image = db.query(ProductImage).filter(
                ProductImage.product_id == item.product_id,
                ProductImage.is_primary == True
            ).first()
            
            image_url = None
            if primary_image and primary_image.cdn_url:
                # Use S3 URL if available, otherwise construct proxy URL
                if primary_image.cdn_url.startswith('http'):
                    image_url = primary_image.cdn_url
                else:
                    image_url = f"http://localhost:8005{primary_image.cdn_url}"
            else:
                # Fallback to proxy URL
                image_url = f"http://localhost:8005/api/images/proxy/{item.product_id}/1"
            
            result.append({
                "product_id": str(item.product_id),
                "name": item.name,
                "price": float(item.price) if item.price else 0,
                "discount_percent": float(item.discount_percent) if item.discount_percent else 0,
                "added_at": item.added_at.isoformat(),
                "image_url": image_url
            })
        
        logger.info(f"❤️ [WISHLIST] Fetched {len(result)} items for user {user_id}")
        return result
        
    except Exception as e:
        logger.error(f"❌ [WISHLIST] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch wishlist: {str(e)}")

@router.get("/purchases/{user_id}")
async def get_user_purchases(user_id: UUID, db: Session = Depends(get_db)):
    """Get user's purchases from dedicated purchase_history table"""
    try:
        # Get purchases from dedicated table
        purchases = db.query(
            PurchaseHistory.product_id,
            PurchaseHistory.quantity,
            PurchaseHistory.unit_price,
            PurchaseHistory.total_price,
            PurchaseHistory.purchased_at,
            Product.name,
            Product.price,
            Product.discount_percent
        ).join(Product, PurchaseHistory.product_id == Product.product_id).filter(
            PurchaseHistory.user_id == user_id
        ).order_by(desc(PurchaseHistory.purchased_at)).limit(50).all()
        
        result = []
        for purchase in purchases:
            # Get the primary image URL from the database
            primary_image = db.query(ProductImage).filter(
                ProductImage.product_id == purchase.product_id,
                ProductImage.is_primary == True
            ).first()
            
            image_url = None
            if primary_image and primary_image.cdn_url:
                # Use S3 URL if available, otherwise construct proxy URL
                if primary_image.cdn_url.startswith('http'):
                    image_url = primary_image.cdn_url
                else:
                    image_url = f"http://localhost:8005{primary_image.cdn_url}"
            else:
                # Fallback to proxy URL
                image_url = f"http://localhost:8005/api/images/proxy/{purchase.product_id}/1"
            
            result.append({
                "product_id": str(purchase.product_id),
                "name": purchase.name,
                "price": float(purchase.price) if purchase.price else 0,
                "discount_percent": float(purchase.discount_percent) if purchase.discount_percent else 0,
                "quantity": purchase.quantity,
                "unit_price": float(purchase.unit_price) if purchase.unit_price else 0,
                "total_price": float(purchase.total_price) if purchase.total_price else 0,
                "purchased_at": purchase.purchased_at.isoformat(),
                "image_url": image_url
            })
        
        logger.info(f"💰 [PURCHASES] Fetched {len(result)} purchases for user {user_id}")
        return result
        
    except Exception as e:
        logger.error(f"❌ [PURCHASES] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch purchases: {str(e)}")

@router.get("/stats/{user_id}")
async def get_user_stats(user_id: UUID, db: Session = Depends(get_db)):
    """Get user's stats - Simple and fast"""
    try:
        # Get total interactions
        total_interactions = db.query(func.count(Interaction.id)).filter(
            Interaction.user_id == user_id
        ).scalar() or 0
        
        # Get event type counts
        event_types = db.query(
            Interaction.event_type,
            func.count(Interaction.id).label('count')
        ).filter(
            Interaction.user_id == user_id
        ).group_by(Interaction.event_type).all()
        
        event_type_stats = {event_type: count for event_type, count in event_types}
        
        # Get platform counts
        platforms = db.query(
            Interaction.platform,
            func.count(Interaction.id).label('count')
        ).filter(
            Interaction.user_id == user_id
        ).group_by(Interaction.platform).all()
        
        platform_stats = {platform: count for platform, count in platforms}
        
        # Get last activity
        last_interaction = db.query(Interaction.created_at).filter(
            Interaction.user_id == user_id
        ).order_by(desc(Interaction.created_at)).first()
        
        last_activity = last_interaction.created_at.isoformat() if last_interaction else None
        
        # Get total spent from purchase_history table
        total_spent = db.query(func.sum(PurchaseHistory.total_price)).filter(
            PurchaseHistory.user_id == user_id
        ).scalar() or 0
        
        # Get purchases count from purchase_history table
        purchases_count = db.query(func.count(PurchaseHistory.id)).filter(
            PurchaseHistory.user_id == user_id
        ).scalar() or 0
        
        # Get cart items count from user_cart table
        cart_count = db.query(func.count(UserCart.id)).filter(
            UserCart.user_id == user_id
        ).scalar() or 0
        
        # Get wishlist items count from user_wishlist table
        wishlist_count = db.query(func.count(UserWishlist.id)).filter(
            UserWishlist.user_id == user_id
        ).scalar() or 0
        
        stats = {
            "total_interactions": total_interactions,
            "event_types": event_type_stats,
            "platforms": platform_stats,
            "last_activity": last_activity,
            "totalSpent": float(total_spent),
            "purchases": purchases_count,
            "cart_items": cart_count,
            "wishlist_items": wishlist_count
        }
        
        logger.info(f"📊 [STATS] Fetched stats for user {user_id}")
        return stats
        
    except Exception as e:
        logger.error(f"❌ [STATS] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {str(e)}")

@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify router is working"""
    return {"message": "User data router is working"}

@router.post("/checkout/{user_id}")
async def checkout_cart(user_id: UUID, db: Session = Depends(get_db)):
    """Process checkout - convert cart items to purchases and clear cart"""
    try:
        # Get all cart items for the user
        cart_items = db.query(Interaction).filter(
            Interaction.user_id == user_id,
            Interaction.event_type == 'add_to_cart'
        ).all()
        
        if not cart_items:
            return {"message": "Cart is empty", "purchases": 0, "total_value": 0}
        
        # Convert cart items to purchases
        purchases_created = 0
        total_value = 0
        
        for cart_item in cart_items:
            # Get product details
            product = db.query(Product).filter(Product.product_id == cart_item.product_id).first()
            if product:
                # Create purchase interaction
                purchase_interaction = Interaction(
                    user_id=user_id,
                    product_id=cart_item.product_id,
                    session_id=cart_item.session_id,
                    event_type='purchase',
                    event_value=product.price,  # Use actual product price
                    platform=cart_item.platform,
                    device=cart_item.device
                )
                db.add(purchase_interaction)
                purchases_created += 1
                total_value += float(product.price)
        
        # Remove all cart items (add_to_cart interactions)
        db.query(Interaction).filter(
            Interaction.user_id == user_id,
            Interaction.event_type == 'add_to_cart'
        ).delete()
        
        db.commit()
        
        logger.info(f"🛒 [CHECKOUT] User {user_id} purchased {purchases_created} items worth ₹{total_value}")
        
        return {
            "message": "Checkout successful",
            "purchases": purchases_created,
            "total_value": total_value
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ [CHECKOUT] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Checkout failed: {str(e)}")
