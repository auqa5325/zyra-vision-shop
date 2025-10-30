#!/bin/bash
# Install Python requirements with optimized PyTorch installation
# This script installs PyTorch CPU-only from the official index (faster)
# Then installs the rest of the requirements

set -e

echo "Step 1: Installing PyTorch CPU-only (this is faster from PyTorch's official index)..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu --no-cache-dir

echo ""
echo "Step 2: Installing remaining requirements..."
# Temporarily exclude packages that depend on torch to avoid re-download
pip install --no-cache-dir \
    fastapi==0.109.0 \
    uvicorn[standard]==0.27.0 \
    python-multipart==0.0.6 \
    sqlalchemy==2.0.25 \
    psycopg2-binary==2.9.9 \
    alembic==1.13.1 \
    pydantic==2.5.3 \
    pydantic-settings==2.1.0 \
    python-dotenv==1.0.0 \
    implicit==0.7.2 \
    faiss-cpu==1.8.0 \
    numpy==1.26.4 \
    pandas==2.1.4 \
    scikit-learn==1.4.0 \
    python-jose[cryptography]==3.3.0 \
    passlib[bcrypt]==1.7.4 \
    boto3==1.34.34 \
    httpx==0.28.1 \
    Pillow==10.2.0 \
    google-generativeai>=0.3.0 \
    faker==22.6.0 \
    pytest==7.4.4 \
    pytest-asyncio==0.23.3 \
    requests==2.32.3 \
    python-dateutil>=2.8.2 \
    PyJWT>=2.10.1

echo ""
echo "Step 3: Installing ML packages that depend on PyTorch..."
pip install --no-cache-dir sentence-transformers==2.3.1

echo ""
echo "✓ All packages installed successfully!"

