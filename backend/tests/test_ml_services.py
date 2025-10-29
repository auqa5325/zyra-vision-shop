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
    
    @patch('app.services.content_based.model_loader')
    def test_get_similar_products(self, mock_model_loader):
        """Test getting similar products"""
        # Mock the model loader
        mock_model_loader.get_sentence_transformer.return_value = Mock()
        mock_model_loader.get_faiss_index.return_value = Mock()
        mock_model_loader.get_product_ids.return_value = np.array(['product1', 'product2'])
        
        service = ContentBasedService()
        
        # Mock FAISS search
        mock_index = Mock()
        mock_index.search.return_value = (np.array([[0.9, 0.8]]), np.array([[0, 1]]))
        mock_model_loader.get_faiss_index.return_value = mock_index
        
        # Mock sentence transformer
        mock_transformer = Mock()
        mock_transformer.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_model_loader.get_sentence_transformer.return_value = mock_transformer
        
        result = service.get_similar_products("test query", top_k=2)
        
        assert isinstance(result, list)
        assert len(result) <= 2
    
    @patch('app.services.content_based.model_loader')
    def test_get_similar_products_empty_query(self, mock_model_loader):
        """Test getting similar products with empty query"""
        service = ContentBasedService()
        
        result = service.get_similar_products("", top_k=5)
        
        assert isinstance(result, list)
    
    @patch('app.services.content_based.model_loader')
    def test_get_similar_products_no_model(self, mock_model_loader):
        """Test getting similar products when model is not loaded"""
        mock_model_loader.get_sentence_transformer.side_effect = RuntimeError("Model not loaded")
        
        service = ContentBasedService()
        
        result = service.get_similar_products("test query", top_k=5)
        
        assert isinstance(result, list)
        assert len(result) == 0


class TestCollaborativeService:
    """Test collaborative filtering service"""
    
    def test_collaborative_service_init(self):
        """Test collaborative service initialization"""
        service = CollaborativeService()
        assert service is not None
    
    @patch('app.services.collaborative.model_loader')
    def test_get_user_recommendations(self, mock_model_loader):
        """Test getting user recommendations"""
        # Mock the model loader
        mock_model_loader.get_user_factors.return_value = np.array([[0.1, 0.2], [0.3, 0.4]])
        mock_model_loader.get_item_factors.return_value = np.array([[0.5, 0.6], [0.7, 0.8]])
        mock_model_loader.get_als_mappings.return_value = {
            "idx_to_item_id": {0: "item1", 1: "item2"},
            "user_id_to_idx": {"user1": 0, "user2": 1}
        }
        
        service = CollaborativeService()
        
        result = service.get_user_recommendations("user1", top_k=2)
        
        assert isinstance(result, list)
        assert len(result) <= 2
    
    @patch('app.services.collaborative.model_loader')
    def test_get_user_recommendations_unknown_user(self, mock_model_loader):
        """Test getting recommendations for unknown user"""
        mock_model_loader.get_als_mappings.return_value = {
            "user_id_to_idx": {"user1": 0}
        }
        
        service = CollaborativeService()
        
        result = service.get_user_recommendations("unknown_user", top_k=5)
        
        assert isinstance(result, list)
        assert len(result) == 0
    
    @patch('app.services.collaborative.model_loader')
    def test_get_user_recommendations_no_model(self, mock_model_loader):
        """Test getting recommendations when model is not loaded"""
        mock_model_loader.get_user_factors.side_effect = RuntimeError("Model not loaded")
        
        service = CollaborativeService()
        
        result = service.get_user_recommendations("user1", top_k=5)
        
        assert isinstance(result, list)
        assert len(result) == 0


class TestHybridRecommender:
    """Test hybrid recommendation service"""
    
    def test_hybrid_recommender_init(self):
        """Test hybrid recommender initialization"""
        recommender = HybridRecommender()
        assert recommender is not None
    
    @patch('app.services.recommender.ContentBasedService')
    @patch('app.services.recommender.CollaborativeService')
    def test_get_hybrid_recommendations(self, mock_cf_service, mock_cb_service):
        """Test getting hybrid recommendations"""
        # Mock the services
        mock_cb_instance = Mock()
        mock_cb_instance.get_similar_products.return_value = [
            {"product_id": "prod1", "score": 0.9},
            {"product_id": "prod2", "score": 0.8}
        ]
        mock_cb_service.return_value = mock_cb_instance
        
        mock_cf_instance = Mock()
        mock_cf_instance.get_user_recommendations.return_value = [
            {"product_id": "prod2", "score": 0.7},
            {"product_id": "prod3", "score": 0.6}
        ]
        mock_cf_service.return_value = mock_cf_instance
        
        recommender = HybridRecommender()
        
        result = recommender.get_hybrid_recommendations(
            user_id="user1",
            query="test query",
            alpha=0.6,
            top_k=5
        )
        
        assert isinstance(result, list)
        assert len(result) <= 5
    
    @patch('app.services.recommender.ContentBasedService')
    @patch('app.services.recommender.CollaborativeService')
    def test_get_hybrid_recommendations_content_only(self, mock_cf_service, mock_cb_service):
        """Test getting content-only recommendations (alpha=1.0)"""
        mock_cb_instance = Mock()
        mock_cb_instance.get_similar_products.return_value = [
            {"product_id": "prod1", "score": 0.9}
        ]
        mock_cb_service.return_value = mock_cb_instance
        
        recommender = HybridRecommender()
        
        result = recommender.get_hybrid_recommendations(
            user_id="user1",
            query="test query",
            alpha=1.0,
            top_k=5
        )
        
        assert isinstance(result, list)
        # Should only use content-based recommendations
    
    @patch('app.services.recommender.ContentBasedService')
    @patch('app.services.recommender.CollaborativeService')
    def test_get_hybrid_recommendations_collaborative_only(self, mock_cf_service, mock_cb_service):
        """Test getting collaborative-only recommendations (alpha=0.0)"""
        mock_cf_instance = Mock()
        mock_cf_instance.get_user_recommendations.return_value = [
            {"product_id": "prod1", "score": 0.8}
        ]
        mock_cf_service.return_value = mock_cf_instance
        
        recommender = HybridRecommender()
        
        result = recommender.get_hybrid_recommendations(
            user_id="user1",
            query="test query",
            alpha=0.0,
            top_k=5
        )
        
        assert isinstance(result, list)
        # Should only use collaborative recommendations
    
    def test_get_hybrid_recommendations_invalid_alpha(self):
        """Test getting recommendations with invalid alpha values"""
        recommender = HybridRecommender()
        
        # Test alpha > 1.0
        result = recommender.get_hybrid_recommendations(
            user_id="user1",
            query="test query",
            alpha=1.5,
            top_k=5
        )
        
        assert isinstance(result, list)
        
        # Test alpha < 0.0
        result = recommender.get_hybrid_recommendations(
            user_id="user1",
            query="test query",
            alpha=-0.5,
            top_k=5
        )
        
        assert isinstance(result, list)
