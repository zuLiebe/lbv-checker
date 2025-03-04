#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Запуск Telegram-бота для мониторинга бронирования
"""

import os
import sys
from loguru import logger
import time
import signal

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

# Флаг для корректного завершения
should_exit = False

def signal_handler(sig, frame):
    """Обработчик сигналов завершения (Ctrl+C)."""
    global should_exit
    logger.info("Получен сигнал завершения. Завершаем работу...")
    should_exit = True

def main():
    """Основная функция для запуска бота."""
    # Настраиваем обработчик сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Создаем необходимые директории
    create_project_dirs([
        'logs',
        'database',
        os.path.dirname("database/" + config.DB_NAME)
    ])
    
    # Настраиваем логирование
    setup_logger(config.LOG_PATH, config.LOG_LEVEL)
    logger.info("Запуск Telegram-бота для мониторинга бронирования")
    
    try:
        # Инициализируем обработчик базы данных
        db_path = "database/" + config.DB_NAME
        db_handler = DatabaseHandler(db_path)
        logger.info("База данных инициализирована")
        
        # Инициализируем обработчик браузера
        browser_handler = BrowserHandler(
            headless=config.HEADLESS_MODE,
            timeout=config.SELENIUM_TIMEOUT
        )
        
        # Получаем драйвер браузера
        driver = browser_handler.start()
        logger.info("Браузер запущен")
        
        # Инициализируем обработчик бронирования
        booking_checker = BookingChecker(
            driver=driver,
            site_url=config.FRONTEND_URL
        )
        
        # Инициализируем Telegram бота
        bot = TelegramBot(
            token=config.TELEGRAM_TOKEN,
            db_handler=db_handler,
            booking_checker=booking_checker,
            config=config
        )
        
        # Запускаем бота
        bot.start()  # синхронный вызов для версии 13.x
        logger.info("Telegram-бот запущен и ожидает команд")
        logger.info("Отправьте 'старт' в бот для запуска мониторинга")
        
        # Основной цикл программы
        while not should_exit:
            time.sleep(1)
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        # Корректно закрываем все ресурсы
        try:
            logger.info("Завершение работы приложения")
            
            if 'bot' in locals():
                bot.stop()
            
            if 'browser_handler' in locals() and 'driver' in locals():
                browser_handler.close(driver)
            
            logger.info("Приложение завершено")
        except Exception as e:
            logger.error(f"Ошибка при завершении приложения: {e}")

if __name__ == "__main__":
    main() 