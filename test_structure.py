#!/usr/bin/env python3
"""
Minimal test script to verify the application structure
without requiring all dependencies.
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if we can import core modules."""
    try:
        # Test config import
        import config
        print("✓ Config module imported successfully")
        
        # Test basic structure
        from app import routes, api
        print("✓ Routes and API modules imported successfully")
        
        print("✓ All core modules imported successfully!")
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_directory_structure():
    """Test if required directories exist."""
    required_dirs = [
        'app',
        'app/templates',
        'app/utils',
        'data',
        'data/documents',
        'data/plots',
        'data/metadata'
    ]
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✓ Directory exists: {directory}")
        else:
            print(f"✗ Directory missing: {directory}")
            return False
    
    return True

def test_template_files():
    """Test if template files exist."""
    template_files = [
        'app/templates/base.html',
        'app/templates/index.html',
        'app/templates/upload.html',
        'app/templates/chat.html',
        'app/templates/analytics.html',
        'app/templates/documents.html',
        'app/templates/settings.html'
    ]
    
    for template in template_files:
        if os.path.exists(template):
            print(f"✓ Template exists: {template}")
        else:
            print(f"✗ Template missing: {template}")
            return False
    
    return True

def main():
    """Run all tests."""
    print("Testing RHP RAG Application Structure")
    print("=" * 40)
    
    tests = [
        ("Directory Structure", test_directory_structure),
        ("Template Files", test_template_files),
        ("Module Imports", test_imports)
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * len(test_name))
        
        if not test_func():
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("✓ All tests passed! Application structure is ready.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Copy .env.example to .env and configure your API keys")
        print("3. Run the application: python run.py")
    else:
        print("✗ Some tests failed. Please check the errors above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())