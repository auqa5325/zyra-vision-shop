#!/usr/bin/env python3
"""
Test runner for Zyra backend
"""

import subprocess
import sys
import os


def run_tests():
    """Run all backend tests"""
    print("🧪 Running Zyra Backend Tests")
    print("=" * 50)
    
    # Change to backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    # Run pytest with coverage
    cmd = [
        "python", "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--cov=app",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ All tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ pytest not found. Please install it with: pip install pytest pytest-cov")
        return False


def run_specific_test(test_file):
    """Run a specific test file"""
    print(f"🧪 Running {test_file}")
    print("=" * 50)
    
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    cmd = ["python", "-m", "pytest", f"tests/{test_file}", "-v"]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"\n✅ {test_file} tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {test_file} tests failed with exit code {e.returncode}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test file
        test_file = sys.argv[1]
        success = run_specific_test(test_file)
    else:
        # Run all tests
        success = run_tests()
    
    sys.exit(0 if success else 1)
