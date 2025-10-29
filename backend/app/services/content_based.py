"""
Content-based recommendation service using Sentence Transformers
"""

import numpy as np
import faiss
from typing import List, Tuple, Optional, Dict
from uuid import UUID
from collections import Counter
from sqlalchemy.orm import Session
from app.ml.model_loader import model_loader
from app.models.interaction import Interaction
from app.models.product import Product
from app.models.user_states import PurchaseHistory, UserWishlist, UserCart


class ContentBasedService:
    """Content-based recommendation service"""
    
    def __init__(self):
        self.model_loader = model_loader
    
    def embed_query(self, text: str) -> np.ndarray:
        """Generate embedding for search query"""
        # Try to get model, load if not available
        try:
            model = self.model_loader.get_sentence_transformer()
        except RuntimeError:
            # Lazy load models if not loaded yet
            self.model_loader.load_models()
            model = self.model_loader.get_sentence_transformer()
        embedding = model.encode([text])
        return embedding[0]
    
    def find_similar_products(self, product_id: UUID, k: int = 10) -> List[Tuple[UUID, float]]:
        """Find similar products based on content"""
        # Get product embedding from FAISS index (with lazy loading if needed)
        try:
            faiss_index = self.model_loader.get_faiss_index()
            product_ids = self.model_loader.get_product_ids()
        except RuntimeError:
            # Lazy load models if not loaded yet
            self.model_loader.load_models()
            faiss_index = self.model_loader.get_faiss_index()
            product_ids = self.model_loader.get_product_ids()
        
        # Find product index
        product_idx = np.where(product_ids == product_id)[0]
        if len(product_idx) == 0:
            return []
        
        product_idx = int(product_idx[0])  # Convert numpy int64 to Python int
        
        # Get product embedding
        product_embedding = faiss_index.reconstruct(product_idx).reshape(1, -1)
        
        # Search for similar products
        scores, indices = faiss_index.search(product_embedding, k + 1)  # +1 to exclude self
        
        # Filter out the query product itself
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != product_idx:  # Exclude self
                results.append((product_ids[idx], float(score)))
        
        return results[:k]
    
    def search_products(self, query: str, k: int = 10) -> List[Tuple[UUID, float]]:
        """Search products using semantic similarity"""
        # Generate query embedding
        query_embedding = self.embed_query(query)
        query_embedding = query_embedding.reshape(1, -1)
        
        # Normalize for cosine similarity
        faiss.normalize_L2(query_embedding)
        
        # Search FAISS index (with lazy loading if needed)
        try:
            faiss_index = self.model_loader.get_faiss_index()
            product_ids = self.model_loader.get_product_ids()
        except RuntimeError:
            # Lazy load models if not loaded yet
            self.model_loader.load_models()
            faiss_index = self.model_loader.get_faiss_index()
            product_ids = self.model_loader.get_product_ids()
        
        scores, indices = faiss_index.search(query_embedding, k)
        
        # Return results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            results.append((product_ids[idx], float(score)))
        
        return results
    
    def get_content_score(self, product_id: UUID, query: Optional[str] = None) -> float:
        """Get content-based score for a product"""
        if query:
            # Use query-based search
            results = self.search_products(query, k=100)
            for pid, score in results:
                if pid == product_id:
                    return score
            return 0.0
        else:
            # Use product similarity (average of top similar products)
            similar = self.find_similar_products(product_id, k=5)
            if similar:
                return sum(score for _, score in similar) / len(similar)
            return 0.0

    def get_user_content_profile(self, user_id: UUID, db: Session) -> Dict[str, float]:
        """Analyze user's past actions to build a content profile"""
        
        # Get user's interactions
        interactions = db.query(Interaction).filter(
            Interaction.user_id == user_id,
            Interaction.event_type.in_(['view', 'add_to_cart', 'wishlist', 'purchase'])
        ).all()
        
        if not interactions:
            return {}
        
        # Weight different actions differently
        action_weights = {
            'purchase': 3.0,      # Highest weight - actual purchase
            'add_to_cart': 2.0,   # High weight - strong intent
            'wishlist': 1.5,      # Medium weight - interest
            'view': 1.0           # Base weight - browsing
        }
        
        # Collect product features from user's actions
        product_features = {}
        
        for interaction in interactions:
            product_id = interaction.product_id
            weight = action_weights.get(interaction.event_type, 1.0)
            
            # Get product details
            product = db.query(Product).filter(Product.product_id == product_id).first()
            if not product:
                continue
            
            # Extract features
            features = self._extract_product_features(product)
            
            # Weight features by action importance
            for feature, value in features.items():
                if feature not in product_features:
                    product_features[feature] = 0.0
                product_features[feature] += value * weight
        
        # Normalize feature weights
        total_weight = sum(product_features.values())
        if total_weight > 0:
            for feature in product_features:
                product_features[feature] /= total_weight
        
        return product_features
    
    def _extract_product_features(self, product: Product) -> Dict[str, float]:
        """Extract features from a product"""
        features = {}
        
        # Category features
        if product.category_id:
            features[f'category_{product.category_id}'] = 1.0
        
        # Brand features
        if product.brand:
            features[f'brand_{product.brand.lower()}'] = 1.0
        
        # Price range features
        if product.price:
            price_ranges = [
                (0, 500, 'budget'),
                (500, 2000, 'mid_range'),
                (2000, 10000, 'premium'),
                (10000, float('inf'), 'luxury')
            ]
            
            for min_price, max_price, range_name in price_ranges:
                if min_price <= product.price <= max_price:
                    features[f'price_range_{range_name}'] = 1.0
                    break
        
        # Tag features
        if product.tags:
            for tag in product.tags:
                features[f'tag_{tag.lower()}'] = 1.0
        
        return features
    
    def generate_user_query(self, user_profile: Dict[str, float]) -> str:
        """Generate a semantic query based on user's content profile"""
        
        if not user_profile:
            return "popular trending products"
        
        # Sort features by importance
        sorted_features = sorted(user_profile.items(), key=lambda x: x[1], reverse=True)
        
        # Build query from top features
        query_parts = []
        
        for feature, weight in sorted_features[:5]:  # Top 5 features
            if weight > 0.1:  # Only include significant features
                if feature.startswith('category_'):
                    query_parts.append("products in this category")
                elif feature.startswith('brand_'):
                    brand = feature.replace('brand_', '')
                    query_parts.append(f"{brand} brand products")
                elif feature.startswith('price_range_'):
                    price_range = feature.replace('price_range_', '')
                    query_parts.append(f"{price_range} price range products")
                elif feature.startswith('tag_'):
                    tag = feature.replace('tag_', '')
                    query_parts.append(f"{tag} products")
        
        if query_parts:
            # Combine query parts
            query = " ".join(query_parts[:3])  # Use top 3 features
            return f"recommended {query}"
        else:
            return "popular trending products"
    
    def get_personalized_content_recommendations(
        self, 
        user_id: UUID, 
        db: Session, 
        k: int = 10
    ) -> List[Tuple[UUID, float]]:
        """Get content-based recommendations based on user's behavior"""
        
        print(f"\n👤 PERSONALIZED CONTENT-BASED FILTERING:")
        print(f"   - User ID: {user_id}")
        print(f"   - Requested k: {k}")
        
        # Build user's content profile
        user_profile = self.get_user_content_profile(user_id, db)
        print(f"   - User profile features: {len(user_profile)}")
        for feature, weight in sorted(user_profile.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"     {feature}: {weight:.4f}")
        
        # Generate personalized query
        query = self.generate_user_query(user_profile)
        print(f"   - Generated query: '{query}'")
        
        # Use content-based search with personalized query
        results = self.search_products(query, k=k)
        print(f"   - Personalized results: {len(results)} products")
        for i, (pid, score) in enumerate(results[:5], 1):
            print(f"     {i}. {pid} - {score:.4f}")
        if len(results) > 5:
            print(f"     ... and {len(results) - 5} more")
        
        return results
    
    def get_user_content_recommendations_from_all_sources(
        self,
        user_id: UUID,
        db: Session,
        k: int = 10
    ) -> List[Tuple[UUID, float]]:
        """
        Get content-based recommendations by aggregating user data from:
        - Purchase history (most recent purchases)
        - Wishlist
        - Cart
        Then find similar products using embeddings
        """
        print(f"\n🔍 CONTENT-BASED RECOMMENDATIONS FROM ALL SOURCES:")
        print(f"   - User ID: {user_id}")
        print(f"   - Requested k: {k}")
        
        # Get products from purchase history (latest purchases)
        recent_purchases = db.query(PurchaseHistory.product_id).filter(
            PurchaseHistory.user_id == user_id,
            PurchaseHistory.payment_status == 'completed'
        ).order_by(PurchaseHistory.purchased_at.desc()).limit(20).all()
        
        purchase_product_ids = [p.product_id for p in recent_purchases]
        print(f"   - Found {len(purchase_product_ids)} recent purchases")
        
        # Get products from wishlist
        wishlist_items = db.query(UserWishlist.product_id).filter(
            UserWishlist.user_id == user_id
        ).order_by(UserWishlist.added_at.desc()).limit(20).all()
        
        wishlist_product_ids = [w.product_id for w in wishlist_items]
        print(f"   - Found {len(wishlist_product_ids)} wishlist items")
        
        # Get products from cart
        cart_items = db.query(UserCart.product_id).filter(
            UserCart.user_id == user_id
        ).order_by(UserCart.added_at.desc()).limit(20).all()
        
        cart_product_ids = [c.product_id for c in cart_items]
        print(f"   - Found {len(cart_product_ids)} cart items")
        
        # Combine all product IDs (with weights)
        # Purchase history has highest weight, then wishlist, then cart
        all_product_ids = []
        
        # Add purchase products with weight 3.0
        for pid in purchase_product_ids:
            all_product_ids.append((pid, 3.0))
        
        # Add wishlist products with weight 2.0 (if not already in purchases)
        for pid in wishlist_product_ids:
            if pid not in purchase_product_ids:
                all_product_ids.append((pid, 2.0))
        
        # Add cart products with weight 1.5 (if not already in purchases or wishlist)
        for pid in cart_product_ids:
            if pid not in purchase_product_ids and pid not in wishlist_product_ids:
                all_product_ids.append((pid, 1.5))
        
        if not all_product_ids:
            print(f"   ⚠️ No products found in purchase history, wishlist, or cart")
            return []
        
        print(f"   - Total unique products: {len(all_product_ids)}")
        
        # Get embeddings for all products and find similar products
        try:
            faiss_index = self.model_loader.get_faiss_index()
            product_ids = self.model_loader.get_product_ids()
        except RuntimeError:
            self.model_loader.load_models()
            faiss_index = self.model_loader.get_faiss_index()
            product_ids = self.model_loader.get_product_ids()
        
        # Aggregate embeddings weighted by importance
        aggregated_embedding = None
        total_weight = 0.0
        
        for pid, weight in all_product_ids:
            product_idx = np.where(product_ids == pid)[0]
            if len(product_idx) == 0:
                continue
            
            product_idx = int(product_idx[0])
            product_embedding = faiss_index.reconstruct(product_idx)
            
            if aggregated_embedding is None:
                aggregated_embedding = product_embedding * weight
            else:
                aggregated_embedding += product_embedding * weight
            
            total_weight += weight
        
        if aggregated_embedding is None:
            print(f"   ⚠️ Could not aggregate embeddings")
            return []
        
        # Normalize the aggregated embedding
        aggregated_embedding = aggregated_embedding / total_weight
        aggregated_embedding = aggregated_embedding.reshape(1, -1)
        faiss.normalize_L2(aggregated_embedding)
        
        # Exclude products user already has
        exclude_ids = set(purchase_product_ids + wishlist_product_ids + cart_product_ids)
        
        # Search for similar products (get more than k to account for exclusions)
        search_k = min(k * 3, len(product_ids))
        scores, indices = faiss_index.search(aggregated_embedding, search_k)
        
        # Filter and return top k
        results = []
        seen = set()
        
        for score, idx in zip(scores[0], indices[0]):
            pid = product_ids[idx]
            
            # Skip products user already has
            if pid in exclude_ids:
                continue
            
            # Skip duplicates
            if pid in seen:
                continue
            
            seen.add(pid)
            results.append((pid, float(score)))
            
            if len(results) >= k:
                break
        
        print(f"   - Found {len(results)} similar products")
        for i, (pid, score) in enumerate(results[:5], 1):
            print(f"     {i}. {pid} - {score:.4f}")
        if len(results) > 5:
            print(f"     ... and {len(results) - 5} more")
        
        return results

