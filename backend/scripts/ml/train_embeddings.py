#!/usr/bin/env python3
"""
Train Sentence Transformers embeddings for products
"""

import os
import sys
import numpy as np
from sentence_transformers import SentenceTransformer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.models import Product, EmbeddingsMeta

# Database setup
engine = create_engine(settings.get_database_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def load_products():
    """Load all products from database"""
    session = SessionLocal()
    try:
        products = session.query(Product).filter(Product.available == True).all()
        print(f"Loaded {len(products)} products")
        return products
    finally:
        session.close()


def prepare_text_data(products):
    """Prepare text data for embedding"""
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


def train_embeddings():
    """Train embeddings using Sentence Transformers"""
    print("Loading Sentence Transformer model...")
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    
    print("Loading products...")
    products = load_products()
    
    print("Preparing text data...")
    texts, product_ids = prepare_text_data(products)
    
    print("Generating embeddings...")
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
    
    # Update embeddings metadata
    session = SessionLocal()
    try:
        # Clear existing metadata
        session.query(EmbeddingsMeta).filter(EmbeddingsMeta.object_type == "product").delete()
        
        # Add new metadata
        for i, product_id in enumerate(product_ids):
            meta = EmbeddingsMeta(
                object_type="product",
                object_id=product_id,
                embedding_file=embeddings_path,
                vector_index=i,
                dim=embeddings.shape[1]
            )
            session.add(meta)
        
        session.commit()
        print("Updated embeddings metadata")
        
    finally:
        session.close()
    
    print("✅ Embeddings training completed!")


if __name__ == "__main__":
    train_embeddings()

