from datetime import datetime, timedelta
import re
from loguru import logger

def parse_date(date_str):
    """Преобразует строку с датой в объект datetime."""
    try:
        # Поддержка формата DD.MM.YYYY
        if re.match(r'\d{2}\.\d{2}\.\d{4}', date_str):
            return datetime.strptime(date_str, '%d.%m.%Y')
        
        # Поддержка формата YYYY-MM-DD
        elif re.match(r'\d{4}-\d{2}-\d{2}', date_str):
            return datetime.strptime(date_str, '%Y-%m-%d')
        
        logger.warning(f"Неизвестный формат даты: {date_str}")
        return None
    except Exception as e:
        logger.error(f"Ошибка при разборе даты {date_str}: {e}")
        return None

def check_if_dates_in_range(dates, preferred_range):
    """
    Проверяет, находятся ли даты в пределах предпочтительного диапазона.
    
    Args:
        dates: список строк с датами
        preferred_range: строка с предпочтительным диапазоном ('week', 'two_weeks', 'month', 'any')
    
    Returns:
        True, если хотя бы одна дата находится в предпочтительном диапазоне
    """
    if not dates or preferred_range == 'any':
        return True  # По умолчанию все даты подходят
    
    today = datetime.now()
    logger.info(f"Текущая дата: {today.strftime('%d.%m.%Y')}")
    
    # Определяем конечную дату диапазона
    if preferred_range == 'week':
        end_date = today + timedelta(days=7)
    elif preferred_range == 'two_weeks':
        end_date = today + timedelta(days=14)
    elif preferred_range == 'month':
        # Учитываем, что месяц может быть 28-31 день, поэтому берем с запасом
        end_date = today + timedelta(days=31)
    else:
        logger.warning(f"Неизвестный диапазон: {preferred_range}, считаем все даты подходящими")
        return True
    
    logger.info(f"Конечная дата диапазона '{preferred_range}': {end_date.strftime('%d.%m.%Y')}")
    
    # Проверяем каждую дату
    for date_str in dates:
        date_obj = parse_date(date_str)
        if date_obj:
            logger.info(f"Проверка даты {date_str}: {today <= date_obj <= end_date}")
            if today <= date_obj <= end_date:
                logger.info(f"Дата {date_str} находится в предпочтительном диапазоне {preferred_range}")
                return True
    
    logger.info(f"Ни одна из дат {dates} не находится в диапазоне {preferred_range}")
    return False 