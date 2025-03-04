from typing import Optional, Dict
from loguru import logger
import asyncio
from datetime import datetime

from config.settings import settings
from exceptions.custom_exceptions import NotificationException
from metrics.prometheus import NOTIFICATION_COUNTER, NOTIFICATION_ERRORS

class NotificationManager:
    """
    Handles all notification-related operations with retry logic and metrics.
    """
    
    def __init__(self):
        self.config = settings.notifications
        self.last_message_ids: Dict[int, int] = {}
        
    async def send_notification(self,
                              chat_id: int,
                              message: str,
                              image_path: Optional[str] = None,
                              disable_notification: bool = False) -> bool:
        """
        Send notification with retry logic and metrics.
        """
        for attempt in range(self.config.retry_attempts):
            try:
                # Здесь будет ваш код отправки уведомлений через Telegram
                result = await self._send_telegram_message(
                    chat_id, 
                    message, 
                    image_path, 
                    disable_notification
                )
                
                if result:
                    NOTIFICATION_COUNTER.labels(
                        type='telegram',
                        status='success'
                    ).inc()
                    return True
                    
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {e}")
                NOTIFICATION_ERRORS.labels(error_type=type(e).__name__).inc()
                
                if attempt < self.config.retry_attempts - 1:
                    await asyncio.sleep(self.config.retry_delay)
                    
        NOTIFICATION_COUNTER.labels(type='telegram', status='error').inc()
        return False

    async def update_message(self,
                           chat_id: int,
                           message: str,
                           image_path: Optional[str] = None) -> bool:
        """
        Update existing message instead of sending new one.
        """
        if chat_id not in self.last_message_ids:
            return await self.send_notification(chat_id, message, image_path)
            
        try:
            # Здесь будет ваш код обновления сообщения в Telegram
            message_id = self.last_message_ids[chat_id]
            result = await self._update_telegram_message(
                chat_id,
                message_id,
                message,
                image_path
            )
            
            NOTIFICATION_COUNTER.labels(
                type='update',
                status='success' if result else 'error'
            ).inc()
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to update message: {e}")
            NOTIFICATION_ERRORS.labels(error_type=type(e).__name__).inc()
            return False

    def _save_message_id(self, chat_id: int, message_id: int) -> None:
        """Save message ID for future updates."""
        self.last_message_ids[chat_id] = message_id 