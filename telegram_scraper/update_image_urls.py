#!/usr/bin/env python3
"""
Update existing image URLs with signed URLs that never expire
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.core.database import db_manager
from src.models.database import TelegramPost
from src.utils.image_processor import image_processor
from src.utils.logger import logger

def update_image_urls():
    """Update all existing image URLs with public URLs"""
    
    try:
        with db_manager.get_session() as session:
            # Get all posts with images
            posts = session.query(TelegramPost).filter(
                TelegramPost.gcs_image_url.isnot(None)
            ).all()
            
            logger.info(f"Found {len(posts)} posts with images to update")
            
            updated_count = 0
            failed_count = 0
            
            for post in posts:
                try:
                    # Make existing image publicly accessible
                    public_url = image_processor.make_existing_image_public(post.gcs_image_url)
                    
                    if public_url:
                        # Update the post with public URL
                        post.gcs_image_url = public_url
                        updated_count += 1
                        logger.info(f"Updated post {post.id} with public URL")
                    else:
                        failed_count += 1
                        logger.warning(f"Failed to make image public for post {post.id}")
                        
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Error updating post {post.id}: {e}")
            
            # Commit all changes
            session.commit()
            
            logger.info(f"✅ Successfully updated {updated_count} posts with public URLs")
            if failed_count > 0:
                logger.warning(f"⚠️  Failed to update {failed_count} posts")
                
    except Exception as e:
        logger.error(f"❌ Error updating image URLs: {e}")
        raise

if __name__ == "__main__":
    logger.info("🔄 Starting image URL update process...")
    update_image_urls()
    logger.info("✅ Image URL update process completed!") 