#!/usr/bin/env python3
"""
Update FAISS index from current product table
Regenerates embeddings and rebuilds FAISS index for all current products
"""

import os
import sys
import numpy as np
import faiss
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


def load_products_from_db():
    """Load all available products from database"""
    session = SessionLocal()
    try:
        products = session.query(Product).filter(Product.available == True).all()
        print(f"📦 Loaded {len(products)} products from database")
        return products
    finally:
        session.close()


def prepare_product_texts(products):
    """Prepare text data for product embeddings"""
    texts = []
    product_ids = []
    
    for product in products:
        # Combine name, description, brand, and tags
        text_parts = []
        
        if product.name:
            text_parts.append(product.name)
        
        if product.short_description:
            text_parts.append(product.short_description)
        
        if product.long_description:
            text_parts.append(product.long_description)
        
        if product.tags:
            if isinstance(product.tags, list):
                text_parts.extend(product.tags)
            else:
                text_parts.append(str(product.tags))
        
        if product.brand:
            text_parts.append(product.brand)
        
        # Join all parts
        combined_text = " ".join(str(part) for part in text_parts if part)
        texts.append(combined_text)
        product_ids.append(product.product_id)
    
    return texts, product_ids


def generate_embeddings(texts):
    """Generate embeddings using Sentence Transformer"""
    print("🤖 Loading Sentence Transformer model...")
    
    # Try to load local model first, then fallback to Hugging Face
    local_model_path = "artifacts/sentence_transformer_model"
    if os.path.exists(local_model_path):
        print(f"   Loading local model from {local_model_path}")
        model = SentenceTransformer(local_model_path)
    else:
        print(f"   Loading model from Hugging Face: {settings.embedding_model}")
        model = SentenceTransformer(settings.embedding_model)
        # Save model locally for next time
        os.makedirs("artifacts", exist_ok=True)
        model.save(local_model_path)
        print(f"   Saved model locally to {local_model_path}")
    
    print(f"📊 Generating embeddings for {len(texts)} products...")
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)
    
    print(f"✅ Generated embeddings shape: {embeddings.shape}")
    return embeddings, model


def build_and_save_faiss_index(embeddings, product_ids):
    """Build and save FAISS index"""
    print("🔨 Building FAISS index...")
    
    # Normalize embeddings for cosine similarity
    normalized_embeddings = embeddings.copy()
    faiss.normalize_L2(normalized_embeddings)
    
    # Create FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
    
    # Add embeddings to index
    index.add(normalized_embeddings)
    
    print(f"✅ Built FAISS index with {index.ntotal} vectors (dimension: {dimension})")
    
    # Create artifacts directory
    os.makedirs("artifacts", exist_ok=True)
    
    # Save FAISS index
    index_path = settings.faiss_index_path
    faiss.write_index(index, index_path)
    print(f"💾 Saved FAISS index to {index_path}")
    
    # Save binary backup
    binary_path = index_path.replace('.index', '_binary.index')
    faiss.write_index(index, binary_path)
    print(f"💾 Saved FAISS index binary backup to {binary_path}")
    
    # Save product IDs mapping
    product_ids_path = "artifacts/product_ids.npy"
    np.save(product_ids_path, product_ids)
    print(f"💾 Saved product IDs mapping ({len(product_ids)} IDs) to {product_ids_path}")
    
    return index


def update_embeddings_metadata(product_ids, embeddings):
    """Update embeddings metadata in database"""
    print("📝 Updating embeddings metadata in database...")
    
    session = SessionLocal()
    try:
        # Clear existing product metadata
        deleted = session.query(EmbeddingsMeta).filter(
            EmbeddingsMeta.object_type == "product"
        ).delete()
        print(f"   Cleared {deleted} old metadata records")
        
        # Add new metadata
        embeddings_path = settings.embeddings_path
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
        print(f"✅ Added {len(product_ids)} new metadata records")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error updating metadata: {e}")
        raise
    finally:
        session.close()


def save_embeddings(embeddings):
    """Save embeddings to file"""
    print(f"💾 Saving embeddings to {settings.embeddings_path}...")
    os.makedirs("artifacts", exist_ok=True)
    np.save(settings.embeddings_path, embeddings)
    print(f"✅ Saved embeddings (shape: {embeddings.shape})")


def test_faiss_index(index, product_ids, embeddings):
    """Test the FAISS index with a sample query"""
    print("🧪 Testing FAISS index...")
    
    # Use first product as test query
    test_query = embeddings[0:1].copy()
    faiss.normalize_L2(test_query)
    
    k = min(5, len(product_ids))
    scores, indices = index.search(test_query, k)
    
    print(f"   Test query: Product ID {product_ids[0]}")
    print(f"   Top {k} similar products:")
    for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
        print(f"      {i+1}. Product ID: {product_ids[idx]}, Similarity: {score:.4f}")


def main():
    """Main function to update FAISS index from database"""
    print("=" * 60)
    print("🔄 Updating FAISS index from current product table")
    print("=" * 60)
    
    # Load products from database
    products = load_products_from_db()
    
    if not products:
        print("❌ No products found in database. Please add products first.")
        return
    
    # Prepare text data
    print("📝 Preparing product text data...")
    texts, product_ids = prepare_product_texts(products)
    
    # Generate embeddings
    embeddings, model = generate_embeddings(texts)
    
    # Save embeddings
    save_embeddings(embeddings)
    
    # Build FAISS index
    index = build_and_save_faiss_index(embeddings, product_ids)
    
    # Update database metadata
    update_embeddings_metadata(product_ids, embeddings)
    
    # Test the index
    test_faiss_index(index, product_ids, embeddings)
    
    print("\n" + "=" * 60)
    print("✅ FAISS index update completed successfully!")
    print("=" * 60)
    print(f"📊 Summary:")
    print(f"   - Products processed: {len(products)}")
    print(f"   - Embeddings shape: {embeddings.shape}")
    print(f"   - FAISS vectors: {index.ntotal}")
    print(f"   - Product IDs saved: {len(product_ids)}")
    print(f"   - Model: {settings.embedding_model}")
    print(f"   - Index path: {settings.faiss_index_path}")
    print(f"   - Embeddings path: {settings.embeddings_path}")


if __name__ == "__main__":
    main()

