from fastapi import APIRouter, HTTPException, Query, Path, Depends
from typing import List, Optional
from datetime import datetime

from .models import (
    ChannelResponse, PostResponse, ScrapingLogResponse, StatisticsResponse,
    ScrapingResultResponse, PaginatedResponse, SearchFilters, ScrapingRequest
)
from .services import ChannelService, PostService, StatisticsService, ScrapingService, LogService

router = APIRouter()

# Helper function to convert SQLAlchemy models to Pydantic models
def convert_channel_to_response(channel) -> ChannelResponse:
    return ChannelResponse(
        id=channel.id,
        name=channel.name,
        username=channel.username,
        url=channel.url,
        category=channel.category,
        language=channel.language,
        is_active=channel.is_active,
        last_scraped=channel.last_scraped,
        created_at=channel.created_at,
        updated_at=channel.updated_at
    )

def convert_post_to_response(post) -> PostResponse:
    # Extract channel data while post is still bound to session
    channel_data = None
    if hasattr(post, 'channel') and post.channel:
        channel_data = convert_channel_to_response(post.channel)
    
    return PostResponse(
        id=post.id,
        telegram_id=post.telegram_id,
        title=post.title,
        content=post.content,
        excerpt=post.excerpt,
        url=post.url,
        image_url=post.image_url,
        gcs_image_url=post.gcs_image_url,
        published_date=post.published_date,
        scraped_date=post.scraped_date,
        channel_id=post.channel_id,
        category=post.category,
        language=post.language,
        is_duplicate=post.is_duplicate,
        similarity_score=post.similarity_score,
        views=post.views,
        forwards=post.forwards,
        replies=post.replies,
        has_media=post.has_media,
        media_type=post.media_type,
        moderation_status=post.moderation_status,
        channel=channel_data
    )

def convert_log_to_response(log) -> ScrapingLogResponse:
    # Extract channel data while log is still bound to session
    channel_data = None
    if hasattr(log, 'channel') and log.channel:
        channel_data = convert_channel_to_response(log.channel)
    
    return ScrapingLogResponse(
        id=log.id,
        channel_id=log.channel_id,
        status=log.status,
        posts_found=log.posts_found,
        posts_new=log.posts_new,
        posts_duplicate=log.posts_duplicate,
        images_downloaded=log.images_downloaded,
        error_message=log.error_message,
        duration=log.duration,
        created_at=log.created_at,
        channel=channel_data
    )

# Channel endpoints
@router.get("/channels", response_model=List[ChannelResponse], tags=["Channels"])
async def get_channels():
    """Get all channels"""
    channels = ChannelService.get_all_channels()
    return [ChannelResponse(**channel) for channel in channels]

@router.get("/channels/{channel_id}", response_model=ChannelResponse, tags=["Channels"])
async def get_channel(channel_id: int):
    """Get channel by ID"""
    channel = ChannelService.get_channel_by_id(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    return ChannelResponse(**channel)

@router.get("/channels/username/{username}", response_model=ChannelResponse, tags=["Channels"])
async def get_channel_by_username(username: str):
    """Get channel by username"""
    channel = ChannelService.get_channel_by_username(username)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    return ChannelResponse(**channel)

# Post endpoints
@router.get("/posts", response_model=PaginatedResponse, tags=["Posts"])
async def get_posts(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    channel_id: Optional[int] = Query(None, description="Filter by channel ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    language: Optional[str] = Query(None, description="Filter by language"),
    moderation_status: Optional[str] = Query(None, description="Filter by moderation status"),
    has_media: Optional[bool] = Query(None, description="Filter by media presence"),
    search: Optional[str] = Query(None, description="Search in title, content, and excerpt"),
    date_from: Optional[datetime] = Query(None, description="Filter by date from"),
    date_to: Optional[datetime] = Query(None, description="Filter by date to")
):
    """Get posts with pagination and filtering"""
    filters = SearchFilters(
        channel_id=channel_id,
        category=category,
        language=language,
        moderation_status=moderation_status,
        has_media=has_media,
        search=search,
        date_from=date_from,
        date_to=date_to
    )
    
    result = PostService.get_posts(page=page, size=size, filters=filters)
    posts = [PostResponse(**post) for post in result["items"]]
    
    return PaginatedResponse(
        items=posts,
        total=result["total"],
        page=result["page"],
        size=result["size"],
        pages=result["pages"]
    )

@router.get("/posts/approved", response_model=PaginatedResponse, tags=["Posts"])
async def get_approved_posts(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    channel_id: Optional[int] = Query(None, description="Filter by channel ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    language: Optional[str] = Query(None, description="Filter by language"),
    has_media: Optional[bool] = Query(None, description="Filter by media presence"),
    search: Optional[str] = Query(None, description="Search in title, content, and excerpt"),
    date_from: Optional[datetime] = Query(None, description="Filter by date from"),
    date_to: Optional[datetime] = Query(None, description="Filter by date to")
):
    """Get posts that are not rejected (accepted and pending)"""
    # Use a custom service method for approved posts
    result = PostService.get_approved_posts(
        page=page, 
        size=size,
        channel_id=channel_id,
        category=category,
        language=language,
        has_media=has_media,
        search=search,
        date_from=date_from,
        date_to=date_to
    )
    posts = [PostResponse(**post) for post in result["items"]]
    
    return PaginatedResponse(
        items=posts,
        total=result["total"],
        page=result["page"],
        size=result["size"],
        pages=result["pages"]
    )

@router.get("/posts/recent/{limit}", response_model=List[PostResponse], tags=["Posts"])
async def get_recent_posts(limit: int = Path(ge=1, le=50, description="Number of recent posts")):
    """Get recent posts"""
    posts = PostService.get_recent_posts(limit=limit)
    return [PostResponse(**post) for post in posts]

@router.get("/posts/{post_id}", response_model=PostResponse, tags=["Posts"])
async def get_post(post_id: int):
    """Get post by ID"""
    post = PostService.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return PostResponse(**post)

@router.post("/posts/{post_id}/moderate", response_model=PostResponse, tags=["Posts"])
async def moderate_post(
    post_id: int,
    status: str = Query(..., description="Moderation status: accepted, rejected, or pending"),
    moderator: str = Query("web_interface", description="Name of the moderator"),
    notes: str = Query(None, description="Optional moderation notes")
):
    """Update moderation status of a post"""
    if status not in ["accepted", "rejected", "pending"]:
        raise HTTPException(status_code=400, detail="Invalid status. Must be 'accepted', 'rejected', or 'pending'")
    
    post = PostService.update_moderation_status(post_id, status, moderator, notes)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return PostResponse(**post)

# Statistics endpoints
@router.get("/statistics", response_model=StatisticsResponse, tags=["Statistics"])
async def get_statistics():
    """Get comprehensive statistics"""
    stats = StatisticsService.get_statistics()
    return StatisticsResponse(**stats)

# Scraping endpoints
@router.post("/scrape", response_model=List[ScrapingResultResponse], tags=["Scraping"])
async def scrape_channels(request: ScrapingRequest):
    """Scrape channels"""
    try:
        results = await ScrapingService.scrape_channels(request)
        return [
            ScrapingResultResponse(
                channel_name=result["channel_name"],
                posts_found=result["posts_found"],
                posts_new=result["posts_new"],
                posts_duplicate=result["posts_duplicate"],
                images_downloaded=result["images_downloaded"],
                error=result["error"],
                status="success" if not result["error"] else "error"
            )
            for result in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

# Log endpoints
@router.get("/logs", response_model=PaginatedResponse, tags=["Logs"])
async def get_logs(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size")
):
    """Get scraping logs with pagination"""
    result = LogService.get_logs(page=page, size=size)
    logs = [ScrapingLogResponse(**log) for log in result["items"]]
    
    return PaginatedResponse(
        items=logs,
        total=result["total"],
        page=result["page"],
        size=result["size"],
        pages=result["pages"]
    )

# Health check endpoint
@router.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()} 