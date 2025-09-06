import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# For Vercel deployment, use in-memory SQLite or a cloud database
def get_database_url():
    """Get database URL, with fallback for serverless environments"""
    if os.getenv("VERCEL"):
        # In Vercel, use in-memory SQLite or a cloud database
        # For demo purposes, we'll use in-memory SQLite
        return "sqlite:///:memory:"
    return settings.database_url

# Create database engine
engine = create_engine(
    get_database_url(),
    connect_args={"check_same_thread": False} if "sqlite" in get_database_url() else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    from models import Base
    Base.metadata.create_all(bind=engine)
