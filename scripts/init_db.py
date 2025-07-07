#!/usr/bin/env python3
"""
Database Initialization Script
for Queue Management System

This script initializes the database schema and creates sample data.
"""

import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.application import Application
from app.models.queue import Queue
from app.models.queue_user import QueueUser
from app.models.log import Log
from app.services.database import DATABASE_URL
from dotenv import load_dotenv

load_dotenv()

def init_database():
    """Initialize the database"""
    print("🗄️  Initializing database...")
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    try:
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    try:
        # Force import all models to ensure table creation
        import app.models.application
        import app.models.queue
        import app.models.queue_user
        import app.models.log
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False
    
    # Create sample data
    try:
        create_sample_data(engine)
        print("✅ Sample data created successfully")
    except Exception as e:
        print(f"❌ Failed to create sample data: {e}")
        return False
    
    print("🎉 Database initialization completed!")
    return True

def create_sample_data(engine):
    """Create sample data for testing"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if sample data already exists
        existing_app = db.query(Application).filter_by(name="Sample Application").first()
        if existing_app:
            print("ℹ️  Sample data already exists, skipping...")
            return
        
        # Create sample application
        sample_app = Application(
            name="Sample Application",
            domain="sample.com",
            callback_url="https://sample.com/callback",
            api_key="sample-api-key-123"
        )
        db.add(sample_app)
        db.commit()
        db.refresh(sample_app)
        
        # Create sample queue
        sample_queue = Queue(
            application_id=sample_app.id,
            name="Main Queue",
            max_users_per_minute=10,
            priority=1
        )
        db.add(sample_queue)
        db.commit()
        
        print(f"✅ Created sample application: {sample_app.name}")
        print(f"✅ Created sample queue: {sample_queue.name}")
        print(f"✅ API Key: {sample_app.api_key}")
        
    finally:
        db.close()

def run_migrations():
    """Run database migrations using Alembic"""
    print("🔄 Running database migrations...")
    
    try:
        import subprocess
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        if result.returncode == 0:
            print("✅ Database migrations completed successfully")
            return True
        else:
            print(f"❌ Migration failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("⚠️  Alembic not found, skipping migrations")
        return True
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False

def main():
    """Main initialization function"""
    print("🚀 Queue Management System - Database Initialization")
    print("=" * 60)
    print()
    
    # Check if DATABASE_URL is set
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable not set")
        print("Please check your .env file")
        return False
    
    # Run migrations first
    if not run_migrations():
        print("⚠️  Continuing without migrations...")
    
    # Initialize database
    if not init_database():
        print("❌ Database initialization failed")
        return False
    
    print()
    print("🎉 Setup completed successfully!")
    print()
    print("📋 Next steps:")
    print("1. Start the application: docker-compose up -d")
    print("2. Access the API: http://localhost:8000")
    print("3. View documentation: http://localhost:8000/docs")
    print("4. Test with sample API key: sample-api-key-123")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 