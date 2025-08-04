import os
import hashlib
import aiofiles
import httpx
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image
import io
from google.cloud import storage
from loguru import logger

from ..config.settings import Config

class ImageProcessor:
    def __init__(self):
        self.gcs_client = None
        self.bucket = None
        self._setup_gcs()
    
    def _setup_gcs(self):
        """Setup Google Cloud Storage client"""
        try:
            if Config.GCS_CREDENTIALS_PATH and os.path.exists(Config.GCS_CREDENTIALS_PATH):
                self.gcs_client = storage.Client.from_service_account_json(Config.GCS_CREDENTIALS_PATH)
            else:
                # Try to use default credentials
                self.gcs_client = storage.Client()
            
            self.bucket = self.gcs_client.bucket(Config.GCS_BUCKET_NAME)
            logger.info(f"GCS client initialized with bucket: {Config.GCS_BUCKET_NAME}")
        except Exception as e:
            logger.warning(f"Failed to initialize GCS client: {e}")
            self.gcs_client = None
            self.bucket = None
    
    async def download_image(self, url: str, filename: str = None) -> Optional[Tuple[str, str]]:
        """
        Download image from URL and save to local storage
        
        Returns:
            Tuple of (local_path, gcs_url) or None if failed
        """
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                # Validate image
                image_data = response.content
                if len(image_data) > Config.MAX_IMAGE_SIZE:
                    logger.warning(f"Image too large: {len(image_data)} bytes")
                    return None
                
                # Process image with PIL
                image = Image.open(io.BytesIO(image_data))
                
                # Convert to RGB if necessary
                if image.mode in ('RGBA', 'LA', 'P'):
                    image = image.convert('RGB')
                
                # Generate filename if not provided
                if not filename:
                    file_hash = hashlib.md5(image_data).hexdigest()
                    extension = self._get_extension_from_url(url) or '.jpg'
                    filename = f"{file_hash}{extension}"
                
                # Save to local storage
                local_path = Config.IMAGES_DIR / filename
                image.save(local_path, 'JPEG', quality=85, optimize=True)
                
                # Upload to GCS
                gcs_url = await self._upload_to_gcs(local_path, filename)
                
                logger.info(f"Image downloaded and uploaded: {local_path} -> {gcs_url}")
                return str(local_path), gcs_url
                
        except Exception as e:
            logger.error(f"Failed to download image from {url}: {e}")
            return None
    
    async def _upload_to_gcs(self, local_path: Path, filename: str) -> Optional[str]:
        """Upload image to Google Cloud Storage and return normal GCS URL"""
        if not self.bucket:
            logger.warning("GCS not configured, skipping upload")
            return None
        
        try:
            blob = self.bucket.blob(f"telegram_images/{filename}")
            blob.upload_from_filename(str(local_path))
            
            # Return normal GCS URL
            gcs_url = f"https://storage.googleapis.com/{Config.GCS_BUCKET_NAME}/telegram_images/{filename}"
            
            logger.info(f"Uploaded to GCS with normal URL: {gcs_url}")
            return gcs_url
            
        except Exception as e:
            logger.error(f"Failed to upload to GCS: {e}")
            return None
    
    def _get_extension_from_url(self, url: str) -> Optional[str]:
        """Extract file extension from URL"""
        for ext in Config.SUPPORTED_IMAGE_FORMATS:
            if ext in url.lower():
                return ext
        return None
    
    def cleanup_local_image(self, local_path: str):
        """Remove local image file"""
        try:
            path = Path(local_path)
            if path.exists():
                path.unlink()
                logger.debug(f"Cleaned up local image: {local_path}")
        except Exception as e:
            logger.error(f"Failed to cleanup local image {local_path}: {e}")
    
    def make_existing_image_public(self, gcs_url: str) -> Optional[str]:
        """Make an existing image in GCS publicly accessible"""
        if not self.bucket or not gcs_url:
            return None
        
        try:
            # Extract blob name from GCS URL
            # URL format: https://storage.googleapis.com/bucket-name/path/to/file
            url_parts = gcs_url.replace("https://storage.googleapis.com/", "").split("/")
            if len(url_parts) < 2:
                logger.error(f"Invalid GCS URL format: {gcs_url}")
                return None
            
            bucket_name = url_parts[0]
            blob_name = "/".join(url_parts[1:])
            
            # Get the blob
            blob = self.bucket.blob(blob_name)
            
            # Check if blob exists
            if not blob.exists():
                logger.warning(f"Blob does not exist: {blob_name}")
                return None
            
            # Make the blob publicly accessible
            blob.make_public()
            
            # Return the public URL
            public_url = f"https://storage.googleapis.com/{Config.GCS_BUCKET_NAME}/{blob_name}"
            
            logger.info(f"Made existing image public: {public_url}")
            return public_url
            
        except Exception as e:
            logger.error(f"Failed to make image public for {gcs_url}: {e}")
            return None

# Global image processor instance
image_processor = ImageProcessor() 