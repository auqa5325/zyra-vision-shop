"""
Session Interaction API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from uuid import UUID

from app.database import get_db
from app.services.session_interaction_tracker import session_tracker
from app.middleware.auth import JWTSecurity

router = APIRouter(prefix="/api/session", tags=["session-interactions"])


@router.post("/log-interaction")
async def log_interaction(
    event_type: str,
    product_id: Optional[str] = None,
    additional_data: Optional[Dict[str, Any]] = None,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTSecurity())
):
    """Log an interaction for the current session"""
    try:
        # Validate event_type - allow core interaction types
        allowed_types = ['view', 'click', 'add_to_cart', 'purchase', 'review', 'wishlist']
        if event_type not in allowed_types:
            raise HTTPException(status_code=400, detail=f"Invalid event_type. Allowed types: {allowed_types}")
        
        user_id = current_user.get("user_id") or current_user.get("sub")
        session_id = current_user.get("session_id")
        
        if not user_id or not session_id:
            raise HTTPException(status_code=400, detail="User ID or session ID not found in token")
        
        # Set event_value based on event_type
        if event_type == 'review' and additional_data and 'rating' in additional_data:
            additional_data['event_value'] = additional_data['rating']
        elif event_type in ['view', 'click', 'purchase', 'wishlist']:
            additional_data = additional_data or {}
            additional_data['event_value'] = 1
        elif event_type == 'add_to_cart':
            additional_data = additional_data or {}
            additional_data['event_value'] = additional_data.get('quantity', 1)
        
        success = session_tracker.log_interaction(
            db=db,
            session_id=session_id,
            user_id=user_id,
            event_type=event_type,
            product_id=product_id,
            additional_data=additional_data
        )
        
        if success:
            return {"message": "Interaction logged successfully", "event_type": event_type}
        else:
            raise HTTPException(status_code=500, detail="Failed to log interaction")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error logging interaction: {str(e)}")


@router.post("/log-review")
async def log_review(
    product_id: str,
    rating: int,
    review_text: Optional[str] = None,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTSecurity())
):
    """Log a product review interaction"""
    try:
        if rating < 1 or rating > 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        user_id = current_user.get("user_id") or current_user.get("sub")
        session_id = current_user.get("session_id")
        
        if not user_id or not session_id:
            raise HTTPException(status_code=400, detail="User ID or session ID not found in token")
        
        success = session_tracker.log_review(
            db=db,
            session_id=session_id,
            user_id=user_id,
            product_id=product_id,
            rating=rating,
            review_text=review_text
        )
        
        if success:
            return {
                "message": "Review logged successfully", 
                "product_id": product_id,
                "rating": rating,
                "review_text": review_text
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to log review")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log review: {str(e)}")


@router.post("/log-page-view")
async def log_page_view(
    page_path: str,
    referrer: Optional[str] = None,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTSecurity())
):
    """Log a page view interaction"""
    try:
        user_id = current_user.get("user_id") or current_user.get("sub")
        session_id = current_user.get("session_id")
        
        if not user_id or not session_id:
            raise HTTPException(status_code=400, detail="User ID or session ID not found in token")
        
        success = session_tracker.log_page_view(
            db=db,
            session_id=session_id,
            user_id=user_id,
            page_path=page_path,
            referrer=referrer
        )
        
        if success:
            return {"message": "Page view logged successfully", "page_path": page_path}
        else:
            raise HTTPException(status_code=500, detail="Failed to log page view")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error logging page view: {str(e)}")


@router.post("/log-product-view")
async def log_product_view(
    product_id: str,
    product_name: Optional[str] = None,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTSecurity())
):
    """Log a product view interaction"""
    try:
        user_id = current_user.get("user_id") or current_user.get("sub")
        session_id = current_user.get("session_id")
        
        if not user_id or not session_id:
            raise HTTPException(status_code=400, detail="User ID or session ID not found in token")
        
        success = session_tracker.log_product_view(
            db=db,
            session_id=session_id,
            user_id=user_id,
            product_id=product_id,
            product_name=product_name
        )
        
        if success:
            return {"message": "Product view logged successfully", "product_id": product_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to log product view")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error logging product view: {str(e)}")


@router.post("/log-cart-action")
async def log_cart_action(
    product_id: str,
    action: str,  # add, remove, update
    quantity: Optional[int] = None,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTSecurity())
):
    """Log a cart action interaction"""
    try:
        user_id = current_user.get("user_id") or current_user.get("sub")
        session_id = current_user.get("session_id")
        
        if not user_id or not session_id:
            raise HTTPException(status_code=400, detail="User ID or session ID not found in token")
        
        success = session_tracker.log_cart_action(
            db=db,
            session_id=session_id,
            user_id=user_id,
            product_id=product_id,
            action=action,
            quantity=quantity
        )
        
        if success:
            return {"message": "Cart action logged successfully", "action": action, "product_id": product_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to log cart action")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error logging cart action: {str(e)}")


@router.post("/log-search")
async def log_search(
    query: str,
    results_count: Optional[int] = None,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTSecurity())
):
    """Log a search interaction"""
    try:
        user_id = current_user.get("user_id") or current_user.get("sub")
        session_id = current_user.get("session_id")
        
        if not user_id or not session_id:
            raise HTTPException(status_code=400, detail="User ID or session ID not found in token")
        
        success = session_tracker.log_search(
            db=db,
            session_id=session_id,
            user_id=user_id,
            query=query,
            results_count=results_count
        )
        
        if success:
            return {"message": "Search logged successfully", "query": query}
        else:
            raise HTTPException(status_code=500, detail="Failed to log search")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error logging search: {str(e)}")


@router.get("/interactions")
async def get_session_interactions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTSecurity())
):
    """Get all interactions for the current session"""
    try:
        user_id = current_user.get("user_id") or current_user.get("sub")
        session_id = current_user.get("session_id")
        
        if not user_id or not session_id:
            raise HTTPException(status_code=400, detail="User ID or session ID not found in token")
        
        interactions = session_tracker.get_session_interactions(db, session_id)
        
        return {
            "session_id": session_id,
            "user_id": user_id,
            "interactions": interactions,
            "total_interactions": len(interactions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting interactions: {str(e)}")


@router.get("/summary")
async def get_session_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTSecurity())
):
    """Get session summary with interaction statistics"""
    try:
        user_id = current_user.get("user_id") or current_user.get("sub")
        session_id = current_user.get("session_id")
        
        if not user_id or not session_id:
            raise HTTPException(status_code=400, detail="User ID or session ID not found in token")
        
        summary = session_tracker.get_session_summary(db, session_id)
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting session summary: {str(e)}")


@router.get("/summary/{session_id}")
async def get_session_summary_by_id(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTSecurity())
):
    """Get session summary for a specific session ID (admin only)"""
    try:
        user_id = current_user.get("user_id") or current_user.get("sub")
        
        # For now, allow any authenticated user to get any session summary
        # In production, you might want to add admin role checking
        
        summary = session_tracker.get_session_summary(db, session_id)
        
        if not summary:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting session summary: {str(e)}")
