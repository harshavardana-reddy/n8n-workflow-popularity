from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

Base = declarative_base()

class YouTubeVideo(Base):
    __tablename__ = "youtube_videos"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, unique=True, index=True)
    title = Column(String)
    description = Column(Text)
    channel_title = Column(String)
    published_at = Column(DateTime)
    view_count = Column(Integer)
    like_count = Column(Integer)
    comment_count = Column(Integer)
    like_to_view_ratio = Column(Float)
    comment_to_view_ratio = Column(Float)
    search_query = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class ForumPost(Base):
    __tablename__ = "forum_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, unique=True, index=True)
    title = Column(String)
    content = Column(Text)
    author = Column(String)
    category = Column(String)
    reply_count = Column(Integer)
    like_count = Column(Integer)
    view_count = Column(Integer)
    unique_contributors = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class TrendData(Base):
    __tablename__ = "trend_data"
    
    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, index=True)
    country = Column(String)
    interest_score = Column(Float)
    date = Column(DateTime)
    created_at = Column(DateTime, default=func.now())

class N8nCommunityPost(Base):
    __tablename__ = "n8n_community_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, unique=True, index=True)
    title = Column(String)
    views = Column(Integer)
    reply_count = Column(Integer)
    like_count = Column(Integer)
    author = Column(String)
    category = Column(Integer)
    slug = Column(String)
    excerpt = Column(Text)
    created_at = Column(DateTime)
    last_posted_at = Column(DateTime)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

# Pydantic models for API responses
class PopularityMetrics(BaseModel):
    views: int
    likes: int
    comments: int
    like_to_view_ratio: float
    comment_to_view_ratio: float

class WorkflowResponse(BaseModel):
    workflow: str
    platform: str
    popularity_metrics: PopularityMetrics
    country: str
    last_updated: str

class YouTubeVideoResponse(BaseModel):
    video_id: str
    title: str
    channel_title: str
    view_count: int
    like_count: int
    comment_count: int
    like_to_view_ratio: float
    comment_to_view_ratio: float
    search_query: str
    published_at: datetime

class ForumPostResponse(BaseModel):
    post_id: int
    title: str
    author: str
    category: str
    reply_count: int
    like_count: int
    view_count: int
    unique_contributors: int

class TrendDataResponse(BaseModel):
    query: str
    country: str
    interest_score: float
    date: datetime

class PopularWorkflowResponse(BaseModel):
    workflow_name: str
    platform: str
    popularity_score: float
    metrics: dict
    last_updated: datetime

class WorkflowSummaryResponse(BaseModel):
    total_workflows: int
    top_platforms: list
    trending_queries: list
    last_updated: datetime

class N8nCommunityPostResponse(BaseModel):
    topic_id: int
    title: str
    views: int
    reply_count: int
    like_count: int
    author: str
    category: int
    slug: str
    excerpt: str
    created_at: datetime
    last_posted_at: datetime
