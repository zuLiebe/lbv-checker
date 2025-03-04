from typing import Optional, List, Tuple, Dict
from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import asyncio
import time

from core.browser import BrowserHandler
from core.notifications import NotificationManager
from config.settings import settings
from exceptions.custom_exceptions import SlotCheckException
from metrics.prometheus import SLOT_CHECK_DURATION, SLOTS_FOUND, ACTIVE_CHECKS

class SlotChecker:
    """
    Enhanced slot checking with metrics, error handling, and notifications.
    """
    
    def __init__(self):
        self.browser = BrowserHandler()
        self.notifier = NotificationManager()
        self.config = settings.slot_checker
        self.stop_event = asyncio.Event()
        
    async def start_monitoring(self, chat_id: int, preferred_range: str = 'any'):
        """Start monitoring slots for a specific user."""
        ACTIVE_CHECKS.inc()
        
        try:
            with self.browser.create_session() as driver:
                while not self.stop_event.is_set():
                    with SLOT_CHECK_DURATION.time():
                        try:
                            available, dates = await self._check_availability(driver)
                            
                            if available:
                                # Проверяем, соответствуют ли даты предпочтительному диапазону
                                is_preferred = self._check_dates_in_range(dates, preferred_range)
                                
                                if is_preferred:
                                    # Отправляем уведомление со звуком только если даты в диапазоне
                                    await self._notify_slots_found(
                                        chat_id,
                                        dates,
                                        preferred_range,
                                        disable_notification=False
                                    )
                                    SLOTS_FOUND.labels(location='preferred').inc()
                                else:
                                    # Тихо обновляем сообщение если даты не в диапазоне
                                    await self._update_status(
                                        chat_id,
                                        dates,
                                        preferred_range
                                    )
                                    SLOTS_FOUND.labels(location='other').inc()
                            else:
                                # Обновляем статус без звука
                                await self._update_status(
                                    chat_id,
                                    [],
                                    preferred_range
                                )
                            
                        except Exception as e:
                            logger.error(f"Error during slot check: {e}")
                            await self._notify_error(chat_id, str(e))
                            
                    # Случайная задержка между проверками
                    delay = self._get_random_delay()
                    await asyncio.sleep(delay)
                    
        finally:
            ACTIVE_CHECKS.dec()
            
    def stop_monitoring(self):
        """Stop the monitoring process."""
        self.stop_event.set()
        
    async def _check_availability(self, driver) -> Tuple[bool, List[str]]:
        """Check slot availability with enhanced error handling."""
        try:
            # Проверка календаря
            calendar = self.browser.wait_for_element(
                driver,
                (By.CLASS_NAME, "calendar")
            )
            
            if not calendar:
                return False, []
                
            # Поиск активных дат
            available_days = calendar.find_elements(
                By.CSS_SELECTOR,
                ".calendar-day:not(.disabled)"
            )
            
            if not available_days:
                return False, []
                
            # Извлечение дат
            dates = []
            for day in available_days:
                date = day.get_attribute("data-date")
                if date:
                    dates.append(date)
                    self.browser.highlight_element(driver, day, "green")
                    
            return bool(dates), dates
            
        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            raise SlotCheckException(f"Failed to check slots: {e}")
            
    def _check_dates_in_range(self, dates: List[str], preferred_range: str) -> bool:
        """Check if dates are within preferred range."""
        if not dates or preferred_range == 'any':
            return True
            
        # Здесь ваша логика проверки дат
        from utils.date_utils import check_if_dates_in_range
        return check_if_dates_in_range(dates, preferred_range)
        
    async def _notify_slots_found(self,
                                chat_id: int,
                                dates: List[str],
                                preferred_range: str,
                                disable_notification: bool = True):
        """Send notification about found slots."""
        range_text = self._get_range_text(preferred_range)
        
        message = (
            f"🎯 *Найдены доступные слоты!*\n\n"
            f"📅 Даты: {', '.join(dates)}\n"
            f"🔍 Ваш диапазон: {range_text}\n\n"
            f"_Мониторинг продолжает работать_"
        )
        
        await self.notifier.send_notification(
            chat_id,
            message,
            disable_notification=disable_notification
        )
        
    async def _update_status(self,
                           chat_id: int,
                           dates: List[str],
                           preferred_range: str):
        """Update status message without notification."""
        range_text = self._get_range_text(preferred_range)
        
        if dates:
            message = (
                f"ℹ️ *Статус мониторинга*\n\n"
                f"📅 Найдены даты: {', '.join(dates)}\n"
                f"⚠️ Даты НЕ в выбранном диапазоне\n"
                f"🔍 Ваш диапазон: {range_text}"
            )
        else:
            message = (
                f"ℹ️ *Статус мониторинга*\n\n"
                f"❌ Доступных слотов не найдено\n"
                f"🔍 Ваш диапазон: {range_text}"
            )
            
        await self.notifier.update_message(chat_id, message)
        
    def _get_range_text(self, preferred_range: str) -> str:
        """Get human-readable range text."""
        ranges = {
            'week': 'неделя',
            'two_weeks': 'две недели',
            'month': 'месяц',
            'any': 'любой период'
        }
        return ranges.get(preferred_range, 'любой период')
        
    def _get_random_delay(self) -> int:
        """Get random delay between checks."""
        import random
        base_delay = self.config.check_interval
        return random.randint(base_delay - 60, base_delay + 60) 