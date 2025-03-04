import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler
from telegram.ext._context import CallbackContext
from loguru import logger
import os
from dotenv import load_dotenv
from .browser import BrowserHandler
import time

# Загрузка переменных окружения
load_dotenv()

class AppointmentBot:
    def __init__(self):
        self.token = os.getenv('BOT_TOKEN')
        if not self.token:
            raise ValueError("BOT_TOKEN не найден в переменных окружения")
            
        self.browser = BrowserHandler(headless=True)
        self.checking = False
        self.driver = None
        
    async def start(self, update: Update, context: CallbackContext) -> None:
        """Обработчик команды /start"""
        if update.message:
            await update.message.reply_text(
                "Привет! Я бот для проверки доступных слотов записи в LBV.\n"
                "Используйте /check для начала проверки\n"
                "Используйте /stop для остановки проверки"
            )

    async def check_command(self, update: Update, context: CallbackContext) -> None:
        """Обработчик команды /check"""
        if not update.message:
            return
            
        if self.checking:
            await update.message.reply_text("Проверка уже запущена!")
            return
            
        self.checking = True
        await update.message.reply_text("Начинаю проверку слотов...")
        
        try:
            self.driver = self.browser.init_driver()
            while self.checking:
                try:
                    # Открываем страницу
                    self.driver.get("https://www.berlin.de/labo/mobil/dienstleistungen/termin/")
                    
                    # Проверяем слоты
                    has_slots, message = self.browser.check_slots(self.driver)
                    
                    if has_slots and update.message:
                        await update.message.reply_text(
                            f"🎉 Найдены свободные слоты!\n{message}\n"
                            "Перейдите по ссылке: https://www.berlin.de/labo/mobil/dienstleistungen/termin/"
                        )
                        break
                    
                    # Ждем перед следующей проверкой
                    await asyncio.sleep(60)
                    
                except Exception as e:
                    logger.error(f"Ошибка при проверке: {e}")
                    if update.message:
                        await update.message.reply_text(f"Произошла ошибка: {str(e)}")
                    break
                    
        finally:
            self.checking = False
            if self.driver:
                self.browser.close(self.driver)
                self.driver = None

    async def stop_command(self, update: Update, context: CallbackContext) -> None:
        """Обработчик команды /stop"""
        if not update.message:
            return
            
        if not self.checking:
            await update.message.reply_text("Проверка не запущена!")
            return
            
        self.checking = False
        await update.message.reply_text("Останавливаю проверку...")
        
        if self.driver:
            self.browser.close(self.driver)
            self.driver = None

    def run(self):
        """Запускает бота"""
        try:
            application = Application.builder().token(self.token).build()
            
            # Регистрация обработчиков команд
            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(CommandHandler("check", self.check_command))
            application.add_handler(CommandHandler("stop", self.stop_command))
            
            # Запуск бота
            application.run_polling()
        except Exception as e:
            logger.error(f"Ошибка при запуске бота: {e}")
            print(f"Ошибка при запуске бота: {str(e)}")

if __name__ == "__main__":
    bot = AppointmentBot()
    bot.run() 