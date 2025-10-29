"""
Chatbot API endpoints using Google Gemini with recommendation integration
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import google.generativeai as genai
import os
import logging
import re
from uuid import UUID

from app.database import get_db
from app.models import Product
from app.config import settings
from app.services import HybridRecommender

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])

# Configure Gemini
GEMINI_API_KEY = settings.gemini_api_key
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info("✅ Gemini API configured successfully")
else:
    logger.warning("GEMINI_API_KEY not found in environment variables")

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    user_id: Optional[str] = None

class ProductSuggestion(BaseModel):
    product_id: str
    name: str
    price: float
    discount_percent: Optional[float] = None
    image_url: Optional[str] = None
    reason: str

class ChatResponse(BaseModel):
    message: str
    suggestions: Optional[List[str]] = None
    products: Optional[List[ProductSuggestion]] = None

def extract_product_intent(user_message: str) -> Dict[str, Any]:
    """Extract product search intent from user message"""
    intent = {
        "has_product_query": False,
        "product_type": None,
        "price_range": None,
        "features": [],
        "search_query": None
    }
    
    # Common product types
    product_types = {
        "laptop": ["laptop", "notebook", "computer", "macbook", "pc"],
        "phone": ["phone", "smartphone", "iphone", "android", "mobile"],
        "headphones": ["headphones", "earphones", "earbuds", "airpods", "headset"],
        "camera": ["camera", "dslr", "mirrorless", "photography"],
        "watch": ["watch", "smartwatch", "apple watch", "fitness tracker"],
        "shoes": ["shoes", "sneakers", "boots", "sandals", "footwear"],
        "clothes": ["clothes", "clothing", "shirt", "dress", "jacket", "pants"]
    }
    
    message_lower = user_message.lower()
    
    # Check for product types
    for product_type, keywords in product_types.items():
        if any(keyword in message_lower for keyword in keywords):
            intent["has_product_query"] = True
            intent["product_type"] = product_type
            break
    
    # Extract price range
    price_patterns = [
        r"under \$?(\d+)",
        r"less than \$?(\d+)",
        r"below \$?(\d+)",
        r"around \$?(\d+)",
        r"about \$?(\d+)",
        r"\$?(\d+)\s*-\s*\$?(\d+)",
        r"between \$?(\d+)\s+and \$?(\d+)"
    ]
    
    for pattern in price_patterns:
        match = re.search(pattern, message_lower)
        if match:
            if len(match.groups()) == 1:
                intent["price_range"] = {"max": int(match.group(1))}
            else:
                intent["price_range"] = {"min": int(match.group(1)), "max": int(match.group(2))}
            break
    
    # Extract features
    feature_keywords = ["wireless", "bluetooth", "waterproof", "gaming", "professional", "portable", "lightweight"]
    for feature in feature_keywords:
        if feature in message_lower:
            intent["features"].append(feature)
    
    # Set search query
    if intent["has_product_query"]:
        intent["search_query"] = user_message
    
    return intent

def get_recommendations_for_intent(intent: Dict[str, Any], user_id: Optional[str], db: Session) -> List[ProductSuggestion]:
    """Get product recommendations based on user intent"""
    try:
        recommender = HybridRecommender()
        suggestions = []
        
        if not intent["has_product_query"]:
            return suggestions
        
        # Get recommendations based on intent
        user_uuid = None
        if user_id:
            try:
                user_uuid = UUID(user_id)
            except (ValueError, TypeError):
                user_uuid = None
        
        if intent["search_query"]:
            # Use hybrid search with query
            results = recommender.hybrid_recommend(
                user_id=user_uuid,
                query=intent["search_query"],
                alpha=0.6,
                k=5
            )
        else:
            # Use personalized recommendations
            results = recommender.hybrid_recommend(
                user_id=user_uuid,
                alpha=0.7,
                k=5
            )
        
        # Get product details
        product_ids = [result[0] for result in results]
        products = db.query(Product).filter(Product.product_id.in_(product_ids)).all()
        
        # Create mapping
        product_map = {p.product_id: p for p in products}
        
        for product_id, score, reason_features in results:
            if product_id in product_map:
                product = product_map[product_id]
                
                # Get primary image
                primary_image = None
                for img in product.images:
                    if img.is_primary:
                        primary_image = img.cdn_url
                        break
                
                # Create reason
                reason = f"Recommended based on your preferences (score: {score:.2f})"
                if reason_features and "source" in reason_features:
                    if reason_features["source"] == "content":
                        reason = "Similar to products you might like"
                    elif reason_features["source"] == "collaborative":
                        reason = "Popular among users with similar tastes"
                
                suggestion = ProductSuggestion(
                    product_id=str(product.product_id),
                    name=product.name,
                    price=float(product.price),
                    discount_percent=float(product.discount_percent) if product.discount_percent else None,
                    image_url=primary_image,
                    reason=reason
                )
                suggestions.append(suggestion)
        
        return suggestions
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        return []

@router.post("/chat", response_model=ChatResponse)
async def chat_with_gemini(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    try:
        user_message = None
        for msg in reversed(request.messages):
            if msg.role == "user":
                user_message = msg.content
                break
        
        if not user_message:
            raise HTTPException(status_code=400, detail="No user message found")

        # Extract product intent
        intent = extract_product_intent(user_message)
        
        # Get product recommendations if relevant
        product_suggestions = []
        if intent["has_product_query"]:
            product_suggestions = get_recommendations_for_intent(intent, request.user_id, db)

        # Build context for Gemini
        context = ""
        if request.user_id:
            recent_products = db.query(Product).limit(5).all()
            if recent_products:
                product_names = [p.name for p in recent_products]
                context = f"User has shown interest in: {', '.join(product_names)}. "

        # Add product suggestions to context
        if product_suggestions:
            context += f"Here are some product recommendations: "
            for suggestion in product_suggestions[:3]:  # Limit to top 3
                context += f"- {suggestion.name} (${suggestion.price}) - {suggestion.reason}. "
        
        system_prompt = f"""You are Zyra, an AI shopping assistant for an e-commerce platform. 
        Context: {context}
        
        Your role:
        - Help users find products they're looking for
        - Provide product recommendations based on their needs
        - Answer questions about products, categories, and shopping
        - Be friendly, helpful, and concise
        - If you don't know specific product details, suggest browsing categories or using search
        - When recommending products, mention specific features and benefits
        
        Current conversation:
        """
        
        conversation_text = system_prompt
        for msg in request.messages[-10:]:
            conversation_text += f"\n{msg.role}: {msg.content}"

        model = genai.GenerativeModel('gemini-pro-latest')
        response = model.generate_content(conversation_text)
        
        # Generate suggestions based on response
        suggestions = []
        response_text = response.text
        
        # Add product-specific suggestions
        if product_suggestions:
            suggestions.extend([f"View {suggestion.name}" for suggestion in product_suggestions[:2]])
        
        # Add general suggestions
        general_suggestions = [
            "Browse Electronics", "Browse Fashion", "Browse Home & Garden", 
            "View Cart", "Check Wishlist", "Search Products"
        ]
        suggestions.extend(general_suggestions[:2])
        
        return ChatResponse(
            message=response_text,
            suggestions=suggestions[:3] if suggestions else None,
            products=product_suggestions[:3] if product_suggestions else None
        )
        
    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat service error: {str(e)}")

@router.get("/health")
async def chatbot_health():
    if not GEMINI_API_KEY:
        return {"status": "unhealthy", "gemini_accessible": False, "error": "API key not configured"}
    try:
        model = genai.GenerativeModel('gemini-pro-latest')
        test_response = model.generate_content("Hello")
        return {"status": "healthy", "gemini_accessible": True}
    except Exception as e:
        return {"status": "unhealthy", "gemini_accessible": False, "error": str(e)}