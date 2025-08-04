#!/usr/bin/env python3
"""
Test script to verify the Telegram scraper setup
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from src.config.settings import Config
        print("✅ Config imported successfully")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from src.core.database import db_manager
        print("✅ Database manager imported successfully")
    except Exception as e:
        print(f"❌ Database manager import failed: {e}")
        return False
    
    try:
        from src.models.database import TelegramChannel, TelegramPost, ScrapingLog
        print("✅ Database models imported successfully")
    except Exception as e:
        print(f"❌ Database models import failed: {e}")
        return False
    
    try:
        from src.utils.logger import logger
        print("✅ Logger imported successfully")
    except Exception as e:
        print(f"❌ Logger import failed: {e}")
        return False
    
    try:
        from src.utils.image_processor import image_processor
        print("✅ Image processor imported successfully")
    except Exception as e:
        print(f"❌ Image processor import failed: {e}")
        return False
    
    try:
        from src.scrapers.telegram_scraper import TelegramScraper
        print("✅ Telegram scraper imported successfully")
    except Exception as e:
        print(f"❌ Telegram scraper import failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration"""
    print("\nTesting configuration...")
    
    from src.config.settings import Config
    
    # Check required environment variables
    missing_vars = []
    if not Config.TELEGRAM_API_ID:
        missing_vars.append("TELEGRAM_API_ID")
    if not Config.TELEGRAM_API_HASH:
        missing_vars.append("TELEGRAM_API_HASH")
    if not Config.TELEGRAM_PHONE:
        missing_vars.append("TELEGRAM_PHONE")
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("   These are required for scraping but not for testing")
    else:
        print("✅ All required environment variables are set")
    
    # Check channels configuration
    print(f"✅ Configured {len(Config.TELEGRAM_CHANNELS)} channels")
    for channel in Config.TELEGRAM_CHANNELS:
        print(f"   - {channel.name} (@{channel.username})")
    
    # Check directories
    print(f"✅ Data directory: {Config.DATA_DIR}")
    print(f"✅ Logs directory: {Config.LOGS_DIR}")
    print(f"✅ Images directory: {Config.IMAGES_DIR}")

def test_database():
    """Test database connection"""
    print("\nTesting database...")
    
    try:
        from src.core.database import db_manager
        
        # Test creating tables
        db_manager.create_tables()
        print("✅ Database tables created successfully")
        
        # Test session
        with db_manager.get_session() as session:
            print("✅ Database session works")
        
        print("✅ Database connection successful")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Telegram Scraper Setup")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Please check your installation.")
        return False
    
    # Test configuration
    test_config()
    
    # Test database
    if not test_database():
        print("\n❌ Database tests failed.")
        return False
    
    print("\n✅ All tests passed! Setup is ready.")
    print("\nNext steps:")
    print("1. Set up your Telegram API credentials in .env file")
    print("2. Run: python main.py init")
    print("3. Run: python main.py scrape")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 