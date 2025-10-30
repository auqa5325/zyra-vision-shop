#!/bin/bash
# Alternative: Install with increased timeout and retries
# Use this if the PyTorch index method doesn't work

set -e

echo "Installing requirements with increased timeout and retries..."
pip install --default-timeout=1000 --retries=5 --no-cache-dir -r requirements.txt

echo ""
echo "✓ Installation complete!"

