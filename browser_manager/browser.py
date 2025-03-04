from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from config.config import FRONTEND_URL, BROWSER_WINDOW_SIZE, SELECTORS, USER_DATA
from loguru import logger
import time
import json
from utils.date_utils import check_if_dates_in_range
import re
from database.db_handler import DatabaseHandler

class BrowserHandler:
    def __init__(self, headless=False, timeout=30):
        self.headless = headless
        self.timeout = timeout
        self.options = Options()
        
        logger.info(f"Инициализация браузера: headless={headless}, timeout={timeout}")
        
        if headless:
            logger.info("Запуск в headless режиме")
            self.options.add_argument('--headless=new')
        else:
            logger.info("Запуск в видимом режиме")
        
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--window-size=1920,1080')
        
        # Исправим проблемы с кодировкой
        self.options.add_argument('--lang=de-DE')
        self.options.add_argument('--disable-extensions')
        
    def init_driver(self):
        """Инициализирует и возвращает драйвер Chrome"""
        try:
            logger.info("Инициализация драйвера Chrome...")
            driver = webdriver.Chrome(options=self.options)
            driver.set_window_size(BROWSER_WINDOW_SIZE['width'], BROWSER_WINDOW_SIZE['height'])
            driver.implicitly_wait(self.timeout)
            logger.info("Драйвер Chrome успешно инициализирован")
            return driver
        except Exception as e:
            logger.error(f"Ошибка при инициализации Chrome драйвера: {e}")
            # Попробуем вывести больше информации об ошибке
            import traceback
            logger.error(f"Трассировка: {traceback.format_exc()}")
            raise e
    
    def start(self):
        """Обратная совместимость со старым кодом"""
        driver = self.init_driver()
        logger.info("Браузер успешно инициализирован")
        return driver
    
    def close(self, driver=None):
        """Закрывает браузер"""
        if driver:
            try:
                driver.quit()
                logger.info("Браузер закрыт")
            except Exception as e:
                logger.error(f"Ошибка при закрытии браузера: {e}")
    
    def js_click(self, driver, element):
        """Клик с использованием JavaScript, избегая проблем с перекрытием элементов"""
        try:
            driver.execute_script("arguments[0].click();", element)
            return True
        except Exception as e:
            logger.error(f"Ошибка при JS-клике: {e}")
            return False
    
    def safe_click(self, driver, element):
        """Безопасный клик с использованием разных стратегий"""
        logger.info("Пытаемся безопасно кликнуть по элементу")
        try:
            # Стратегия 1: прямой клик
            try:
                logger.info("Стратегия 1: прямой клик")
                element.click()
                logger.info("Прямой клик успешен")
                return True
            except Exception as e:
                logger.info(f"Прямой клик не сработал: {e}")
                pass
            
            # Стратегия 2: скроллинг к элементу и клик
            try:
                logger.info("Стратегия 2: скроллинг к элементу и клик")
                driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(0.5)
                element.click()
                logger.info("Клик после скроллинга успешен")
                return True
            except Exception as e:
                logger.info(f"Клик после скроллинга не сработал: {e}")
                pass
            
            # Стратегия 3: JavaScript клик
            logger.info("Стратегия 3: JavaScript клик")
            success = self.js_click(driver, element)
            if success:
                logger.info("JavaScript клик успешен")
            else:
                logger.info("JavaScript клик не сработал")
            return success
        except Exception as e:
            logger.error(f"Все стратегии клика не удались: {e}")
            return False

    def highlight_element(self, driver, element, color="red", border=4):
        """Выделяет элемент на странице для наглядности"""
        try:
            # Сначала удаляем предыдущие выделения
            driver.execute_script("""
                var elements = document.querySelectorAll('[style*="border:"]');
                for (var i = 0; i < elements.length; i++) {
                    elements[i].style.border = '';
                }
            """)
            
            # Затем выделяем нужный элемент
            driver.execute_script(
                "arguments[0].style.border = '%spx solid %s';" % (border, color), 
                element
            )
            return True
        except Exception as e:
            logger.error(f"Ошибка при выделении элемента: {e}")
            return False

    def take_screenshot_and_update(self, driver, step_name, chat_ids=None):
        """Делает скриншот и обновляет сообщение в Telegram"""
        try:
            # Если строка шага слишком длинная (например, ошибка), обрезаем её
            if len(step_name) > 100 and step_name.startswith("ОШИБКА"):
                step_name = step_name[:100] + "... [смотрите логи для деталей]"
            
            # Выводим в лог для отладки
            logger.info(f"Делаем скриншот шага: {step_name}, chat_ids: {chat_ids}")
            
            # Получаем токен из конфига
            from config.config import TELEGRAM_TOKEN
            from utils.notification import update_message_with_photo, last_message_ids, send_photo_with_caption
            
            screenshot_path = f"current_state.png"
            driver.save_screenshot(screenshot_path)
            logger.info(f"Шаг: {step_name} - сохранен скриншот: {screenshot_path}")
            
            # Если заданы chat_ids, отправляем обновление
            if chat_ids:
                for chat_id in chat_ids:
                    # Проверяем, есть ли для этого чата последнее сообщение
                    if chat_id in last_message_ids:
                        message_id = last_message_ids[chat_id]
                        logger.info(f"Обновляем сообщение для {chat_id}, message_id: {message_id}")
                        update_message_with_photo(chat_id, message_id, step_name, screenshot_path, TELEGRAM_TOKEN)
                    else:
                        # Если нет - отправляем новое сообщение
                        send_photo_with_caption(chat_id, step_name, screenshot_path, TELEGRAM_TOKEN)
        
            return screenshot_path
        except Exception as e:
            logger.error(f"Ошибка при создании скриншота: {e}")
            return None

    def run_selenium_side_script(self, driver, chat_ids=None):
        """Выполняет скрипт Selenium IDE строго по шагам из lbv.side"""
        try:
            # Debug: вывод информации о chat_ids
            logger.info(f"Запуск скрипта с chat_ids: {chat_ids}")
            
            # Если chat_ids пуст или None, попробуем загрузить из системы
            if not chat_ids:
                from utils.notification import load_chat_ids
                chat_ids = load_chat_ids()
                logger.info(f"Загружены chat_ids из системы: {chat_ids}")
            
            # Подтверждаем, что драйвер запущен
            if not driver:
                logger.error("Драйвер не инициализирован!")
                return False, "Ошибка: Браузер не запустился"
            
            # Шаг 1: Открываем страницу
            logger.info("Шаг 1: Открываем страницу")
            driver.get(f"{FRONTEND_URL}/index.php")
            time.sleep(2)
            self.take_screenshot_and_update(driver, "1. Открываем страницу", chat_ids)
            
            # Шаг 2: Установка размера окна (уже выполняется при инициализации драйвера)
            logger.info("Шаг 2: Установка размера окна")
            driver.set_window_size(BROWSER_WINDOW_SIZE['width'], BROWSER_WINDOW_SIZE['height'])
            self.take_screenshot_and_update(driver, "2. Установка размера окна", chat_ids)
            
            # Шаг 3: Закрываем модальное окно
            logger.info("Шаг 3: Закрываем модальное окно")
            try:
                modal_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, SELECTORS['modal_button']))
                )
                self.highlight_element(driver, modal_button)
                self.take_screenshot_and_update(driver, "3. Закрываем модальное окно", chat_ids)
                self.safe_click(driver, modal_button)
                time.sleep(1)
            except Exception as e:
                logger.warning(f"Не удалось закрыть модальное окно: {e} (возможно, его нет)")
                self.take_screenshot_and_update(driver, "3. Модальное окно не найдено", chat_ids)
            
            # Шаг 4: Выбираем категорию
            logger.info("Шаг 4: Выбираем категорию")
            try:
                category_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, SELECTORS['category_button']))
                )
                self.highlight_element(driver, category_button)
                self.take_screenshot_and_update(driver, "4. Выбираем категорию", chat_ids)
                
                # Используем JavaScript для клика (избегаем проблем с перекрытием)
                logger.info("Кликаем на категорию с помощью JavaScript")
                driver.execute_script("arguments[0].click();", category_button)
                time.sleep(2)
            except Exception as e:
                logger.error(f"Не удалось выбрать категорию: {e}")
                self.take_screenshot_and_update(driver, "Ошибка: не удалось выбрать категорию", chat_ids)
                return False, f"Не удалось выбрать категорию: {str(e)}"
            
            # Шаг 5: Выбираем услугу
            logger.info("Шаг 5: Выбираем услугу")
            try:
                service_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, SELECTORS['service_button']))
                )
                self.highlight_element(driver, service_button)
                self.take_screenshot_and_update(driver, "5. Выбираем услугу", chat_ids)
                self.safe_click(driver, service_button)
                time.sleep(1)
            except Exception as e:
                logger.error(f"Не удалось выбрать услугу: {e}")
                self.take_screenshot_and_update(driver, "Ошибка: не удалось выбрать услугу", chat_ids)
                return False, f"Не удалось выбрать услугу: {str(e)}"
            
            # Шаг 6: Нажимаем 'продолжить'
            logger.info("Шаг 6: Нажимаем 'продолжить'")
            try:
                continue_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, SELECTORS['continue_button']))
                )
                self.highlight_element(driver, continue_button)
                self.take_screenshot_and_update(driver, "6. Нажимаем 'продолжить'", chat_ids)
                
                # Скролл вниз, чтобы избежать перекрытия элементов
                driver.execute_script("window.scrollBy(0, 250);")
                time.sleep(1)
                
                # Используем JavaScript для клика
                driver.execute_script("arguments[0].click();", continue_button)
                time.sleep(2)
            except Exception as e:
                logger.error(f"Не удалось нажать кнопку продолжить: {e}")
                self.take_screenshot_and_update(driver, "Ошибка: не удалось нажать кнопку продолжить", chat_ids)
                return False, f"Не удалось нажать кнопку продолжить: {str(e)}"
            
            # Шаг 7: Устанавливаем галочку согласия
            logger.info("Шаг 7: Устанавливаем галочку согласия")
            try:
                privacy_checkbox = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, SELECTORS['privacy_checkbox']))
                )
                self.highlight_element(driver, privacy_checkbox)
                self.take_screenshot_and_update(driver, "7. Устанавливаем галочку согласия", chat_ids)
                
                # Используем JavaScript для установки галочки
                driver.execute_script("arguments[0].click();", privacy_checkbox)
                time.sleep(1)
            except Exception as e:
                logger.error(f"Не удалось установить галочку согласия: {e}")
                self.take_screenshot_and_update(driver, "Ошибка: не удалось установить галочку согласия", chat_ids)
                return False, f"Не удалось установить галочку согласия: {str(e)}"
            
            # Шаг 8: Нажимаем кнопку "weiter"
            logger.info("Шаг 8: Нажимаем кнопку 'weiter'")
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "weiterbutton"))
                )
                self.highlight_element(driver, next_button)
                self.take_screenshot_and_update(driver, "8. Нажимаем кнопку 'weiter'", chat_ids)
                
                # Используем JavaScript для клика
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(2)
            except Exception as e:
                logger.error(f"Не удалось нажать кнопку weiter: {e}")
                self.take_screenshot_and_update(driver, "Ошибка: не удалось нажать кнопку weiter", chat_ids)
                return False, f"Не удалось нажать кнопку weiter: {str(e)}"
            
            # Шаг 9: Заполняем поле имени
            logger.info("Шаг 9: Заполняем поле имени")
            try:
                firstname_field = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "vorname"))
                )
                self.highlight_element(driver, firstname_field)
                self.take_screenshot_and_update(driver, "9. Заполняем поле имени", chat_ids)
                
                firstname_field.click()
                firstname_field.clear()
                firstname_field.send_keys(USER_DATA['firstname'])
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"Не удалось заполнить поле имени: {e}")
                self.take_screenshot_and_update(driver, "Ошибка: не удалось заполнить поле имени", chat_ids)
                return False, f"Не удалось заполнить поле имени: {str(e)}"
            
            # Шаг 10: Заполняем поле фамилии
            logger.info("Шаг 10: Заполняем поле фамилии")
            try:
                lastname_field = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "nachname"))
                )
                self.highlight_element(driver, lastname_field)
                lastname_field.clear()
                lastname_field.send_keys(USER_DATA['lastname'])
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"Не удалось заполнить поле фамилии: {e}")
                self.take_screenshot_and_update(driver, "Ошибка: не удалось заполнить поле фамилии", chat_ids)
                return False, f"Не удалось заполнить поле фамилии: {str(e)}"
            
            # Шаг 11: Заполняем поле email
            logger.info("Шаг 11: Заполняем поле email")
            try:
                email_field = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "email"))
                )
                self.highlight_element(driver, email_field)
                email_field.clear()
                email_field.send_keys(USER_DATA['email'])
                time.sleep(0.5)
                
                # Делаем скриншот заполненной формы
                self.take_screenshot_and_update(driver, "11. Форма персональных данных заполнена", chat_ids)
            except Exception as e:
                logger.error(f"Не удалось заполнить поле email: {e}")
                self.take_screenshot_and_update(driver, "Ошибка: не удалось заполнить поле email", chat_ids)
                return False, f"Не удалось заполнить поле email: {str(e)}"
            
            # Шаг 12: Нажимаем кнопку "weiter" для перехода к выбору локации
            logger.info("Шаг 12: Нажимаем кнопку 'weiter' для перехода к выбору локации")
            try:
                final_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "weiterbutton"))
                )
                self.highlight_element(driver, final_button)
                self.take_screenshot_and_update(driver, "12. Нажимаем кнопку 'weiter' для перехода к выбору локации", chat_ids)
                
                # Используем JavaScript для клика
                driver.execute_script("arguments[0].click();", final_button)
                time.sleep(3)  # Даем время для загрузки страницы
                
                # Проверяем, что мы на странице выбора локации
                current_url = driver.current_url
                logger.info(f"Текущий URL после заполнения формы: {current_url}")
                
                self.take_screenshot_and_update(driver, "13. После перехода на страницу выбора локации", chat_ids)
                
                # Проверяем наличие доступных слотов на этой странице
                return self.check_slots_on_location_page(driver, chat_ids)
                
            except Exception as e:
                logger.error(f"Не удалось перейти к выбору локации: {e}")
                self.take_screenshot_and_update(driver, "Ошибка: не удалось перейти к выбору локации", chat_ids)
                return False, f"Не удалось перейти к выбору локации: {str(e)}"
            
        except Exception as e:
            error_message = str(e)
            logger.error(f"Ошибка при выполнении скрипта: {error_message}")
            # Сделаем скриншот для анализа ошибки
            try:
                driver.save_screenshot("error_state.png")
                logger.info("Сохранен скриншот состояния при ошибке: error_state.png")
                self.take_screenshot_and_update(driver, f"ОШИБКА: {error_message}", chat_ids)
            except:
                pass
            return False, error_message
    
    def check_booking_availability(self, driver):
        """Проверяет доступность слотов, запуская скрипт из lbv.side"""
        return self.run_selenium_side_script(driver)

    def check_slots_on_location_page(self, driver, chat_ids=None):
        """Проверяет наличие доступных слотов на странице выбора локации."""
        try:
            logger.info("Проверка доступных слотов на странице выбора локации")
            
            # Проверяем наличие кнопок выбора (auswählen)
            select_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'auswählen')]")
            clickable_buttons = []
            available_dates = []

            # Проверяем каждую кнопку на возможность нажатия
            for button in select_buttons:
                try:
                    if button.is_displayed() and button.is_enabled():
                        clickable_buttons.append(button)
                        # Ищем связанную дату для этой кнопки
                        parent = button.find_element(By.XPATH, "./ancestor::tr")
                        date_element = parent.find_element(By.XPATH, ".//div[contains(text(), 'Termine verfügbar ab')]")
                        date_text = date_element.text.strip()
                        date_match = re.search(r'(\d{2}\.\d{2}\.\d{4})', date_text)
                        if date_match:
                            available_dates.append(date_match.group(1))
                            self.highlight_element(driver, date_element, "green")
                            self.highlight_element(driver, button, "green")
                except Exception as e:
                    logger.error(f"Ошибка при проверке кнопки: {e}")
                    continue

            if clickable_buttons:
                logger.info(f"Найдено {len(clickable_buttons)} активных кнопок 'auswählen'")
                
                # Формируем базовое сообщение
                if available_dates:
                    dates_text = ", ".join(available_dates)
                    message = f"Доступна запись на даты: {dates_text}"
                else:
                    message = f"Найдено {len(clickable_buttons)} доступных слотов (даты не определены)"

                # Обрабатываем уведомления для каждого пользователя
                if chat_ids:
                    for chat_id in chat_ids:
                        try:
                            # Получаем предпочтительный диапазон из базы данных
                            db_path = "database/booking_bot.db"
                            db = DatabaseHandler(db_path)
                            preferred_range = db.get_user_preferred_dates(chat_id) or 'any'
                            
                            # Проверяем, соответствуют ли найденные даты предпочтениям
                            is_preferred = True
                            if available_dates and preferred_range != 'any':
                                from utils.date_utils import check_if_dates_in_range
                                is_preferred = check_if_dates_in_range(available_dates, preferred_range)
                            
                            # Получаем читаемое название диапазона
                            range_text = {
                                'week': 'неделя',
                                'two_weeks': 'две недели',
                                'month': 'месяц',
                                'any': 'любой период'
                            }.get(preferred_range, 'любой период')

                            if is_preferred:
                                # Даты в выбранном диапазоне - отправляем новое уведомление со звуком
                                notification_text = (
                                    f"🚨 *СРОЧНО! НАЙДЕНЫ СЛОТЫ!*\n\n"
                                    f"✅ {message}\n"
                                    f"📅 Даты соответствуют выбранному диапазону: *{range_text}*\n\n"
                                    f"❗️ Перейдите на сайт и нажмите кнопку 'auswählen'!"
                                )
                                
                                logger.info(f"Отправка нового уведомления для {chat_id} (даты в диапазоне)")
                                token = self.get_telegram_token()
                                from utils.notification import send_telegram_notification
                                send_telegram_notification(
                                    chat_id,
                                    notification_text,
                                    "current_state.png",
                                    token,
                                    disable_notification=False
                                )
                            else:
                                # Даты не в диапазоне - обновляем существующее сообщение
                                notification_text = (
                                    f"ℹ️ *Статус мониторинга*\n\n"
                                    f"👉 {message}\n"
                                    f"⚠️ Найденные даты вне выбранного диапазона\n"
                                    f"📅 Ваш диапазон: *{range_text}*\n\n"
                                    f"_Используйте команду 'старт' для изменения диапазона_"
                                )
                                
                                logger.info(f"Обновление статуса для {chat_id} (даты не в диапазоне)")
                                self.take_screenshot_and_update(driver, notification_text, [chat_id])
                                
                        except Exception as e:
                            logger.error(f"Ошибка при обработке уведомлений: {e}")
                            continue

                return True, message
            else:
                # Если нет активных кнопок, обновляем статус
                status_message = "ℹ️ *Статус мониторинга*\n\n❌ Нет доступных слотов"
                if chat_ids:
                    for chat_id in chat_ids:
                        self.take_screenshot_and_update(driver, status_message, [chat_id])
                return False, "Нет доступных слотов"

        except Exception as e:
            logger.error(f"Ошибка при проверке слотов: {e}")
            error_message = f"ℹ️ *Статус мониторинга*\n\n⚠️ Ошибка при проверке: {str(e)}"
            if chat_ids:
                for chat_id in chat_ids:
                    self.take_screenshot_and_update(driver, error_message, [chat_id])
            return False, f"Ошибка: {str(e)}"

    def get_telegram_token(self):
        """Безопасно получает токен Telegram из конфигурации."""
        try:
            from config.config import TELEGRAM_TOKEN
            return TELEGRAM_TOKEN
        except Exception as e:
            logger.error(f"Ошибка при импорте TELEGRAM_TOKEN: {e}")
            # Альтернативный способ получить токен
            import os
            return os.environ.get("TELEGRAM_TOKEN", "")

if __name__ == "__main__":
    pass