#!/usr/bin/env python3
"""
Automated data update script for n8n Workflow Popularity Tracker
This script can be run as a cron job or GitHub Action for daily/weekly updates
"""

import asyncio
import logging
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database import SessionLocal, create_tables
from collectors import YouTubeCollector, ForumCollector, TrendsCollector
from config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('update_data.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DataUpdater:
    def __init__(self):
        self.youtube_collector = YouTubeCollector()
        self.forum_collector = ForumCollector()
        self.trends_collector = TrendsCollector()
        
    async def update_all_data(self, youtube_max: int = 50, forum_max: int = 100):
        """Update data from all platforms"""
        db = SessionLocal()
        
        try:
            logger.info("Starting automated data update...")
            start_time = datetime.utcnow()
            
            # Update YouTube data
            if settings.youtube_api_key:
                logger.info("Updating YouTube data...")
                try:
                    youtube_data = await self.youtube_collector.collect_workflow_videos(db, youtube_max)
                    logger.info(f"Updated {len(youtube_data)} YouTube videos")
                except Exception as e:
                    logger.error(f"Error updating YouTube data: {e}")
            else:
                logger.warning("YouTube API key not configured, skipping YouTube update")
            
            # Update Forum data
            if settings.n8n_forum_api_key:
                logger.info("Updating Forum data...")
                try:
                    forum_data = await self.forum_collector.collect_workflow_posts(db, forum_max)
                    logger.info(f"Updated {len(forum_data)} forum posts")
                except Exception as e:
                    logger.error(f"Error updating Forum data: {e}")
            else:
                logger.warning("Forum API key not configured, skipping Forum update")
            
            # Update Trends data
            logger.info("Updating Google Trends data...")
            try:
                trends_data = await self.trends_collector.collect_trends_data(db)
                logger.info(f"Updated {len(trends_data)} trends data points")
            except Exception as e:
                logger.error(f"Error updating Trends data: {e}")
            
            # Commit all changes
            db.commit()
            
            end_time = datetime.utcnow()
            duration = end_time - start_time
            
            logger.info(f"Data update completed successfully in {duration}")
            
            # Log summary statistics
            self._log_summary_stats(db)
            
        except Exception as e:
            logger.error(f"Error during data update: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    def _log_summary_stats(self, db):
        """Log summary statistics after update"""
        try:
            from models import YouTubeVideo, ForumPost, TrendData
            
            youtube_count = db.query(YouTubeVideo).count()
            forum_count = db.query(ForumPost).count()
            trends_count = db.query(TrendData).count()
            
            logger.info(f"Database summary:")
            logger.info(f"  - YouTube videos: {youtube_count}")
            logger.info(f"  - Forum posts: {forum_count}")
            logger.info(f"  - Trends data points: {trends_count}")
            logger.info(f"  - Total workflows: {youtube_count + forum_count + trends_count}")
            
        except Exception as e:
            logger.error(f"Error logging summary stats: {e}")
    
    async def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old data to keep database size manageable"""
        db = SessionLocal()
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            from models import YouTubeVideo, ForumPost, TrendData
            
            # Clean up old YouTube videos
            old_youtube = db.query(YouTubeVideo).filter(
                YouTubeVideo.created_at < cutoff_date
            ).count()
            if old_youtube > 0:
                db.query(YouTubeVideo).filter(
                    YouTubeVideo.created_at < cutoff_date
                ).delete()
                logger.info(f"Cleaned up {old_youtube} old YouTube videos")
            
            # Clean up old forum posts
            old_forum = db.query(ForumPost).filter(
                ForumPost.created_at < cutoff_date
            ).count()
            if old_forum > 0:
                db.query(ForumPost).filter(
                    ForumPost.created_at < cutoff_date
                ).delete()
                logger.info(f"Cleaned up {old_forum} old forum posts")
            
            # Clean up old trends data
            old_trends = db.query(TrendData).filter(
                TrendData.created_at < cutoff_date
            ).count()
            if old_trends > 0:
                db.query(TrendData).filter(
                    TrendData.created_at < cutoff_date
                ).delete()
                logger.info(f"Cleaned up {old_trends} old trends data points")
            
            db.commit()
            logger.info("Data cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during data cleanup: {e}")
            db.rollback()
        finally:
            db.close()

def main():
    """Main function for the update script"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Update n8n workflow data")
    parser.add_argument("--youtube-max", type=int, default=50, 
                       help="Maximum YouTube videos to collect")
    parser.add_argument("--forum-max", type=int, default=100,
                       help="Maximum forum posts to collect")
    parser.add_argument("--cleanup", action="store_true",
                       help="Clean up old data")
    parser.add_argument("--cleanup-days", type=int, default=30,
                       help="Days of data to keep during cleanup")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be done without making changes")
    
    args = parser.parse_args()
    
    if args.dry_run:
        logger.info("DRY RUN MODE - No changes will be made")
        logger.info(f"Would collect up to {args.youtube_max} YouTube videos")
        logger.info(f"Would collect up to {args.forum_max} forum posts")
        if args.cleanup:
            logger.info(f"Would clean up data older than {args.cleanup_days} days")
        return
    
    # Ensure database tables exist
    create_tables()
    
    # Run the update
    updater = DataUpdater()
    
    try:
        # Update data
        asyncio.run(updater.update_all_data(args.youtube_max, args.forum_max))
        
        # Cleanup if requested
        if args.cleanup:
            asyncio.run(updater.cleanup_old_data(args.cleanup_days))
        
        logger.info("Update script completed successfully")
        
    except Exception as e:
        logger.error(f"Update script failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
