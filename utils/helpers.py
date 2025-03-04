import os
import time
from loguru import logger

def create_project_dirs(dirs):
    """Создает требуемые директории для проекта."""
    for directory in dirs:
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError as e:
                print(f"Ошибка при создании директории {directory}: {e}")

def retry_on_exception(func, max_attempts=3, delay=5, exception_types=(Exception,)):
    """
    Декоратор для повторного выполнения функции при возникновении исключения.
    
    Args:
        func: Функция, которую нужно выполнить
        max_attempts: Максимальное количество попыток
        delay: Задержка между попытками (в секундах)
        exception_types: Типы исключений, при которых нужно повторить попытку
    
    Returns:
        Результат выполнения функции или вызывает исключение после последней попытки
    """
    attempt = 1
    
    while attempt <= max_attempts:
        try:
            return func()
        except exception_types as e:
            if attempt == max_attempts:
                logger.error(f"Превышено максимальное количество попыток ({max_attempts}). Последняя ошибка: {e}")
                raise
            
            logger.warning(f"Попытка {attempt} из {max_attempts} не удалась: {e}. Повторная попытка через {delay} сек.")
            time.sleep(delay)
            attempt += 1 