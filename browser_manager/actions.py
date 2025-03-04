from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from loguru import logger
from config.config import USER_DATA, SELECTORS
import time

class BookingChecker:
    def __init__(self, driver, site_url, service_type=None):
        self.driver = driver
        self.site_url = site_url

    def check_availability(self):
        """Прокси-метод для обновленной логики"""
        from browser_manager.browser import BrowserHandler
        
        browser_handler = BrowserHandler()
        return browser_handler.check_booking_availability(self.driver)
    
    def perform_full_check(self, first_name=None, last_name=None, email=None):
        """Совместимость со старым кодом"""
        from browser_manager.browser import BrowserHandler
        
        browser_handler = BrowserHandler()
        return browser_handler.check_booking_availability(self.driver)

    def navigate_to_site(self):
        """Переходит на сайт бронирования."""
        try:
            self.driver.get(self.site_url)
            logger.info(f"Выполнен переход на сайт: {self.site_url}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при переходе на сайт: {e}")
            return False
    
    def select_service(self):
        """Выбирает тип услуги (Führerschein)."""
        try:
            # Ожидаем загрузки страницы и появления выбора услуги
            service_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{self.service_type}')]"))
            )
            service_button.click()
            logger.info(f"Выбрана услуга: {self.service_type}")
            return True
        except TimeoutException:
            logger.error(f"Не удалось найти кнопку для выбора услуги: {self.service_type}")
            return False
        except Exception as e:
            logger.error(f"Ошибка при выборе услуги: {e}")
            return False
    
    def fill_form(self, first_name, last_name, email):
        """Заполняет форму персональными данными."""
        try:
            # Заполняем имя
            first_name_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "firstname"))
            )
            first_name_input.clear()
            first_name_input.send_keys(first_name)
            
            # Заполняем фамилию
            last_name_input = self.driver.find_element(By.ID, "lastname")
            last_name_input.clear()
            last_name_input.send_keys(last_name)
            
            # Заполняем email
            email_input = self.driver.find_element(By.ID, "email")
            email_input.clear()
            email_input.send_keys(email)
            
            # Нажимаем кнопку "Weiter" (Далее)
            continue_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Weiter')]")
            continue_button.click()
            
            logger.info(f"Форма заполнена данными: {first_name} {last_name}, {email}")
            return True
        except NoSuchElementException as e:
            logger.error(f"Не удалось найти элемент формы: {e}")
            return False
        except Exception as e:
            logger.error(f"Ошибка при заполнении формы: {e}")
            return False
    
    def check_availability(self):
        """Проверяет наличие доступных слотов для бронирования."""
        try:
            # Ждем загрузки календаря или сообщения об отсутствии слотов
            time.sleep(3)  # Даем странице время на загрузку
            
            # Проверяем наличие сообщения об отсутствии слотов
            try:
                no_slots_msg = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Leider stehen keine freien Termine zur Verfügung')]"))
                )
                logger.info("Нет доступных слотов для бронирования")
                return False, "Нет доступных слотов"
            except TimeoutException:
                # Если сообщение не найдено, проверяем наличие календаря или дат
                try:
                    calendar = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "calendar"))
                    )
                    available_days = calendar.find_elements(By.CLASS_NAME, "active")
                    
                    if available_days:
                        dates = [day.get_attribute("data-date") for day in available_days]
                        logger.info(f"Найдены доступные слоты на даты: {', '.join(dates)}")
                        return True, f"Доступны слоты на даты: {', '.join(dates)}"
                    else:
                        logger.info("Календарь загружен, но активных дат не найдено")
                        return False, "Календарь без доступных дат"
                except TimeoutException:
                    # Попробуем найти другие элементы, которые могут указывать на доступность слотов
                    try:
                        date_selection = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.ID, "dates"))
                        )
                        logger.info("Найдены элементы выбора даты - возможно, есть доступные слоты")
                        return True, "Обнаружены элементы выбора даты"
                    except TimeoutException:
                        logger.warning("Неопределенное состояние - не удалось определить наличие слотов")
                        return None, "Не удалось определить наличие слотов"
        except Exception as e:
            logger.error(f"Ошибка при проверке доступности: {e}")
            return None, f"Ошибка проверки: {str(e)}" 