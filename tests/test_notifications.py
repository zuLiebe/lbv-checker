import pytest
import asyncio
from core.notifications import NotificationManager

@pytest.fixture
def notifier():
    return NotificationManager()

@pytest.mark.asyncio
async def test_send_notification(notifier):
    result = await notifier.send_notification(
        123456789,
        "Test message"
    )
    assert result is True

@pytest.mark.asyncio
async def test_update_message(notifier):
    # First send a message
    await notifier.send_notification(123456789, "Initial message")
    
    # Then try to update it
    result = await notifier.update_message(
        123456789,
        "Updated message"
    )
    assert result is True

@pytest.mark.asyncio
async def test_notification_retry(notifier):
    # Simulate failed attempts
    notifier._send_telegram_message = lambda *args: False
    
    result = await notifier.send_notification(
        123456789,
        "Test retry"
    )
    assert result is False 