from browser_manager.browser import BrowserHandler
from loguru import logger
import sys
import time

logger.remove()
logger.add(sys.stdout, level="INFO")

def test_booking():
    browser = BrowserHandler(headless=False)
    driver = browser.init_driver()
    
    try:
        logger.info("Запуск проверки доступности слотов...")
        available, message = browser.run_selenium_side_script(driver)
        logger.info(f"Результат: Доступность={available}, Сообщение={message}")
        
        # Даем время посмотреть результат перед закрытием браузера
        logger.info("Ожидание 10 секунд перед закрытием браузера...")
        time.sleep(10)
        
    finally:
        browser.close(driver)
        logger.info("Тест завершен")

if __name__ == "__main__":
    test_booking() 