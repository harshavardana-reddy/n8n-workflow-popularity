import asyncio
import logging
from contextlib import asynccontextmanager
from typing import List, Dict, Optional
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from config import settings
from database import get_db, create_tables
from models import (
    YouTubeVideoResponse, ForumPostResponse, TrendDataResponse,
    PopularWorkflowResponse, WorkflowSummaryResponse, WorkflowResponse
)
from collectors import YouTubeCollector, ForumCollector
try:
    from collectors import TrendsCollector
    TRENDS_AVAILABLE = True
except Exception as e:
    print(f"Warning: Trends collector not available: {e}")
    TRENDS_AVAILABLE = False
from processing import PopularityAnalyzer
from services import WorkflowService

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

# Initialize collectors, analyzer, and services
youtube_collector = YouTubeCollector()
forum_collector = ForumCollector()
if TRENDS_AVAILABLE:
    trends_collector = TrendsCollector()
else:
    trends_collector = None
popularity_analyzer = PopularityAnalyzer()
workflow_service = WorkflowService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting n8n Workflow Popularity Tracker API")
    create_tables()
    logger.info("Database tables created")
    yield
    # Shutdown
    logger.info("Shutting down API")

app = FastAPI(
    title=settings.app_name,
    description="A production-ready system that identifies the most popular n8n workflows across multiple platforms",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_model=Dict)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "n8n Workflow Popularity Tracker API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow()
    }

@app.get("/health", response_model=Dict)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }

# Main Workflow Endpoints (as per requirements)
@app.get("/workflows", response_model=List[WorkflowResponse])
async def get_all_workflows(db: Session = Depends(get_db)):
    """Get all workflows from all platforms in the specified JSON format"""
    try:
        workflows = workflow_service.get_all_workflows(db)
        return workflows
    except Exception as e:
        logger.error(f"Error getting all workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/workflows/{platform}", response_model=List[WorkflowResponse])
async def get_workflows_by_platform(
    platform: str,
    db: Session = Depends(get_db)
):
    """Get workflows filtered by platform (YouTube, Forum, Google)"""
    try:
        workflows = workflow_service.get_workflows_by_platform(db, platform)
        return workflows
    except Exception as e:
        logger.error(f"Error getting workflows for platform '{platform}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/workflows/top/{n}", response_model=List[WorkflowResponse])
async def get_top_workflows(
    n: int,
    db: Session = Depends(get_db)
):
    """Get top N workflows ranked by engagement"""
    try:
        if n <= 0:
            raise HTTPException(status_code=400, detail="n must be a positive integer")
        if n > 100:
            raise HTTPException(status_code=400, detail="n cannot exceed 100")
        
        workflows = workflow_service.get_top_workflows(db, n)
        return workflows
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting top {n} workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/workflows/stats", response_model=Dict)
async def get_workflow_statistics(db: Session = Depends(get_db)):
    """Get workflow statistics"""
    try:
        stats = workflow_service.get_workflow_statistics(db)
        return stats
    except Exception as e:
        logger.error(f"Error getting workflow statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Data Collection Endpoints
@app.post("/collect/youtube", response_model=Dict)
async def collect_youtube_data(
    background_tasks: BackgroundTasks,
    max_results: int = 50,
    db: Session = Depends(get_db)
):
    """Collect YouTube data for n8n workflows"""
    try:
        background_tasks.add_task(
            youtube_collector.collect_workflow_videos,
            db, max_results
        )
        return {
            "message": "YouTube data collection started",
            "max_results": max_results,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error starting YouTube collection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/collect/forum", response_model=Dict)
async def collect_forum_data(
    background_tasks: BackgroundTasks,
    max_results: int = 100,
    db: Session = Depends(get_db)
):
    """Collect forum data for n8n workflows"""
    try:
        background_tasks.add_task(
            forum_collector.collect_workflow_posts,
            db, max_results
        )
        return {
            "message": "Forum data collection started",
            "max_results": max_results,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error starting forum collection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/collect/trends", response_model=Dict)
async def collect_trends_data(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Collect Google Trends data for n8n workflows"""
    if not TRENDS_AVAILABLE or trends_collector is None:
        return {
            "message": "Trends collector not available",
            "timestamp": datetime.utcnow()
        }
    try:
        background_tasks.add_task(
            trends_collector.collect_trends_data,
            db
        )
        return {
            "message": "Trends data collection started",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error starting trends collection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/collect/all", response_model=Dict)
async def collect_all_data(
    background_tasks: BackgroundTasks,
    youtube_max: int = 50,
    forum_max: int = 100,
    db: Session = Depends(get_db)
):
    """Collect data from all platforms"""
    try:
        background_tasks.add_task(
            youtube_collector.collect_workflow_videos,
            db, youtube_max
        )
        background_tasks.add_task(
            forum_collector.collect_workflow_posts,
            db, forum_max
        )
        if TRENDS_AVAILABLE and trends_collector is not None:
            background_tasks.add_task(
                trends_collector.collect_trends_data,
                db
            )
        return {
            "message": "Data collection started for all platforms",
            "youtube_max": youtube_max,
            "forum_max": forum_max,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error starting data collection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# YouTube Endpoints
@app.get("/youtube/popular", response_model=List[YouTubeVideoResponse])
async def get_popular_youtube_videos(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get most popular YouTube videos"""
    try:
        videos = youtube_collector.get_popular_videos(db, limit)
        return videos
    except Exception as e:
        logger.error(f"Error getting popular YouTube videos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/youtube/engagement", response_model=List[YouTubeVideoResponse])
async def get_high_engagement_youtube_videos(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get YouTube videos with highest engagement ratios"""
    try:
        videos = youtube_collector.get_high_engagement_videos(db, limit)
        return videos
    except Exception as e:
        logger.error(f"Error getting high engagement YouTube videos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Forum Endpoints
@app.get("/forum/popular", response_model=List[ForumPostResponse])
async def get_popular_forum_posts(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get most popular forum posts"""
    try:
        posts = forum_collector.get_popular_posts(db, limit)
        return posts
    except Exception as e:
        logger.error(f"Error getting popular forum posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/forum/engagement", response_model=List[ForumPostResponse])
async def get_high_engagement_forum_posts(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get forum posts with highest engagement"""
    try:
        posts = forum_collector.get_high_engagement_posts(db, limit)
        return posts
    except Exception as e:
        logger.error(f"Error getting high engagement forum posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/forum/categories", response_model=List[Dict])
async def get_forum_categories(db: Session = Depends(get_db)):
    """Get forum posts grouped by category"""
    try:
        categories = forum_collector.get_workflow_categories(db)
        return categories
    except Exception as e:
        logger.error(f"Error getting forum categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Trends Endpoints
@app.get("/trends/popular", response_model=List[Dict])
async def get_trending_queries(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get trending queries from Google Trends"""
    try:
        trends = trends_collector.get_trending_queries(db, limit)
        return trends
    except Exception as e:
        logger.error(f"Error getting trending queries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/trends/countries", response_model=List[Dict])
async def get_country_trends(db: Session = Depends(get_db)):
    """Get trend data grouped by country"""
    try:
        trends = trends_collector.get_country_trends(db)
        return trends
    except Exception as e:
        logger.error(f"Error getting country trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/trends/recent", response_model=List[TrendDataResponse])
async def get_recent_trends(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get recent trend data"""
    try:
        trends = trends_collector.get_recent_trends(db, days)
        return trends
    except Exception as e:
        logger.error(f"Error getting recent trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/trends/analysis/{query}", response_model=Dict)
async def get_trend_analysis(
    query: str,
    db: Session = Depends(get_db)
):
    """Get detailed trend analysis for a specific query"""
    try:
        analysis = trends_collector.get_trend_analysis(db, query)
        return analysis
    except Exception as e:
        logger.error(f"Error getting trend analysis for '{query}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Popularity Analysis Endpoints
@app.get("/popularity/top", response_model=List[PopularWorkflowResponse])
async def get_top_workflows(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get top popular workflows across all platforms"""
    try:
        workflows = popularity_analyzer.get_top_workflows(db, limit)
        return workflows
    except Exception as e:
        logger.error(f"Error getting top workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/popularity/trending", response_model=List[PopularWorkflowResponse])
async def get_trending_workflows(
    days: int = 7,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get trending workflows based on recent activity"""
    try:
        workflows = popularity_analyzer.get_trending_workflows(db, days, limit)
        return workflows
    except Exception as e:
        logger.error(f"Error getting trending workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/popularity/analysis/{workflow_name}", response_model=Dict)
async def get_workflow_popularity(
    workflow_name: str,
    db: Session = Depends(get_db)
):
    """Get detailed popularity analysis for a specific workflow"""
    try:
        analysis = popularity_analyzer.calculate_workflow_popularity(db, workflow_name)
        return analysis
    except Exception as e:
        logger.error(f"Error getting popularity analysis for '{workflow_name}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/summary", response_model=WorkflowSummaryResponse)
async def get_platform_summary(db: Session = Depends(get_db)):
    """Get summary statistics for all platforms"""
    try:
        summary = popularity_analyzer.get_platform_summary(db)
        return summary
    except Exception as e:
        logger.error(f"Error getting platform summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
