from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from config.config import FRONTEND_URL, BROWSER_WINDOW_SIZE, SELECTORS, USER_DATA
import logging
import time

class BrowserHandler:
    def __init__(self, headless=False):
        self.logger = logging.getLogger(__name__)
        self.options = Options()
        if headless:
            self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        
    def init_driver(self):
        driver = webdriver.Chrome(options=self.options)
        driver.set_window_size(BROWSER_WINDOW_SIZE['width'], BROWSER_WINDOW_SIZE['height'])
        return driver

    async def check_booking_availability(self):
        driver = None
        try:
            driver = self.init_driver()
            
            # 1. Открываем начальную страницу
            driver.get(f"{FRONTEND_URL}/index.php")
            
            # 2. Закрываем модальное окно
            modal_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, SELECTORS['modal_button']))
            )
            modal_button.click()
            
            # 3. Выбираем категорию
            category_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, SELECTORS['category_button']))
            )
            category_button.click()
            
            # 4. Выбираем услугу
            try:
                service_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, SELECTORS['service_button']))
                )
                service_button.click()
                
                # 5. Нажимаем "продолжить"
                continue_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, SELECTORS['continue_button']))
                )
                
                # Если кнопка доступна, значит есть свободные слоты
                if continue_button.is_enabled():
                    return True, "Доступны слоты для бронирования!"
                
            except TimeoutException:
                return False, "Нет доступных слотов"
                
        except Exception as e:
            error_message = str(e)
            self.logger.error(f"Error during booking check: {error_message}")
            return False, error_message
            
        finally:
            if driver:
                driver.quit()

    async def make_booking(self):
        """Метод для выполнения бронирования"""
        driver = None
        try:
            driver = self.init_driver()
            
            # Повторяем шаги проверки доступности
            is_available, _ = await self.check_booking_availability()
            
            if not is_available:
                return False, "Слоты недоступны"
            
            # Соглашаемся с условиями
            privacy_checkbox = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, SELECTORS['privacy_checkbox']))
            )
            privacy_checkbox.click()
            
            # Нажимаем "далее"
            next_button = driver.find_element(By.CSS_SELECTOR, SELECTORS['next_button'])
            next_button.click()
            
            # Заполняем форму
            driver.find_element(By.CSS_SELECTOR, SELECTORS['firstname']).send_keys(USER_DATA['firstname'])
            driver.find_element(By.CSS_SELECTOR, SELECTORS['lastname']).send_keys(USER_DATA['lastname'])
            driver.find_element(By.CSS_SELECTOR, SELECTORS['email']).send_keys(USER_DATA['email'])
            
            # Подтверждаем форму
            next_button = driver.find_element(By.CSS_SELECTOR, SELECTORS['next_button'])
            next_button.click()
            
            return True, "Бронирование выполнено успешно!"
            
        except Exception as e:
            error_message = str(e)
            self.logger.error(f"Error during booking: {error_message}")
            return False, error_message
            
        finally:
            if driver:
                driver.quit() 