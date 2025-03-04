import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

class Config:
    # Токен Telegram бота
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # Настройки браузера
    BROWSER_HEADLESS = True
    BROWSER_TIMEOUT = 30
    
    # URL для проверки
    TARGET_URL = "https://www.berlin.de/labo/mobil/dienstleistungen/termin/"
    
    # Интервал проверки в секундах
    CHECK_INTERVAL = 60
    
    # Настройки логирования
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "{time} {level} {message}" 