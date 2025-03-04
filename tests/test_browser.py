import pytest
from ..bot.browser import BrowserHandler

def test_browser_handler_init():
    """Test BrowserHandler initialization"""
    handler = BrowserHandler()
    assert not handler.headless
    assert handler.timeout == 30
    
    handler = BrowserHandler(headless=True, timeout=60)
    assert handler.headless
    assert handler.timeout == 60

def test_browser_options():
    """Test browser options configuration"""
    handler = BrowserHandler(headless=True)
    options = handler._configure_options()
    
    # Check basic options
    assert '--headless=new' in options.arguments
    assert '--no-sandbox' in options.arguments
    assert '--disable-dev-shm-usage' in options.arguments
    assert '--disable-gpu' in options.arguments
    assert '--window-size=1920,1080' in options.arguments
    assert '--lang=de-DE' in options.arguments 