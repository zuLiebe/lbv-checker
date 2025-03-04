from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from contextlib import contextmanager
from loguru import logger
import time

from config.settings import settings
from exceptions.custom_exceptions import BrowserException
from metrics.prometheus import BROWSER_OPERATIONS, BROWSER_OPERATION_DURATION

class BrowserSession:
    """Context manager for browser sessions."""
    def __init__(self, handler: 'BrowserHandler'):
        self.handler = handler
        self.driver = None

    def __enter__(self) -> webdriver.Chrome:
        self.driver = self.handler.init_driver()
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            self.handler.close(self.driver)

class BrowserHandler:
    """
    Enhanced browser handler with metrics and better error handling.
    
    Attributes:
        config (BrowserConfig): Browser configuration
        options (Options): Chrome options
    """
    
    def __init__(self):
        self.config = settings.browser
        self.options = self._configure_browser_options()
        
    def _configure_browser_options(self) -> Options:
        """Configure Chrome options based on settings."""
        options = Options()
        
        if self.config.headless:
            options.add_argument('--headless=new')
            
        # Basic options for stability
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        # Window size
        size = f"{self.config.window_size['width']},{self.config.window_size['height']}"
        options.add_argument(f'--window-size={size}')
        
        # Additional options
        if self.config.user_agent:
            options.add_argument(f'user-agent={self.config.user_agent}')
            
        for option in self.config.chrome_options:
            options.add_argument(option)
            
        return options

    @BROWSER_OPERATION_DURATION.time()
    def init_driver(self) -> webdriver.Chrome:
        """Initialize and return a new Chrome driver."""
        try:
            driver = webdriver.Chrome(options=self.options)
            driver.implicitly_wait(self.config.timeout)
            BROWSER_OPERATIONS.labels(operation='init', status='success').inc()
            return driver
        except Exception as e:
            BROWSER_OPERATIONS.labels(operation='init', status='error').inc()
            raise BrowserException(f"Failed to initialize Chrome driver: {e}")

    def close(self, driver: webdriver.Chrome) -> None:
        """Safely close the browser."""
        try:
            if driver:
                driver.quit()
                BROWSER_OPERATIONS.labels(operation='close', status='success').inc()
        except Exception as e:
            BROWSER_OPERATIONS.labels(operation='close', status='error').inc()
            logger.error(f"Error closing browser: {e}")

    @contextmanager
    def create_session(self):
        """Context manager for browser sessions."""
        with BrowserSession(self) as driver:
            yield driver

    def safe_click(self, driver: webdriver.Chrome, element, retry_count: int = 3) -> bool:
        """Enhanced safe click with multiple strategies and retries."""
        for attempt in range(retry_count):
            try:
                # Strategy 1: Direct click
                try:
                    element.click()
                    return True
                except Exception:
                    pass

                # Strategy 2: Scroll and click
                driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(0.5)
                element.click()
                return True

            except Exception as e:
                if attempt == retry_count - 1:
                    logger.error(f"All click attempts failed: {e}")
                    return False
                time.sleep(1)

        return False

    def wait_for_element(self, 
                        driver: webdriver.Chrome, 
                        locator: tuple, 
                        timeout: Optional[int] = None) -> Any:
        """Wait for element with custom timeout."""
        timeout = timeout or self.config.timeout
        try:
            return WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
        except TimeoutException as e:
            raise BrowserException(f"Element not found: {locator}") from e

    def take_screenshot(self, 
                       driver: webdriver.Chrome, 
                       filename: str = "screenshot.png") -> Optional[str]:
        """Take screenshot with error handling."""
        try:
            driver.save_screenshot(filename)
            BROWSER_OPERATIONS.labels(operation='screenshot', status='success').inc()
            return filename
        except Exception as e:
            BROWSER_OPERATIONS.labels(operation='screenshot', status='error').inc()
            logger.error(f"Screenshot failed: {e}")
            return None

    def highlight_element(self, 
                         driver: webdriver.Chrome, 
                         element: Any, 
                         color: str = "red", 
                         border: int = 4) -> bool:
        """Highlight element for debugging."""
        try:
            driver.execute_script(
                "arguments[0].style.border = '%spx solid %s';" % (border, color),
                element
            )
            return True
        except Exception as e:
            logger.error(f"Failed to highlight element: {e}")
            return False 