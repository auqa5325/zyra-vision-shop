#!/usr/bin/env python3
"""
Build FAISS index for fast similarity search
"""

import os
import sys
import numpy as np
import faiss

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings


def build_faiss_index():
    """Build FAISS index from embeddings"""
    print("Loading embeddings...")
    
    # Load embeddings
    embeddings_path = settings.embeddings_path
    if not os.path.exists(embeddings_path):
        print(f"❌ Embeddings file not found: {embeddings_path}")
        print("Please run train_embeddings.py first.")
        return
    
    embeddings = np.load(embeddings_path)
    print(f"Loaded embeddings shape: {embeddings.shape}")
    
    # Load product IDs
    product_ids_path = "artifacts/product_ids.npy"
    if not os.path.exists(product_ids_path):
        print(f"❌ Product IDs file not found: {product_ids_path}")
        return
    
    product_ids = np.load(product_ids_path, allow_pickle=True)
    print(f"Loaded {len(product_ids)} product IDs")
    
    # Normalize embeddings for cosine similarity
    print("Normalizing embeddings...")
    faiss.normalize_L2(embeddings)
    
    # Create FAISS index
    print("Building FAISS index...")
    dimension = embeddings.shape[1]
    
    # Use IndexFlatIP for inner product (cosine similarity after normalization)
    index = faiss.IndexFlatIP(dimension)
    
    # Add embeddings to index
    index.add(embeddings)
    
    print(f"Index built with {index.ntotal} vectors")
    
    # Create artifacts directory
    os.makedirs("artifacts", exist_ok=True)
    
    # Save FAISS index
    index_path = settings.faiss_index_path
    faiss.write_index(index, index_path)
    print(f"Saved FAISS index to {index_path}")
    
    # Save product IDs mapping
    product_ids_path = "artifacts/product_ids.npy"
    np.save(product_ids_path, product_ids)
    print(f"Saved product IDs mapping to {product_ids_path}")
    
    # Test the index
    print("Testing index...")
    test_query = embeddings[0:1]  # Use first embedding as test query
    scores, indices = index.search(test_query, k=5)
    
    print("Top 5 similar products for test query:")
    for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
        print(f"  {i+1}. Product ID: {product_ids[idx]}, Score: {score:.4f}")
    
    print("✅ FAISS index building completed!")


def main():
    """Main function for script execution"""
    build_faiss_index()


if __name__ == "__main__":
    main()

