#!/usr/bin/env python3
"""
Generate sample data for n8n Workflow Popularity Tracker
This script creates at least 50 sample workflows for testing and demonstration
"""

import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database import SessionLocal, create_tables
from models import YouTubeVideo, ForumPost, TrendData

# Sample workflow names and descriptions
SAMPLE_WORKFLOWS = [
    "Google Sheets → Slack Automation",
    "Gmail → Trello Task Creation",
    "Webhook → Discord Notification",
    "RSS Feed → Email Digest",
    "Form Submission → CRM Update",
    "Calendar Event → Team Notification",
    "GitHub Issue → Slack Alert",
    "Weather API → SMS Alert",
    "Salesforce → Google Sheets Sync",
    "Stripe Payment → Email Receipt",
    "Twitter Mention → Slack Notification",
    "Instagram Post → Facebook Share",
    "YouTube Upload → Twitter Announcement",
    "Shopify Order → Inventory Update",
    "Zapier → n8n Migration",
    "Airtable → Google Docs Report",
    "Typeform → Notion Database",
    "Mailchimp → HubSpot Contact",
    "WordPress Post → Social Media",
    "Jira Ticket → Email Update",
    "Asana Task → Calendar Event",
    "Dropbox File → Google Drive Copy",
    "Figma Design → Slack Share",
    "Canva Design → Social Media Post",
    "Zoom Meeting → Calendar Block",
    "Calendly Booking → Email Confirmation",
    "Intercom Message → Slack Alert",
    "Freshdesk Ticket → Email Notification",
    "Pipedrive Deal → Slack Update",
    "Monday.com Board → Email Report",
    "ClickUp Task → Calendar Event",
    "Notion Page → Email Digest",
    "Linear Issue → Slack Notification",
    "Figma Comment → Email Alert",
    "Loom Video → Slack Share",
    "Miro Board → Email Summary",
    "Airtable Record → Google Sheets",
    "Typeform Response → CRM Update",
    "Calendly Event → Email Reminder",
    "Stripe Webhook → Slack Notification",
    "GitHub Push → Discord Message",
    "Trello Card → Email Update",
    "Asana Project → Slack Report",
    "Monday.com Item → Email Alert",
    "ClickUp List → Calendar Event",
    "Notion Database → Email Digest",
    "Linear Project → Slack Update",
    "Figma File → Email Notification",
    "Loom Recording → Slack Share",
    "Miro Canvas → Email Summary"
]

SAMPLE_CHANNELS = [
    "n8n Tutorials",
    "Automation Academy",
    "Workflow Master",
    "n8n Community",
    "Automation Hub",
    "Workflow Wizard",
    "n8n Expert",
    "Automation Pro",
    "Workflow Builder",
    "n8n Academy"
]

SAMPLE_AUTHORS = [
    "john_doe",
    "jane_smith",
    "mike_wilson",
    "sarah_jones",
    "alex_brown",
    "emma_davis",
    "chris_miller",
    "lisa_garcia",
    "david_rodriguez",
    "anna_martinez"
]

SAMPLE_CATEGORIES = [
    "Workflows",
    "Integrations",
    "Automation",
    "Tutorials",
    "Examples",
    "Templates",
    "Best Practices",
    "Tips & Tricks"
]

COUNTRIES = ["US", "IN", "GB", "CA", "AU", "DE", "FR", "JP"]

def generate_sample_youtube_data(db, count=20):
    """Generate sample YouTube video data"""
    print(f"Generating {count} sample YouTube videos...")
    
    for i in range(count):
        workflow = random.choice(SAMPLE_WORKFLOWS)
        channel = random.choice(SAMPLE_CHANNELS)
        
        # Generate realistic metrics
        views = random.randint(100, 50000)
        likes = random.randint(10, views // 20)  # 5% like rate
        comments = random.randint(1, views // 100)  # 1% comment rate
        
        like_ratio = likes / views if views > 0 else 0
        comment_ratio = comments / views if views > 0 else 0
        
        # Random date within last 6 months
        days_ago = random.randint(1, 180)
        published_date = datetime.utcnow() - timedelta(days=days_ago)
        
        video = YouTubeVideo(
            video_id=f"sample_video_{i:03d}",
            title=f"{workflow} - n8n Tutorial",
            description=f"Learn how to create a {workflow} using n8n automation platform.",
            channel_title=channel,
            published_at=published_date,
            view_count=views,
            like_count=likes,
            comment_count=comments,
            like_to_view_ratio=like_ratio,
            comment_to_view_ratio=comment_ratio,
            search_query="n8n workflow"
        )
        
        db.add(video)
    
    print(f"Generated {count} YouTube videos")

def generate_sample_forum_data(db, count=20):
    """Generate sample forum post data"""
    print(f"Generating {count} sample forum posts...")
    
    for i in range(count):
        workflow = random.choice(SAMPLE_WORKFLOWS)
        author = random.choice(SAMPLE_AUTHORS)
        category = random.choice(SAMPLE_CATEGORIES)
        
        # Generate realistic metrics
        views = random.randint(50, 5000)
        replies = random.randint(0, views // 50)  # 2% reply rate
        likes = random.randint(0, views // 20)  # 5% like rate
        contributors = random.randint(1, replies + 1)
        
        post = ForumPost(
            post_id=1000 + i,
            title=f"How to build: {workflow}",
            content=f"Step-by-step guide to creating a {workflow} using n8n. This workflow automates the process of...",
            author=author,
            category=category,
            reply_count=replies,
            like_count=likes,
            view_count=views,
            unique_contributors=contributors
        )
        
        db.add(post)
    
    print(f"Generated {count} forum posts")

def generate_sample_trends_data(db, count=20):
    """Generate sample Google Trends data"""
    print(f"Generating {count} sample trends data points...")
    
    for i in range(count):
        workflow = random.choice(SAMPLE_WORKFLOWS)
        country = random.choice(COUNTRIES)
        
        # Generate realistic interest scores
        interest_score = random.randint(10, 100)
        
        # Random date within last 3 months
        days_ago = random.randint(1, 90)
        trend_date = datetime.utcnow() - timedelta(days=days_ago)
        
        trend = TrendData(
            query=f"n8n {workflow}",
            country=country,
            interest_score=interest_score,
            date=trend_date
        )
        
        db.add(trend)
    
    print(f"Generated {count} trends data points")

def main():
    """Main function to generate sample data"""
    print("Generating sample data for n8n Workflow Popularity Tracker...")
    
    # Create database tables
    create_tables()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Generate sample data
        generate_sample_youtube_data(db, 20)
        generate_sample_forum_data(db, 20)
        generate_sample_trends_data(db, 20)
        
        # Commit all changes
        db.commit()
        
        # Print summary
        youtube_count = db.query(YouTubeVideo).count()
        forum_count = db.query(ForumPost).count()
        trends_count = db.query(TrendData).count()
        
        print("\n" + "="*50)
        print("Sample data generation completed!")
        print(f"Total workflows generated: {youtube_count + forum_count + trends_count}")
        print(f"  - YouTube videos: {youtube_count}")
        print(f"  - Forum posts: {forum_count}")
        print(f"  - Trends data points: {trends_count}")
        print("="*50)
        
        print("\nYou can now:")
        print("1. Start the API server: python main.py")
        print("2. Test the endpoints: python test_api.py")
        print("3. View the API docs: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"Error generating sample data: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
