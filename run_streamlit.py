#!/usr/bin/env python3
"""
Launcher script for Streamlit frontend
"""

import subprocess
import sys
import argparse
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import streamlit
        import plotly
        import pandas
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def run_streamlit_app(app_file: str, port: int = 8501, host: str = "localhost"):
    """Run the Streamlit app"""
    if not check_dependencies():
        sys.exit(1)
    
    # Check if app file exists
    if not Path(app_file).exists():
        print(f"Error: App file '{app_file}' not found")
        sys.exit(1)
    
    # Run Streamlit
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        app_file,
        "--server.port", str(port),
        "--server.address", host,
        "--server.headless", "true"
    ]
    
    print(f"Starting Streamlit app: {app_file}")
    print(f"Server will be available at: http://{host}:{port}")
    print("Press Ctrl+C to stop the server")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nServer stopped")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Run Streamlit frontend for n8n Workflow Tracker")
    parser.add_argument(
        "--app",
        choices=["basic", "advanced"],
        default="basic",
        help="Choose which Streamlit app to run"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8501,
        help="Port to run the app on"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host to bind the app to"
    )
    
    args = parser.parse_args()
    
    # Map app choice to file
    app_files = {
        "basic": "streamlit_app.py",
        "advanced": "streamlit_advanced.py"
    }
    
    app_file = app_files[args.app]
    
    print(f"n8n Workflow Popularity Tracker - Streamlit Frontend")
    print(f"App: {args.app} ({app_file})")
    print(f"Port: {args.port}")
    print(f"Host: {args.host}")
    print("-" * 50)
    
    run_streamlit_app(app_file, args.port, args.host)

if __name__ == "__main__":
    main()
