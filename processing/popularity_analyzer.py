import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from models import YouTubeVideo, ForumPost, TrendData

logger = logging.getLogger(__name__)

class PopularityAnalyzer:
    def __init__(self):
        self.weights = {
            'youtube_views': 0.3,
            'youtube_engagement': 0.2,
            'forum_activity': 0.2,
            'trends_interest': 0.3
        }
    
    def calculate_workflow_popularity(self, db: Session, workflow_name: str) -> Dict:
        """Calculate overall popularity score for a specific workflow"""
        try:
            # Get data from all sources
            youtube_score = self._calculate_youtube_score(db, workflow_name)
            forum_score = self._calculate_forum_score(db, workflow_name)
            trends_score = self._calculate_trends_score(db, workflow_name)
            
            # Calculate weighted popularity score
            popularity_score = (
                youtube_score * self.weights['youtube_views'] +
                youtube_score * self.weights['youtube_engagement'] +
                forum_score * self.weights['forum_activity'] +
                trends_score * self.weights['trends_interest']
            )
            
            return {
                'workflow_name': workflow_name,
                'popularity_score': round(popularity_score, 2),
                'youtube_score': round(youtube_score, 2),
                'forum_score': round(forum_score, 2),
                'trends_score': round(trends_score, 2),
                'last_updated': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error calculating popularity for workflow '{workflow_name}': {e}")
            return {'error': str(e)}
    
    def _calculate_youtube_score(self, db: Session, workflow_name: str) -> float:
        """Calculate YouTube popularity score for a workflow"""
        try:
            # Search for videos containing the workflow name
            videos = db.query(YouTubeVideo).filter(
                YouTubeVideo.title.ilike(f'%{workflow_name}%')
            ).all()
            
            if not videos:
                return 0.0
            
            # Calculate score based on views and engagement
            total_views = sum(video.view_count for video in videos)
            avg_engagement = sum(
                (video.like_to_view_ratio + video.comment_to_view_ratio) / 2
                for video in videos
            ) / len(videos)
            
            # Normalize scores (views in millions, engagement as percentage)
            views_score = min(total_views / 1000000, 100)  # Cap at 100M views
            engagement_score = avg_engagement * 100  # Convert to percentage
            
            return (views_score + engagement_score) / 2
            
        except Exception as e:
            logger.error(f"Error calculating YouTube score: {e}")
            return 0.0
    
    def _calculate_forum_score(self, db: Session, workflow_name: str) -> float:
        """Calculate forum popularity score for a workflow"""
        try:
            # Search for posts containing the workflow name
            posts = db.query(ForumPost).filter(
                ForumPost.title.ilike(f'%{workflow_name}%')
            ).all()
            
            if not posts:
                return 0.0
            
            # Calculate score based on activity and engagement
            total_views = sum(post.view_count for post in posts)
            total_replies = sum(post.reply_count for post in posts)
            total_likes = sum(post.like_count for post in posts)
            
            # Normalize scores
            views_score = min(total_views / 10000, 100)  # Cap at 10K views
            activity_score = min((total_replies + total_likes) / 100, 100)  # Cap at 100 interactions
            
            return (views_score + activity_score) / 2
            
        except Exception as e:
            logger.error(f"Error calculating forum score: {e}")
            return 0.0
    
    def _calculate_trends_score(self, db: Session, workflow_name: str) -> float:
        """Calculate trends popularity score for a workflow"""
        try:
            # Search for trend data containing the workflow name
            trends = db.query(TrendData).filter(
                TrendData.query.ilike(f'%{workflow_name}%')
            ).all()
            
            if not trends:
                return 0.0
            
            # Calculate average interest score
            avg_interest = sum(trend.interest_score for trend in trends) / len(trends)
            max_interest = max(trend.interest_score for trend in trends)
            
            # Use both average and peak interest
            return (avg_interest + max_interest) / 2
            
        except Exception as e:
            logger.error(f"Error calculating trends score: {e}")
            return 0.0
    
    def get_top_workflows(self, db: Session, limit: int = 10) -> List[Dict]:
        """Get top popular workflows across all platforms"""
        try:
            # Get unique workflow names from all sources
            workflow_names = set()
            
            # From YouTube titles
            youtube_workflows = db.query(YouTubeVideo.title).filter(
                YouTubeVideo.title.ilike('%n8n%')
            ).all()
            for title in youtube_workflows:
                # Extract potential workflow names (simplified)
                words = title[0].lower().split()
                for word in words:
                    if 'n8n' in word or 'workflow' in word or 'automation' in word:
                        workflow_names.add(word)
            
            # From forum titles
            forum_workflows = db.query(ForumPost.title).filter(
                ForumPost.title.ilike('%n8n%')
            ).all()
            for title in forum_workflows:
                words = title[0].lower().split()
                for word in words:
                    if 'n8n' in word or 'workflow' in word or 'automation' in word:
                        workflow_names.add(word)
            
            # From trends queries
            trends_workflows = db.query(TrendData.query).all()
            for query in trends_workflows:
                words = query[0].lower().split()
                for word in words:
                    if 'n8n' in word or 'workflow' in word or 'automation' in word:
                        workflow_names.add(word)
            
            # Calculate popularity for each workflow
            workflow_scores = []
            for workflow_name in workflow_names:
                if len(workflow_name) > 3:  # Filter out very short names
                    popularity = self.calculate_workflow_popularity(db, workflow_name)
                    if 'error' not in popularity:
                        workflow_scores.append(popularity)
            
            # Sort by popularity score and return top results
            workflow_scores.sort(key=lambda x: x['popularity_score'], reverse=True)
            return workflow_scores[:limit]
            
        except Exception as e:
            logger.error(f"Error getting top workflows: {e}")
            return []
    
    def get_platform_summary(self, db: Session) -> Dict:
        """Get summary statistics for all platforms"""
        try:
            # YouTube statistics
            youtube_stats = db.query(
                func.count(YouTubeVideo.id).label('total_videos'),
                func.sum(YouTubeVideo.view_count).label('total_views'),
                func.avg(YouTubeVideo.like_to_view_ratio).label('avg_engagement')
            ).first()
            
            # Forum statistics
            forum_stats = db.query(
                func.count(ForumPost.id).label('total_posts'),
                func.sum(ForumPost.view_count).label('total_views'),
                func.sum(ForumPost.reply_count).label('total_replies')
            ).first()
            
            # Trends statistics
            trends_stats = db.query(
                func.count(TrendData.id).label('total_data_points'),
                func.avg(TrendData.interest_score).label('avg_interest'),
                func.max(TrendData.interest_score).label('max_interest')
            ).first()
            
            return {
                'youtube': {
                    'total_videos': youtube_stats.total_videos or 0,
                    'total_views': youtube_stats.total_views or 0,
                    'avg_engagement': round(youtube_stats.avg_engagement or 0, 4)
                },
                'forum': {
                    'total_posts': forum_stats.total_posts or 0,
                    'total_views': forum_stats.total_views or 0,
                    'total_replies': forum_stats.total_replies or 0
                },
                'trends': {
                    'total_data_points': trends_stats.total_data_points or 0,
                    'avg_interest': round(trends_stats.avg_interest or 0, 2),
                    'max_interest': trends_stats.max_interest or 0
                },
                'last_updated': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error getting platform summary: {e}")
            return {'error': str(e)}
    
    def get_trending_workflows(self, db: Session, days: int = 7, limit: int = 10) -> List[Dict]:
        """Get trending workflows based on recent activity"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get recent YouTube videos
            recent_youtube = db.query(YouTubeVideo).filter(
                YouTubeVideo.created_at >= cutoff_date
            ).order_by(desc(YouTubeVideo.view_count)).limit(limit).all()
            
            # Get recent forum posts
            recent_forum = db.query(ForumPost).filter(
                ForumPost.created_at >= cutoff_date
            ).order_by(desc(ForumPost.view_count)).limit(limit).all()
            
            # Get recent trends
            recent_trends = db.query(TrendData).filter(
                TrendData.date >= cutoff_date
            ).order_by(desc(TrendData.interest_score)).limit(limit).all()
            
            trending_workflows = []
            
            # Process YouTube videos
            for video in recent_youtube:
                trending_workflows.append({
                    'workflow_name': video.title[:50] + '...' if len(video.title) > 50 else video.title,
                    'platform': 'YouTube',
                    'popularity_score': video.view_count / 1000,  # Normalize
                    'metrics': {
                        'views': video.view_count,
                        'likes': video.like_count,
                        'comments': video.comment_count,
                        'engagement_ratio': video.like_to_view_ratio
                    },
                    'last_updated': video.updated_at
                })
            
            # Process forum posts
            for post in recent_forum:
                trending_workflows.append({
                    'workflow_name': post.title[:50] + '...' if len(post.title) > 50 else post.title,
                    'platform': 'Forum',
                    'popularity_score': (post.view_count + post.reply_count) / 100,  # Normalize
                    'metrics': {
                        'views': post.view_count,
                        'replies': post.reply_count,
                        'likes': post.like_count,
                        'contributors': post.unique_contributors
                    },
                    'last_updated': post.updated_at
                })
            
            # Process trends
            for trend in recent_trends:
                trending_workflows.append({
                    'workflow_name': trend.query,
                    'platform': 'Google Trends',
                    'popularity_score': trend.interest_score,
                    'metrics': {
                        'interest_score': trend.interest_score,
                        'country': trend.country,
                        'date': trend.date
                    },
                    'last_updated': trend.date
                })
            
            # Sort by popularity score
            trending_workflows.sort(key=lambda x: x['popularity_score'], reverse=True)
            return trending_workflows[:limit]
            
        except Exception as e:
            logger.error(f"Error getting trending workflows: {e}")
            return []
