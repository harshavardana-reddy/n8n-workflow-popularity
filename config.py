import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Only load .env file if not in Vercel environment
if not os.getenv("VERCEL"):
    load_dotenv()

class Settings(BaseSettings):
    # API Keys
    youtube_api_key: str = os.getenv("YOUTUBE_API_KEY", "AIzaSyBEaKtU5aB2DiIQT2f_svHCIkdBQOBaq6k")
    n8n_forum_api_key: str = os.getenv("N8N_FORUM_API_KEY", "")
    n8n_forum_base_url: str = os.getenv("N8N_FORUM_BASE_URL", "https://community.n8n.io")
    
    # Database Configuration - use in-memory for Vercel
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///:memory:" if os.getenv("VERCEL") else "sqlite:///./workflow_data.db")
    
    # Application Settings
    app_name: str = os.getenv("APP_NAME", "n8n Workflow Popularity Tracker")
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Data Collection Settings
    youtube_search_queries: List[str] = os.getenv("YOUTUBE_SEARCH_QUERIES", "n8n workflow,n8n automation,n8n integration").split(",")
    trends_queries: List[str] = os.getenv("TRENDS_QUERIES", "n8n Slack integration,n8n Gmail automation,n8n workflow").split(",")
    trends_countries: List[str] = os.getenv("TRENDS_COUNTRIES", "US,IN").split(",")
    
    class Config:
        env_file = ".env"

settings = Settings()
