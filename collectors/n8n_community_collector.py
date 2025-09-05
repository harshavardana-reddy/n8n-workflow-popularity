import asyncio
import logging
import requests
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from models import N8nCommunityPost
from config import settings

logger = logging.getLogger(__name__)

class N8nCommunityCollector:
    def __init__(self):
        self.base_url = "https://community.n8n.io"
        
    async def collect_workflow_posts(self, db: Session, max_results: int = 100) -> List[Dict]:
        """Collect n8n workflow posts from the community forum"""
        collected_posts = []
        
        try:
            # Use the working API endpoint
            url = f"{self.base_url}/latest.json"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                topics = data.get("topic_list", {}).get("topics", [])
                
                for topic in topics[:max_results]:
                    # Extract topic information
                    post_record = N8nCommunityPost(
                        topic_id=topic.get("id"),
                        title=topic.get("title", ""),
                        views=topic.get("views", 0),
                        reply_count=topic.get("reply_count", 0),
                        like_count=topic.get("like_count", 0),
                        created_at=datetime.fromisoformat(
                            topic.get("created_at", "").replace("Z", "+00:00")
                        ) if topic.get("created_at") else datetime.utcnow(),
                        last_posted_at=datetime.fromisoformat(
                            topic.get("last_posted_at", "").replace("Z", "+00:00")
                        ) if topic.get("last_posted_at") else datetime.utcnow(),
                        author=topic.get("last_poster_username", ""),
                        category=topic.get("category_id", 0),
                        slug=topic.get("slug", ""),
                        excerpt=topic.get("excerpt", "")
                    )
                    
                    # Check if topic already exists
                    existing_topic = db.query(N8nCommunityPost).filter(
                        N8nCommunityPost.topic_id == post_record.topic_id
                    ).first()
                    
                    if existing_topic:
                        # Update existing record
                        existing_topic.views = post_record.views
                        existing_topic.reply_count = post_record.reply_count
                        existing_topic.like_count = post_record.like_count
                        existing_topic.last_posted_at = post_record.last_posted_at
                        existing_topic.updated_at = datetime.utcnow()
                    else:
                        db.add(post_record)
                    
                    collected_posts.append({
                        'topic_id': post_record.topic_id,
                        'title': post_record.title,
                        'views': post_record.views,
                        'reply_count': post_record.reply_count,
                        'like_count': post_record.like_count,
                        'author': post_record.author,
                        'category': post_record.category,
                        'created_at': post_record.created_at,
                        'last_posted_at': post_record.last_posted_at,
                        'slug': post_record.slug,
                        'excerpt': post_record.excerpt
                    })
                
                db.commit()
                logger.info(f"Collected {len(collected_posts)} n8n community posts")
                
            else:
                logger.error(f"Failed to fetch n8n community data: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error collecting n8n community posts: {e}")
            
        return collected_posts
    
    def get_popular_posts(self, db: Session, limit: int = 10) -> List[Dict]:
        """Get most popular n8n community posts by views"""
        posts = db.query(N8nCommunityPost).order_by(
            N8nCommunityPost.views.desc()
        ).limit(limit).all()
        
        return [
            {
                'topic_id': post.topic_id,
                'title': post.title,
                'views': post.views,
                'reply_count': post.reply_count,
                'like_count': post.like_count,
                'author': post.author,
                'category': post.category,
                'created_at': post.created_at,
                'last_posted_at': post.last_posted_at,
                'slug': post.slug,
                'excerpt': post.excerpt
            }
            for post in posts
        ]
    
    def get_high_engagement_posts(self, db: Session, limit: int = 10) -> List[Dict]:
        """Get posts with highest engagement (replies + likes)"""
        posts = db.query(N8nCommunityPost).order_by(
            (N8nCommunityPost.reply_count + N8nCommunityPost.like_count).desc()
        ).limit(limit).all()
        
        return [
            {
                'topic_id': post.topic_id,
                'title': post.title,
                'views': post.views,
                'reply_count': post.reply_count,
                'like_count': post.like_count,
                'author': post.author,
                'category': post.category,
                'created_at': post.created_at,
                'last_posted_at': post.last_posted_at,
                'slug': post.slug,
                'excerpt': post.excerpt
            }
            for post in posts
        ]
    
    def get_recent_posts(self, db: Session, limit: int = 10) -> List[Dict]:
        """Get most recently posted topics"""
        posts = db.query(N8nCommunityPost).order_by(
            N8nCommunityPost.last_posted_at.desc()
        ).limit(limit).all()
        
        return [
            {
                'topic_id': post.topic_id,
                'title': post.title,
                'views': post.views,
                'reply_count': post.reply_count,
                'like_count': post.like_count,
                'author': post.author,
                'category': post.category,
                'created_at': post.created_at,
                'last_posted_at': post.last_posted_at,
                'slug': post.slug,
                'excerpt': post.excerpt
            }
            for post in posts
        ]
    
    def get_posts_by_category(self, db: Session, category_id: int, limit: int = 10) -> List[Dict]:
        """Get posts filtered by category"""
        posts = db.query(N8nCommunityPost).filter(
            N8nCommunityPost.category == category_id
        ).order_by(N8nCommunityPost.views.desc()).limit(limit).all()
        
        return [
            {
                'topic_id': post.topic_id,
                'title': post.title,
                'views': post.views,
                'reply_count': post.reply_count,
                'like_count': post.like_count,
                'author': post.author,
                'category': post.category,
                'created_at': post.created_at,
                'last_posted_at': post.last_posted_at,
                'slug': post.slug,
                'excerpt': post.excerpt
            }
            for post in posts
        ]
