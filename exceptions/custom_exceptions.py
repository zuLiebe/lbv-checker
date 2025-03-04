class BrowserException(Exception):
    """Base exception for browser-related errors."""
    pass

class NotificationException(Exception):
    """Base exception for notification-related errors."""
    pass

class SlotCheckException(Exception):
    """Base exception for slot checking errors."""
    pass

class ConfigurationException(Exception):
    """Base exception for configuration errors."""
    pass 