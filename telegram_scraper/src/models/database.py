from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Index, Float, Enum, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import hashlib
import enum

Base = declarative_base()

class ModerationStatus(enum.Enum):
    PENDING = "pending"
    READY = "ready"
    WRONG = "wrong"

class TelegramChannel(Base):
    __tablename__ = "telegram_channels"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    username = Column(String(255), nullable=False, unique=True, index=True)
    url = Column(String(500), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    language = Column(String(10), nullable=False)
    is_active = Column(Boolean, default=True)
    last_scraped = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationship
    posts = relationship("TelegramPost", back_populates="channel")

class TelegramPost(Base):
    __tablename__ = "telegram_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, nullable=False, unique=True, index=True)
    title = Column(String(500), nullable=True, index=True)
    content = Column(Text, nullable=True)
    excerpt = Column(Text, nullable=True)
    url = Column(String(1000), nullable=True)
    image_url = Column(String(1000), nullable=True)
    image_path = Column(String(500), nullable=True)
    gcs_image_url = Column(String(1000), nullable=True)
    published_date = Column(DateTime, nullable=True, index=True)
    scraped_date = Column(DateTime, default=func.now(), index=True)
    channel_id = Column(Integer, ForeignKey("telegram_channels.id"), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    language = Column(String(10), nullable=False)
    is_duplicate = Column(Boolean, default=False)
    duplicate_of = Column(Integer, ForeignKey("telegram_posts.id"), nullable=True)
    similarity_score = Column(Float, nullable=True)
    content_hash = Column(String(64), nullable=False, index=True)
    title_hash = Column(String(64), nullable=True, index=True)
    
    # Telegram specific fields
    views = Column(Integer, nullable=True)
    forwards = Column(Integer, nullable=True)
    replies = Column(Integer, nullable=True)
    has_media = Column(Boolean, default=False)
    media_type = Column(String(50), nullable=True)  # photo, video, document, etc.
    
    # Moderation fields
    moderation_status = Column(Enum(ModerationStatus), default=ModerationStatus.PENDING, index=True)
    moderated_by = Column(String(100), nullable=True)
    moderated_at = Column(DateTime, nullable=True)
    moderation_notes = Column(Text, nullable=True)
    
    # Relationships
    channel = relationship("TelegramChannel", back_populates="posts")
    duplicates = relationship("TelegramPost", back_populates="original_post")
    original_post = relationship("TelegramPost", back_populates="duplicates", remote_side=[id])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.title:
            self.title_hash = hashlib.sha256(self.title.encode()).hexdigest()
        if self.content:
            self.content_hash = hashlib.sha256(self.content.encode()).hexdigest()

class ScrapingLog(Base):
    __tablename__ = "scraping_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("telegram_channels.id"), nullable=False)
    status = Column(String(50), nullable=False)  # success, error, partial
    posts_found = Column(Integer, default=0)
    posts_new = Column(Integer, default=0)
    posts_duplicate = Column(Integer, default=0)
    images_downloaded = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    duration = Column(Float, nullable=True)  # seconds
    created_at = Column(DateTime, default=func.now(), index=True)
    
    # Relationship
    channel = relationship("TelegramChannel")

# Indexes for better performance
Index('idx_posts_published_date', TelegramPost.published_date)
Index('idx_posts_category', TelegramPost.category)
Index('idx_posts_language', TelegramPost.language)
Index('idx_posts_content_hash', TelegramPost.content_hash)
Index('idx_posts_title_hash', TelegramPost.title_hash)
Index('idx_posts_telegram_id', TelegramPost.telegram_id)
Index('idx_posts_moderation_status', TelegramPost.moderation_status)
Index('idx_scraping_logs_channel_date', ScrapingLog.channel_id, ScrapingLog.created_at) 