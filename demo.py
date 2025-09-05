#!/usr/bin/env python3
"""
Demo script showing how to use the n8n Workflow Popularity Tracker
"""

import subprocess
import time
import sys
import requests
from pathlib import Path

def check_api_health():
    """Check if the API is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def start_api_server():
    """Start the FastAPI server"""
    print("🚀 Starting FastAPI server...")
    try:
        # Start the server in the background
        process = subprocess.Popen([
            sys.executable, "main.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        print("⏳ Waiting for API server to start...")
        for i in range(30):  # Wait up to 30 seconds
            if check_api_health():
                print("✅ API server is running!")
                return process
            time.sleep(1)
        
        print("❌ Failed to start API server")
        process.terminate()
        return None
        
    except Exception as e:
        print(f"❌ Error starting API server: {e}")
        return None

def generate_sample_data():
    """Generate sample data"""
    print("📊 Generating sample data...")
    try:
        result = subprocess.run([
            sys.executable, "generate_sample_data.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Sample data generated successfully!")
            return True
        else:
            print(f"❌ Error generating sample data: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error generating sample data: {e}")
        return False

def start_streamlit():
    """Start the Streamlit frontend"""
    print("🎨 Starting Streamlit frontend...")
    try:
        # Start Streamlit
        subprocess.run([
            sys.executable, "run_streamlit.py", "--app", "advanced"
        ])
    except KeyboardInterrupt:
        print("\n👋 Streamlit frontend stopped")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")

def show_api_examples():
    """Show API usage examples"""
    print("\n📚 API Usage Examples:")
    print("=" * 50)
    
    examples = [
        ("Get all workflows", "curl http://localhost:8000/workflows"),
        ("Get top 10 workflows", "curl http://localhost:8000/workflows/top/10"),
        ("Get YouTube workflows", "curl http://localhost:8000/workflows/YouTube"),
        ("Get workflow stats", "curl http://localhost:8000/workflows/stats"),
        ("Collect all data", "curl -X POST http://localhost:8000/collect/all"),
    ]
    
    for description, command in examples:
        print(f"\n{description}:")
        print(f"  {command}")
    
    print(f"\n📖 API Documentation: http://localhost:8000/docs")

def main():
    """Main demo function"""
    print("🚀 n8n Workflow Popularity Tracker - Demo")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ Please run this script from the assignment directory")
        sys.exit(1)
    
    # Check if API is already running
    if check_api_health():
        print("✅ API server is already running!")
    else:
        # Start API server
        api_process = start_api_server()
        if not api_process:
            print("❌ Failed to start API server. Exiting.")
            sys.exit(1)
    
    # Generate sample data
    if not generate_sample_data():
        print("⚠️  Warning: Could not generate sample data")
    
    # Show API examples
    show_api_examples()
    
    # Ask user what they want to do
    print("\n🎯 What would you like to do?")
    print("1. Start Streamlit frontend")
    print("2. Show API examples only")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        start_streamlit()
    elif choice == "2":
        print("\n✅ Demo completed! API server is running.")
        print("You can now use the API endpoints or start the frontend manually.")
    elif choice == "3":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice. Exiting.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"❌ Demo error: {e}")
        sys.exit(1)
