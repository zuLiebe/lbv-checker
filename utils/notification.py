"""
Модуль для отправки уведомлений пользователям
"""
import json
import os
import requests
from loguru import logger
from config.config import TELEGRAM_TOKEN
from telegram import Bot, ParseMode
import asyncio

# Словарь для хранения ID последних сообщений для каждого чата
last_message_ids = {}

def send_telegram_notification(chat_id, message, screenshot_path=None, token=None, disable_notification=False):
    """
    Отправляет уведомление пользователю.
    
    Args:
        chat_id: ID чата
        message: текст сообщения
        screenshot_path: путь к скриншоту
        token: токен бота
        disable_notification: True для отправки уведомления без звука
    """
    if not token:
        from config.config import TELEGRAM_TOKEN
        token = TELEGRAM_TOKEN
    
    bot = Bot(token=token)
    
    try:
        if screenshot_path and os.path.exists(screenshot_path):
            # Отправляем фото с подписью
            with open(screenshot_path, 'rb') as photo:
                # Не использовать await с синхронными методами
                sent_message = bot.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                    caption=message,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_notification=disable_notification
                )
                
                # Сохраняем ID сообщения
                if sent_message:
                    last_message_ids[str(chat_id)] = sent_message.message_id
                    save_last_message_ids()
                return sent_message
        else:
            # Отправляем только текст
            sent_message = bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN,
                disable_notification=disable_notification
            )
            return sent_message
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления: {e}")
        return None

def send_text_message(chat_id, text, token):
    """Отправляет текстовое сообщение"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=data, timeout=10)
    if response.status_code != 200:
        logger.error(f"Ошибка отправки текста: {response.text}")
        return None
    return response.json().get('result')

def truncate_message(message, max_length=1000):
    """Обрезает длинные сообщения для Telegram."""
    if not message or len(message) <= max_length:
        return message
        
    # Обрезаем сообщение и добавляем метку
    return message[:max_length-20] + "... [обрезано]"

def send_photo_with_caption(chat_id, caption, photo_path, token):
    """Отправляет фото с подписью в Telegram."""
    try:
        # Обрезаем слишком длинные подписи
        caption = truncate_message(caption, max_length=1024)  # Telegram ограничивает подписи до 1024 символов
        
        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        
        with open(photo_path, 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': chat_id, 'caption': caption, 'parse_mode': 'Markdown'}
            
            response = requests.post(url, files=files, data=data)
            
        if response.status_code == 200:
            result = response.json()
            # Сохраняем ID сообщения
            if result.get('ok'):
                message_id = result['result']['message_id']
                last_message_ids[chat_id] = message_id
                save_last_message_ids()
            return True
        else:
            logger.error(f"Ошибка отправки фото: {response.text}")
            
            # Если проблема в длине сообщения, отправляем отдельно
            if "caption is too long" in response.text:
                # Отправляем фото без подписи
                with open(photo_path, 'rb') as photo:
                    files = {'photo': photo}
                    data = {'chat_id': chat_id}
                    response = requests.post(url, files=files, data=data)
                
                # Отправляем текст отдельным сообщением
                text_url = f"https://api.telegram.org/bot{token}/sendMessage"
                # Разбиваем сообщение на части по 4000 символов
                for i in range(0, len(caption), 4000):
                    part = caption[i:i+4000]
                    data = {'chat_id': chat_id, 'text': part, 'parse_mode': 'Markdown'}
                    requests.post(text_url, data=data)
                
                return True
            
            return False
    except Exception as e:
        logger.error(f"Ошибка отправки фото: {e}")
        return False

def update_message_text(chat_id, message_id, text, token):
    """Обновляет текст существующего сообщения"""
    url = f"https://api.telegram.org/bot{token}/editMessageText"
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=data, timeout=10)
    if response.status_code != 200:
        logger.error(f"Ошибка обновления текста: {response.text}")
        return None
    return response.json().get('result')

def update_message_with_photo(chat_id, message_id, caption, photo_path, token):
    """Обновляет сообщение с фото."""
    try:
        # Обрезаем слишком длинные подписи
        caption = truncate_message(caption, max_length=1024)
        
        url = f"https://api.telegram.org/bot{token}/editMessageMedia"
        
        with open(photo_path, 'rb') as photo:
            media = {
                'type': 'photo',
                'media': f'attach://photo',
                'caption': caption,
                'parse_mode': 'Markdown'
            }
            
            files = {'photo': photo}
            data = {
                'chat_id': chat_id,
                'message_id': message_id,
                'media': json.dumps(media)
            }
            
            response = requests.post(url, files=files, data=data)
            
        if response.status_code == 200:
            return True
        else:
            logger.error(f"Ошибка обновления сообщения с фото: {response.text}")
            
            # Если проблема в длине сообщения, отправляем новое
            if "caption is too long" in response.text:
                return send_photo_with_caption(chat_id, caption, photo_path, token)
                
            return False
    except Exception as e:
        logger.error(f"Ошибка обновления сообщения с фото: {e}")
        return False

def load_chat_ids():
    """Загружает ID чатов из файла"""
    try:
        if os.path.exists("telegram_users.json"):
            with open("telegram_users.json", "r") as f:
                data = json.load(f)
                return data.get("chat_ids", [])
        return []
    except Exception as e:
        logger.error(f"Ошибка при загрузке ID чатов: {e}")
        return []

def save_last_message_ids():
    """Сохраняет ID последних сообщений в файл"""
    try:
        with open("last_message_ids.json", "w") as f:
            json.dump(last_message_ids, f)
        return True
    except Exception as e:
        logger.error(f"Ошибка при сохранении ID сообщений: {e}")
        return False

def load_last_message_ids():
    """Загружает ID последних сообщений из файла"""
    global last_message_ids
    try:
        if os.path.exists("last_message_ids.json"):
            with open("last_message_ids.json", "r") as f:
                last_message_ids = json.load(f)
            return True
        return False
    except Exception as e:
        logger.error(f"Ошибка при загрузке ID сообщений: {e}")
        return False

def update_last_message(chat_id, text, screenshot_path=None, token=None):
    """
    Обновляет последнее отправленное сообщение вместо отправки нового.
    
    Args:
        chat_id: ID чата
        text: новый текст сообщения
        screenshot_path: путь к новому скриншоту
        token: токен бота
    
    Returns:
        True в случае успеха, False иначе
    """
    global last_message_ids
    
    if not token:
        from config.config import TELEGRAM_TOKEN
        token = TELEGRAM_TOKEN
    
    # Получаем ID последнего сообщения для этого чата
    chat_id_str = str(chat_id)
    if chat_id_str not in last_message_ids:
        # Если нет сохраненного ID, отправляем новое сообщение
        logger.warning(f"Нет сохраненного ID сообщения для чата {chat_id}, отправляем новое")
        return send_telegram_notification(chat_id, text, screenshot_path, token)
    
    message_id = last_message_ids[chat_id_str]
    
    try:
        bot = Bot(token=token)
        
        if screenshot_path and os.path.exists(screenshot_path):
            # Обновляем сообщение с фото
            with open(screenshot_path, 'rb') as photo:
                # Сначала удаляем старое сообщение
                try:
                    bot.delete_message(chat_id=chat_id, message_id=message_id)
                except Exception as e:
                    logger.warning(f"Не удалось удалить старое сообщение: {e}")
                
                # Отправляем новое сообщение
                sent_message = bot.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                    caption=text,
                    parse_mode=ParseMode.MARKDOWN
                )
                
                # Сохраняем новый ID сообщения
                if sent_message:
                    last_message_ids[str(chat_id)] = sent_message.message_id
                    save_last_message_ids()
                
                return sent_message
        else:
            # Обновляем текстовое сообщение
            edited_message = bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                parse_mode=ParseMode.MARKDOWN
            )
            return edited_message
    
    except Exception as e:
        logger.error(f"Ошибка при обновлении сообщения: {e}")
        # Если не удалось обновить, пробуем отправить новое
        return send_telegram_notification(chat_id, text, screenshot_path, token) 