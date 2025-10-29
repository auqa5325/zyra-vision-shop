"""
Simple Session and Interaction Console Logging
Logs session and interaction data to console from start to end
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models import Session as SessionModel, Interaction, User

# Configure console logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Console output
    ]
)

logger = logging.getLogger(__name__)


class SimpleSessionLogger:
    """Simple console logger for sessions and interactions"""
    
    def __init__(self):
        self.logger = logger
    
    def log_session_start(self, user_id: str, session_id: str, context: Dict[str, Any] = None):
        """Log session start to console"""
        log_data = {
            "event": "SESSION_START",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "session_id": session_id,
            "context": context or {}
        }
        
        self.logger.info(f"🚀 SESSION START: {json.dumps(log_data, indent=2)}")
    
    def log_session_end(self, user_id: str, session_id: str, duration_seconds: float, context: Dict[str, Any] = None):
        """Log session end to console"""
        try:
            # Ensure context is a dictionary
            if context is None:
                context = {}
            elif isinstance(context, str):
                self.logger.warning(f"⚠️ [CONSOLE] Context is a string, converting to dict: {context}")
                context = {}
            
            log_data = {
                "event": "SESSION_END",
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "session_id": session_id,
                "duration_seconds": duration_seconds,
                "context": context
            }
            
            self.logger.info(f"🏁 SESSION END: {json.dumps(log_data, indent=2)}")
        except Exception as e:
            self.logger.error(f"❌ [CONSOLE] Error in log_session_end: {str(e)}")
            import traceback
            self.logger.error(f"❌ [CONSOLE] Traceback: {traceback.format_exc()}")
    
    def log_interaction(self, user_id: str, event_type: str, session_id: str = None, 
                       product_id: str = None, context: Dict[str, Any] = None):
        """Log interaction to console"""
        log_data = {
            "event": "INTERACTION",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "event_type": event_type,
            "session_id": session_id,
            "product_id": product_id,
            "context": context or {}
        }
        
        self.logger.info(f"📝 INTERACTION: {json.dumps(log_data, indent=2)}")
    
    def log_auth_event(self, user_id: str, event_type: str, session_id: str = None, 
                      success: bool = True, context: Dict[str, Any] = None):
        """Log authentication events to console"""
        try:
            # Ensure context is a dictionary
            if context is None:
                context = {}
            elif isinstance(context, str):
                self.logger.warning(f"⚠️ [CONSOLE] Context is a string, converting to dict: {context}")
                context = {}
            
            log_data = {
                "event": "AUTH_EVENT",
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "event_type": event_type,
                "session_id": session_id,
                "success": success,
                "context": context
            }
            
            emoji = "✅" if success else "❌"
            self.logger.info(f"{emoji} AUTH EVENT: {json.dumps(log_data, indent=2)}")
        except Exception as e:
            self.logger.error(f"❌ [CONSOLE] Error in log_auth_event: {str(e)}")
            import traceback
            self.logger.error(f"❌ [CONSOLE] Traceback: {traceback.format_exc()}")
    
    def log_user_action(self, user_id: str, action: str, details: Dict[str, Any] = None):
        """Log general user actions to console"""
        log_data = {
            "event": "USER_ACTION",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "details": details or {}
        }
        
        self.logger.info(f"👤 USER ACTION: {json.dumps(log_data, indent=2)}")
    
    def log_error(self, user_id: str, error_type: str, error_message: str, context: Dict[str, Any] = None):
        """Log errors to console"""
        log_data = {
            "event": "ERROR",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "error_type": error_type,
            "error_message": error_message,
            "context": context or {}
        }
        
        self.logger.error(f"🚨 ERROR: {json.dumps(log_data, indent=2)}")
    
    def log_system_event(self, event_type: str, details: Dict[str, Any] = None):
        """Log system events to console"""
        log_data = {
            "event": "SYSTEM_EVENT",
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "details": details or {}
        }
        
        self.logger.info(f"⚙️ SYSTEM EVENT: {json.dumps(log_data, indent=2)}")


# Global simple logger instance
simple_logger = SimpleSessionLogger()


def log_session_to_console(db: Session, user_id: str, session_id: str, action: str, 
                          context: Dict[str, Any] = None):
    """Log session data to console"""
    try:
        if action == "start":
            simple_logger.log_session_start(user_id, session_id, context)
        elif action == "end":
            # Get session duration
            session = db.query(SessionModel).filter(
                SessionModel.session_id == session_id
            ).first()
            
            duration = 0
            if session and session.started_at:
                end_time = datetime.utcnow()
                duration = (end_time - session.started_at).total_seconds()
            
            simple_logger.log_session_end(user_id, session_id, duration, context)
            
    except Exception as e:
        simple_logger.log_error(user_id, "SESSION_LOGGING_ERROR", str(e))


def log_interaction_to_console(user_id: str, event_type: str, session_id: str = None,
                              product_id: str = None, context: Dict[str, Any] = None):
    """Log interaction data to console"""
    try:
        simple_logger.log_interaction(user_id, event_type, session_id, product_id, context)
    except Exception as e:
        simple_logger.log_error(user_id, "INTERACTION_LOGGING_ERROR", str(e))


def log_auth_to_console(user_id: str, event_type: str, session_id: str = None,
                       success: bool = True, context: Dict[str, Any] = None):
    """Log authentication events to console"""
    try:
        simple_logger.log_auth_event(user_id, event_type, session_id, success, context)
    except Exception as e:
        simple_logger.log_error(user_id, "AUTH_LOGGING_ERROR", str(e))


# Example usage functions
def demo_session_logging():
    """Demo function showing how to use the console logger"""
    
    print("\n" + "="*60)
    print("DEMO: Simple Session and Interaction Console Logging")
    print("="*60)
    
    # Simulate user login
    user_id = "demo-user-123"
    session_id = "session-456"
    
    # Log session start
    simple_logger.log_session_start(
        user_id=user_id,
        session_id=session_id,
        context={
            "login_method": "password",
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0...",
            "platform": "web"
        }
    )
    
    # Log authentication success
    simple_logger.log_auth_event(
        user_id=user_id,
        event_type="login",
        session_id=session_id,
        success=True,
        context={"username": "demo_user"}
    )
    
    # Log some interactions
    simple_logger.log_interaction(
        user_id=user_id,
        event_type="page_view",
        session_id=session_id,
        context={"page": "/products", "category": "electronics"}
    )
    
    simple_logger.log_interaction(
        user_id=user_id,
        event_type="product_view",
        session_id=session_id,
        product_id="product-789",
        context={"product_name": "iPhone 15", "price": 999.99}
    )
    
    simple_logger.log_interaction(
        user_id=user_id,
        event_type="add_to_cart",
        session_id=session_id,
        product_id="product-789",
        context={"quantity": 1, "cart_total": 999.99}
    )
    
    # Log user action
    simple_logger.log_user_action(
        user_id=user_id,
        action="search",
        details={"query": "smartphone", "results_count": 25}
    )
    
    # Log session end
    simple_logger.log_session_end(
        user_id=user_id,
        session_id=session_id,
        duration_seconds=1800.5,  # 30 minutes
        context={
            "logout_method": "manual",
            "total_interactions": 5,
            "pages_viewed": 8
        }
    )
    
    # Log logout
    simple_logger.log_auth_event(
        user_id=user_id,
        event_type="logout",
        session_id=session_id,
        success=True,
        context={"session_duration": "30m 30s"}
    )
    
    print("\n" + "="*60)
    print("Demo completed! Check console output above.")
    print("="*60)


if __name__ == "__main__":
    demo_session_logging()
