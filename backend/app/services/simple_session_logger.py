"""
Simple Session Logging Service
"""

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.interaction import Session as SessionModel, Interaction
from app.models.product import Product
import logging

logger = logging.getLogger(__name__)

class SimpleSessionLogger:
    """Simple session logging service"""
    
    def create_session(self, db: Session, user_id: str, request=None) -> str:
        """Create a new session"""
        try:
            session = SessionModel(
                user_id=user_id,
                started_at=datetime.now(timezone.utc),
                context={"session_started": True}
            )
            db.add(session)
            db.commit()
            
            logger.info(f"✅ [SESSION] Created session {session.session_id} for user {user_id}")
            
            # Console log for login session details stored in DB
            print(f"🔐 [DB_LOGIN] Session created and stored in database:")
            print(f"   Session ID: {session.session_id}")
            print(f"   User ID: {user_id}")
            print(f"   Started At: {session.started_at}")
            print(f"   Context: {session.context}")
            print(f"   Database Record: ✅ VERIFIED")
            
            return str(session.session_id)
            
        except Exception as e:
            logger.error(f"❌ [SESSION] Failed to create session: {str(e)}")
            db.rollback()
            raise
    
    def end_session(self, db: Session, user_id: str, session_id: str, request=None) -> bool:
        """End a session and log logout interaction"""
        try:
            logger.info(f"🔍 [SIMPLE_SESSION] Starting to end session {session_id} for user {user_id}")
            
            # Find the session
            session = db.query(SessionModel).filter(
                SessionModel.session_id == session_id,
                SessionModel.user_id == user_id,
                SessionModel.ended_at.is_(None)
            ).first()
            
            if not session:
                logger.warning(f"⚠️ [SIMPLE_SESSION] No active session found for user {user_id}")
                return False
            
            logger.info(f"🔍 [SIMPLE_SESSION] Found session {session_id}, updating...")
            
            # Update session end time
            session.ended_at = datetime.now(timezone.utc)
            
            # Calculate duration
            duration = (session.ended_at - session.started_at).total_seconds()
            
            # Update context
            context = session.context or {}
            context.update({
                "session_ended": True,
                "duration_seconds": duration,
                "logout_time": session.ended_at.isoformat()
            })
            session.context = context
            
            # Force SQLAlchemy to detect the JSON field change
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(session, 'context')
            
            logger.info(f"🔍 [SIMPLE_SESSION] Updated session context: {context}")
            
            # Get all interactions for this session
            session_interactions = db.query(Interaction).filter(
                Interaction.session_id == session_id
            ).order_by(Interaction.created_at).all()
            
            # Convert interactions to JSON-serializable format with product names
            interactions_json = []
            for interaction in session_interactions:
                # Get product name if product_id exists
                product_name = None
                if interaction.product_id:
                    product = db.query(Product).filter(Product.product_id == interaction.product_id).first()
                    if product:
                        product_name = product.name
                
                interaction_data = {
                    "id": str(interaction.id),
                    "user_id": str(interaction.user_id) if interaction.user_id else None,
                    "product_id": str(interaction.product_id) if interaction.product_id else None,
                    "product_name": product_name,
                    "session_id": str(interaction.session_id) if interaction.session_id else None,
                    "event_type": interaction.event_type,
                    "event_value": float(interaction.event_value) if interaction.event_value else None,
                    "platform": interaction.platform,
                    "device": interaction.device,
                    "created_at": interaction.created_at.isoformat() if interaction.created_at else None
                }
                interactions_json.append(interaction_data)
            
            logger.info(f"🔍 [SIMPLE_SESSION] Found {len(interactions_json)} interactions for session")
            
            # Log logout interaction with detailed context including all session interactions
            interaction_context = {
                "logout_event": True,
                "session_duration": duration,
                "logout_timestamp": session.ended_at.isoformat(),
                "session_context": context,
                "session_interactions": interactions_json,
                "total_interactions": len(interactions_json),
                "user_agent": getattr(request, 'headers', {}).get('user-agent', 'unknown') if request else 'unknown',
                "logout_method": "api_call"
            }
            
            interaction = Interaction(
                user_id=user_id,
                session_id=session_id,
                event_type="logout",
                event_value=1,
                platform="web",
                device=interaction_context,  # Store detailed context in device field
                created_at=datetime.now(timezone.utc)
            )
            db.add(interaction)
            
            logger.info(f"🔍 [SIMPLE_SESSION] Added logout interaction to database")
            
            # Commit everything
            db.commit()
            
            # Console log for logout session details and context stored in DB
            print(f"🚪 [DB_LOGOUT] Session ended and stored in database:")
            print(f"   Session ID: {session_id}")
            print(f"   User ID: {user_id}")
            print(f"   Started At: {session.started_at}")
            print(f"   Ended At: {session.ended_at}")
            print(f"   Duration: {duration:.1f} seconds")
            print(f"   Session Context: {context}")
            print(f"   Total Interactions: {len(interactions_json)}")
            print(f"   User Agent: {interaction_context.get('user_agent', 'unknown')}")
            print(f"   Database Records: ✅ VERIFIED")
            
            # Console log for all session interactions stored in DB
            if interactions_json:
                print(f"📊 [DB_INTERACTIONS] All session interactions stored in database:")
                for i, interaction in enumerate(interactions_json, 1):
                    product_info = f"Product: {interaction['product_name']} ({interaction['product_id']})" if interaction['product_name'] else f"Product ID: {interaction['product_id'] or 'N/A'}"
                    print(f"   {i}. Event: {interaction['event_type']}")
                    print(f"      {product_info}")
                    print(f"      Created At: {interaction['created_at']}")
                    print(f"      Device Data: {interaction.get('device', {})}")
            else:
                print(f"📊 [DB_INTERACTIONS] No interactions recorded during this session")
            
            logger.info(f"✅ [SIMPLE_SESSION] Successfully ended session {session_id} for user {user_id} (duration: {duration:.1f}s)")
            return True
            
        except Exception as e:
            logger.error(f"❌ [SIMPLE_SESSION] Failed to end session: {str(e)}")
            import traceback
            logger.error(f"❌ [SIMPLE_SESSION] Traceback: {traceback.format_exc()}")
            db.rollback()
            return False

# Global instance
session_logger = SimpleSessionLogger()
