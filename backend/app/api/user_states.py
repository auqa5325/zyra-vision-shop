"""
Optimized API endpoints for user states - Cart, Wishlist, Purchase History
Using dedicated tables instead of scanning interactions
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import List, Optional
from uuid import UUID
import logging

from app.database import get_db
from app.models import UserCart, UserWishlist, PurchaseHistory, Product, User
from app.models.product import ProductImage
from app.schemas.user_states import (
    CartItemCreate, CartItemUpdate, CartItemResponse, CartResponse,
    WishlistItemCreate, WishlistItemResponse, WishlistResponse,
    PurchaseItemCreate, PurchaseItemResponse, PurchaseHistoryResponse,
    OrderCreate, OrderResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/user-states", tags=["user-states"])


def get_product_image_url(db: Session, product_id: UUID) -> str:
    """Get the proper image URL for a product from the database"""
    try:
        # Get the primary image URL from the database
        primary_image = db.query(ProductImage).filter(
            ProductImage.product_id == product_id,
            ProductImage.is_primary == True
        ).first()
        
        if primary_image and primary_image.cdn_url:
            # Use S3 URL if available, otherwise construct proxy URL
            if primary_image.cdn_url.startswith('http'):
                return primary_image.cdn_url
            else:
                return f"http://localhost:8005{primary_image.cdn_url}"
        else:
            # Fallback to proxy URL
            return f"http://localhost:8005/api/images/proxy/{product_id}/1"
    except Exception as e:
        logger.warning(f"Failed to get image URL for product {product_id}: {e}")
        return f"http://localhost:8005/api/images/proxy/{product_id}/1"


# Cart Endpoints
@router.get("/cart/{user_id}")
async def get_user_cart(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Get user's cart items - FAST query using dedicated table"""
    try:
        # Single optimized query with JOIN
        cart_items = db.query(
            UserCart.id,
            UserCart.user_id,
            UserCart.product_id,
            UserCart.quantity,
            UserCart.added_at,
            UserCart.updated_at,
            Product.name.label('product_name'),
            Product.price.label('product_price'),
            Product.discount_percent.label('product_discount_percent')
        ).join(
            Product, UserCart.product_id == Product.product_id
        ).filter(
            UserCart.user_id == user_id
        ).order_by(
            desc(UserCart.added_at)
        ).all()
        
        # Calculate totals
        total_items = sum(item.quantity for item in cart_items)
        total_price = sum(item.product_price * item.quantity for item in cart_items)
        
        # Transform to simple dict format
        items = []
        for item in cart_items:
            items.append({
                "id": item.id,
                "user_id": str(item.user_id),
                "product_id": str(item.product_id),
                "quantity": item.quantity,
                "added_at": item.added_at.isoformat(),
                "updated_at": item.updated_at.isoformat(),
                "product_name": item.product_name,
                "product_price": float(item.product_price) if item.product_price else 0,
                "product_discount_percent": float(item.product_discount_percent) if item.product_discount_percent else 0,
                "product_image": get_product_image_url(db, item.product_id)
            })
        
        logger.info(f"🛒 [CART] Fetched {len(items)} items for user {user_id}")
        return {
            "items": items,
            "total_items": total_items,
            "total_price": float(total_price) if total_price else 0
        }
        
    except Exception as e:
        logger.error(f"❌ [CART] Failed to fetch cart: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch cart: {str(e)}")


@router.post("/cart/{user_id}/add", response_model=CartItemResponse)
async def add_to_cart(
    user_id: UUID,
    item: CartItemCreate,
    db: Session = Depends(get_db)
):
    """Add item to cart - FAST operation using dedicated table"""
    try:
        # Check if item already exists in cart
        existing_item = db.query(UserCart).filter(
            and_(UserCart.user_id == user_id, UserCart.product_id == item.product_id)
        ).first()
        
        if existing_item:
            # Update quantity
            existing_item.quantity += item.quantity
            db.commit()
            db.refresh(existing_item)
            
            # Get product details for response
            product = db.query(Product).filter(Product.product_id == item.product_id).first()
            
            # Construct image URL
            image_url = get_product_image_url(db, item.product_id)
            
            logger.info(f"🛒 [CART] Updated quantity for user {user_id}, product {item.product_id}")
            return CartItemResponse(
                id=existing_item.id,
                user_id=existing_item.user_id,
                product_id=existing_item.product_id,
                quantity=existing_item.quantity,
                added_at=existing_item.added_at,
                updated_at=existing_item.updated_at,
                product_name=product.name,
                product_price=product.price,
                product_image=image_url
            )
        else:
            # Add new item
            cart_item = UserCart(
                user_id=user_id,
                product_id=item.product_id,
                quantity=item.quantity
            )
            db.add(cart_item)
            db.commit()
            db.refresh(cart_item)
            
            # Get product details for response
            product = db.query(Product).filter(Product.product_id == item.product_id).first()
            
            # Construct image URL
            image_url = get_product_image_url(db, item.product_id)
            
            logger.info(f"🛒 [CART] Added new item for user {user_id}, product {item.product_id}")
            return CartItemResponse(
                id=cart_item.id,
                user_id=cart_item.user_id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                added_at=cart_item.added_at,
                updated_at=cart_item.updated_at,
                product_name=product.name,
                product_price=product.price,
                product_image=image_url
            )
            
    except Exception as e:
        db.rollback()
        logger.error(f"❌ [CART] Failed to add to cart: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add to cart: {str(e)}")


@router.put("/cart/{user_id}/update/{item_id}", response_model=CartItemResponse)
async def update_cart_item(
    user_id: UUID,
    item_id: int,
    update: CartItemUpdate,
    db: Session = Depends(get_db)
):
    """Update cart item quantity"""
    try:
        cart_item = db.query(UserCart).filter(
            and_(UserCart.id == item_id, UserCart.user_id == user_id)
        ).first()
        
        if not cart_item:
            raise HTTPException(status_code=404, detail="Cart item not found")
        
        if update.quantity == 0:
            # Remove item
            db.delete(cart_item)
            db.commit()
            return None
        else:
            # Update quantity
            cart_item.quantity = update.quantity
            db.commit()
            db.refresh(cart_item)
            
            # Get product details
            product = db.query(Product).filter(Product.product_id == cart_item.product_id).first()
            
            # Construct image URL
            image_url = get_product_image_url(db, cart_item.product_id)
            
            return CartItemResponse(
                id=cart_item.id,
                user_id=cart_item.user_id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                added_at=cart_item.added_at,
                updated_at=cart_item.updated_at,
                product_name=product.name,
                product_price=product.price,
                product_image=image_url
            )
            
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ [CART] Failed to update cart item: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update cart item: {str(e)}")


@router.delete("/cart/{user_id}/clear")
async def clear_cart(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Clear user's entire cart"""
    try:
        deleted_count = db.query(UserCart).filter(UserCart.user_id == user_id).delete()
        db.commit()
        
        logger.info(f"🛒 [CART] Cleared {deleted_count} items for user {user_id}")
        return {"message": f"Cleared {deleted_count} items from cart"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ [CART] Failed to clear cart: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cart: {str(e)}")


@router.delete("/cart/{user_id}/remove/{product_id}")
async def remove_from_cart(
    user_id: UUID,
    product_id: UUID,
    db: Session = Depends(get_db)
):
    """Remove specific item from cart"""
    try:
        deleted_count = db.query(UserCart).filter(
            and_(UserCart.user_id == user_id, UserCart.product_id == product_id)
        ).delete()
        
        if deleted_count == 0:
            raise HTTPException(status_code=404, detail="Item not found in cart")
        
        db.commit()
        logger.info(f"🛒 [CART] Removed item for user {user_id}, product {product_id}")
        return {"message": "Item removed from cart"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ [CART] Failed to remove from cart: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to remove from cart: {str(e)}")


# Test endpoint
@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify router is working"""
    return {"message": "User states router is working"}

# Wishlist Endpoints
@router.get("/wishlist/{user_id}")
async def get_user_wishlist(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Get user's wishlist - FAST query using dedicated table"""
    try:
        wishlist_items = db.query(
            UserWishlist.id,
            UserWishlist.user_id,
            UserWishlist.product_id,
            UserWishlist.added_at,
            Product.name.label('product_name'),
            Product.price.label('product_price'),
            Product.discount_percent.label('product_discount_percent')
        ).join(
            Product, UserWishlist.product_id == Product.product_id
        ).filter(
            UserWishlist.user_id == user_id
        ).order_by(
            desc(UserWishlist.added_at)
        ).all()
        
        # Transform to simple dict format
        items = []
        for item in wishlist_items:
            items.append({
                "id": item.id,
                "user_id": str(item.user_id),
                "product_id": str(item.product_id),
                "added_at": item.added_at.isoformat(),
                "product_name": item.product_name,
                "product_price": float(item.product_price) if item.product_price else 0,
                "product_discount_percent": float(item.product_discount_percent) if item.product_discount_percent else 0,
                "product_image": get_product_image_url(db, item.product_id)
            })
        
        logger.info(f"❤️ [WISHLIST] Fetched {len(items)} items for user {user_id}")
        return {
            "items": items,
            "total_items": len(items)
        }
        
    except Exception as e:
        logger.error(f"❌ [WISHLIST] Failed to fetch wishlist: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch wishlist: {str(e)}")


@router.post("/wishlist/{user_id}/add", response_model=WishlistItemResponse)
async def add_to_wishlist(
    user_id: UUID,
    item: WishlistItemCreate,
    db: Session = Depends(get_db)
):
    """Add item to wishlist"""
    try:
        # Check if already in wishlist
        existing = db.query(UserWishlist).filter(
            and_(UserWishlist.user_id == user_id, UserWishlist.product_id == item.product_id)
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Item already in wishlist")
        
        wishlist_item = UserWishlist(
            user_id=user_id,
            product_id=item.product_id
        )
        db.add(wishlist_item)
        db.commit()
        db.refresh(wishlist_item)
        
        # Get product details
        product = db.query(Product).filter(Product.product_id == item.product_id).first()
        
        # Construct image URL
        image_url = f"http://localhost:8005/api/images/proxy/{item.product_id}/1"
        
        logger.info(f"❤️ [WISHLIST] Added item for user {user_id}, product {item.product_id}")
        return WishlistItemResponse(
            id=wishlist_item.id,
            user_id=wishlist_item.user_id,
            product_id=wishlist_item.product_id,
            added_at=wishlist_item.added_at,
            product_name=product.name,
            product_price=product.price,
            product_image=image_url
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ [WISHLIST] Failed to add to wishlist: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add to wishlist: {str(e)}")


@router.delete("/wishlist/{user_id}/remove/{product_id}")
async def remove_from_wishlist(
    user_id: UUID,
    product_id: UUID,
    db: Session = Depends(get_db)
):
    """Remove item from wishlist"""
    try:
        logger.info(f"💔 [WISHLIST] Attempting to remove product {product_id} from user {user_id} wishlist")
        
        # Check if item exists first
        existing_item = db.query(UserWishlist).filter(
            and_(UserWishlist.user_id == user_id, UserWishlist.product_id == product_id)
        ).first()
        
        if not existing_item:
            logger.warning(f"⚠️ [WISHLIST] Item not found in wishlist: user={user_id}, product={product_id}")
            raise HTTPException(status_code=404, detail="Item not found in wishlist")
        
        deleted_count = db.query(UserWishlist).filter(
            and_(UserWishlist.user_id == user_id, UserWishlist.product_id == product_id)
        ).delete()
        
        db.commit()
        logger.info(f"❤️ [WISHLIST] Successfully removed item for user {user_id}, product {product_id}")
        return {"message": "Item removed from wishlist", "success": True}
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ [WISHLIST] Failed to remove from wishlist: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to remove from wishlist: {str(e)}")


# Purchase History Endpoints
@router.get("/purchases/{user_id}", response_model=PurchaseHistoryResponse)
async def get_user_purchases(
    user_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get user's purchase history - FAST query using dedicated table"""
    try:
        purchases = db.query(
            PurchaseHistory.id,
            PurchaseHistory.user_id,
            PurchaseHistory.product_id,
            PurchaseHistory.quantity,
            PurchaseHistory.unit_price,
            PurchaseHistory.total_price,
            PurchaseHistory.order_id,
            PurchaseHistory.purchased_at,
            PurchaseHistory.payment_method,
            PurchaseHistory.payment_status,
            Product.name.label('product_name')
        ).join(
            Product, PurchaseHistory.product_id == Product.product_id
        ).filter(
            PurchaseHistory.user_id == user_id
        ).order_by(
            desc(PurchaseHistory.purchased_at)
        ).offset(offset).limit(limit).all()
        
        # Calculate totals
        total_spent = db.query(func.sum(PurchaseHistory.total_price)).filter(
            PurchaseHistory.user_id == user_id
        ).scalar() or 0
        
        unique_orders = db.query(func.count(func.distinct(PurchaseHistory.order_id))).filter(
            PurchaseHistory.user_id == user_id
        ).scalar() or 0
        
        # Transform to response format
        items = []
        for purchase in purchases:
            items.append(PurchaseItemResponse(
                id=purchase.id,
                user_id=purchase.user_id,
                product_id=purchase.product_id,
                quantity=purchase.quantity,
                unit_price=purchase.unit_price,
                total_price=purchase.total_price,
                order_id=purchase.order_id,
                purchased_at=purchase.purchased_at,
                payment_method=purchase.payment_method,
                payment_status=purchase.payment_status,
                product_name=purchase.product_name,
                product_image=get_product_image_url(db, purchase.product_id)
            ))
        
        logger.info(f"💰 [PURCHASES] Fetched {len(items)} purchases for user {user_id}")
        return PurchaseHistoryResponse(
            items=items,
            total_items=len(items),
            total_spent=total_spent,
            orders=unique_orders
        )
        
    except Exception as e:
        logger.error(f"❌ [PURCHASES] Failed to fetch purchases: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch purchases: {str(e)}")


@router.post("/purchases/{user_id}/checkout")
async def checkout_cart(
    user_id: UUID,
    order: OrderCreate,
    db: Session = Depends(get_db)
):
    """Process checkout - move cart items to purchase history"""
    try:
        from uuid import uuid4
        order_id = uuid4()
        
        # Handle empty cart case
        if not order.items:
            return {
                "order_id": str(order_id),
                "user_id": str(user_id),
                "items": [],
                "total_amount": 0.0,
                "payment_method": order.payment_method,
                "payment_status": order.payment_status,
                "created_at": None
            }
        
        # Create purchase records
        purchase_items = []
        total_amount = 0
        
        for item in order.items:
            # Get product details
            product = db.query(Product).filter(Product.product_id == item.product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
            
            purchase = PurchaseHistory(
                user_id=user_id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=product.price,
                total_price=product.price * item.quantity,
                order_id=order_id,
                payment_method=order.payment_method,
                payment_status=order.payment_status
            )
            db.add(purchase)
            purchase_items.append(purchase)
            total_amount += purchase.total_price
        
        # Remove items from cart
        db.query(UserCart).filter(UserCart.user_id == user_id).delete()
        
        db.commit()
        
        # Refresh to get IDs
        for item in purchase_items:
            db.refresh(item)
        
        logger.info(f"💰 [CHECKOUT] Processed order {order_id} for user {user_id}, total: {total_amount}")
        
        # Return order response
        return {
            "order_id": str(order_id),
            "user_id": str(user_id),
            "items": [],  # Would need to populate with product details
            "total_amount": float(total_amount),
            "payment_method": order.payment_method,
            "payment_status": order.payment_status,
            "created_at": purchase_items[0].purchased_at.isoformat() if purchase_items else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ [CHECKOUT] Failed to process checkout: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process checkout: {str(e)}")
