"""
Collaborative filtering service using Implicit ALS
"""

import numpy as np
from typing import List, Tuple, Optional
from uuid import UUID
from app.ml.model_loader import model_loader


class CollaborativeService:
    """Collaborative filtering service using ALS"""
    
    def __init__(self):
        self.model_loader = model_loader
    
    def get_user_recommendations(self, user_id: UUID, k: int = 10) -> List[Tuple[UUID, float]]:
        """Get ALS-based collaborative filtering recommendations"""
        print(f"\n👥 COLLABORATIVE FILTERING RECOMMENDATIONS:")
        print(f"   - User ID: {user_id}")
        print(f"   - Requested k: {k}")
        
        try:
            user_factors, item_factors, mappings = self.model_loader.get_als_factors()
        except RuntimeError as e:
            print(f"   ⚠️ Error loading ALS factors: {e}")
            return []
        
        # Convert user_id to string for mapping lookup
        user_id_str = str(user_id)
        
        # Check if user exists in mappings
        if user_id_str not in mappings["user_id_to_idx"]:
            print(f"   ⚠️ Cold user - not found in mappings")
            return []  # Cold user
        
        user_idx = mappings["user_id_to_idx"][user_id_str]
        print(f"   ✅ User found at index: {user_idx}")
        
        # Get user factor
        user_factor = user_factors[user_idx]
        
        # Compute scores for all items
        scores = np.dot(item_factors, user_factor)
        print(f"   📊 Computed scores for {len(scores)} items")
        
        # Calculate min/max across ALL items for proper normalization
        all_scores_min = float(np.min(scores))
        all_scores_max = float(np.max(scores))
        print(f"   📈 Score range across all items: [{all_scores_min:.4f}, {all_scores_max:.4f}]")
        
        # Get top-k items
        top_indices = np.argsort(scores)[::-1][:k]
        print(f"   🎯 Selected top {len(top_indices)} items")
        
        # Convert to product IDs and normalized scores
        results = []
        idx_to_item_id = mappings["idx_to_item_id"]
        
        for idx in top_indices:
            idx_str = str(int(idx))  # Convert numpy int to string for JSON key lookup
            if idx_str not in idx_to_item_id:
                print(f"   ⚠️ Index {idx} ({idx_str}) not found in mappings")
                continue
            item_id_str = idx_to_item_id[idx_str]
            try:
                item_id = UUID(item_id_str)  # Convert string to UUID
                raw_score = float(scores[idx])
                
                # Normalize using ALL items' min/max (not just top-k)
                # This ensures scores are meaningful even for lower-ranked items
                if all_scores_max != all_scores_min:
                    normalized_score = (raw_score - all_scores_min) / (all_scores_max - all_scores_min)
                    # Scale to 0.5-1.0 range to show these are top items
                    normalized_score = 0.5 + (normalized_score * 0.5)
                else:
                    normalized_score = 0.9  # Default if all scores are same
                
                # Return both raw and normalized for API to use normalized
                results.append((item_id, normalized_score))
            except (ValueError, TypeError) as e:
                print(f"   ⚠️ Error converting item ID {item_id_str}: {e}")
                continue
        
        print(f"   ✅ Found {len(results)} recommendations")
        for i, (pid, score) in enumerate(results[:5], 1):
            print(f"     {i}. {pid} - {score:.4f} (normalized from all items)")
        if len(results) > 5:
            print(f"     ... and {len(results) - 5} more")
        
        return results
    
    def get_item_similar(self, product_id: UUID, k: int = 10) -> List[Tuple[UUID, float]]:
        """Get item-item collaborative filtering recommendations"""
        user_factors, item_factors, mappings = self.model_loader.get_als_factors()
        
        # Check if item exists in mappings
        if str(product_id) not in mappings["item_id_to_idx"]:
            return []
        
        item_idx = mappings["item_id_to_idx"][str(product_id)]
        
        # Get item factor
        item_factor = item_factors[item_idx]
        
        # Compute similarity with all other items
        similarities = np.dot(item_factors, item_factor)
        
        # Get top-k similar items (excluding self)
        top_indices = np.argsort(similarities)[::-1][1:k+1]  # Skip first (self)
        
        # Convert to product IDs and scores
        results = []
        idx_to_item_id = mappings["idx_to_item_id"]
        
        for idx in top_indices:
            item_id_str = idx_to_item_id[idx]
            item_id = UUID(item_id_str)  # Convert string to UUID
            score = float(similarities[idx])
            results.append((item_id, score))
        
        return results
    
    def get_collaborative_score(self, user_id: UUID, product_id: UUID) -> float:
        """Get collaborative filtering score for a user-item pair"""
        user_factors, item_factors, mappings = self.model_loader.get_als_factors()
        
        # Check if both user and item exist
        if str(user_id) not in mappings["user_id_to_idx"] or str(product_id) not in mappings["item_id_to_idx"]:
            return 0.0
        
        user_idx = mappings["user_id_to_idx"][str(user_id)]
        item_idx = mappings["item_id_to_idx"][str(product_id)]
        
        # Compute score
        user_factor = user_factors[user_idx]
        item_factor = item_factors[item_idx]
        score = np.dot(user_factor, item_factor)
        
        return float(score)
    
    def get_collaborative_score_with_normalization(self, user_id: UUID, product_id: UUID) -> Tuple[float, float]:
        """
        Get collaborative filtering score for a user-item pair with normalization
        Returns: (raw_score, normalized_score)
        Normalized score is relative to all items for this user (0-1 range, scaled to 0.5-1.0 for top items)
        """
        user_factors, item_factors, mappings = self.model_loader.get_als_factors()
        
        # Check if both user and item exist
        if str(user_id) not in mappings["user_id_to_idx"] or str(product_id) not in mappings["item_id_to_idx"]:
            return (0.0, 0.0)
        
        user_idx = mappings["user_id_to_idx"][str(user_id)]
        item_idx = mappings["item_id_to_idx"][str(product_id)]
        
        # Get user factor
        user_factor = user_factors[user_idx]
        
        # Compute scores for ALL items to get proper normalization range
        all_scores = np.dot(item_factors, user_factor)
        
        # Get score for this specific item
        item_score = float(np.dot(item_factors[item_idx], user_factor))
        
        # Normalize relative to all items
        all_scores_min = float(np.min(all_scores))
        all_scores_max = float(np.max(all_scores))
        
        if all_scores_max != all_scores_min:
            # Normalize to 0-1 range
            normalized = (item_score - all_scores_min) / (all_scores_max - all_scores_min)
            # Scale to 0.5-1.0 range to show it's a meaningful score (typical range for items user might like)
            normalized = 0.5 + (normalized * 0.5)
        else:
            normalized = 0.75  # Default if all scores are same
        
        return (item_score, normalized)
    
    def is_cold_user(self, user_id: UUID) -> bool:
        """Check if user is cold (no interactions)"""
        _, _, mappings = self.model_loader.get_als_factors()
        return str(user_id) not in mappings["user_id_to_idx"]
    
    def is_cold_item(self, product_id: UUID) -> bool:
        """Check if item is cold (no interactions)"""
        _, _, mappings = self.model_loader.get_als_factors()
        return str(product_id) not in mappings["item_id_to_idx"]
    
    def get_user_recommendations_filtered_by_category(
        self, 
        user_id: UUID, 
        category_product_ids: List[UUID],
        k: int = 10
    ) -> List[Tuple[UUID, float]]:
        """
        Get ALS-based collaborative filtering recommendations filtered to specific products
        Useful for category-based recommendations
        """
        print(f"\n👥 COLLABORATIVE FILTERING (Category-Filtered):")
        print(f"   - User ID: {user_id}")
        print(f"   - Category products: {len(category_product_ids)}")
        print(f"   - Requested k: {k}")
        
        try:
            user_factors, item_factors, mappings = self.model_loader.get_als_factors()
        except RuntimeError as e:
            print(f"   ⚠️ Error loading ALS factors: {e}")
            return []
        
        # Convert user_id to string for mapping lookup
        user_id_str = str(user_id)
        
        # Check if user exists in mappings
        if user_id_str not in mappings["user_id_to_idx"]:
            print(f"   ⚠️ Cold user - not found in mappings")
            return []  # Cold user
        
        user_idx = mappings["user_id_to_idx"][user_id_str]
        print(f"   ✅ User found at index: {user_idx}")
        
        # Get user factor
        user_factor = user_factors[user_idx]
        
        # Filter category product IDs to only those that exist in ALS model
        category_ids_set = {str(pid) for pid in category_product_ids}
        valid_category_indices = []
        idx_to_product_id = {}
        
        for idx_str, product_id_str in mappings["idx_to_item_id"].items():
            if product_id_str in category_ids_set:
                try:
                    valid_category_indices.append(int(idx_str))
                    idx_to_product_id[int(idx_str)] = UUID(product_id_str)
                except (ValueError, TypeError):
                    continue
        
        if not valid_category_indices:
            print(f"   ⚠️ No category products found in ALS model")
            return []
        
        print(f"   ✅ Found {len(valid_category_indices)} category products in ALS model")
        
        # Compute scores only for category products
        category_scores = []
        for idx in valid_category_indices:
            item_factor = item_factors[idx]
            score = float(np.dot(user_factor, item_factor))
            category_scores.append((idx, score))
        
        # Calculate min/max across category products for normalization
        scores_only = [s for _, s in category_scores]
        if not scores_only:
            return []
        
        all_scores_min = float(min(scores_only))
        all_scores_max = float(max(scores_only))
        print(f"   📈 Score range for category products: [{all_scores_min:.4f}, {all_scores_max:.4f}]")
        
        # Sort by score and get top-k
        category_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Normalize and return
        results = []
        for idx, raw_score in category_scores[:k]:
            product_id = idx_to_product_id[idx]
            
            # Normalize using category products' min/max
            if all_scores_max != all_scores_min:
                normalized_score = (raw_score - all_scores_min) / (all_scores_max - all_scores_min)
                # Scale to 0.5-1.0 range
                normalized_score = 0.5 + (normalized_score * 0.5)
            else:
                normalized_score = 0.9
            
            results.append((product_id, normalized_score))
        
        print(f"   ✅ Found {len(results)} category-filtered recommendations")
        for i, (pid, score) in enumerate(results[:5], 1):
            print(f"     {i}. {pid} - {score:.4f}")
        if len(results) > 5:
            print(f"     ... and {len(results) - 5} more")
        
        return results

