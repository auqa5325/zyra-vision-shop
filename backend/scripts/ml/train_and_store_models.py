#!/usr/bin/env python3
"""
Train and Store ML Models Locally
This script trains all ML models and stores them locally for the API to load
"""

import os
import sys
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from implicit.als import AlternatingLeastSquares
import faiss
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
from datetime import datetime

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.models import Product, Interaction, User, EmbeddingsMeta

# Database setup
engine = create_engine(settings.get_database_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def load_data():
    """Load all data from database"""
    session = SessionLocal()
    try:
        # Load products
        products = session.query(Product).filter(Product.available == True).all()
        print(f"Loaded {len(products)} products")
        
        # Load interactions
        interactions = session.query(Interaction).all()
        print(f"Loaded {len(interactions)} interactions")
        
        # Load users
        users = session.query(User).all()
        print(f"Loaded {len(users)} users")
        
        return products, interactions, users
        
    finally:
        session.close()


def prepare_product_texts(products):
    """Prepare text data for product embeddings"""
    texts = []
    product_ids = []
    
    for product in products:
        # Combine name, description, and tags
        text_parts = []
        
        if product.name:
            text_parts.append(product.name)
        
        if product.short_description:
            text_parts.append(product.short_description)
        
        if product.long_description:
            text_parts.append(product.long_description)
        
        if product.tags:
            text_parts.extend(product.tags)
        
        if product.brand:
            text_parts.append(product.brand)
        
        # Join all parts
        combined_text = " ".join(text_parts)
        texts.append(combined_text)
        product_ids.append(product.product_id)
    
    return texts, product_ids


def train_sentence_transformer(texts, product_ids):
    """Train Sentence Transformer embeddings"""
    print("Training Sentence Transformer embeddings...")
    
    # Load model
    model = SentenceTransformer(settings.embedding_model)
    
    # Generate embeddings
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)
    
    print(f"Generated embeddings shape: {embeddings.shape}")
    
    # Create artifacts directory
    os.makedirs("artifacts", exist_ok=True)
    
    # Save embeddings
    embeddings_path = settings.embeddings_path
    np.save(embeddings_path, embeddings)
    print(f"Saved embeddings to {embeddings_path}")
    
    # Save product IDs mapping
    product_ids_path = "artifacts/product_ids.npy"
    np.save(product_ids_path, product_ids)
    print(f"Saved product IDs to {product_ids_path}")
    
    # Save model locally
    model_path = "artifacts/sentence_transformer_model"
    model.save(model_path)
    print(f"Saved Sentence Transformer model to {model_path}")
    
    return embeddings, product_ids


def build_faiss_index(embeddings, product_ids):
    """Build FAISS index for fast similarity search"""
    print("Building FAISS index...")
    
    # Normalize embeddings for cosine similarity
    faiss.normalize_L2(embeddings)
    
    # Create FAISS index (completely local)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
    
    # Add embeddings to index
    index.add(embeddings)
    
    print(f"Index built with {index.ntotal} vectors")
    
    # Save FAISS index locally
    index_path = settings.faiss_index_path
    faiss.write_index(index, index_path)
    print(f"Saved FAISS index locally to {index_path}")
    
    # Also save as binary for backup
    binary_path = index_path.replace('.index', '_binary.index')
    faiss.write_index(index, binary_path)
    print(f"Saved FAISS index binary backup to {binary_path}")
    
    return index


def train_als_model(interactions, users, products):
    """Train Implicit ALS model"""
    print("Training ALS collaborative filtering model...")
    
    # Create mappings
    user_id_to_idx = {}
    item_id_to_idx = {}
    user_idx = 0
    item_idx = 0
    
    # Collect all unique users and items
    for interaction in interactions:
        if interaction.user_id and interaction.user_id not in user_id_to_idx:
            user_id_to_idx[interaction.user_id] = user_idx
            user_idx += 1
        
        if interaction.product_id and interaction.product_id not in item_id_to_idx:
            item_id_to_idx[interaction.product_id] = item_idx
            item_idx += 1
    
    print(f"Found {len(user_id_to_idx)} users and {len(item_id_to_idx)} items")
    
    # Build sparse matrix
    rows = []
    cols = []
    data = []
    
    for interaction in interactions:
        if interaction.user_id and interaction.product_id:
            user_idx = user_id_to_idx[interaction.user_id]
            item_idx = item_id_to_idx[interaction.product_id]
            
            # Weight different event types for utility matrix
            # Higher weights = stronger signal of preference
            weight = float(interaction.event_value)
            if interaction.event_type == "purchase":
                weight *= 2.0   # Highest - actual conversion
            elif interaction.event_type == "add_to_cart":
                weight *= 1.5   # Strong intent - user wants to buy
            elif interaction.event_type == "review":
                weight *= 1.6   # Explicit feedback - weighted by rating (1-5)
            elif interaction.event_type == "wishlist":
                weight *= 1.3   # Interest - user saved for later
            elif interaction.event_type == "click":
                weight *= 1.2   # Engagement - user clicked to explore
            # view: base weight (1.0) - just browsing
            
            rows.append(user_idx)
            cols.append(item_idx)
            data.append(weight)
    
    # Create sparse matrix
    from scipy.sparse import csr_matrix
    matrix = csr_matrix((data, (rows, cols)), shape=(len(user_id_to_idx), len(item_id_to_idx)))
    
    # Train ALS model
    model = AlternatingLeastSquares(
        factors=64,
        iterations=15,
        regularization=0.01,
        random_state=42
    )
    
    model.fit(matrix)
    
    # Create reverse mappings
    idx_to_user_id = {v: str(k) for k, v in user_id_to_idx.items()}
    idx_to_item_id = {v: str(k) for k, v in item_id_to_idx.items()}
    
    # Save model artifacts
    user_factors_path = "artifacts/user_factors.npy"
    np.save(user_factors_path, model.user_factors)
    print(f"Saved user factors to {user_factors_path}")
    
    item_factors_path = settings.als_factors_path
    np.save(item_factors_path, model.item_factors)
    print(f"Saved item factors to {item_factors_path}")
    
    # Save mappings
    mappings = {
        "user_id_to_idx": {str(k): v for k, v in user_id_to_idx.items()},
        "item_id_to_idx": {str(k): v for k, v in item_id_to_idx.items()},
        "idx_to_user_id": {v: str(k) for k, v in idx_to_user_id.items()},
        "idx_to_item_id": {v: str(k) for k, v in idx_to_item_id.items()}
    }
    
    mappings_path = "artifacts/als_mappings.json"
    with open(mappings_path, 'w') as f:
        json.dump(mappings, f, indent=2)
    print(f"Saved mappings to {mappings_path}")
    
    return model, mappings


def update_embeddings_metadata(product_ids, embeddings):
    """Update embeddings metadata in database"""
    print("Updating embeddings metadata...")
    
    session = SessionLocal()
    try:
        # Clear existing metadata
        session.query(EmbeddingsMeta).filter(EmbeddingsMeta.object_type == "product").delete()
        
        # Add new metadata
        for i, product_id in enumerate(product_ids):
            meta = EmbeddingsMeta(
                object_type="product",
                object_id=product_id,
                embedding_file=settings.embeddings_path,
                vector_index=i,
                dim=embeddings.shape[1]
            )
            session.add(meta)
        
        session.commit()
        print("Updated embeddings metadata in database")
        
    finally:
        session.close()


def save_model_info():
    """Save model information and metadata"""
    model_info = {
        "created_at": datetime.utcnow().isoformat(),
        "embedding_model": settings.embedding_model,
        "embedding_dimension": 384,  # all-MiniLM-L6-v2 dimension
        "faiss_index_type": "IndexFlatIP",
        "als_factors": 64,
        "als_iterations": 15,
        "als_regularization": 0.01,
        "artifacts": {
            "embeddings": settings.embeddings_path,
            "faiss_index": settings.faiss_index_path,
            "item_factors": settings.als_factors_path,
            "user_factors": "artifacts/user_factors.npy",
            "product_ids": "artifacts/product_ids.npy",
            "sentence_transformer": "artifacts/sentence_transformer_model",
            "als_mappings": "artifacts/als_mappings.json"
        }
    }
    
    info_path = "artifacts/model_info.json"
    with open(info_path, 'w') as f:
        json.dump(model_info, f, indent=2)
    print(f"Saved model info to {info_path}")


def main():
    """Main training function"""
    print("Starting ML model training and storage...")
    
    # Load data
    products, interactions, users = load_data()
    
    if not products:
        print("❌ No products found. Please run generate_mock_data.py first.")
        return
    
    if not interactions:
        print("❌ No interactions found. Please run generate_mock_data.py first.")
        return
    
    # Prepare product texts
    texts, product_ids = prepare_product_texts(products)
    
    # Train Sentence Transformer
    embeddings, product_ids = train_sentence_transformer(texts, product_ids)
    
    # Build FAISS index
    faiss_index = build_faiss_index(embeddings, product_ids)
    
    # Train ALS model
    als_model, mappings = train_als_model(interactions, users, products)
    
    # Update database metadata
    update_embeddings_metadata(product_ids, embeddings)
    
    # Save model information
    save_model_info()
    
    print("\n✅ ML model training completed successfully!")
    print(f"📊 Summary:")
    print(f"   - Products: {len(products)}")
    print(f"   - Embeddings: {embeddings.shape}")
    print(f"   - FAISS vectors: {faiss_index.ntotal}")
    print(f"   - ALS users: {len(mappings['user_id_to_idx'])}")
    print(f"   - ALS items: {len(mappings['item_id_to_idx'])}")
    print(f"   - All artifacts saved to artifacts/ directory")


if __name__ == "__main__":
    main()


