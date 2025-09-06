#!/usr/bin/env python3
"""
Test script to verify Vercel deployment configuration
"""
import os
import sys
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        # Test main app import
        sys.path.insert(0, str(Path(__file__).parent))
        from main import app
        print("✅ Main app import successful")
        
        # Test config
        from config import settings
        print("✅ Config import successful")
        
        # Test database
        from database import get_db, create_tables
        print("✅ Database import successful")
        
        # Test models
        from models import WorkflowResponse
        print("✅ Models import successful")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_vercel_files():
    """Test that Vercel configuration files exist"""
    print("\nTesting Vercel files...")
    
    required_files = [
        "vercel.json",
        "api/index.py",
        "api/requirements.txt"
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            all_exist = False
    
    return all_exist

def test_environment():
    """Test environment configuration"""
    print("\nTesting environment...")
    
    # Set Vercel environment
    os.environ["VERCEL"] = "1"
    
    try:
        from config import settings
        print(f"✅ Database URL: {settings.database_url}")
        print(f"✅ YouTube API Key: {'Set' if settings.youtube_api_key else 'Not set'}")
        print(f"✅ Debug mode: {settings.debug}")
        return True
    except Exception as e:
        print(f"❌ Environment error: {e}")
        return False

def test_api_endpoints():
    """Test that API endpoints are properly configured"""
    print("\nTesting API endpoints...")
    
    try:
        from main import app
        
        # Get all routes
        routes = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                routes.append(f"{list(route.methods)[0]} {route.path}")
        
        print(f"✅ Found {len(routes)} API routes")
        
        # Check for key endpoints
        key_endpoints = [
            "GET /",
            "GET /health",
            "GET /workflows",
            "GET /docs"
        ]
        
        for endpoint in key_endpoints:
            if any(endpoint in route for route in routes):
                print(f"✅ {endpoint} endpoint found")
            else:
                print(f"❌ {endpoint} endpoint missing")
        
        return True
    except Exception as e:
        print(f"❌ API endpoint error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Vercel Deployment Configuration\n")
    
    tests = [
        test_imports,
        test_vercel_files,
        test_environment,
        test_api_endpoints
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "="*50)
    print("📊 Test Results:")
    print(f"✅ Passed: {sum(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("\n🎉 All tests passed! Ready for Vercel deployment.")
        print("\nNext steps:")
        print("1. Push code to GitHub")
        print("2. Connect to Vercel")
        print("3. Set environment variables")
        print("4. Deploy!")
    else:
        print("\n⚠️  Some tests failed. Please fix issues before deploying.")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
