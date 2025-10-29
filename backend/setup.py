#!/usr/bin/env python3
"""
Environment Setup Script for Zyra Backend
This script helps you set up the required environment for the Zyra backend
"""

import os
import sys
import subprocess
from pathlib import Path


def create_env_file():
    """Create .env file from template"""
    env_example = Path("env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not env_example.exists():
        print("❌ env.example file not found")
        return False
    
    # Copy template
    with open(env_example, 'r') as f:
        content = f.read()
    
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✅ Created .env file from template")
    print("📝 Please edit .env file with your actual values")
    return True


def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True, text=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print(f"Error output: {e.stderr}")
        return False


def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        "artifacts",
        "logs",
        "data",
        "data/embeddings",
        "data/models"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   Created: {directory}")
    
    print("✅ Directories created")
    return True


def check_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible")
        print("   Required: Python 3.8 or higher")
        return False


def print_setup_instructions():
    """Print detailed setup instructions"""
    print("\n" + "="*60)
    print("🚀 ZYRA BACKEND SETUP INSTRUCTIONS")
    print("="*60)
    
    print("\n📋 REQUIRED SERVICES:")
    print("1. PostgreSQL Database (AWS RDS or local)")
    print("2. AWS S3 Bucket for image storage")
    print("3. AWS Account with programmatic access")
    
    print("\n🔧 ENVIRONMENT SETUP:")
    print("1. Edit .env file with your actual values:")
    print("   - DATABASE_URL: PostgreSQL connection string")
    print("   - JWT_SECRET_KEY: Strong secret key for JWT tokens")
    print("   - AWS credentials and S3 bucket name")
    
    print("\n📊 DATABASE SETUP:")
    print("1. Create PostgreSQL database")
    print("2. Run: python scripts/init_db.py")
    print("3. Run: python scripts/generate_mock_data.py")
    
    print("\n🤖 ML MODEL TRAINING:")
    print("1. Run: python scripts/train_and_store_models.py")
    print("   This will train and store all models locally")
    
    print("\n🧪 TESTING:")
    print("1. Run: python scripts/test_connectivity.py")
    print("   This will test all connections")
    
    print("\n🚀 STARTING THE API:")
    print("1. Run: python app/main.py")
    print("2. API will be available at: http://localhost:8000")
    print("3. Documentation at: http://localhost:8000/docs")
    
    print("\n🔐 AUTHENTICATION:")
    print("1. Register: POST /api/auth/register")
    print("2. Login: POST /api/auth/login")
    print("3. Use Bearer token in Authorization header")
    
    print("\n" + "="*60)


def main():
    """Main setup function"""
    print("🚀 Zyra Backend Setup")
    print("="*30)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed at dependency installation")
        return
    
    # Create .env file
    if not create_env_file():
        print("❌ Setup failed at .env file creation")
        return
    
    # Print instructions
    print_setup_instructions()
    
    print("\n✅ Basic setup completed!")
    print("📝 Next steps:")
    print("   1. Edit .env file with your actual values")
    print("   2. Set up PostgreSQL database")
    print("   3. Set up AWS S3 bucket")
    print("   4. Run connectivity test: python scripts/test_connectivity.py")


if __name__ == "__main__":
    main()
