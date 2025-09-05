#!/usr/bin/env python3
"""
Run script for n8n Workflow Popularity Tracker
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.11+"""
    if sys.version_info < (3, 11):
        print("Error: Python 3.11+ is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

def check_env_file():
    """Check if .env file exists"""
    if not Path(".env").exists():
        print("Warning: .env file not found")
        print("Please copy env_example.txt to .env and configure your API keys")
        print("cp env_example.txt .env")
        return False
    return True

def run_server(host="0.0.0.0", port=8000, reload=True):
    """Run the FastAPI server"""
    print(f"Starting server on {host}:{port}")
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", host, 
            "--port", str(port),
            "--reload" if reload else "--no-reload"
        ])
    except KeyboardInterrupt:
        print("\nServer stopped")

def run_setup():
    """Run the setup script"""
    print("Running setup...")
    try:
        subprocess.check_call([sys.executable, "setup.py"])
    except subprocess.CalledProcessError as e:
        print(f"Error during setup: {e}")
        sys.exit(1)

def run_tests():
    """Run the test script"""
    print("Running tests...")
    try:
        subprocess.check_call([sys.executable, "test_api.py"])
    except subprocess.CalledProcessError as e:
        print(f"Error during tests: {e}")
        sys.exit(1)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="n8n Workflow Popularity Tracker")
    parser.add_argument("command", choices=["install", "setup", "run", "test"], 
                       help="Command to run")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")
    
    args = parser.parse_args()
    
    # Check Python version
    check_python_version()
    
    if args.command == "install":
        install_dependencies()
    
    elif args.command == "setup":
        if not check_env_file():
            print("Please configure your .env file first")
            sys.exit(1)
        run_setup()
    
    elif args.command == "run":
        if not check_env_file():
            print("Warning: .env file not found. Some features may not work.")
        run_server(args.host, args.port, not args.no_reload)
    
    elif args.command == "test":
        run_tests()

if __name__ == "__main__":
    main()
