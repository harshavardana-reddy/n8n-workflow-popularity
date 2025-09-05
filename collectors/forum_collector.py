import asyncio
import logging
import httpx
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from models import ForumPost
from config import settings

logger = logging.getLogger(__name__)

class ForumCollector:
    def __init__(self):
        self.base_url = settings.n8n_forum_base_url
        self.api_key = settings.n8n_forum_api_key
        self.headers = {
            'Api-Key': self.api_key,
            'Api-Username': 'system',
            'Content-Type': 'application/json'
        }
        
    async def collect_workflow_posts(self, db: Session, max_results: int = 100) -> List[Dict]:
        """Collect n8n workflow posts from the forum"""
        collected_posts = []
        
        try:
            # Search for workflow-related posts
            posts = await self._search_workflow_posts(max_results)
            
            for post_data in posts:
                post_details = await self._get_post_details(post_data['id'])
                if post_details:
                    # Calculate unique contributors (simplified - using reply count as proxy)
                    unique_contributors = post_details.get('reply_count', 0)
                    
                    # Store in database
                    post_record = ForumPost(
                        post_id=post_data['id'],
                        title=post_data.get('title', ''),
                        content=post_data.get('cooked', ''),
                        author=post_data.get('username', ''),
                        category=post_data.get('category_name', ''),
                        reply_count=post_details.get('reply_count', 0),
                        like_count=post_details.get('like_count', 0),
                        view_count=post_details.get('views', 0),
                        unique_contributors=unique_contributors
                    )
                    
                    # Check if post already exists
                    existing_post = db.query(ForumPost).filter(
                        ForumPost.post_id == post_record.post_id
                    ).first()
                    
                    if existing_post:
                        # Update existing record
                        existing_post.reply_count = post_record.reply_count
                        existing_post.like_count = post_record.like_count
                        existing_post.view_count = post_record.view_count
                        existing_post.unique_contributors = post_record.unique_contributors
                        existing_post.updated_at = datetime.utcnow()
                    else:
                        db.add(post_record)
                    
                    collected_posts.append({
                        'post_id': post_record.post_id,
                        'title': post_record.title,
                        'author': post_record.author,
                        'category': post_record.category,
                        'reply_count': post_record.reply_count,
                        'like_count': post_record.like_count,
                        'view_count': post_record.view_count,
                        'unique_contributors': post_record.unique_contributors
                    })
            
            db.commit()
            logger.info(f"Collected {len(collected_posts)} forum posts")
            
        except Exception as e:
            logger.error(f"Error collecting forum posts: {e}")
            
        return collected_posts
    
    async def _search_workflow_posts(self, max_results: int) -> List[Dict]:
        """Search for workflow-related posts in the forum"""
        try:
            async with httpx.AsyncClient() as client:
                # Search for posts with workflow-related keywords
                search_terms = ['workflow', 'automation', 'integration', 'n8n workflow']
                all_posts = []
                
                for term in search_terms:
                    response = await client.get(
                        f"{self.base_url}/search.json",
                        headers=self.headers,
                        params={
                            'q': term,
                            'type': 'topic',
                            'order': 'latest',
                            'page': 0
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        posts = data.get('topics', [])
                        all_posts.extend(posts[:max_results // len(search_terms)])
                
                # Remove duplicates based on post ID
                unique_posts = {post['id']: post for post in all_posts}.values()
                return list(unique_posts)[:max_results]
                
        except Exception as e:
            logger.error(f"Error searching forum posts: {e}")
            return []
    
    async def _get_post_details(self, post_id: int) -> Optional[Dict]:
        """Get detailed information about a specific post"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/t/{post_id}.json",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Failed to get post details for ID {post_id}: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting post details for ID {post_id}: {e}")
            return None
    
    def get_popular_posts(self, db: Session, limit: int = 10) -> List[Dict]:
        """Get most popular forum posts"""
        posts = db.query(ForumPost).order_by(
            ForumPost.view_count.desc()
        ).limit(limit).all()
        
        return [
            {
                'post_id': post.post_id,
                'title': post.title,
                'author': post.author,
                'category': post.category,
                'reply_count': post.reply_count,
                'like_count': post.like_count,
                'view_count': post.view_count,
                'unique_contributors': post.unique_contributors
            }
            for post in posts
        ]
    
    def get_high_engagement_posts(self, db: Session, limit: int = 10) -> List[Dict]:
        """Get posts with highest engagement (replies + likes)"""
        posts = db.query(ForumPost).order_by(
            (ForumPost.reply_count + ForumPost.like_count).desc()
        ).limit(limit).all()
        
        return [
            {
                'post_id': post.post_id,
                'title': post.title,
                'author': post.author,
                'category': post.category,
                'reply_count': post.reply_count,
                'like_count': post.like_count,
                'view_count': post.view_count,
                'unique_contributors': post.unique_contributors
            }
            for post in posts
        ]
    
    def get_workflow_categories(self, db: Session) -> List[Dict]:
        """Get posts grouped by category"""
        from sqlalchemy import func
        
        categories = db.query(
            ForumPost.category,
            func.count(ForumPost.id).label('post_count'),
            func.sum(ForumPost.reply_count).label('total_replies'),
            func.sum(ForumPost.like_count).label('total_likes'),
            func.sum(ForumPost.view_count).label('total_views')
        ).group_by(ForumPost.category).all()
        
        return [
            {
                'category': cat.category,
                'post_count': cat.post_count,
                'total_replies': cat.total_replies or 0,
                'total_likes': cat.total_likes or 0,
                'total_views': cat.total_views or 0
            }
            for cat in categories
        ]
