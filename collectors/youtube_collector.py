import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlalchemy.orm import Session
from models import YouTubeVideo
from config import settings

logger = logging.getLogger(__name__)

class YouTubeCollector:
    def __init__(self):
        self.api_key = settings.youtube_api_key
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        self.search_queries = settings.youtube_search_queries
        
    async def collect_workflow_videos(self, db: Session, max_results: int = 50) -> List[Dict]:
        """Collect n8n workflow videos from YouTube"""
        collected_videos = []
        
        for query in self.search_queries:
            try:
                videos = await self._search_videos(query, max_results)
                for video_data in videos:
                    video_info = await self._get_video_details(video_data['id']['videoId'])
                    if video_info:
                        # Calculate ratios
                        view_count = video_info.get('statistics', {}).get('viewCount', 0)
                        like_count = video_info.get('statistics', {}).get('likeCount', 0)
                        comment_count = video_info.get('statistics', {}).get('commentCount', 0)
                        
                        like_to_view_ratio = float(like_count) / float(view_count) if view_count > 0 else 0
                        comment_to_view_ratio = float(comment_count) / float(view_count) if view_count > 0 else 0
                        
                        # Store in database
                        video_record = YouTubeVideo(
                            video_id=video_data['id']['videoId'],
                            title=video_info['snippet']['title'],
                            description=video_info['snippet']['description'],
                            channel_title=video_info['snippet']['channelTitle'],
                            published_at=datetime.fromisoformat(
                                video_info['snippet']['publishedAt'].replace('Z', '+00:00')
                            ),
                            view_count=int(view_count),
                            like_count=int(like_count),
                            comment_count=int(comment_count),
                            like_to_view_ratio=like_to_view_ratio,
                            comment_to_view_ratio=comment_to_view_ratio,
                            search_query=query
                        )
                        
                        # Check if video already exists
                        existing_video = db.query(YouTubeVideo).filter(
                            YouTubeVideo.video_id == video_record.video_id
                        ).first()
                        
                        if existing_video:
                            # Update existing record
                            existing_video.view_count = video_record.view_count
                            existing_video.like_count = video_record.like_count
                            existing_video.comment_count = video_record.comment_count
                            existing_video.like_to_view_ratio = video_record.like_to_view_ratio
                            existing_video.comment_to_view_ratio = video_record.comment_to_view_ratio
                            existing_video.updated_at = datetime.utcnow()
                        else:
                            db.add(video_record)
                        
                        collected_videos.append({
                            'video_id': video_record.video_id,
                            'title': video_record.title,
                            'view_count': video_record.view_count,
                            'like_count': video_record.like_count,
                            'comment_count': video_record.comment_count,
                            'like_to_view_ratio': video_record.like_to_view_ratio,
                            'comment_to_view_ratio': video_record.comment_to_view_ratio,
                            'search_query': query
                        })
                        
                db.commit()
                logger.info(f"Collected {len(videos)} videos for query: {query}")
                
            except HttpError as e:
                logger.error(f"YouTube API error for query '{query}': {e}")
            except Exception as e:
                logger.error(f"Error collecting videos for query '{query}': {e}")
                
        return collected_videos
    
    async def _search_videos(self, query: str, max_results: int) -> List[Dict]:
        """Search for videos using YouTube Data API"""
        try:
            search_response = self.youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=max_results,
                type='video',
                order='relevance',
                publishedAfter=(datetime.now() - timedelta(days=365)).isoformat() + 'Z'
            ).execute()
            
            return search_response.get('items', [])
        except Exception as e:
            logger.error(f"Error searching videos for query '{query}': {e}")
            return []
    
    async def _get_video_details(self, video_id: str) -> Optional[Dict]:
        """Get detailed information about a specific video"""
        try:
            video_response = self.youtube.videos().list(
                part='snippet,statistics',
                id=video_id
            ).execute()
            
            items = video_response.get('items', [])
            return items[0] if items else None
        except Exception as e:
            logger.error(f"Error getting video details for ID '{video_id}': {e}")
            return None
    
    def get_popular_videos(self, db: Session, limit: int = 10) -> List[Dict]:
        """Get most popular n8n workflow videos"""
        videos = db.query(YouTubeVideo).order_by(
            YouTubeVideo.view_count.desc()
        ).limit(limit).all()
        
        return [
            {
                'video_id': video.video_id,
                'title': video.title,
                'channel_title': video.channel_title,
                'view_count': video.view_count,
                'like_count': video.like_count,
                'comment_count': video.comment_count,
                'like_to_view_ratio': video.like_to_view_ratio,
                'comment_to_view_ratio': video.comment_to_view_ratio,
                'published_at': video.published_at,
                'search_query': video.search_query
            }
            for video in videos
        ]
    
    def get_high_engagement_videos(self, db: Session, limit: int = 10) -> List[Dict]:
        """Get videos with highest engagement ratios"""
        videos = db.query(YouTubeVideo).order_by(
            YouTubeVideo.like_to_view_ratio.desc()
        ).limit(limit).all()
        
        return [
            {
                'video_id': video.video_id,
                'title': video.title,
                'channel_title': video.channel_title,
                'view_count': video.view_count,
                'like_count': video.like_count,
                'comment_count': video.comment_count,
                'like_to_view_ratio': video.like_to_view_ratio,
                'comment_to_view_ratio': video.comment_to_view_ratio,
                'published_at': video.published_at,
                'search_query': video.search_query
            }
            for video in videos
        ]
