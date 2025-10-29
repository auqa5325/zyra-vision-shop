"""
Hybrid recommendation service combining content-based and collaborative filtering
"""

import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from app.services.content_based import ContentBasedService
from app.services.collaborative import CollaborativeService
from app.config import settings


class HybridRecommender:
    """Hybrid recommendation service"""
    
    def __init__(self):
        self.content_service = ContentBasedService()
        self.collaborative_service = CollaborativeService()
        # Ensure models are loaded
        from app.ml.model_loader import model_loader
        model_loader.load_models()
    
    def hybrid_recommend(
        self, 
        user_id: Optional[UUID] = None, 
        query: Optional[str] = None, 
        alpha: float = None, 
        k: int = None,
        db: Optional[Session] = None
    ) -> List[Tuple[UUID, float, Dict[str, Any]]]:
        """Main hybrid recommendation logic"""
        
        if alpha is None:
            alpha = settings.default_alpha
        if k is None:
            k = settings.default_top_k
            
        print(f"\n🔄 HYBRID RECOMMENDER PROCESSING:")
        print(f"   - User ID: {user_id}")
        print(f"   - Query: {query}")
        print(f"   - Alpha (CF weight): {alpha}")
        print(f"   - K (number of recommendations): {k}")
        
        # Get content-based scores
        if query:
            print(f"\n📝 CONTENT-BASED FILTERING (Query-based):")
            print(f"   - Using explicit query: '{query}'")
            content_results = self.content_service.search_products(query, k=k*2)
        else:
            # If no query, use personalized content-based recommendations
            if user_id and db:
                print(f"\n👤 CONTENT-BASED FILTERING (Personalized):")
                print(f"   - Using personalized recommendations for user: {user_id}")
                try:
                    content_results = self.content_service.get_personalized_content_recommendations(
                        user_id, db, k=k*2
                    )
                    # Only fallback if we get no results
                    if not content_results:
                        print(f"   ⚠️ No personalized results, falling back to trending products")
                        content_results = self._get_trending_products(k=k*2)
                except Exception as e:
                    # Fallback to trending products if personalized fails
                    print(f"   ⚠️ Personalized content-based failed: {e}")
                    print(f"   🔄 Falling back to trending products")
                    content_results = self._get_trending_products(k=k*2)
            else:
                # No user context - use trending/popular products
                print(f"\n📈 CONTENT-BASED FILTERING (General):")
                print(f"   - No user context, using trending products")
                content_results = self._get_trending_products(k=k*2)
        
        print(f"   - Content-based results: {len(content_results)} products")
        for i, (pid, score) in enumerate(content_results[:5], 1):
            print(f"     {i}. {pid} - {score:.4f}")
        if len(content_results) > 5:
            print(f"     ... and {len(content_results) - 5} more")
        
        # Get collaborative scores
        cf_results = []
        if user_id and not self.collaborative_service.is_cold_user(user_id):
            print(f"\n🤝 COLLABORATIVE FILTERING (User-based):")
            print(f"   - Getting recommendations for user: {user_id}")
            cf_results = self.collaborative_service.get_user_recommendations(user_id, k=k*2)
        elif not user_id:
            # No user context - use popular products for collaborative component
            print(f"\n🤝 COLLABORATIVE FILTERING (Popular):")
            print(f"   - No user ID, using popular products")
            cf_results = self._get_popular_products(k=k*2)
        else:
            print(f"\n🤝 COLLABORATIVE FILTERING (Cold User):")
            print(f"   - User {user_id} is cold, skipping collaborative filtering")
        
        print(f"   - Collaborative results: {len(cf_results)} products")
        for i, (pid, score) in enumerate(cf_results[:5], 1):
            print(f"     {i}. {pid} - {score:.4f}")
        if len(cf_results) > 5:
            print(f"     ... and {len(cf_results) - 5} more")
        
        # Normalize scores
        content_scores = self._normalize_scores(content_results)
        cf_scores = self._normalize_scores(cf_results)
        
        print(f"\n⚖️ HYBRID SCORING:")
        print(f"   - Content weight: {1-alpha:.2f}")
        print(f"   - Collaborative weight: {alpha:.2f}")
        print(f"   - Normalized content scores: {len(content_scores)} products")
        print(f"   - Normalized CF scores: {len(cf_scores)} products")
        
        # Combine scores
        hybrid_scores = {}
        
        # Add content scores
        for product_id, score in content_scores.items():
            hybrid_scores[product_id] = {
                "content_score": score,
                "cf_score": 0.0,
                "hybrid_score": (1 - alpha) * score,
                "source": "content_only"
            }
        
        # Add collaborative scores
        for product_id, score in cf_scores.items():
            if product_id in hybrid_scores:
                hybrid_scores[product_id]["cf_score"] = score
                hybrid_scores[product_id]["hybrid_score"] += alpha * score
                hybrid_scores[product_id]["source"] = "hybrid"
            else:
                hybrid_scores[product_id] = {
                    "content_score": 0.0,
                    "cf_score": score,
                    "hybrid_score": alpha * score,
                    "source": "collaborative_only"
                }
        
        print(f"   - Combined hybrid scores: {len(hybrid_scores)} products")
        
        # Sort by hybrid score and return top-k
        sorted_results = sorted(
            hybrid_scores.items(), 
            key=lambda x: x[1]["hybrid_score"], 
            reverse=True
        )
        
        print(f"\n🎁 FINAL HYBRID RESULTS:")
        results = []
        for i, (product_id, scores) in enumerate(sorted_results[:k], 1):
            print(f"   {i}. {product_id}")
            print(f"      Content: {scores['content_score']:.4f}, CF: {scores['cf_score']:.4f}")
            print(f"      Hybrid: {scores['hybrid_score']:.4f} ({scores['source']})")
            
            results.append((
                product_id,
                scores["hybrid_score"],
                {
                    "content_score": scores["content_score"],
                    "cf_score": scores["cf_score"],
                    "source": scores["source"]
                }
            ))
        
        print(f"\n✅ HYBRID RECOMMENDATION COMPLETE")
        print(f"   - Returning {len(results)} recommendations")
        
        return results
    
    def _normalize_scores(self, results: List[Tuple[UUID, float]]) -> Dict[UUID, float]:
        """Normalize scores to [0, 1] range"""
        if not results:
            return {}
        
        scores = [score for _, score in results]
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score == min_score:
            # All scores are the same
            return {product_id: 1.0 for product_id, _ in results}
        
        # Normalize to [0, 1]
        normalized = {}
        for product_id, score in results:
            normalized[product_id] = (score - min_score) / (max_score - min_score)
        
        return normalized
    
    def explain_recommendation(self, product_id: UUID, user_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Generate explanation for a recommendation"""
        explanation = {
            "matched_tags": [],
            "cf_score": 0.0,
            "content_score": 0.0,
            "source": "unknown"
        }
        
        # Get content score
        content_score = self.content_service.get_content_score(product_id)
        explanation["content_score"] = content_score
        
        # Get collaborative score if user provided
        if user_id and not self.collaborative_service.is_cold_user(user_id):
            cf_score = self.collaborative_service.get_collaborative_score(user_id, product_id)
            explanation["cf_score"] = cf_score
        
        # Determine source
        if explanation["cf_score"] > 0 and explanation["content_score"] > 0:
            explanation["source"] = "hybrid"
        elif explanation["cf_score"] > 0:
            explanation["source"] = "collaborative"
        elif explanation["content_score"] > 0:
            explanation["source"] = "content"
        
        return explanation
    
    def get_recommendation_for_product(
        self, 
        product_id: UUID, 
        user_id: Optional[UUID] = None, 
        k: int = 10
    ) -> List[Tuple[UUID, float, Dict[str, Any]]]:
        """Get recommendations similar to a specific product"""
        
        # Get content-based similar products
        content_results = self.content_service.find_similar_products(product_id, k=k*2)
        
        # Get collaborative similar products if user provided
        cf_results = []
        if user_id and not self.collaborative_service.is_cold_user(user_id):
            cf_results = self.collaborative_service.get_item_similar(product_id, k=k*2)
        
        # Normalize and combine scores
        content_scores = self._normalize_scores(content_results)
        cf_scores = self._normalize_scores(cf_results)
        
        # Combine scores
        hybrid_scores = {}
        
        # Add content scores
        for pid, score in content_scores.items():
            hybrid_scores[pid] = {
                "content_score": score,
                "cf_score": 0.0,
                "hybrid_score": 0.5 * score  # Equal weight for product similarity
            }
        
        # Add collaborative scores
        for pid, score in cf_scores.items():
            if pid in hybrid_scores:
                hybrid_scores[pid]["cf_score"] = score
                hybrid_scores[pid]["hybrid_score"] += 0.5 * score
            else:
                hybrid_scores[pid] = {
                    "content_score": 0.0,
                    "cf_score": score,
                    "hybrid_score": 0.5 * score
                }
        
        # Sort and return top-k
        sorted_results = sorted(
            hybrid_scores.items(), 
            key=lambda x: x[1]["hybrid_score"], 
            reverse=True
        )
        
        results = []
        for pid, scores in sorted_results[:k]:
            results.append((
                pid,
                scores["hybrid_score"],
                {
                    "content_score": scores["content_score"],
                    "cf_score": scores["cf_score"],
                    "source": "hybrid"
                }
            ))
        
        return results

    def _get_trending_products(self, k: int = 10) -> List[Tuple[UUID, float]]:
        """Get trending products using content-based diversity"""
        # Use content service to get diverse products
        # For trending, we'll use a generic query that should return diverse results
        try:
            # Use a broad query to get diverse products
            results = self.content_service.search_products("popular trending products", k=k)
            return results
        except Exception:
            # Fallback to random selection if content service fails
            import random
            from app.ml.model_loader import model_loader
            product_ids = model_loader.get_product_ids()
            total_products = len(product_ids)
            
            results = []
            sample_indices = random.sample(range(total_products), min(k, total_products))
            
            for idx in sample_indices:
                product_id = product_ids[idx]
                score = 0.8 + random.uniform(0, 0.2)  # Score between 0.8-1.0
                results.append((product_id, score))
            
            return results
    
    def _get_popular_products(self, k: int = 10) -> List[Tuple[UUID, float]]:
        """Get popular products using collaborative filtering insights"""
        try:
            # Use collaborative service to get popular products
            # We'll simulate this by getting recommendations for a "popular" user
            from app.ml.model_loader import model_loader
            user_factors, item_factors, mappings = model_loader.get_als_factors()
            
            # Calculate average item popularity (sum of all user factors for each item)
            item_popularity = np.sum(item_factors, axis=1)
            
            # Get top-k popular items
            top_indices = np.argsort(item_popularity)[::-1][:k]
            
            results = []
            idx_to_item_id = mappings["idx_to_item_id"]
            
            for idx in top_indices:
                item_id = idx_to_item_id[idx]
                score = float(item_popularity[idx])
                results.append((item_id, score))
            
            return results
        except Exception:
            # Fallback to random selection if collaborative service fails
            import random
            from app.ml.model_loader import model_loader
            product_ids = model_loader.get_product_ids()
            total_products = len(product_ids)
            
            results = []
            sample_indices = random.sample(range(total_products), min(k, total_products))
            
            for idx in sample_indices:
                product_id = product_ids[idx]
                score = 0.7 + random.uniform(0, 0.3)  # Score between 0.7-1.0
                results.append((product_id, score))
            
            return results

