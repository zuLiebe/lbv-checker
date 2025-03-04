from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from loguru import logger
import time

class BrowserHandler:
    def __init__(self, headless=False, timeout=30):
        self.headless = headless
        self.timeout = timeout
        self.options = self._configure_options()
        
    def _configure_options(self):
        """Настраивает опции браузера"""
        options = Options()
        if self.headless:
            options.add_argument('--headless=new')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--lang=de-DE')
        
        return options
    
    def init_driver(self):
        """Инициализирует и возвращает драйвер Chrome"""
        try:
            driver = webdriver.Chrome(options=self.options)
            driver.implicitly_wait(self.timeout)
            return driver
        except Exception as e:
            logger.error(f"Ошибка при инициализации Chrome драйвера: {e}")
            raise
    
    def close(self, driver):
        """Закрывает браузер"""
        if driver:
            try:
                driver.quit()
            except Exception as e:
                logger.error(f"Ошибка при закрытии браузера: {e}")
    
    def safe_click(self, driver, element):
        """Безопасный клик по элементу"""
        try:
            # Прямой клик
            try:
                element.click()
                return True
            except:
                pass
            
            # Скролл и клик
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)
            element.click()
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при клике: {e}")
            return False
    
    def check_slots(self, driver, chat_ids=None):
        """Проверяет наличие доступных слотов"""
        try:
            # Проверяем наличие кнопок выбора (auswählen)
            select_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'auswählen')]")
            clickable_buttons = []
            available_dates = []

            # Проверяем каждую кнопку на возможность нажатия
            for button in select_buttons:
                try:
                    if button.is_displayed() and button.is_enabled():
                        clickable_buttons.append(button)
                        # Ищем связанную дату
                        parent = button.find_element(By.XPATH, "./ancestor::tr")
                        date_element = parent.find_element(By.XPATH, ".//div[contains(text(), 'Termine verfügbar ab')]")
                        date_text = date_element.text.strip()
                        import re
                        date_match = re.search(r'(\d{2}\.\d{2}\.\d{4})', date_text)
                        if date_match:
                            available_dates.append(date_match.group(1))
                except Exception as e:
                    logger.error(f"Ошибка при проверке кнопки: {e}")
                    continue

            if clickable_buttons:
                if available_dates:
                    return True, f"Доступна запись на даты: {', '.join(available_dates)}"
                return True, f"Найдено {len(clickable_buttons)} доступных слотов"
            
            return False, "Нет доступных слотов"
            
        except Exception as e:
            logger.error(f"Ошибка при проверке слотов: {e}")
            return False, f"Ошибка: {str(e)}" 