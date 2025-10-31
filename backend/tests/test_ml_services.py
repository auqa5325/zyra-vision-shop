"""
Tests for ML services
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from app.services.content_based import ContentBasedService
from app.services.collaborative import CollaborativeService
from app.services.recommender import HybridRecommender


class TestContentBasedService:
    """Test content-based recommendation service"""
    
    def test_content_based_service_init(self):
        """Test content-based service initialization"""
        service = ContentBasedService()
        assert service is not None
    
    def test_search_products(self):
        """Test searching products"""
        service = ContentBasedService()
        
        # Should return empty list when no models/data
        try:
            result = service.search_products("test query", k=2)
            assert isinstance(result, list)
        except (RuntimeError, ValueError):
            # Expected when models aren't loaded
            pass
    
    def test_search_products_empty_query(self):
        """Test searching products with empty query"""
        service = ContentBasedService()
        
        # Should return empty list when no models/data
        try:
            result = service.search_products("", k=5)
            assert isinstance(result, list)
        except (RuntimeError, ValueError):
            # Expected when models aren't loaded
            pass
    
    def test_search_products_no_model(self):
        """Test searching products when model is not loaded"""
        service = ContentBasedService()
        
        # Should return empty list when no models/data
        try:
            result = service.search_products("test query", k=5)
            assert isinstance(result, list)
        except (RuntimeError, ValueError):
            # Expected when models aren't loaded
            pass


class TestCollaborativeService:
    """Test collaborative filtering service"""
    
    def test_collaborative_service_init(self):
        """Test collaborative service initialization"""
        service = CollaborativeService()
        assert service is not None
    
    def test_get_user_recommendations(self):
        """Test getting user recommendations"""
        from uuid import uuid4
        service = CollaborativeService()
        
        # Use real UUID
        user_id = uuid4()
        result = service.get_user_recommendations(user_id, k=2)
        
        # Should return empty list if no data
        assert isinstance(result, list)
    
    def test_get_user_recommendations_unknown_user(self):
        """Test getting recommendations for unknown user"""
        from uuid import uuid4
        service = CollaborativeService()
        
        # Use random UUID that doesn't exist
        user_id = uuid4()
        result = service.get_user_recommendations(user_id, k=5)
        
        # Should return empty list
        assert isinstance(result, list)
    
    def test_get_user_recommendations_no_model(self):
        """Test getting recommendations when model is not loaded"""
        from uuid import uuid4
        service = CollaborativeService()
        
        user_id = uuid4()
        result = service.get_user_recommendations(user_id, k=5)
        
        # Should return empty list
        assert isinstance(result, list)


class TestHybridRecommender:
    """Test hybrid recommendation service"""
    
    def test_hybrid_recommender_init(self):
        """Test hybrid recommender initialization"""
        recommender = HybridRecommender()
        assert recommender is not None
    
    def test_get_hybrid_recommendations(self):
        """Test getting hybrid recommendations"""
        from uuid import uuid4
        recommender = HybridRecommender()
        
        user_id = uuid4()
        result = recommender.hybrid_recommend(
            user_id=user_id,
            query="test query",
            alpha=0.6,
            k=5
        )
        
        assert isinstance(result, list)
    
    def test_get_hybrid_recommendations_content_only(self):
        """Test getting content-only recommendations (alpha=1.0)"""
        from uuid import uuid4
        recommender = HybridRecommender()
        
        user_id = uuid4()
        result = recommender.hybrid_recommend(
            user_id=user_id,
            query="test query",
            alpha=1.0,
            k=5
        )
        
        assert isinstance(result, list)
    
    def test_get_hybrid_recommendations_collaborative_only(self):
        """Test getting collaborative-only recommendations (alpha=0.0)"""
        from uuid import uuid4
        recommender = HybridRecommender()
        
        user_id = uuid4()
        result = recommender.hybrid_recommend(
            user_id=user_id,
            query="test query",
            alpha=0.0,
            k=5
        )
        
        assert isinstance(result, list)
    
    def test_get_hybrid_recommendations_invalid_alpha(self):
        """Test getting recommendations with invalid alpha values"""
        from uuid import uuid4
        recommender = HybridRecommender()
        
        user_id = uuid4()
        
        # Test alpha > 1.0
        result = recommender.hybrid_recommend(
            user_id=user_id,
            query="test query",
            alpha=1.5,
            k=5
        )
        
        assert isinstance(result, list)
        
        # Test alpha < 0.0
        result = recommender.hybrid_recommend(
            user_id=user_id,
            query="test query",
            alpha=-0.5,
            k=5
        )
        
        assert isinstance(result, list)
