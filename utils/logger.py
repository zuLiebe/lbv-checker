from loguru import logger
import sys
import os

def setup_logger(log_path, log_level="INFO"):
    """Настраивает логирование в файл и консоль."""
    # Очищаем предыдущие настройки
    logger.remove()
    
    # Создаем директорию для логов, если она не существует
    log_dir = os.path.dirname(log_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Настраиваем вывод в консоль
    logger.add(sys.stdout, level=log_level)
    
    # Настраиваем вывод в файл
    logger.add(log_path, rotation="1 day", level=log_level)
    
    return logger 