import os
import sys
from loguru import logger
import time
import signal
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# Добавляем текущую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импортируем модули проекта
from config import config
from utils.logger import setup_logger
from utils.helpers import create_project_dirs
from database.db_handler import DatabaseHandler
from browser_manager.browser import BrowserHandler
from browser_manager.actions import BookingChecker
from telegram_bot.bot import TelegramBot
from core.slot_checker import SlotChecker
from core.notifications import NotificationManager
from config.settings import settings
from metrics.prometheus import ACTIVE_CHECKS

# Флаг для корректного завершения
should_exit = False

class BookingBot:
    """
    Main application class that handles bot commands and monitoring.
    """
    
    def __init__(self):
        self.slot_checker = SlotChecker()
        self.notifier = NotificationManager()
        self.db = DatabaseHandler()
        self.active_monitors = {}  # chat_id -> monitoring task
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        chat_id = update.effective_chat.id
        
        # Остановим предыдущий мониторинг если есть
        await self.stop_monitoring(chat_id)
        
        # Запрашиваем предпочтительный диапазон дат
        keyboard = [
            ["неделя", "две недели"],
            ["месяц", "любой период"]
        ]
        
        await context.bot.send_message(
            chat_id=chat_id,
            text="Выберите предпочтительный диапазон дат для мониторинга:",
            reply_markup={"keyboard": keyboard, "one_time_keyboard": True}
        )
        
    async def handle_range_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle date range selection."""
        chat_id = update.effective_chat.id
        selected_range = update.message.text.lower()
        
        range_mapping = {
            "неделя": "week",
            "две недели": "two_weeks",
            "месяц": "month",
            "любой период": "any"
        }
        
        preferred_range = range_mapping.get(selected_range)
        if not preferred_range:
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ Неверный выбор диапазона. Используйте кнопки."
            )
            return
            
        # Сохраняем предпочтения пользователя
        self.db.update_user_preferred_dates(chat_id, preferred_range)
        
        # Запускаем мониторинг
        await self.start_monitoring(chat_id, preferred_range)
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ Мониторинг запущен!\n"
                 f"📅 Выбранный диапазон: {selected_range}\n"
                 f"ℹ️ Вы будете получать уведомления о новых слотах."
        )
        
    async def stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stop command."""
        chat_id = update.effective_chat.id
        await self.stop_monitoring(chat_id)
        
        await context.bot.send_message(
            chat_id=chat_id,
            text="🛑 Мониторинг остановлен."
        )
        
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        chat_id = update.effective_chat.id
        
        is_active = chat_id in self.active_monitors
        preferred_range = self.db.get_user_preferred_dates(chat_id) or "any"
        
        status_text = (
            f"📊 *Статус мониторинга*\n\n"
            f"🔄 Активен: {'✅' if is_active else '❌'}\n"
            f"📅 Диапазон дат: {self.slot_checker._get_range_text(preferred_range)}\n"
            f"👥 Всего активных проверок: {len(self.active_monitors)}"
        )
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=status_text,
            parse_mode='Markdown'
        )
        
    async def start_monitoring(self, chat_id: int, preferred_range: str):
        """Start monitoring for a specific user."""
        if chat_id in self.active_monitors:
            await self.stop_monitoring(chat_id)
            
        # Создаем новую задачу мониторинга
        task = asyncio.create_task(
            self.slot_checker.start_monitoring(chat_id, preferred_range)
        )
        self.active_monitors[chat_id] = task
        
    async def stop_monitoring(self, chat_id: int):
        """Stop monitoring for a specific user."""
        if chat_id in self.active_monitors:
            task = self.active_monitors.pop(chat_id)
            self.slot_checker.stop_event.set()
            await task
            self.slot_checker.stop_event.clear()
            
    async def stop_all_monitoring(self):
        """Stop all monitoring tasks."""
        tasks = []
        for chat_id in list(self.active_monitors.keys()):
            tasks.append(self.stop_monitoring(chat_id))
        if tasks:
            await asyncio.gather(*tasks)

def signal_handler(sig, frame):
    """Обработчик сигналов завершения (Ctrl+C)."""
    global should_exit
    logger.info("Получен сигнал завершения. Завершаем работу...")
    should_exit = True

def main():
    """Main application entry point."""
    try:
        # Настройка логирования
        logger.add(
            "logs/app.log",
            rotation="1 day",
            retention="7 days",
            level="INFO"
        )
        
        # Инициализация бота
        bot = BookingBot()
        application = Application.builder().token(settings.notifications.telegram_token).build()
        
        # Регистрация обработчиков команд
        application.add_handler(CommandHandler("start", bot.start_command))
        application.add_handler(CommandHandler("stop", bot.stop_command))
        application.add_handler(CommandHandler("status", bot.status_command))
        application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                bot.handle_range_selection
            )
        )
        
        # Обработка сигналов завершения
        def signal_handler(signum, frame):
            logger.info("Получен сигнал завершения. Останавливаем мониторинг...")
            asyncio.create_task(bot.stop_all_monitoring())
            application.stop()
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Запуск бота
        logger.info("Запуск Telegram-бота для мониторинга бронирования")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 