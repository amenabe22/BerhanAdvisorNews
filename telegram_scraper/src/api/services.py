from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
import asyncio

from ..core.database import db_manager
from ..models.database import TelegramChannel, TelegramPost, ScrapingLog
from ..scrapers.telegram_scraper import TelegramScraper
from ..config.settings import Config
from .models import SearchFilters, ScrapingRequest

class ChannelService:
    @staticmethod
    def get_all_channels() -> List[dict]:
        """Get all channels"""
        with db_manager.get_session() as session:
            channels = session.query(TelegramChannel).all()
            return [
                {
                    'id': channel.id,
                    'name': channel.name,
                    'username': channel.username,
                    'url': channel.url,
                    'category': channel.category,
                    'language': channel.language,
                    'is_active': channel.is_active,
                    'last_scraped': channel.last_scraped,
                    'created_at': channel.created_at,
                    'updated_at': channel.updated_at
                }
                for channel in channels
            ]
    
    @staticmethod
    def get_channel_by_id(channel_id: int) -> Optional[dict]:
        """Get channel by ID"""
        with db_manager.get_session() as session:
            channel = session.query(TelegramChannel).filter_by(id=channel_id).first()
            if channel:
                return {
                    'id': channel.id,
                    'name': channel.name,
                    'username': channel.username,
                    'url': channel.url,
                    'category': channel.category,
                    'language': channel.language,
                    'is_active': channel.is_active,
                    'last_scraped': channel.last_scraped,
                    'created_at': channel.created_at,
                    'updated_at': channel.updated_at
                }
            return None
    
    @staticmethod
    def get_channel_by_username(username: str) -> Optional[dict]:
        """Get channel by username"""
        with db_manager.get_session() as session:
            channel = session.query(TelegramChannel).filter_by(username=username).first()
            if channel:
                return {
                    'id': channel.id,
                    'name': channel.name,
                    'username': channel.username,
                    'url': channel.url,
                    'category': channel.category,
                    'language': channel.language,
                    'is_active': channel.is_active,
                    'last_scraped': channel.last_scraped,
                    'created_at': channel.created_at,
                    'updated_at': channel.updated_at
                }
            return None

class PostService:
    @staticmethod
    def get_posts(
        page: int = 1,
        size: int = 20,
        filters: Optional[SearchFilters] = None
    ) -> Dict[str, Any]:
        """Get posts with pagination and filtering"""
        with db_manager.get_session() as session:
            query = session.query(TelegramPost).join(TelegramChannel)
            
            # Apply filters
            if filters:
                if filters.channel_id:
                    query = query.filter(TelegramPost.channel_id == filters.channel_id)
                if filters.category:
                    query = query.filter(TelegramPost.category == filters.category)
                if filters.language:
                    query = query.filter(TelegramPost.language == filters.language)
                if filters.moderation_status:
                    query = query.filter(TelegramPost.moderation_status == filters.moderation_status)
                if filters.has_media is not None:
                    query = query.filter(TelegramPost.has_media == filters.has_media)
                if filters.date_from:
                    query = query.filter(TelegramPost.published_date >= filters.date_from)
                if filters.date_to:
                    query = query.filter(TelegramPost.published_date <= filters.date_to)
                if filters.search:
                    search_term = f"%{filters.search}%"
                    query = query.filter(
                        or_(
                            TelegramPost.title.ilike(search_term),
                            TelegramPost.content.ilike(search_term),
                            TelegramPost.excerpt.ilike(search_term)
                        )
                    )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            posts = query.order_by(TelegramPost.published_date.desc()).offset(offset).limit(size).all()
            
            # Convert posts to dictionaries while still in session
            post_dicts = []
            for post in posts:
                channel_data = None
                if post.channel:
                    channel_data = {
                        'id': post.channel.id,
                        'name': post.channel.name,
                        'username': post.channel.username,
                        'url': post.channel.url,
                        'category': post.channel.category,
                        'language': post.channel.language,
                        'is_active': post.channel.is_active,
                        'last_scraped': post.channel.last_scraped,
                        'created_at': post.channel.created_at,
                        'updated_at': post.channel.updated_at
                    }
                
                post_dicts.append({
                    'id': post.id,
                    'telegram_id': post.telegram_id,
                    'title': post.title,
                    'content': post.content,
                    'excerpt': post.excerpt,
                    'url': post.url,
                    'image_url': post.image_url,
                    'gcs_image_url': post.gcs_image_url,
                    'published_date': post.published_date,
                    'scraped_date': post.scraped_date,
                    'channel_id': post.channel_id,
                    'category': post.category,
                    'language': post.language,
                    'is_duplicate': post.is_duplicate,
                    'similarity_score': post.similarity_score,
                    'views': post.views,
                    'forwards': post.forwards,
                    'replies': post.replies,
                    'has_media': post.has_media,
                    'media_type': post.media_type,
                    'moderation_status': post.moderation_status,
                    'channel': channel_data
                })
            
            return {
                "items": post_dicts,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            }
    
    @staticmethod
    def get_post_by_id(post_id: int) -> Optional[dict]:
        """Get post by ID"""
        with db_manager.get_session() as session:
            post = session.query(TelegramPost).filter_by(id=post_id).first()
            if post:
                channel_data = None
                if post.channel:
                    channel_data = {
                        'id': post.channel.id,
                        'name': post.channel.name,
                        'username': post.channel.username,
                        'url': post.channel.url,
                        'category': post.channel.category,
                        'language': post.channel.language,
                        'is_active': post.channel.is_active,
                        'last_scraped': post.channel.last_scraped,
                        'created_at': post.channel.created_at,
                        'updated_at': post.channel.updated_at
                    }
                
                return {
                    'id': post.id,
                    'telegram_id': post.telegram_id,
                    'title': post.title,
                    'content': post.content,
                    'excerpt': post.excerpt,
                    'url': post.url,
                    'image_url': post.image_url,
                    'gcs_image_url': post.gcs_image_url,
                    'published_date': post.published_date,
                    'scraped_date': post.scraped_date,
                    'channel_id': post.channel_id,
                    'category': post.category,
                    'language': post.language,
                    'is_duplicate': post.is_duplicate,
                    'similarity_score': post.similarity_score,
                    'views': post.views,
                    'forwards': post.forwards,
                    'replies': post.replies,
                    'has_media': post.has_media,
                    'media_type': post.media_type,
                    'moderation_status': post.moderation_status,
                    'channel': channel_data
                }
            return None
    
    @staticmethod
    def get_recent_posts(limit: int = 10) -> List[dict]:
        """Get recent posts"""
        with db_manager.get_session() as session:
            posts = session.query(TelegramPost).order_by(
                TelegramPost.scraped_date.desc()
            ).limit(limit).all()
            
            # Convert posts to dictionaries while still in session
            post_dicts = []
            for post in posts:
                channel_data = None
                if post.channel:
                    channel_data = {
                        'id': post.channel.id,
                        'name': post.channel.name,
                        'username': post.channel.username,
                        'url': post.channel.url,
                        'category': post.channel.category,
                        'language': post.channel.language,
                        'is_active': post.channel.is_active,
                        'last_scraped': post.channel.last_scraped,
                        'created_at': post.channel.created_at,
                        'updated_at': post.channel.updated_at
                    }
                
                post_dicts.append({
                    'id': post.id,
                    'telegram_id': post.telegram_id,
                    'title': post.title,
                    'content': post.content,
                    'excerpt': post.excerpt,
                    'url': post.url,
                    'image_url': post.image_url,
                    'gcs_image_url': post.gcs_image_url,
                    'published_date': post.published_date,
                    'scraped_date': post.scraped_date,
                    'channel_id': post.channel_id,
                    'category': post.category,
                    'language': post.language,
                    'is_duplicate': post.is_duplicate,
                    'similarity_score': post.similarity_score,
                    'views': post.views,
                    'forwards': post.forwards,
                    'replies': post.replies,
                    'has_media': post.has_media,
                    'media_type': post.media_type,
                    'moderation_status': post.moderation_status,
                    'channel': channel_data
                })
            
            return post_dicts
    
    @staticmethod
    def update_moderation_status(post_id: int, status: str, moderator: str = "web_interface", notes: str = None) -> Optional[dict]:
        """Update moderation status of a post"""
        from ..models.database import ModerationStatus
        
        with db_manager.get_session() as session:
            post = session.query(TelegramPost).filter_by(id=post_id).first()
            if not post:
                return None
            
            # Map status string to enum
            status_map = {
                "accepted": ModerationStatus.READY,
                "rejected": ModerationStatus.WRONG,
                "pending": ModerationStatus.PENDING
            }
            
            if status not in status_map:
                return None
            
            # Update moderation fields
            post.moderation_status = status_map[status]
            post.moderated_by = moderator
            post.moderated_at = datetime.now()
            post.moderation_notes = notes
            
            session.commit()
            
            # Return updated post data
            channel_data = None
            if post.channel:
                channel_data = {
                    'id': post.channel.id,
                    'name': post.channel.name,
                    'username': post.channel.username,
                    'url': post.channel.url,
                    'category': post.channel.category,
                    'language': post.channel.language,
                    'is_active': post.channel.is_active,
                    'last_scraped': post.channel.last_scraped,
                    'created_at': post.channel.created_at,
                    'updated_at': post.channel.updated_at
                }
            
            return {
                'id': post.id,
                'telegram_id': post.telegram_id,
                'title': post.title,
                'content': post.content,
                'excerpt': post.excerpt,
                'url': post.url,
                'image_url': post.image_url,
                'gcs_image_url': post.gcs_image_url,
                'published_date': post.published_date,
                'scraped_date': post.scraped_date,
                'channel_id': post.channel_id,
                'category': post.category,
                'language': post.language,
                'is_duplicate': post.is_duplicate,
                'similarity_score': post.similarity_score,
                'views': post.views,
                'forwards': post.forwards,
                'replies': post.replies,
                'has_media': post.has_media,
                'media_type': post.media_type,
                'moderation_status': post.moderation_status,
                'moderated_by': post.moderated_by,
                'moderated_at': post.moderated_at,
                'moderation_notes': post.moderation_notes,
                'channel': channel_data
            }
    
    @staticmethod
    def get_approved_posts(
        page: int = 1,
        size: int = 20,
        channel_id: Optional[int] = None,
        category: Optional[str] = None,
        language: Optional[str] = None,
        has_media: Optional[bool] = None,
        search: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get posts that are not rejected (accepted and pending)"""
        with db_manager.get_session() as session:
            from ..models.database import ModerationStatus
            
            query = session.query(TelegramPost).join(TelegramChannel)
            
            # Filter out rejected posts
            query = query.filter(TelegramPost.moderation_status != ModerationStatus.WRONG)
            
            # Apply other filters
            if channel_id:
                query = query.filter(TelegramPost.channel_id == channel_id)
            if category:
                query = query.filter(TelegramPost.category == category)
            if language:
                query = query.filter(TelegramPost.language == language)
            if has_media is not None:
                query = query.filter(TelegramPost.has_media == has_media)
            if date_from:
                query = query.filter(TelegramPost.published_date >= date_from)
            if date_to:
                query = query.filter(TelegramPost.published_date <= date_to)
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        TelegramPost.title.ilike(search_term),
                        TelegramPost.content.ilike(search_term),
                        TelegramPost.excerpt.ilike(search_term)
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            posts = query.order_by(TelegramPost.published_date.desc()).offset(offset).limit(size).all()
            
            # Convert posts to dictionaries while still in session
            post_dicts = []
            for post in posts:
                channel_data = None
                if post.channel:
                    channel_data = {
                        'id': post.channel.id,
                        'name': post.channel.name,
                        'username': post.channel.username,
                        'url': post.channel.url,
                        'category': post.channel.category,
                        'language': post.channel.language,
                        'is_active': post.channel.is_active,
                        'last_scraped': post.channel.last_scraped,
                        'created_at': post.channel.created_at,
                        'updated_at': post.channel.updated_at
                    }
                
                post_dicts.append({
                    'id': post.id,
                    'telegram_id': post.telegram_id,
                    'title': post.title,
                    'content': post.content,
                    'excerpt': post.excerpt,
                    'url': post.url,
                    'image_url': post.image_url,
                    'gcs_image_url': post.gcs_image_url,
                    'published_date': post.published_date,
                    'scraped_date': post.scraped_date,
                    'channel_id': post.channel_id,
                    'category': post.category,
                    'language': post.language,
                    'is_duplicate': post.is_duplicate,
                    'similarity_score': post.similarity_score,
                    'views': post.views,
                    'forwards': post.forwards,
                    'replies': post.replies,
                    'has_media': post.has_media,
                    'media_type': post.media_type,
                    'moderation_status': post.moderation_status,
                    'channel': channel_data
                })
            
            return {
                "items": post_dicts,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            }

class StatisticsService:
    @staticmethod
    def get_statistics() -> Dict[str, Any]:
        """Get comprehensive statistics"""
        with db_manager.get_session() as session:
            # Basic counts
            total_channels = session.query(TelegramChannel).count()
            total_posts = session.query(TelegramPost).count()
            total_logs = session.query(ScrapingLog).count()
            
            # Posts by category
            posts_by_category = session.query(
                TelegramPost.category,
                func.count(TelegramPost.id)
            ).group_by(TelegramPost.category).all()
            
            # Posts by language
            posts_by_language = session.query(
                TelegramPost.language,
                func.count(TelegramPost.id)
            ).group_by(TelegramPost.language).all()
            
            # Recent activity (last 7 days)
            week_ago = datetime.now() - timedelta(days=7)
            recent_posts = session.query(TelegramPost).filter(
                TelegramPost.scraped_date >= week_ago
            ).count()
            
            recent_logs = session.query(ScrapingLog).filter(
                ScrapingLog.created_at >= week_ago
            ).count()
            
            return {
                "total_channels": total_channels,
                "total_posts": total_posts,
                "total_logs": total_logs,
                "posts_by_category": dict(posts_by_category),
                "posts_by_language": dict(posts_by_language),
                "recent_activity": {
                    "posts_last_7_days": recent_posts,
                    "logs_last_7_days": recent_logs
                }
            }

class ScrapingService:
    @staticmethod
    async def scrape_channels(request: ScrapingRequest) -> List[Dict[str, Any]]:
        """Scrape channels based on request"""
        scraper = TelegramScraper()
        
        try:
            await scraper.start()
            
            # Filter channels if specified
            channels_to_scrape = Config.TELEGRAM_CHANNELS
            if request.channels:
                channels_to_scrape = [
                    ch for ch in Config.TELEGRAM_CHANNELS 
                    if ch.username in request.channels or ch.name.lower() in [c.lower() for c in request.channels]
                ]
            
            results = []
            for channel_config in channels_to_scrape:
                if not channel_config.is_active:
                    continue
                
                result = await scraper.scrape_channel(
                    channel_config, 
                    request.posts_per_channel, 
                    request.force
                )
                results.append(result)
                
                # Rate limiting
                await asyncio.sleep(Config.RATE_LIMIT_DELAY)
            
            return results
            
        finally:
            await scraper.stop()

class LogService:
    @staticmethod
    def get_logs(page: int = 1, size: int = 20) -> Dict[str, Any]:
        """Get scraping logs with pagination"""
        with db_manager.get_session() as session:
            query = session.query(ScrapingLog).join(TelegramChannel)
            total = query.count()
            
            offset = (page - 1) * size
            logs = query.order_by(ScrapingLog.created_at.desc()).offset(offset).limit(size).all()
            
            # Convert logs to dictionaries while still in session
            log_dicts = []
            for log in logs:
                channel_data = None
                if log.channel:
                    channel_data = {
                        'id': log.channel.id,
                        'name': log.channel.name,
                        'username': log.channel.username,
                        'url': log.channel.url,
                        'category': log.channel.category,
                        'language': log.channel.language,
                        'is_active': log.channel.is_active,
                        'last_scraped': log.channel.last_scraped,
                        'created_at': log.channel.created_at,
                        'updated_at': log.channel.updated_at
                    }
                
                log_dicts.append({
                    'id': log.id,
                    'channel_id': log.channel_id,
                    'status': log.status,
                    'posts_found': log.posts_found,
                    'posts_new': log.posts_new,
                    'posts_duplicate': log.posts_duplicate,
                    'images_downloaded': log.images_downloaded,
                    'error_message': log.error_message,
                    'duration': log.duration,
                    'created_at': log.created_at,
                    'channel': channel_data
                })
            
            return {
                "items": log_dicts,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            } 