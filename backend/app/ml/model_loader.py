"""
ML Model Loader - Loads pre-trained models at startup
"""

import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import Optional, Dict, Any
from app.config import settings


class ModelLoader:
    """Singleton class to load and manage ML models"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.faiss_index: Optional[faiss.Index] = None
            self.product_ids: Optional[np.ndarray] = None
            self.sentence_transformer: Optional[SentenceTransformer] = None
            self.user_factors: Optional[np.ndarray] = None
            self.item_factors: Optional[np.ndarray] = None
            self.als_mappings: Optional[Dict[str, Any]] = None
            self._initialized = True
    
    def load_models(self):
        """Load all ML models and artifacts"""
        print("Loading ML models...")
        
        try:
            # Load FAISS index
            self._load_faiss_index()
            
            # Load Sentence Transformer
            self._load_sentence_transformer()
            
            # Load ALS factors
            self._load_als_factors()
            
            print("✅ All ML models loaded successfully!")
            
        except Exception as e:
            print(f"❌ Error loading ML models: {e}")
            raise
    
    def _load_faiss_index(self):
        """Load FAISS index and product IDs"""
        index_path = settings.faiss_index_path
        product_ids_path = "artifacts/product_ids.npy"
        
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"FAISS index not found: {index_path}")
        
        if not os.path.exists(product_ids_path):
            raise FileNotFoundError(f"Product IDs not found: {product_ids_path}")
        
        self.faiss_index = faiss.read_index(index_path)
        self.product_ids = np.load(product_ids_path, allow_pickle=True)
        
        print(f"✅ Loaded FAISS index with {self.faiss_index.ntotal} vectors")
    
    def _load_sentence_transformer(self):
        """Load Sentence Transformer model"""
        # Try to load locally stored model first
        local_model_path = "artifacts/sentence_transformer_model"
        
        if os.path.exists(local_model_path):
            self.sentence_transformer = SentenceTransformer(local_model_path)
            print(f"✅ Loaded local Sentence Transformer from {local_model_path}")
        else:
            # Fallback to downloading from Hugging Face
            self.sentence_transformer = SentenceTransformer(settings.embedding_model)
            print(f"✅ Loaded Sentence Transformer from Hugging Face: {settings.embedding_model}")
    
    def _load_als_factors(self):
        """Load ALS factors and mappings"""
        user_factors_path = "artifacts/user_factors.npy"
        item_factors_path = settings.als_factors_path
        mappings_path = "artifacts/als_mappings.json"
        
        if not os.path.exists(user_factors_path):
            raise FileNotFoundError(f"User factors not found: {user_factors_path}")
        
        if not os.path.exists(item_factors_path):
            raise FileNotFoundError(f"Item factors not found: {item_factors_path}")
        
        if not os.path.exists(mappings_path):
            raise FileNotFoundError(f"ALS mappings not found: {mappings_path}")
        
        self.user_factors = np.load(user_factors_path)
        self.item_factors = np.load(item_factors_path)
        
        # Load mappings from JSON
        import json
        with open(mappings_path, 'r') as f:
            self.als_mappings = json.load(f)
        
        print(f"✅ Loaded ALS factors: {self.user_factors.shape[0]} users, {self.item_factors.shape[0]} items")
    
    def get_faiss_index(self) -> faiss.Index:
        """Get FAISS index"""
        if self.faiss_index is None:
            raise RuntimeError("FAISS index not loaded")
        return self.faiss_index
    
    def get_product_ids(self) -> np.ndarray:
        """Get product IDs array"""
        if self.product_ids is None:
            raise RuntimeError("Product IDs not loaded")
        return self.product_ids
    
    def get_sentence_transformer(self) -> SentenceTransformer:
        """Get Sentence Transformer model"""
        if self.sentence_transformer is None:
            raise RuntimeError("Sentence Transformer not loaded")
        return self.sentence_transformer
    
    def get_als_factors(self) -> tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """Get ALS factors and mappings"""
        if self.user_factors is None or self.item_factors is None or self.als_mappings is None:
            raise RuntimeError("ALS factors not loaded")
        return self.user_factors, self.item_factors, self.als_mappings


# Global model loader instance
model_loader = ModelLoader()
