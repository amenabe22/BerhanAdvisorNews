import os
from typing import List, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

@dataclass
class TelegramChannel:
    name: str
    username: str
    url: str
    category: str
    language: str
    is_active: bool = True
    max_posts: int = 10

class Config:
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./telegram_news.db")
    
    # Telegram API credentials
    TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
    TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
    TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE")
    TELEGRAM_SESSION_NAME = os.getenv("TELEGRAM_SESSION_NAME", "telegram_scraper")
    
    # Google Cloud Storage
    GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "telegram-news-images")
    GCS_CREDENTIALS_PATH = os.getenv("GCS_CREDENTIALS_PATH")
    
    # Scraping settings
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    RATE_LIMIT_DELAY = 2  # seconds between requests
    MAX_CONCURRENT_REQUESTS = 5
    
    # Telegram channels configuration
    TELEGRAM_CHANNELS: List[TelegramChannel] = [
        TelegramChannel(
            name="Shega Media",
            username="shegamediaet",
            url="https://t.me/shegamediaet",
            category="tech_startup",
            language="en",
            max_posts=10
        ),
        TelegramChannel(
            name="Tikvah Ethiopia",
            username="tikvahethiopia",
            url="https://t.me/tikvahethiopia",
            category="general",
            language="am",
            max_posts=10
        ),
        TelegramChannel(
            name="Addis Reporter",
            username="Addis_Reporter",
            url="https://t.me/Addis_Reporter",
            category="news",
            language="am",
            max_posts=10
        ),
        TelegramChannel(
            name="ESAT",
            username="Esat_tv1",
            url="https://t.me/Esat_tv1",
            category="news",
            language="am",
            max_posts=10
        ),
        TelegramChannel(
            name="Fana Media Corporation",
            username="fanatelevision",
            url="https://t.me/fanatelevision",
            category="news",
            language="am",
            max_posts=10
        ),
        TelegramChannel(
            name="Addis Neger",
            username="Addis_News",
            url="https://t.me/Addis_News",
            category="news",
            language="am",
            max_posts=10
        )
    ]
    
    # Storage paths
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    IMAGES_DIR = BASE_DIR / "images"
    
    # Create directories if they don't exist
    DATA_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)
    IMAGES_DIR.mkdir(exist_ok=True)
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = LOGS_DIR / "telegram_scraper.log"
    
    # Deduplication settings
    SIMILARITY_THRESHOLD = 0.85
    TITLE_SIMILARITY_THRESHOLD = 0.9
    
    # Image processing
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
    SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.webp']
    
    # CLI settings
    DEFAULT_POSTS_PER_CHANNEL = 10
    DEFAULT_CONCURRENT_CHANNELS = 3
    
    # API settings
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000")) 