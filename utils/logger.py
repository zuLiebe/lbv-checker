from loguru import logger
import sys
from ..config.config import Config

def setup_logger():
    """Configure logging settings"""
    # Remove default handler
    logger.remove()
    
    # Add new handler with configured format
    logger.add(
        sys.stderr,
        format=Config.LOG_FORMAT,
        level=Config.LOG_LEVEL
    )
    
    # Add file handler for logging to file
    logger.add(
        "bot.log",
        rotation="1 day",
        retention="7 days",
        format=Config.LOG_FORMAT,
        level=Config.LOG_LEVEL
    )
    
    return logger 