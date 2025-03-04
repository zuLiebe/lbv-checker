import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Telegram bot token
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # Browser settings
    BROWSER_HEADLESS = True
    BROWSER_TIMEOUT = 30
    
    # Target URL for checking appointments
    TARGET_URL = "https://www.berlin.de/labo/mobil/dienstleistungen/termin/"
    
    # Check interval in seconds
    CHECK_INTERVAL = 60
    
    # Logging settings
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "{time} {level} {message}" 