import logging
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_

from models import YouTubeVideo, ForumPost, TrendData, WorkflowResponse, PopularityMetrics

logger = logging.getLogger(__name__)

class WorkflowService:
    def __init__(self):
        self.platform_mapping = {
            'YouTube': 'YouTube',
            'Forum': 'Forum', 
            'Google': 'Google Trends'
        }
    
    def get_all_workflows(self, db: Session) -> List[WorkflowResponse]:
        """Get all workflows from all platforms in the specified JSON format"""
        workflows = []
        
        # Get YouTube workflows
        youtube_workflows = self._get_youtube_workflows(db)
        workflows.extend(youtube_workflows)
        
        # Get Forum workflows
        forum_workflows = self._get_forum_workflows(db)
        workflows.extend(forum_workflows)
        
        # Get Google Trends workflows
        trends_workflows = self._get_trends_workflows(db)
        workflows.extend(trends_workflows)
        
        return workflows
    
    def get_workflows_by_platform(self, db: Session, platform: str) -> List[WorkflowResponse]:
        """Get workflows filtered by platform"""
        platform_lower = platform.lower()
        
        if platform_lower in ['youtube', 'yt']:
            return self._get_youtube_workflows(db)
        elif platform_lower in ['forum', 'discourse']:
            return self._get_forum_workflows(db)
        elif platform_lower in ['google', 'trends', 'google trends']:
            return self._get_trends_workflows(db)
        else:
            return []
    
    def get_top_workflows(self, db: Session, n: int) -> List[WorkflowResponse]:
        """Get top N workflows ranked by engagement"""
        all_workflows = self.get_all_workflows(db)
        
        # Sort by engagement score (combination of views, likes, and comments)
        def engagement_score(workflow: WorkflowResponse) -> float:
            metrics = workflow.popularity_metrics
            # Weighted engagement score
            return (
                metrics.views * 0.4 +
                metrics.likes * 0.3 +
                metrics.comments * 0.2 +
                (metrics.like_to_view_ratio + metrics.comment_to_view_ratio) * 1000 * 0.1
            )
        
        sorted_workflows = sorted(all_workflows, key=engagement_score, reverse=True)
        return sorted_workflows[:n]
    
    def _get_youtube_workflows(self, db: Session) -> List[WorkflowResponse]:
        """Convert YouTube videos to workflow format"""
        videos = db.query(YouTubeVideo).order_by(desc(YouTubeVideo.view_count)).all()
        workflows = []
        
        for video in videos:
            # Extract workflow name from title
            workflow_name = self._extract_workflow_name(video.title)
            
            metrics = PopularityMetrics(
                views=video.view_count,
                likes=video.like_count,
                comments=video.comment_count,
                like_to_view_ratio=video.like_to_view_ratio,
                comment_to_view_ratio=video.comment_to_view_ratio
            )
            
            workflow = WorkflowResponse(
                workflow=workflow_name,
                platform="YouTube",
                popularity_metrics=metrics,
                country="US",  # Default for YouTube
                last_updated=video.updated_at.strftime("%Y-%m-%d")
            )
            workflows.append(workflow)
        
        return workflows
    
    def _get_forum_workflows(self, db: Session) -> List[WorkflowResponse]:
        """Convert forum posts to workflow format"""
        posts = db.query(ForumPost).order_by(desc(ForumPost.view_count)).all()
        workflows = []
        
        for post in posts:
            # Extract workflow name from title
            workflow_name = self._extract_workflow_name(post.title)
            
            # Convert forum metrics to match YouTube format
            metrics = PopularityMetrics(
                views=post.view_count,
                likes=post.like_count,
                comments=post.reply_count,  # Use replies as comments
                like_to_view_ratio=post.like_count / post.view_count if post.view_count > 0 else 0,
                comment_to_view_ratio=post.reply_count / post.view_count if post.view_count > 0 else 0
            )
            
            workflow = WorkflowResponse(
                workflow=workflow_name,
                platform="Forum",
                popularity_metrics=metrics,
                country="US",  # Default for forum
                last_updated=post.updated_at.strftime("%Y-%m-%d")
            )
            workflows.append(workflow)
        
        return workflows
    
    def _get_trends_workflows(self, db: Session) -> List[WorkflowResponse]:
        """Convert Google Trends data to workflow format"""
        trends = db.query(TrendData).order_by(desc(TrendData.interest_score)).all()
        workflows = []
        
        for trend in trends:
            # Extract workflow name from query
            workflow_name = self._extract_workflow_name(trend.query)
            
            # Convert trends interest score to views-like format
            # Scale interest score (0-100) to realistic view numbers
            estimated_views = int(trend.interest_score * 1000)  # Scale factor
            estimated_likes = int(estimated_views * 0.05)  # 5% like rate
            estimated_comments = int(estimated_views * 0.01)  # 1% comment rate
            
            metrics = PopularityMetrics(
                views=estimated_views,
                likes=estimated_likes,
                comments=estimated_comments,
                like_to_view_ratio=0.05,  # Standard 5% like rate
                comment_to_view_ratio=0.01  # Standard 1% comment rate
            )
            
            workflow = WorkflowResponse(
                workflow=workflow_name,
                platform="Google",
                popularity_metrics=metrics,
                country=trend.country,
                last_updated=trend.date.strftime("%Y-%m-%d")
            )
            workflows.append(workflow)
        
        return workflows
    
    def _extract_workflow_name(self, title: str) -> str:
        """Extract a clean workflow name from title/query"""
        # Remove common prefixes and suffixes
        title = title.replace("n8n", "").replace("workflow", "").replace("automation", "")
        title = title.replace("tutorial", "").replace("how to", "").replace("guide", "")
        
        # Clean up extra spaces and special characters
        title = " ".join(title.split())
        title = title.strip(" -:()[]{}")
        
        # If title is too short or empty, use a default
        if len(title) < 3:
            return "n8n Workflow"
        
        # Capitalize first letter of each word
        return " ".join(word.capitalize() for word in title.split())
    
    def get_workflow_statistics(self, db: Session) -> Dict:
        """Get statistics about workflows"""
        youtube_count = db.query(YouTubeVideo).count()
        forum_count = db.query(ForumPost).count()
        trends_count = db.query(TrendData).count()
        
        total_workflows = youtube_count + forum_count + trends_count
        
        return {
            "total_workflows": total_workflows,
            "youtube_workflows": youtube_count,
            "forum_workflows": forum_count,
            "trends_workflows": trends_count,
            "platforms": ["YouTube", "Forum", "Google"],
            "last_updated": datetime.utcnow().strftime("%Y-%m-%d")
        }
