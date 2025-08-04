import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.tl.types import Message, MessageMediaPhoto, MessageMediaDocument
from telethon.errors import FloodWaitError, ChannelPrivateError, ChatAdminRequiredError
from sqlalchemy.orm import Session
from loguru import logger
import re
from pathlib import Path

from ..config.settings import Config
from ..models.database import TelegramChannel, TelegramPost, ScrapingLog
from ..core.database import db_manager
from ..utils.image_processor import image_processor

class TelegramScraper:
    def __init__(self):
        self.client = None
        self._setup_client()
    
    def _setup_client(self):
        """Setup Telegram client"""
        if not all([Config.TELEGRAM_API_ID, Config.TELEGRAM_API_HASH, Config.TELEGRAM_PHONE]):
            raise ValueError("Telegram API credentials not configured. Please set TELEGRAM_API_ID, TELEGRAM_API_HASH, and TELEGRAM_PHONE environment variables.")
        
        self.client = TelegramClient(
            Config.TELEGRAM_SESSION_NAME,
            Config.TELEGRAM_API_ID,
            Config.TELEGRAM_API_HASH
        )
    
    async def start(self):
        """Start the Telegram client"""
        await self.client.start(phone=Config.TELEGRAM_PHONE)
        logger.info("Telegram client started successfully")
    
    async def stop(self):
        """Stop the Telegram client"""
        if self.client:
            await self.client.disconnect()
            logger.info("Telegram client stopped")
    
    async def scrape_channel(self, channel_config: Config.TELEGRAM_CHANNELS, max_posts: int = 10, force: bool = False) -> Dict[str, Any]:
        """Scrape posts from a Telegram channel"""
        start_time = datetime.now()
        result = {
            'channel_name': channel_config.name,
            'posts_found': 0,
            'posts_new': 0,
            'posts_duplicate': 0,
            'images_downloaded': 0,
            'error': None
        }
        
        try:
            # Get or create channel in database
            with db_manager.get_session() as session:
                channel = self._get_or_create_channel(session, channel_config)
                
                # Get latest posts from Telegram
                posts = await self._get_channel_posts(channel_config.username, max_posts)
                result['posts_found'] = len(posts)
                
                for message in posts:
                    try:
                        # Check if post already exists
                        existing_post = session.query(TelegramPost).filter_by(
                            telegram_id=message.id
                        ).first()
                        
                        if existing_post:
                            if force:
                                # Update existing post with new data
                                formatted_content = self._extract_formatted_content(message)
                                existing_post.title = self._extract_title(formatted_content)
                                existing_post.content = formatted_content
                                existing_post.excerpt = self._extract_excerpt(formatted_content)
                                existing_post.published_date = message.date
                                existing_post.views = message.views
                                existing_post.forwards = message.forwards
                                existing_post.replies = message.reply_to_msg_id
                                existing_post.has_media = bool(message.media)
                                existing_post.media_type = self._get_media_type(message.media)
                                existing_post.scraped_date = datetime.now()
                                session.commit()
                                result['posts_new'] += 1  # Count as new since we updated it
                            else:
                                result['posts_duplicate'] += 1
                                continue
                        else:
                            # Process and save new post
                            await self._process_post(session, channel, message)
                            result['posts_new'] += 1
                        
                        # Download images if present
                        if message.media:
                            image_result = await self._process_post_media(message)
                            if image_result and image_result.get('gcs_url'):
                                # Update post with GCS URL
                                # We need to get the saved post to update it
                                saved_post = session.query(TelegramPost).filter_by(
                                    telegram_id=message.id
                                ).first()
                                if saved_post:
                                    saved_post.gcs_image_url = image_result['gcs_url']
                                    session.commit()
                                result['images_downloaded'] += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing post {message.id}: {e}")
                        continue
                
                # Update channel last_scraped
                channel.last_scraped = datetime.now()
                session.commit()
                
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Error scraping channel {channel_config.name}: {e}")
        
        # Log scraping result
        duration = (datetime.now() - start_time).total_seconds()
        await self._log_scraping_result(channel_config.name, result, duration)
        
        return result
    
    def _get_or_create_channel(self, session: Session, channel_config: Config.TELEGRAM_CHANNELS) -> TelegramChannel:
        """Get or create channel in database"""
        channel = session.query(TelegramChannel).filter_by(
            username=channel_config.username
        ).first()
        
        if not channel:
            channel = TelegramChannel(
                name=channel_config.name,
                username=channel_config.username,
                url=channel_config.url,
                category=channel_config.category,
                language=channel_config.language,
                is_active=channel_config.is_active
            )
            session.add(channel)
            session.commit()
            session.refresh(channel)
            logger.info(f"Created new channel: {channel_config.name}")
        
        return channel
    
    async def _get_channel_posts(self, username: str, max_posts: int) -> List[Message]:
        """Get latest posts from Telegram channel"""
        try:
            entity = await self.client.get_entity(username)
            posts = []
            
            async for message in self.client.iter_messages(entity, limit=max_posts):
                if message and message.text:  # Only process messages with text
                    posts.append(message)
            
            logger.info(f"Retrieved {len(posts)} posts from {username}")
            return posts
            
        except ChannelPrivateError:
            logger.error(f"Channel {username} is private or not accessible")
            return []
        except ChatAdminRequiredError:
            logger.error(f"Admin access required for channel {username}")
            return []
        except Exception as e:
            logger.error(f"Error getting posts from {username}: {e}")
            return []
    
    async def _process_post(self, session: Session, channel: TelegramChannel, message: Message):
        """Process and save a Telegram post"""
        # Extract content with formatting
        content = self._extract_formatted_content(message)
        title = self._extract_title(content)
        excerpt = self._extract_excerpt(content)
        
        # Create post object
        post = TelegramPost(
            telegram_id=message.id,
            title=title,
            content=content,
            excerpt=excerpt,
            published_date=message.date,
            channel_id=channel.id,
            category=channel.category,
            language=channel.language,
            views=message.views,
            forwards=message.forwards,
            replies=message.reply_to_msg_id,
            has_media=bool(message.media),
            media_type=self._get_media_type(message.media)
        )
        
        session.add(post)
        session.commit()
        session.refresh(post)
        
        logger.debug(f"Saved post {message.id} from {channel.name}")
    
    def _extract_formatted_content(self, message: Message) -> str:
        """Extract formatted content from Telegram message"""
        if not message.text:
            return ""
        
        # Get the raw text
        text = message.text
        
        # If message has formatting entities, convert them to HTML
        if message.entities:
            try:
                # Convert entities to HTML formatting
                formatted_text = ""
                last_offset = 0
                
                for entity in message.entities:
                    # Add text before this entity
                    formatted_text += text[last_offset:entity.offset]
                    
                    # Apply formatting based on entity type
                    entity_text = text[entity.offset:entity.offset + entity.length]
                    
                    if hasattr(entity, 'bold') and entity.bold:
                        formatted_text += f"<strong>{entity_text}</strong>"
                    elif hasattr(entity, 'italic') and entity.italic:
                        formatted_text += f"<em>{entity_text}</em>"
                    elif hasattr(entity, 'code') and entity.code:
                        formatted_text += f"<code>{entity_text}</code>"
                    elif hasattr(entity, 'url') and entity.url:
                        formatted_text += f'<a href="{entity.url}" target="_blank">{entity_text}</a>'
                    elif hasattr(entity, 'pre') and entity.pre:
                        formatted_text += f"<pre>{entity_text}</pre>"
                    else:
                        formatted_text += entity_text
                    
                    last_offset = entity.offset + entity.length
                
                # Add remaining text
                formatted_text += text[last_offset:]
                return formatted_text
                
            except Exception as e:
                logger.warning(f"Error processing message entities: {e}")
                return text
        
        return text
    
    async def _process_post_media(self, message: Message) -> Optional[Dict[str, str]]:
        """Process media from a Telegram post"""
        if not message.media:
            return None
        
        try:
            if isinstance(message.media, MessageMediaPhoto):
                # Download photo
                photo_path = await self.client.download_media(message.media)
                if photo_path:
                    # Upload to GCS
                    gcs_url = await image_processor._upload_to_gcs(
                        Path(photo_path), 
                        f"telegram_photo_{message.id}.jpg"
                    )
                    
                    # Cleanup local file
                    image_processor.cleanup_local_image(photo_path)
                    
                    return {
                        'local_path': photo_path,
                        'gcs_url': gcs_url
                    }
            
            elif isinstance(message.media, MessageMediaDocument):
                # Handle documents (could be images)
                doc_path = await self.client.download_media(message.media)
                if doc_path and self._is_image_file(doc_path):
                    gcs_url = await image_processor._upload_to_gcs(
                        Path(doc_path),
                        f"telegram_doc_{message.id}.jpg"
                    )
                    
                    image_processor.cleanup_local_image(doc_path)
                    
                    return {
                        'local_path': doc_path,
                        'gcs_url': gcs_url
                    }
        
        except Exception as e:
            logger.error(f"Error processing media for post {message.id}: {e}")
        
        return None
    
    def _extract_title(self, content: str) -> Optional[str]:
        """Extract title from post content"""
        if not content:
            return None
        
        # Take first line as title if it's short enough
        lines = content.split('\n')
        first_line = lines[0].strip()
        
        if len(first_line) <= 200 and len(first_line) > 10:
            return first_line
        
        # If no suitable title found, create one from content
        if content:
            # Take first 60 characters and clean it up
            title = content.strip()[:60]
            # Remove extra whitespace and newlines
            title = ' '.join(title.split())
            # Add ellipsis if content was longer
            if len(content.strip()) > 60:
                title += '...'
            return title
        
        return None
    
    def _extract_excerpt(self, content: str) -> Optional[str]:
        """Extract excerpt from post content"""
        if not content:
            return None
        
        # Remove title if it exists
        lines = content.split('\n')
        if len(lines) > 1:
            excerpt = '\n'.join(lines[1:]).strip()
            return excerpt[:500] + '...' if len(excerpt) > 500 else excerpt
        
        return content[:500] + '...' if len(content) > 500 else content
    
    def _get_media_type(self, media) -> Optional[str]:
        """Get media type from Telegram message"""
        if isinstance(media, MessageMediaPhoto):
            return 'photo'
        elif isinstance(media, MessageMediaDocument):
            return 'document'
        return None
    
    def _is_image_file(self, file_path: str) -> bool:
        """Check if file is an image"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        return any(file_path.lower().endswith(ext) for ext in image_extensions)
    
    async def _log_scraping_result(self, channel_name: str, result: Dict[str, Any], duration: float):
        """Log scraping result to database"""
        try:
            with db_manager.get_session() as session:
                # Find channel
                channel = session.query(TelegramChannel).filter_by(name=channel_name).first()
                if not channel:
                    return
                
                # Create log entry
                log = ScrapingLog(
                    channel_id=channel.id,
                    status='success' if not result['error'] else 'error',
                    posts_found=result['posts_found'],
                    posts_new=result['posts_new'],
                    posts_duplicate=result['posts_duplicate'],
                    images_downloaded=result['images_downloaded'],
                    error_message=result['error'],
                    duration=duration
                )
                
                session.add(log)
                session.commit()
                
        except Exception as e:
            logger.error(f"Error logging scraping result: {e}")
    
    async def scrape_all_channels(self, max_posts_per_channel: int = 10) -> List[Dict[str, Any]]:
        """Scrape all configured channels"""
        results = []
        
        for channel_config in Config.TELEGRAM_CHANNELS:
            if not channel_config.is_active:
                continue
            
            logger.info(f"Scraping channel: {channel_config.name}")
            result = await self.scrape_channel(channel_config, max_posts_per_channel)
            results.append(result)
            
            # Rate limiting between channels
            await asyncio.sleep(Config.RATE_LIMIT_DELAY)
        
        return results 