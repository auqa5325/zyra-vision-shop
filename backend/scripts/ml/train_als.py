#!/usr/bin/env python3
"""
Train Implicit ALS model for collaborative filtering
"""

import os
import sys
import numpy as np
import pandas as pd
from implicit.als import AlternatingLeastSquares
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from scipy.sparse import csr_matrix

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.models import Interaction, User, Product

# Database setup
engine = create_engine(settings.get_database_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def load_interactions():
    """Load interactions from database"""
    session = SessionLocal()
    try:
        interactions = session.query(Interaction).all()
        print(f"Loaded {len(interactions)} interactions")
        return interactions
    finally:
        session.close()


def build_user_item_matrix(interactions):
    """Build user-item interaction matrix"""
    print("Building user-item matrix...")
    
    # Create mappings
    users = {}
    items = {}
    user_idx = 0
    item_idx = 0
    
    # Collect all unique users and items
    for interaction in interactions:
        if interaction.user_id not in users:
            users[interaction.user_id] = user_idx
            user_idx += 1
        
        if interaction.product_id not in items:
            items[interaction.product_id] = item_idx
            item_idx += 1
    
    print(f"Found {len(users)} users and {len(items)} items")
    
    # Build sparse matrix
    rows = []
    cols = []
    data = []
    
    for interaction in interactions:
        if interaction.user_id and interaction.product_id:
            user_idx = users[interaction.user_id]
            item_idx = items[interaction.product_id]
            
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
    matrix = csr_matrix((data, (rows, cols)), shape=(len(users), len(items)))
    
    # Create reverse mappings
    user_id_to_idx = users
    item_id_to_idx = items
    idx_to_user_id = {v: k for k, v in users.items()}
    idx_to_item_id = {v: k for k, v in items.items()}
    
    return matrix, user_id_to_idx, item_id_to_idx, idx_to_user_id, idx_to_item_id


def train_als_model(matrix):
    """Train ALS model"""
    print("Training ALS model...")
    
    # Initialize ALS model
    model = AlternatingLeastSquares(
        factors=64,
        iterations=15,
        regularization=0.01,
        random_state=42
    )
    
    # Train the model
    model.fit(matrix)
    
    print("✅ ALS model training completed!")
    return model


def save_model_artifacts(model, user_id_to_idx, item_id_to_idx, idx_to_user_id, idx_to_item_id):
    """Save model artifacts"""
    print("Saving model artifacts...")
    
    # Create artifacts directory
    os.makedirs("artifacts", exist_ok=True)
    
    # Save user factors
    user_factors_path = "artifacts/user_factors.npy"
    np.save(user_factors_path, model.user_factors)
    print(f"Saved user factors to {user_factors_path}")
    
    # Save item factors
    item_factors_path = settings.als_factors_path
    np.save(item_factors_path, model.item_factors)
    print(f"Saved item factors to {item_factors_path}")
    
    # Save mappings
    mappings = {
        "user_id_to_idx": user_id_to_idx,
        "item_id_to_idx": item_id_to_idx,
        "idx_to_user_id": idx_to_user_id,
        "idx_to_item_id": idx_to_item_id
    }
    
    mappings_path = "artifacts/als_mappings.npy"
    np.save(mappings_path, mappings)
    print(f"Saved mappings to {mappings_path}")
    
    print("✅ Model artifacts saved!")


def main():
    """Main training function"""
    print("Starting ALS training...")
    
    # Load interactions
    interactions = load_interactions()
    
    if not interactions:
        print("❌ No interactions found. Please run generate_mock_data.py first.")
        return
    
    # Build user-item matrix
    matrix, user_id_to_idx, item_id_to_idx, idx_to_user_id, idx_to_item_id = build_user_item_matrix(interactions)
    
    # Train ALS model
    model = train_als_model(matrix)
    
    # Save artifacts
    save_model_artifacts(model, user_id_to_idx, item_id_to_idx, idx_to_user_id, idx_to_item_id)
    
    print("✅ ALS training completed successfully!")


if __name__ == "__main__":
    main()

