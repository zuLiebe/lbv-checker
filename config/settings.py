from dataclasses import dataclass, field
from typing import Dict, Optional
from pathlib import Path
import os

@dataclass
class BrowserConfig:
    headless: bool = False
    timeout: int = 30
    window_size: Dict[str, int] = field(default_factory=lambda: {'width': 1920, 'height': 1080})
    user_agent: Optional[str] = None
    chrome_options: list = field(default_factory=list)

@dataclass
class NotificationConfig:
    telegram_token: str
    retry_attempts: int = 3
    retry_delay: int = 5
    message_lifetime: int = 3600

@dataclass
class SlotCheckerConfig:
    check_interval: int = 300  # 5 minutes
    max_retries: int = 3
    preferred_locations: list = field(default_factory=list)

class Settings:
    def __init__(self):
        self.browser = BrowserConfig()
        self.notifications = NotificationConfig(
            telegram_token=os.getenv('TELEGRAM_TOKEN', '')
        )
        self.slot_checker = SlotCheckerConfig()
        
    @classmethod
    def from_file(cls, config_path: Path):
        """Load settings from configuration file."""
        # Implementation for loading from file
        pass

settings = Settings() 