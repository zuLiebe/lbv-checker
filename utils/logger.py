from loguru import logger
import sys
from ..config.config import Config

def setup_logger():
    """Настраивает логирование"""
    # Удаляем стандартный обработчик
    logger.remove()
    
    # Добавляем новый обработчик с настроенным форматом
    logger.add(
        sys.stderr,
        format=Config.LOG_FORMAT,
        level=Config.LOG_LEVEL
    )
    
    # Добавляем файловый обработчик для записи логов в файл
    logger.add(
        "bot.log",
        rotation="1 day",
        retention="7 days",
        format=Config.LOG_FORMAT,
        level=Config.LOG_LEVEL
    )
    
    return logger 