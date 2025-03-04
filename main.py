from bot.bot import AppointmentBot
from utils.logger import setup_logger

def main():
    # Настраиваем логирование
    logger = setup_logger()
    
    try:
        # Создаем и запускаем бота
        bot = AppointmentBot()
        logger.info("Запуск бота...")
        bot.run()
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        raise

if __name__ == "__main__":
    main() 