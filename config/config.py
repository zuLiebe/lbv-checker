# Настройки для Telegram бота и Selenium
import os
from pathlib import Path
from loguru import logger

# Определяем путь к файлу .env
env_path = Path(__file__).parent.parent / '.env'
logger.info(f"Loading .env from: {env_path}")

# Загружаем переменные окружения вручную
env_vars = {}
try:
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    logger.debug(f"Loaded environment variables: {env_vars.keys()}")
except Exception as e:
    logger.error(f"Error reading .env file: {e}")

def get_env(key, default=None):
    """Получает значение переменной окружения"""
    return env_vars.get(key, os.getenv(key, default))

# Проверяем наличие необходимых переменных окружения
required_env_vars = [
    'TELEGRAM_TOKEN',
    'USER_FIRSTNAME',
    'USER_LASTNAME',
    'USER_EMAIL'
]

missing_vars = [var for var in required_env_vars if not get_env(var)]
if missing_vars:
    raise ValueError(f"Отсутствуют необходимые переменные окружения: {', '.join(missing_vars)}")

# Telegram настройки
TELEGRAM_TOKEN = get_env('TELEGRAM_TOKEN')
logger.info(f"Loaded TELEGRAM_TOKEN: {'None' if TELEGRAM_TOKEN is None else TELEGRAM_TOKEN[:10] + '...'}")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN не найден в переменных окружения")

if ':' not in TELEGRAM_TOKEN:
    raise ValueError("Неверный формат TELEGRAM_TOKEN. Токен должен содержать ':'")

# Проверяем базовую структуру токена
token_parts = TELEGRAM_TOKEN.split(':')
if not token_parts[0].isdigit():
    raise ValueError("Первая часть токена должна быть числовым ID бота")

# Настройки сайта
BASE_URL = "https://lbv-termine.de"
FRONTEND_URL = f"{BASE_URL}/frontend"

# Селекторы из lbv.side
SELECTORS = {
    'modal_button': '.btn-primary',
    'category_button': '.row:nth-child(3) > .col-12:nth-child(3) .btn',
    'service_button': '#termin147 .btn',
    'continue_button': '.LBV-choosebutton',
    'privacy_checkbox': 'label',
    'next_button': '#weiterbutton',
    'firstname': '#vorname',
    'lastname': '#nachname',
    'email': '#email'
}

# Данные пользователя для заполнения формы
USER_DATA = {
    'firstname': get_env('USER_FIRSTNAME'),
    'lastname': get_env('USER_LASTNAME'),
    'email': get_env('USER_EMAIL')
}

# Проверяем корректность email
if not USER_DATA['email'] or '@' not in USER_DATA['email']:
    raise ValueError("Некорректный формат email в USER_EMAIL")

# Настройки базы данных
DB_NAME = "booking_bot.db"

# Настройки браузера
BROWSER_WINDOW_SIZE = {
    'width': 945,
    'height': 1028
}

# Настройки Selenium
HEADLESS_MODE = get_env('HEADLESS_MODE', 'false').lower() == 'true'
SELENIUM_TIMEOUT = int(get_env('SELENIUM_TIMEOUT', '30'))

# Настройки проверки бронирования
CHECK_INTERVAL = int(get_env('CHECK_INTERVAL', '60'))

# Настройки логирования
LOG_PATH = "logs/bot.log"
LOG_LEVEL = get_env('LOG_LEVEL', 'INFO')

# Настройки Telegram-уведомлений
DEFAULT_CHAT_IDS = []  # Здесь можно предустановить известные ID чатов

def add_chat_id(chat_id):
    """Добавляет ID чата в список получателей уведомлений"""
    import json
    import os
    
    try:
        chat_ids = []
        if os.path.exists("telegram_users.json"):
            with open("telegram_users.json", "r") as f:
                data = json.load(f)
                chat_ids = data.get("chat_ids", [])
        
        if chat_id not in chat_ids:
            chat_ids.append(chat_id)
            
        with open("telegram_users.json", "w") as f:
            json.dump({"chat_ids": chat_ids}, f, indent=2)
            
        return True
    except Exception as e:
        logger.error(f"Ошибка при добавлении chat_id: {e}")
        return False 