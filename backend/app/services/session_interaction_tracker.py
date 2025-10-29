"""
Session Interaction Tracker
Tracks and logs all user interactions during a session
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models import Session as SessionModel, Interaction
from app.models.product import Product

logger = logging.getLogger(__name__)


class SessionInteractionTracker:
    """Tracks all interactions for a session and stores them as JSON"""
    
    def __init__(self):
        self.logger = logger
    
    def log_interaction(
        self,
        db: Session,
        session_id: str,
        user_id: str,
        event_type: str,
        product_id: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Log an interaction and update session context"""
        try:
            # Get current session
            session = db.query(SessionModel).filter(
                SessionModel.session_id == session_id
            ).first()
            
            if not session:
                self.logger.warning(f"⚠️ [SESSION_TRACKER] Session {session_id} not found")
                return False
            
            # Create interaction record
            interaction_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "user_id": user_id,
                "product_id": product_id,
                "additional_data": additional_data or {}
            }
            
            # Create actual Interaction record in database
            interaction_record = Interaction(
                user_id=user_id,
                session_id=session_id,
                product_id=None,  # Set to None if not a valid UUID
                event_type=event_type,
                event_value=1,
                platform="web",
                device=additional_data or {},
                created_at=datetime.utcnow()
            )
            
            # Only set product_id if it's a valid UUID
            if product_id:
                try:
                    import uuid
                    uuid.UUID(product_id)  # Validate UUID format
                    interaction_record.product_id = product_id
                except (ValueError, TypeError):
                    # Store non-UUID product_id in device field instead
                    device_data = additional_data or {}
                    device_data["product_id_string"] = product_id
                    interaction_record.device = device_data
                    self.logger.info(f"📝 [SESSION_TRACKER] Stored non-UUID product_id '{product_id}' in device field")
            
            db.add(interaction_record)
            db.commit()
            
            self.logger.info(f"📝 [SESSION_TRACKER] Created Interaction record with ID: {interaction_record.id}")
            
            # Console log for user interaction stored in DB
            product_name = None
            if interaction_record.product_id:
                product = db.query(Product).filter(Product.product_id == interaction_record.product_id).first()
                if product:
                    product_name = product.name
            
            print(f"👆 [DB_INTERACTION] User interaction stored in database:")
            print(f"   Interaction ID: {interaction_record.id}")
            print(f"   User ID: {user_id}")
            print(f"   Session ID: {session_id}")
            print(f"   Event Type: {event_type}")
            print(f"   Product ID: {product_id or 'N/A'}")
            print(f"   Product Name: {product_name or 'N/A'}")
            print(f"   Platform: web")
            print(f"   Device Data: {additional_data or {}}")
            print(f"   Created At: {interaction_record.created_at}")
            print(f"   Database Record: ✅ VERIFIED")
            
            # Get current interactions from session context
            current_context = session.context or {}
            if isinstance(current_context, str):
                try:
                    import json
                    current_context = json.loads(current_context)
                except (json.JSONDecodeError, TypeError):
                    self.logger.warning(f"⚠️ [SESSION_TRACKER] Failed to parse context as JSON: {current_context}")
                    current_context = {}
            
            # Ensure current_context is a dictionary
            if not isinstance(current_context, dict):
                self.logger.warning(f"⚠️ [SESSION_TRACKER] Context is not a dict after parsing: {type(current_context)}")
                current_context = {}
            
            interactions = current_context.get("interactions", [])
            
            # Add new interaction
            interactions.append(interaction_data)
            
            # Update session context with interactions
            current_context["interactions"] = interactions
            current_context["total_interactions"] = len(interactions)
            current_context["last_interaction"] = interaction_data["timestamp"]
            current_context["last_interaction_type"] = event_type
            
            # Update session
            session.context = current_context
            db.commit()
            
            self.logger.info(f"📝 [SESSION_TRACKER] Logged {event_type} interaction for session {session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ [SESSION_TRACKER] Failed to log interaction: {str(e)}")
            return False
    
    def get_session_interactions(
        self,
        db: Session,
        session_id: str
    ) -> List[Dict[str, Any]]:
        """Get all interactions for a session"""
        try:
            # Query actual Interaction records from database
            interactions = db.query(Interaction).filter(
                Interaction.session_id == session_id
            ).order_by(Interaction.created_at).all()
            
            result = []
            for interaction in interactions:
                result.append({
                    "id": str(interaction.id),
                    "user_id": str(interaction.user_id) if interaction.user_id else None,
                    "product_id": str(interaction.product_id) if interaction.product_id else None,
                    "session_id": str(interaction.session_id) if interaction.session_id else None,
                    "event_type": interaction.event_type,
                    "event_value": float(interaction.event_value) if interaction.event_value else None,
                    "platform": interaction.platform,
                    "device": interaction.device,
                    "created_at": interaction.created_at.isoformat() if interaction.created_at else None
                })
            
            self.logger.info(f"📊 [SESSION_TRACKER] Retrieved {len(result)} interactions for session {session_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ [SESSION_TRACKER] Failed to get interactions: {str(e)}")
            return []
    
    def get_session_summary(
        self,
        db: Session,
        session_id: str
    ) -> Dict[str, Any]:
        """Get session summary with interaction statistics"""
        try:
            session = db.query(SessionModel).filter(
                SessionModel.session_id == session_id
            ).first()
            
            if not session:
                return {}
            
            # Get actual interactions from database
            interactions = db.query(Interaction).filter(
                Interaction.session_id == session_id
            ).order_by(Interaction.created_at).all()
            
            # Calculate statistics
            event_types = {}
            product_interactions = {}
            time_intervals = []
            
            for i, interaction in enumerate(interactions):
                event_type = interaction.event_type
                event_types[event_type] = event_types.get(event_type, 0) + 1
                
                if interaction.product_id:
                    product_id = str(interaction.product_id)
                    product_interactions[product_id] = product_interactions.get(product_id, 0) + 1
                
                # Calculate time intervals between interactions
                if i > 0:
                    prev_time = interactions[i-1].created_at
                    curr_time = interaction.created_at
                    interval = (curr_time - prev_time).total_seconds()
                    time_intervals.append(interval)
            
            # Calculate session duration
            session_duration = None
            if session.started_at:
                end_time = session.ended_at or datetime.utcnow()
                session_duration = (end_time - session.started_at).total_seconds()
            
            # Convert interactions to JSON-serializable format
            interactions_json = []
            for interaction in interactions:
                interactions_json.append({
                    "id": str(interaction.id),
                    "user_id": str(interaction.user_id) if interaction.user_id else None,
                    "product_id": str(interaction.product_id) if interaction.product_id else None,
                    "session_id": str(interaction.session_id) if interaction.session_id else None,
                    "event_type": interaction.event_type,
                    "event_value": float(interaction.event_value) if interaction.event_value else None,
                    "platform": interaction.platform,
                    "device": interaction.device,
                    "created_at": interaction.created_at.isoformat() if interaction.created_at else None
                })
            
            summary = {
                "session_id": str(session.session_id),
                "user_id": str(session.user_id) if session.user_id else None,
                "started_at": session.started_at.isoformat() if session.started_at else None,
                "ended_at": session.ended_at.isoformat() if session.ended_at else None,
                "session_duration_seconds": session_duration,
                "total_interactions": len(interactions),
                "event_type_counts": event_types,
                "product_interaction_counts": product_interactions,
                "average_time_between_interactions": sum(time_intervals) / len(time_intervals) if time_intervals else 0,
                "first_interaction": interactions[0].created_at.isoformat() if interactions else None,
                "last_interaction": interactions[-1].created_at.isoformat() if interactions else None,
                "interactions": interactions_json
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"❌ [SESSION_TRACKER] Failed to get session summary: {str(e)}")
            return {}
    
    def log_page_view(
        self,
        db: Session,
        session_id: str,
        user_id: str,
        page_path: str,
        referrer: Optional[str] = None
    ) -> bool:
        """Log a page view interaction"""
        return self.log_interaction(
            db=db,
            session_id=session_id,
            user_id=user_id,
            event_type="page_view",
            additional_data={
                "page_path": page_path,
                "referrer": referrer
            }
        )
    
    def log_product_view(
        self,
        db: Session,
        session_id: str,
        user_id: str,
        product_id: str,
        product_name: Optional[str] = None
    ) -> bool:
        """Log a product view interaction"""
        return self.log_interaction(
            db=db,
            session_id=session_id,
            user_id=user_id,
            event_type="product_view",
            product_id=product_id,
            additional_data={
                "product_name": product_name
            }
        )
    
    def log_cart_action(
        self,
        db: Session,
        session_id: str,
        user_id: str,
        product_id: str,
        action: str,  # add, remove, update
        quantity: Optional[int] = None
    ) -> bool:
        """Log a cart action interaction"""
        return self.log_interaction(
            db=db,
            session_id=session_id,
            user_id=user_id,
            event_type=f"cart_{action}",
            product_id=product_id,
            additional_data={
                "quantity": quantity,
                "action": action
            }
        )
    
    def log_search(
        self,
        db: Session,
        session_id: str,
        user_id: str,
        query: str,
        results_count: Optional[int] = None
    ) -> bool:
        """Log a search interaction"""
        return self.log_interaction(
            db=db,
            session_id=session_id,
            user_id=user_id,
            event_type="search",
            additional_data={
                "query": query,
                "results_count": results_count
            }
        )
    
    def log_wishlist_action(
        self,
        db: Session,
        session_id: str,
        user_id: str,
        product_id: str,
        action: str  # add, remove
    ) -> bool:
        """Log a wishlist action interaction"""
        return self.log_interaction(
            db=db,
            session_id=session_id,
            user_id=user_id,
            event_type=f"wishlist_{action}",
            product_id=product_id,
            additional_data={
                "action": action
            }
        )


    def log_review(
        self,
        db: Session,
        session_id: str,
        user_id: str,
        product_id: str,
        rating: int,
        review_text: Optional[str] = None
    ) -> bool:
        """Log a product review interaction"""
        print(f"⭐ [REVIEW] Logging review interaction:")
        print(f"   User ID: {user_id}")
        print(f"   Session ID: {session_id}")
        print(f"   Product ID: {product_id}")
        print(f"   Rating: {rating}")
        print(f"   Review Text: {review_text[:100] + '...' if review_text and len(review_text) > 100 else review_text}")
        print(f"   Timestamp: {datetime.utcnow().isoformat()}")
        
        # Log the interaction
        success = self.log_interaction(
            db=db,
            session_id=session_id,
            user_id=user_id,
            event_type="review",
            product_id=product_id,
            additional_data={
                "rating": rating,
                "review_text": review_text,
                "event_value": rating
            }
        )
        
        # If interaction logging was successful, also create a review record and update product ratings
        if success:
            try:
                # Create review record in reviews table
                from app.models.review import Review
                review = Review(
                    user_id=user_id,
                    product_id=product_id,
                    rating=rating,
                    comment=review_text,
                    verified_purchase=True  # Assume verified since it's from interaction
                )
                db.add(review)
                db.commit()
                
                # Update product ratings
                self._update_product_ratings(db, product_id)
                
                print(f"✅ [REVIEW] Review record created and product ratings updated")
                
            except Exception as e:
                self.logger.error(f"❌ [REVIEW] Failed to create review record or update ratings: {str(e)}")
                # Don't fail the interaction logging if review creation fails
        
        return success
    
    def _update_product_ratings(self, db: Session, product_id: str):
        """Update product rating fields based on reviews"""
        try:
            # Calculate rating statistics from reviews table
            rating_stats = db.execute(text("""
                SELECT 
                    COUNT(*) as total_reviews,
                    AVG(rating) as average_rating,
                    COUNT(CASE WHEN rating = 1 THEN 1 END) as rating_1,
                    COUNT(CASE WHEN rating = 2 THEN 1 END) as rating_2,
                    COUNT(CASE WHEN rating = 3 THEN 1 END) as rating_3,
                    COUNT(CASE WHEN rating = 4 THEN 1 END) as rating_4,
                    COUNT(CASE WHEN rating = 5 THEN 1 END) as rating_5
                FROM reviews 
                WHERE product_id = :product_id
            """), {'product_id': product_id}).fetchone()
            
            if rating_stats:
                total_reviews = rating_stats.total_reviews or 0
                average_rating = float(rating_stats.average_rating) if rating_stats.average_rating else 0.0
                
                # Create rating distribution JSON
                rating_distribution = {
                    "1": int(rating_stats.rating_1 or 0),
                    "2": int(rating_stats.rating_2 or 0),
                    "3": int(rating_stats.rating_3 or 0),
                    "4": int(rating_stats.rating_4 or 0),
                    "5": int(rating_stats.rating_5 or 0)
                }
                
                # Update product with rating data
                db.execute(text("""
                    UPDATE products 
                    SET 
                        average_rating = :average_rating,
                        total_reviews = :total_reviews,
                        rating_distribution = :rating_distribution,
                        updated_at = NOW()
                    WHERE product_id = :product_id
                """), {
                    'product_id': product_id,
                    'average_rating': average_rating,
                    'total_reviews': total_reviews,
                    'rating_distribution': str(rating_distribution).replace("'", '"')
                })
                
                db.commit()
                print(f"📊 [RATINGS] Updated product {product_id}: {average_rating:.2f}/5.0 ({total_reviews} reviews)")
                
        except Exception as e:
            self.logger.error(f"❌ [RATINGS] Failed to update product ratings: {str(e)}")
            db.rollback()
    
    def finalize_session(
        self,
        db: Session,
        session_id: str
    ) -> Dict[str, Any]:
        """Finalize session and return complete interaction summary"""
        try:
            summary = self.get_session_summary(db, session_id)
            
            # Update session context with final summary
            session = db.query(SessionModel).filter(
                SessionModel.session_id == session_id
            ).first()
            
            if session:
                context = session.context or {}
                if isinstance(context, str):
                    try:
                        import json
                        context = json.loads(context)
                    except (json.JSONDecodeError, TypeError):
                        self.logger.warning(f"⚠️ [SESSION_TRACKER] Failed to parse context as JSON: {context}")
                        context = {}
                
                context["session_summary"] = summary
                context["finalized_at"] = datetime.utcnow().isoformat()
                session.context = context
                db.commit()
                
                self.logger.info(f"📊 [SESSION_TRACKER] Finalized session {session_id} with {summary.get('total_interactions', 0) if isinstance(summary, dict) else 0} interactions")
            
            return summary
            
        except Exception as e:
            self.logger.error(f"❌ [SESSION_TRACKER] Failed to finalize session: {str(e)}")
            return {}


# Global session interaction tracker instance
session_tracker = SessionInteractionTracker()
