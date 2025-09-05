#!/usr/bin/env python3
"""
Simple test script for the n8n Workflow Popularity Tracker API
"""

import requests
import json
import time
from typing import Dict, List

BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}: {response.text}"}
    
    except requests.exceptions.ConnectionError:
        return {"error": "Connection failed. Is the server running?"}
    except Exception as e:
        return {"error": str(e)}

def test_basic_endpoints():
    """Test basic API endpoints"""
    print("Testing basic endpoints...")
    
    # Test root endpoint
    result = test_endpoint("/")
    print(f"Root endpoint: {result}")
    
    # Test health check
    result = test_endpoint("/health")
    print(f"Health check: {result}")
    
    # Test platform summary
    result = test_endpoint("/summary")
    print(f"Platform summary: {result}")

def test_main_workflow_endpoints():
    """Test the main workflow endpoints"""
    print("\nTesting main workflow endpoints...")
    
    # Test get all workflows
    result = test_endpoint("/workflows")
    print(f"All workflows: {len(result) if isinstance(result, list) else 'Error'}")
    
    # Test get workflows by platform
    result = test_endpoint("/workflows/YouTube")
    print(f"YouTube workflows: {len(result) if isinstance(result, list) else 'Error'}")
    
    result = test_endpoint("/workflows/Forum")
    print(f"Forum workflows: {len(result) if isinstance(result, list) else 'Error'}")
    
    result = test_endpoint("/workflows/Google")
    print(f"Google workflows: {len(result) if isinstance(result, list) else 'Error'}")
    
    # Test get top workflows
    result = test_endpoint("/workflows/top/5")
    print(f"Top 5 workflows: {len(result) if isinstance(result, list) else 'Error'}")
    
    # Test workflow statistics
    result = test_endpoint("/workflows/stats")
    print(f"Workflow stats: {result}")

def test_data_collection():
    """Test data collection endpoints"""
    print("\nTesting data collection endpoints...")
    
    # Test trends collection (doesn't require API key)
    result = test_endpoint("/collect/trends", "POST")
    print(f"Trends collection: {result}")
    
    # Wait a bit for background task to complete
    time.sleep(2)
    
    # Test getting trends data
    result = test_endpoint("/trends/popular")
    print(f"Popular trends: {result}")

def test_analysis_endpoints():
    """Test analysis endpoints"""
    print("\nTesting analysis endpoints...")
    
    # Test top workflows
    result = test_endpoint("/popularity/top")
    print(f"Top workflows: {result}")
    
    # Test trending workflows
    result = test_endpoint("/popularity/trending")
    print(f"Trending workflows: {result}")

def main():
    """Main test function"""
    print("n8n Workflow Popularity Tracker API Test")
    print("=" * 50)
    
    # Test basic endpoints
    test_basic_endpoints()
    
    # Test main workflow endpoints
    test_main_workflow_endpoints()
    
    # Test data collection
    test_data_collection()
    
    # Test analysis endpoints
    test_analysis_endpoints()
    
    print("\nTest completed!")
    print("Visit http://localhost:8000/docs for interactive API documentation")

if __name__ == "__main__":
    main()
