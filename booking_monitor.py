import time
import random
import json
import sys
import os
import requests
from datetime import datetime
from loguru import logger
from browser_manager.browser import BrowserHandler
from config.config import TELEGRAM_TOKEN
from utils.notification import send_telegram_notification, load_chat_ids

# Настройка логирования
logger.remove()
logger.add(sys.stdout, level="INFO")
logger.add("booking_monitor.log", rotation="1 day", level="INFO")

# Глобальные переменные
HISTORY_FILE = "booking_history.json"
LAST_NOTIFICATION_FILE = "last_notification.json"
RANDOM_INTERVAL_MIN = 120  # минимальный интервал в секундах (2 минуты)
RANDOM_INTERVAL_MAX = 240  # максимальный интервал в секундах (4 минуты)

def save_booking_status(status, message):
    """Сохраняет информацию о слотах в историю"""
    try:
        history = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
                
        # Добавляем новую запись
        history.append({
            "timestamp": datetime.now().isoformat(),
            "available": status,
            "message": message
        })
        
        # Ограничиваем историю 100 записями
        if len(history) > 100:
            history = history[-100:]
            
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)
            
        return True
    except Exception as e:
        logger.error(f"Ошибка при сохранении истории: {e}")
        return False

def should_send_notification(status, message):
    """Определяет, нужно ли отправлять уведомление"""
    # Если статус True (найдены слоты), всегда отправляем
    if status:
        return True
        
    try:
        # Проверяем, когда последний раз отправляли уведомление
        if os.path.exists(LAST_NOTIFICATION_FILE):
            with open(LAST_NOTIFICATION_FILE, "r") as f:
                last_notification = json.load(f)
                
            last_time = datetime.fromisoformat(last_notification["timestamp"])
            hours_passed = (datetime.now() - last_time).total_seconds() / 3600
            
            # Отправляем не чаще раза в 6 часов для отрицательных уведомлений
            if hours_passed < 6 and not status:
                return False
                
        return True
    except Exception as e:
        logger.error(f"Ошибка при проверке времени последнего уведомления: {e}")
        return True

def save_notification_time():
    """Сохраняет время отправки уведомления"""
    try:
        data = {
            "timestamp": datetime.now().isoformat()
        }
        with open(LAST_NOTIFICATION_FILE, "w") as f:
            json.dump(data, f)
        return True
    except Exception as e:
        logger.error(f"Ошибка при сохранении времени уведомления: {e}")
        return False

def check_booking_availability():
    """Проверяет доступность слотов и отправляет уведомления"""
    browser = BrowserHandler(headless=False)  # headless=True для фонового режима
    driver = browser.init_driver()
    
    try:
        logger.info("Запуск проверки доступности слотов...")
        available, message = browser.run_selenium_side_script(driver)
        logger.info(f"Результат: Доступность={available}, Сообщение={message}")
        
        # Сохраняем результат в историю
        save_booking_status(available, message)
        
        # Проверяем, нужно ли отправлять уведомление
        if should_send_notification(available, message):
            # Формируем сообщение
            notification_text = f"🔔 *Проверка доступности слотов*\n\n"
            
            if available:
                notification_text += f"✅ *НАЙДЕНЫ ДОСТУПНЫЕ СЛОТЫ!*\n\n{message}\n\nСрочно перейдите на сайт бронирования!"
            else:
                notification_text += f"❌ Слоты недоступны\n\n{message}"
                
            # Отправляем уведомление
            send_telegram_notification(notification_text)
            save_notification_time()
        
        return available, message
    finally:
        # Даем время посмотреть результат в режиме отладки
        if not browser.headless:
            time.sleep(5)
        browser.close(driver)
        logger.info("Проверка завершена")

def run_monitoring():
    """Запускает периодический мониторинг"""
    logger.info("Запуск мониторинга слотов бронирования")
    
    try:
        while True:
            # Проверяем доступность
            check_booking_availability()
            
            # Рассчитываем случайный интервал от 2 до 4 минут
            interval = random.randint(RANDOM_INTERVAL_MIN, RANDOM_INTERVAL_MAX)
            logger.info(f"Следующая проверка через {interval} секунд")
            
            # Ожидаем до следующей проверки
            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("Мониторинг остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка при выполнении мониторинга: {e}")
        # При ошибке пытаемся перезапустить через минуту
        time.sleep(60)
        run_monitoring()  # рекурсивный вызов для перезапуска

# Заменяем автозапуск на функцию для вызова из бота
def start_monitoring():
    """Запускает мониторинг слотов бронирования"""
    logger.info("Запуск мониторинга слотов бронирования")
    run_monitoring()

if __name__ == "__main__":
    # При запуске файла как скрипта, выводим инструкцию
    print("""
Этот файл предназначен для использования как библиотека.
Для запуска мониторинга используйте Telegram-бота с командой 'старт'.

Если вы хотите запустить мониторинг напрямую, используйте:
  python -c "from booking_monitor import start_monitoring; start_monitoring()"
""") 