import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from unittest.mock import Mock, patch
from browser_manager.browser import BrowserHandler
from exceptions.custom_exceptions import BrowserException
from database.db_handler import DatabaseHandler
from metrics.prometheus import BROWSER_OPERATION_DURATION

# Инициализируем метрики с метками
BROWSER_OPERATION_DURATION.labels(operation='init')

@pytest.fixture
def browser():
    return BrowserHandler()

@pytest.fixture
def mock_driver():
    driver = Mock()
    driver.find_elements = Mock()
    driver.execute_script = Mock()
    return driver

@pytest.fixture
def mock_button():
    button = Mock(spec=WebElement)
    button.is_displayed = Mock(return_value=True)
    button.is_enabled = Mock(return_value=True)
    button.get_attribute = Mock(return_value=None)
    return button

@pytest.fixture
def mock_date_element():
    element = Mock(spec=WebElement)
    element.text = "Termine verfügbar ab 01.05.2024"
    return element

class TestCheckSlotsOnLocationPage:
    def test_no_buttons_found(self, browser, mock_driver):
        """Тест случая, когда кнопки auswählen не найдены"""
        mock_driver.find_elements.return_value = []
        
        result, message = browser.check_slots_on_location_page(mock_driver)
        
        assert result is False
        assert "Нет доступных слотов" in message
        mock_driver.find_elements.assert_called_once_with(
            By.XPATH, "//button[contains(text(), 'auswählen')]"
        )

    def test_buttons_found_but_not_clickable(self, browser, mock_driver, mock_button):
        """Тест случая, когда кнопки найдены, но не кликабельны"""
        mock_button.is_enabled.return_value = False
        mock_driver.find_elements.return_value = [mock_button]
        
        result, message = browser.check_slots_on_location_page(mock_driver)
        
        assert result is False
        assert "Нет доступных слотов" in message

    @patch('database.db_handler.DatabaseHandler')
    def test_clickable_button_with_date_in_range(self, mock_db, browser, mock_driver, mock_button, mock_date_element):
        """Тест случая, когда найдена кликабельная кнопка с датой в выбранном диапазоне"""
        # Настраиваем мок для кнопки и связанных элементов
        mock_button.find_element.side_effect = [
            Mock(find_element=Mock(return_value=mock_date_element))  # parent
        ]
        mock_driver.find_elements.return_value = [mock_button]
        
        # Настраиваем мок для базы данных
        mock_db_instance = Mock()
        mock_db_instance.get_user_preferred_dates.return_value = 'week'
        mock_db.return_value = mock_db_instance
        
        # Выполняем тест с chat_ids
        result, message = browser.check_slots_on_location_page(mock_driver, chat_ids=[123])
        
        assert result is True
        assert "Доступна запись на даты: 01.05.2024" in message

    @patch('database.db_handler.DatabaseHandler')
    def test_clickable_button_with_date_not_in_range(self, mock_db, browser, mock_driver, mock_button, mock_date_element):
        """Тест случая, когда найдена кликабельная кнопка с датой вне выбранного диапазона"""
        # Настраиваем мок для кнопки и связанных элементов
        mock_button.find_element.side_effect = [
            Mock(find_element=Mock(return_value=mock_date_element))  # parent
        ]
        mock_driver.find_elements.return_value = [mock_button]
        
        # Настраиваем мок для базы данных
        mock_db_instance = Mock()
        mock_db_instance.get_user_preferred_dates.return_value = 'week'
        mock_db.return_value = mock_db_instance
        
        # Мокаем функцию проверки дат, чтобы она возвращала False
        with patch('utils.date_utils.check_if_dates_in_range', return_value=False):
            result, message = browser.check_slots_on_location_page(mock_driver, chat_ids=[123])
        
        assert result is True  # Все равно True, так как кнопка кликабельна
        assert "Доступна запись на даты: 01.05.2024" in message

    def test_error_handling(self, browser, mock_driver):
        """Тест обработки ошибок"""
        mock_driver.find_elements.side_effect = Exception("Test error")
        
        result, message = browser.check_slots_on_location_page(mock_driver)
        
        assert result is False
        assert "Ошибка" in message

    @patch('utils.notification.send_telegram_notification')
    @patch('database.db_handler.DatabaseHandler')
    def test_notification_handling(self, mock_db, mock_send_notification, browser, mock_driver, mock_button, mock_date_element):
        """Тест отправки уведомлений"""
        # Настраиваем моки
        mock_button.find_element.side_effect = [
            Mock(find_element=Mock(return_value=mock_date_element))
        ]
        mock_driver.find_elements.return_value = [mock_button]
        
        mock_db_instance = Mock()
        mock_db_instance.get_user_preferred_dates.return_value = 'week'
        mock_db.return_value = mock_db_instance
        
        # Проверяем отправку уведомлений
        with patch('utils.date_utils.check_if_dates_in_range', return_value=True):
            result, message = browser.check_slots_on_location_page(mock_driver, chat_ids=[123])
        
        assert result is True
        assert mock_send_notification.called
        
        # Проверяем содержимое уведомления
        notification_args = mock_send_notification.call_args[0]
        assert "СРОЧНО" in notification_args[1]
        assert "01.05.2024" in notification_args[1]

@pytest.mark.skip("Требует реального браузера")
def test_browser_session(browser):
    with browser.create_session() as driver:
        assert driver is not None
        assert driver.current_url == "data:,"

@pytest.mark.skip("Требует реального браузера")
def test_safe_click(browser):
    with browser.create_session() as driver:
        driver.get("https://example.com")
        element = driver.find_element(By.TAG_NAME, "h1")
        assert browser.safe_click(driver, element)

@pytest.mark.skip("Требует реального браузера")
def test_wait_for_element_timeout(browser):
    with browser.create_session() as driver:
        with pytest.raises(BrowserException):
            browser.wait_for_element(
                driver,
                (By.ID, "nonexistent-element"),
                timeout=1
            )

@pytest.mark.skip("Требует реального браузера")
def test_screenshot(browser):
    with browser.create_session() as driver:
        driver.get("https://example.com")
        screenshot = browser.take_screenshot(driver, "test.png")
        assert screenshot == "test.png" 