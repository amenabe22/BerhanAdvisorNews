import sys
from pathlib import Path
from loguru import logger
from ..config.settings import Config

def setup_logger():
    """Setup logger with file and console output"""
    # Remove default logger
    logger.remove()
    
    # Add console logger
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=Config.LOG_LEVEL,
        colorize=True
    )
    
    # Add file logger
    logger.add(
        Config.LOG_FILE,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=Config.LOG_LEVEL,
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )
    
    return logger

# Initialize logger
setup_logger() 