from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ModerationStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    WRONG = "wrong"

class ChannelResponse(BaseModel):
    id: int
    name: str
    username: str
    url: str
    category: str
    language: str
    is_active: bool
    last_scraped: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class PostResponse(BaseModel):
    id: int
    telegram_id: int
    title: Optional[str]
    content: Optional[str]
    excerpt: Optional[str]
    url: Optional[str]
    image_url: Optional[str]
    gcs_image_url: Optional[str]
    published_date: Optional[datetime]
    scraped_date: datetime
    channel_id: int
    category: str
    language: str
    is_duplicate: bool
    similarity_score: Optional[float]
    views: Optional[int]
    forwards: Optional[int]
    replies: Optional[int]
    has_media: bool
    media_type: Optional[str]
    moderation_status: ModerationStatus
    channel: ChannelResponse

class ScrapingLogResponse(BaseModel):
    id: int
    channel_id: int
    status: str
    posts_found: int
    posts_new: int
    posts_duplicate: int
    images_downloaded: int
    error_message: Optional[str]
    duration: Optional[float]
    created_at: datetime
    channel: ChannelResponse

class StatisticsResponse(BaseModel):
    total_channels: int
    total_posts: int
    total_logs: int
    posts_by_category: Dict[str, int]
    posts_by_language: Dict[str, int]
    recent_activity: Dict[str, Any]

class ScrapingResultResponse(BaseModel):
    channel_name: str
    posts_found: int
    posts_new: int
    posts_duplicate: int
    images_downloaded: int
    error: Optional[str]
    status: str

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int

class SearchFilters(BaseModel):
    channel_id: Optional[int] = None
    category: Optional[str] = None
    language: Optional[str] = None
    moderation_status: Optional[ModerationStatus] = None
    has_media: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search: Optional[str] = None

class ScrapingRequest(BaseModel):
    channels: Optional[List[str]] = None
    posts_per_channel: int = Field(default=10, ge=1, le=100)
    force: bool = False 