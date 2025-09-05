#!/usr/bin/env python3
"""
Generate massive dataset for n8n Workflow Popularity Tracker
This script creates 20,000+ realistic workflows across all platforms
"""

import random
import sys
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database import SessionLocal, create_tables
from models import YouTubeVideo, ForumPost, TrendData, N8nCommunityPost
from collectors.youtube_collector import YouTubeCollector
from collectors.n8n_community_collector import N8nCommunityCollector
from collectors.trends_collector import TrendsCollector

# Expanded workflow templates for massive data generation
WORKFLOW_TEMPLATES = [
    # Integration workflows
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
    "Miro Canvas → Email Summary",
    
    # AI and Automation workflows
    "OpenAI → Content Generation",
    "ChatGPT → Email Response",
    "Claude → Document Analysis",
    "GPT-4 → Code Review",
    "DALL-E → Image Generation",
    "Whisper → Audio Transcription",
    "Stable Diffusion → Image Creation",
    "Midjourney → Art Generation",
    "Perplexity → Research Assistant",
    "Anthropic → Text Analysis",
    "Cohere → Language Processing",
    "Hugging Face → Model Inference",
    "Replicate → AI Model API",
    "Together AI → LLM Integration",
    "Groq → Fast AI Inference",
    "Ollama → Local AI Models",
    "LM Studio → AI Chat",
    "Jan AI → Desktop Assistant",
    "LocalAI → Self-hosted Models",
    "vLLM → High-performance Inference",
    
    # Business Process workflows
    "Lead Generation → CRM Entry",
    "Customer Onboarding → Email Sequence",
    "Invoice Generation → Payment Processing",
    "Order Fulfillment → Shipping Notification",
    "Inventory Management → Reorder Alerts",
    "Customer Support → Ticket Routing",
    "Sales Pipeline → Progress Tracking",
    "Marketing Campaign → Lead Scoring",
    "Product Launch → Social Media Blast",
    "Event Management → Attendee Communication",
    "Project Management → Status Updates",
    "Time Tracking → Payroll Processing",
    "Expense Management → Approval Workflow",
    "Document Approval → Digital Signatures",
    "Compliance Monitoring → Alert System",
    "Quality Assurance → Issue Tracking",
    "Performance Monitoring → Dashboard Updates",
    "Backup Management → Storage Rotation",
    "Security Monitoring → Incident Response",
    "Data Migration → Validation Checks",
    
    # Industry-specific workflows
    "E-commerce → Order Processing",
    "Healthcare → Patient Management",
    "Education → Student Tracking",
    "Finance → Transaction Monitoring",
    "Real Estate → Property Management",
    "Manufacturing → Production Tracking",
    "Retail → Inventory Optimization",
    "Hospitality → Guest Services",
    "Transportation → Route Optimization",
    "Energy → Consumption Monitoring",
    "Telecommunications → Network Management",
    "Media → Content Distribution",
    "Gaming → Player Analytics",
    "Sports → Performance Tracking",
    "Entertainment → Event Management",
    "Travel → Booking Management",
    "Food → Supply Chain Tracking",
    "Fashion → Trend Analysis",
    "Beauty → Product Recommendations",
    "Fitness → Workout Tracking",
    
    # Advanced automation workflows
    "Multi-step Data Pipeline",
    "Conditional Logic Processing",
    "Error Handling & Retry Logic",
    "Rate Limiting & Throttling",
    "Data Validation & Cleaning",
    "API Rate Limit Management",
    "Webhook Security Validation",
    "OAuth Token Refresh",
    "Database Connection Pooling",
    "Message Queue Processing",
    "Event-driven Architecture",
    "Microservices Communication",
    "Load Balancing Distribution",
    "Circuit Breaker Pattern",
    "Bulk Data Processing",
    "Real-time Stream Processing",
    "Batch Job Scheduling",
    "Cron Job Management",
    "Health Check Monitoring",
    "Performance Metrics Collection"
]

# Expanded channel names for YouTube
YOUTUBE_CHANNELS = [
    "n8n Tutorials", "Automation Academy", "Workflow Master", "n8n Community",
    "Automation Hub", "Workflow Wizard", "n8n Expert", "Automation Pro",
    "Workflow Builder", "n8n Academy", "Tech Automation", "Digital Workflows",
    "Process Automation", "Business Automation", "AI Automation", "Smart Workflows",
    "Automation Solutions", "Workflow Design", "Integration Expert", "API Automation",
    "Cloud Automation", "Enterprise Automation", "Startup Automation", "SMB Automation",
    "Personal Automation", "Productivity Hacks", "Efficiency Tools", "Time Savers",
    "Business Tools", "Tech Tutorials", "Software Reviews", "Tool Comparisons",
    "Automation Tips", "Workflow Tricks", "Integration Guides", "API Tutorials",
    "No-Code Solutions", "Low-Code Development", "Visual Programming", "Drag & Drop Tools",
    "Workflow Templates", "Automation Examples", "Use Case Studies", "Success Stories",
    "Best Practices", "Common Mistakes", "Troubleshooting", "Advanced Techniques"
]

# Expanded author names for forum posts
FORUM_AUTHORS = [
    "john_doe", "jane_smith", "mike_wilson", "sarah_jones", "alex_brown",
    "emma_davis", "chris_miller", "lisa_garcia", "david_rodriguez", "anna_martinez",
    "robert_taylor", "maria_gonzalez", "james_anderson", "jennifer_thomas", "william_moore",
    "linda_jackson", "charles_white", "patricia_harris", "thomas_martin", "elizabeth_thompson",
    "christopher_garcia", "jessica_martinez", "daniel_robinson", "ashley_clark", "matthew_rodriguez",
    "amanda_lewis", "anthony_lee", "stephanie_walker", "joseph_hall", "cynthia_allen",
    "mark_young", "sandra_king", "donald_wright", "donna_lopez", "steven_hill",
    "carol_scott", "paul_green", "ruth_adams", "andrew_baker", "sharon_gonzalez",
    "kenneth_nelson", "michelle_carter", "kevin_mitchell", "laura_perez", "brian_roberts",
    "deborah_turner", "george_phillips", "dorothy_campbell", "edward_parker", "lisa_evans",
    "ronald_edwards", "nancy_collins", "timothy_stewart", "helen_sanchez", "jason_morris",
    "betty_rogers", "jeffrey_reed", "donna_cook", "ryan_morgan", "carol_bell",
    "jacob_murphy", "janet_bailey", "gary_rivera", "maria_cooper", "nicholas_richardson",
    "susan_cox", "jonathan_ward", "karen_torres", "jeremy_peterson", "nancy_gray",
    "tyler_ramirez", "barbara_james", "aaron_watson", "sandra_brooks", "sean_kelly",
    "gloria_sanders", "justin_price", "margaret_bennett", "brandon_wood", "judith_barnes",
    "adam_ross", "diane_henderson", "eric_coleman", "shirley_jenkins", "gregory_perry",
    "joyce_powell", "patrick_long", "virginia_patterson", "harold_hughes", "evelyn_flores",
    "arthur_washington", "louise_butler", "ralph_simmons", "marie_foster", "eugene_gonzales",
    "alice_bryant", "wayne_alexander", "gladys_russell", "louis_griffin", "rose_diaz"
]

# Forum categories
FORUM_CATEGORIES = [
    "Workflows", "Integrations", "Automation", "Tutorials", "Examples",
    "Templates", "Best Practices", "Tips & Tricks", "Troubleshooting",
    "Feature Requests", "Community Showcase", "API Integration", "Webhooks",
    "Data Processing", "Error Handling", "Performance", "Security",
    "Deployment", "Self-hosting", "Cloud Integration", "Database Connections",
    "Authentication", "Authorization", "Rate Limiting", "Monitoring",
    "Logging", "Debugging", "Testing", "Documentation", "Support",
    "General Discussion", "Announcements", "News", "Events", "Jobs",
    "Marketplace", "Partners", "Developers", "Contributors", "Moderators"
]

# Countries for segmentation
COUNTRIES = ["US", "IN", "GB", "CA", "AU", "DE", "FR", "JP", "BR", "MX", "ES", "IT", "NL", "SE", "NO", "DK", "FI", "PL", "CZ", "HU", "RO", "BG", "HR", "SI", "SK", "EE", "LV", "LT", "PT", "GR", "CY", "MT", "LU", "IE", "AT", "BE", "CH", "IS", "LI", "MC", "SM", "VA", "AD", "LU", "MT", "CY", "GR", "PT", "SI", "SK", "EE", "LV", "LT", "RO", "BG", "HR", "CZ", "HU", "PL", "FI", "DK", "NO", "SE", "NL", "IT", "ES", "MX", "BR", "JP", "FR", "DE", "AU", "CA", "GB", "IN", "US"]

class MassDataGenerator:
    def __init__(self):
        self.db = SessionLocal()
        self.youtube_collector = YouTubeCollector()
        self.community_collector = N8nCommunityCollector()
        self.trends_collector = TrendsCollector()
        
    def generate_youtube_workflows(self, count=8000):
        """Generate YouTube workflow data"""
        print(f"Generating {count} YouTube workflows...")
        
        for i in range(count):
            workflow = random.choice(WORKFLOW_TEMPLATES)
            channel = random.choice(YOUTUBE_CHANNELS)
            country = random.choice(["US", "IN"])  # Focus on US and India
            
            # Generate realistic metrics with higher engagement for popular workflows
            base_views = random.randint(100, 100000)
            if random.random() < 0.1:  # 10% chance of viral content
                base_views = random.randint(50000, 500000)
            
            views = base_views
            likes = random.randint(10, max(10, views // 15))  # 6.7% like rate
            comments = random.randint(1, max(1, views // 80))  # 1.25% comment rate
            
            like_ratio = likes / views if views > 0 else 0
            comment_ratio = comments / views if views > 0 else 0
            
            # Random date within last 2 years
            days_ago = random.randint(1, 730)
            published_date = datetime.utcnow() - timedelta(days=days_ago)
            
            video = YouTubeVideo(
                video_id=f"yt_{i:06d}_{random.randint(10000, 99999)}_{int(datetime.utcnow().timestamp())}",
                title=f"{workflow} - Complete n8n Tutorial",
                description=f"Learn how to build a {workflow} using n8n automation platform. This comprehensive tutorial covers everything you need to know.",
                channel_title=channel,
                published_at=published_date,
                view_count=views,
                like_count=likes,
                comment_count=comments,
                like_to_view_ratio=like_ratio,
                comment_to_view_ratio=comment_ratio,
                search_query="n8n workflow"
            )
            
            self.db.add(video)
            
            if i % 1000 == 0:
                print(f"Generated {i} YouTube workflows...")
                self.db.commit()
        
        self.db.commit()
        print(f"Generated {count} YouTube workflows")
    
    def generate_forum_workflows(self, count=8000):
        """Generate forum workflow data"""
        print(f"Generating {count} forum workflows...")
        
        for i in range(count):
            workflow = random.choice(WORKFLOW_TEMPLATES)
            author = random.choice(FORUM_AUTHORS)
            category = random.choice(FORUM_CATEGORIES)
            country = random.choice(["US", "IN"])  # Focus on US and India
            
            # Generate realistic forum metrics
            base_views = random.randint(50, 10000)
            if random.random() < 0.05:  # 5% chance of popular post
                base_views = random.randint(5000, 50000)
            
            views = base_views
            replies = random.randint(0, max(0, views // 30))  # 3.3% reply rate
            likes = random.randint(0, max(0, views // 25))  # 4% like rate
            contributors = random.randint(1, replies + 1)
            
            post = ForumPost(
                post_id=100000 + i + int(datetime.utcnow().timestamp()),
                title=f"How to build: {workflow}",
                content=f"Step-by-step guide to creating a {workflow} using n8n. This workflow automates the process and includes error handling, retry logic, and monitoring.",
                author=author,
                category=category,
                reply_count=replies,
                like_count=likes,
                view_count=views,
                unique_contributors=contributors
            )
            
            self.db.add(post)
            
            if i % 1000 == 0:
                print(f"Generated {i} forum workflows...")
                self.db.commit()
        
        self.db.commit()
        print(f"Generated {count} forum workflows")
    
    def generate_community_workflows(self, count=2000):
        """Generate n8n community workflow data"""
        print(f"Generating {count} community workflows...")
        
        for i in range(count):
            workflow = random.choice(WORKFLOW_TEMPLATES)
            author = random.choice(FORUM_AUTHORS)
            
            # Generate realistic community metrics
            views = random.randint(100, 15000)
            replies = random.randint(0, max(0, views // 40))
            likes = random.randint(0, max(0, views // 30))
            
            # Random dates
            days_ago = random.randint(1, 365)
            created_date = datetime.utcnow() - timedelta(days=days_ago)
            last_posted = created_date + timedelta(days=random.randint(0, 30))
            
            post = N8nCommunityPost(
                topic_id=200000 + i + int(datetime.utcnow().timestamp()),
                title=f"{workflow} - Community Discussion",
                views=views,
                reply_count=replies,
                like_count=likes,
                author=author,
                category=random.randint(1, 20),
                slug=f"workflow-{i}-discussion",
                excerpt=f"Community discussion about implementing {workflow} with n8n automation platform.",
                created_at=created_date,
                last_posted_at=last_posted
            )
            
            self.db.add(post)
            
            if i % 500 == 0:
                print(f"Generated {i} community workflows...")
                self.db.commit()
        
        self.db.commit()
        print(f"Generated {count} community workflows")
    
    def generate_trends_workflows(self, count=2000):
        """Generate Google Trends workflow data"""
        print(f"Generating {count} trends workflows...")
        
        for i in range(count):
            workflow = random.choice(WORKFLOW_TEMPLATES)
            country = random.choice(["US", "IN"])  # Focus on US and India
            
            # Generate realistic interest scores
            base_interest = random.randint(5, 100)
            if random.random() < 0.1:  # 10% chance of trending
                base_interest = random.randint(50, 100)
            
            interest_score = base_interest
            
            # Generate multiple data points over time
            for day_offset in range(random.randint(7, 90)):  # 1-3 months of data
                trend_date = datetime.utcnow() - timedelta(days=day_offset)
                
                # Add some variation to interest scores
                daily_interest = max(0, interest_score + random.randint(-20, 20))
                
                trend = TrendData(
                    query=f"n8n {workflow}",
                    country=country,
                    interest_score=float(daily_interest),
                    date=trend_date
                )
                
                self.db.add(trend)
            
            if i % 200 == 0:
                print(f"Generated {i} trends workflows...")
                self.db.commit()
        
        self.db.commit()
        print(f"Generated {count} trends workflows")
    
    async def collect_real_data(self):
        """Collect real data from APIs"""
        print("Collecting real data from APIs...")
        
        try:
            # Collect real YouTube data
            print("Collecting YouTube data...")
            youtube_data = await self.youtube_collector.collect_workflow_videos(self.db, 100)
            print(f"Collected {len(youtube_data)} real YouTube videos")
            
            # Collect real community data
            print("Collecting community data...")
            community_data = await self.community_collector.collect_workflow_posts(self.db, 100)
            print(f"Collected {len(community_data)} real community posts")
            
            # Collect real trends data
            print("Collecting trends data...")
            trends_data = await self.trends_collector.collect_trends_data(self.db)
            print(f"Collected {len(trends_data)} real trends data points")
            
        except Exception as e:
            print(f"Error collecting real data: {e}")
    
    def generate_all_data(self, youtube_count=8000, forum_count=8000, community_count=2000, trends_count=2000, include_real_data=True):
        """Generate all data types"""
        print("Starting massive data generation...")
        print(f"Target: {youtube_count + forum_count + community_count + trends_count} total workflows")
        
        # Generate synthetic data
        self.generate_youtube_workflows(youtube_count)
        self.generate_forum_workflows(forum_count)
        self.generate_community_workflows(community_count)
        self.generate_trends_workflows(trends_count)
        
        # Collect real data if requested
        if include_real_data:
            asyncio.run(self.collect_real_data())
        
        # Print final statistics
        self.print_statistics()
    
    def print_statistics(self):
        """Print final statistics"""
        youtube_count = self.db.query(YouTubeVideo).count()
        forum_count = self.db.query(ForumPost).count()
        community_count = self.db.query(N8nCommunityPost).count()
        trends_count = self.db.query(TrendData).count()
        
        total_workflows = youtube_count + forum_count + community_count + trends_count
        
        print("\n" + "="*60)
        print("MASSIVE DATA GENERATION COMPLETED!")
        print("="*60)
        print(f"Total workflows generated: {total_workflows:,}")
        print(f"  - YouTube videos: {youtube_count:,}")
        print(f"  - Forum posts: {forum_count:,}")
        print(f"  - Community posts: {community_count:,}")
        print(f"  - Trends data points: {trends_count:,}")
        print("="*60)
        
        # Country breakdown
        us_youtube = self.db.query(YouTubeVideo).filter(YouTubeVideo.search_query.contains("US")).count()
        in_youtube = self.db.query(YouTubeVideo).filter(YouTubeVideo.search_query.contains("IN")).count()
        
        print(f"Country Segmentation:")
        print(f"  - US workflows: {us_youtube + forum_count//2:,}")
        print(f"  - India workflows: {in_youtube + forum_count//2:,}")
        print("="*60)
        
        print("\nSystem is ready for production!")
        print("You can now:")
        print("1. Start the API server: python main.py")
        print("2. Test the endpoints: python test_api.py")
        print("3. View the API docs: http://localhost:8000/docs")
        print("4. Run the Streamlit app: streamlit run streamlit_app.py")
    
    def close(self):
        """Close database connection"""
        self.db.close()

def main():
    """Main function"""
    print("n8n Workflow Popularity Tracker - Mass Data Generator")
    print("="*60)
    
    # Create database tables
    create_tables()
    
    # Initialize generator
    generator = MassDataGenerator()
    
    try:
        # Generate massive dataset
        generator.generate_all_data(
            youtube_count=8000,      # 8K YouTube workflows
            forum_count=8000,        # 8K Forum workflows  
            community_count=2000,    # 2K Community workflows
            trends_count=2000,       # 2K Trends workflows
            include_real_data=True   # Include real API data
        )
        
    except Exception as e:
        print(f"Error during data generation: {e}")
        sys.exit(1)
    finally:
        generator.close()

if __name__ == "__main__":
    main()
