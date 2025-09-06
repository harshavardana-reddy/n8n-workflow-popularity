"""
Vercel serverless function entry point for n8n Workflow Popularity Tracker
"""
import sys
import os
from pathlib import Path

# Add the parent directory to Python path so we can import our modules
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import the FastAPI app from main.py
from main import app

# Export the app for Vercel
handler = app
