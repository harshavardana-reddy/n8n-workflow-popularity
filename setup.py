#!/usr/bin/env python3
"""
Setup script for n8n Workflow Popularity Tracker
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

from database import create_tables, SessionLocal
from collectors import YouTubeCollector, ForumCollector, TrendsCollector
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if required environment variables are set"""
    required_vars = ['YOUTUBE_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables in your .env file")
        return False
    
    return True

def setup_database():
    """Create database tables"""
    try:
        create_tables()
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        return False

async def collect_initial_data():
    """Collect initial data from all platforms"""
    db = SessionLocal()
    
    try:
        logger.info("Starting initial data collection...")
        
        # Collect YouTube data
        if settings.youtube_api_key:
            logger.info("Collecting YouTube data...")
            youtube_collector = YouTubeCollector()
            await youtube_collector.collect_workflow_videos(db, max_results=50)
            logger.info("YouTube data collection completed")
        else:
            logger.warning("YouTube API key not provided, skipping YouTube data collection")
        
        # Collect forum data
        if settings.n8n_forum_api_key:
            logger.info("Collecting forum data...")
            forum_collector = ForumCollector()
            await forum_collector.collect_workflow_posts(db, max_results=100)
            logger.info("Forum data collection completed")
        else:
            logger.warning("Forum API key not provided, skipping forum data collection")
        
        # Collect trends data
        logger.info("Collecting trends data...")
        trends_collector = TrendsCollector()
        await trends_collector.collect_trends_data(db)
        logger.info("Trends data collection completed")
        
        logger.info("Initial data collection completed successfully")
        
    except Exception as e:
        logger.error(f"Error during data collection: {e}")
    finally:
        db.close()

def main():
    """Main setup function"""
    logger.info("Setting up n8n Workflow Popularity Tracker...")
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Setup database
    if not setup_database():
        sys.exit(1)
    
    # Collect initial data
    try:
        asyncio.run(collect_initial_data())
    except KeyboardInterrupt:
        logger.info("Setup interrupted by user")
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)
    
    logger.info("Setup completed successfully!")
    logger.info("You can now start the API server with: python main.py")

if __name__ == "__main__":
    main()
