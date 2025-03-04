from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from loguru import logger
import threading
import time
import schedule
from browser_manager.browser import BrowserHandler
from browser_manager.actions import BookingChecker
from config.config import add_chat_id

class TelegramBot:
    def __init__(self, token, db_handler, booking_checker, config):
        self.token = token
        self.db_handler = db_handler
        self.booking_checker = booking_checker
        self.config = config
        self.updater = None
        self.is_checking = False
        self.check_thread = None
        self.scheduler_thread = None
        self.stop_event = threading.Event()
    
    def start(self):
        """Запускает Telegram бота."""
        self.updater = Updater(self.token)
        dp = self.updater.dispatcher
        
        # Регистрируем обработчики команд
        dp.add_handler(CommandHandler("start", self.cmd_start))
        dp.add_handler(CommandHandler("help", self.cmd_help))
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, self.handle_message))
        
        # Запускаем бота
        self.updater.start_polling()
        logger.info("Telegram бот запущен и готов к работе")
    
    def stop(self):
        """Останавливает Telegram бота."""
        if self.updater:
            self.updater.stop()
            logger.info("Telegram бот остановлен")
        
        self.stop_checking()
    
    def cmd_start(self, update: Update, context: CallbackContext):
        """Обрабатывает команду /start."""
        user = update.effective_user
        
        # Добавляем пользователя в базу данных
        self.db_handler.add_user(
            user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        # Регистрируем пользователя для получения уведомлений
        add_chat_id(user.id)
        
        message = (
            f"👋 Здравствуйте, {user.first_name}!\n\n"
            f"Я бот для проверки доступности слотов бронирования на сайте LBV.\n\n"
            f"Команды:\n"
            f"*старт* - запустить периодическую проверку\n"
            f"*стоп* - остановить проверку\n"
            f"*статус* - узнать текущий статус\n"
            f"*проверить* - выполнить одну проверку сейчас\n\n"
            f"Я буду уведомлять вас, когда появятся доступные слоты для бронирования."
        )
        
        update.message.reply_text(message, parse_mode='Markdown')
    
    def cmd_help(self, update: Update, context: CallbackContext):
        """Обрабатывает команду /help."""
        message = (
            "🔍 *Как пользоваться ботом:*\n\n"
            "1. Отправьте команду *старт* для запуска периодической проверки\n"
            "2. Бот будет проверять наличие слотов каждые 5 минут\n"
            "3. При обнаружении доступных слотов вы получите уведомление\n"
            "4. Для остановки проверки отправьте *стоп*\n\n"
            "Дополнительные команды:\n"
            "*проверить* - проверить доступность слотов сейчас\n"
            "*статус* - узнать, активны ли проверки\n"
        )
        
        update.message.reply_text(message, parse_mode='Markdown')
    
    def handle_message(self, update: Update, context: CallbackContext):
        """Обрабатывает текстовые сообщения."""
        text = update.message.text.lower().strip()
        user_id = update.effective_user.id
        
        # Проверяем, имеет ли пользователь доступ
        if self.config.ALLOWED_USER_IDS and user_id not in self.config.ALLOWED_USER_IDS:
            update.message.reply_text("У вас нет доступа к этому боту.", parse_mode='Markdown')
            return
        
        if text == "старт":
            self.run_background_monitoring(update, context)
        elif text == "стоп":
            self.stop_checking(update, context)
        elif text == "статус":
            self.check_status(update, context)
        elif text == "проверить":
            self.run_single_check(update, context)
        else:
            update.message.reply_text(
                "Я не понимаю эту команду. Доступные команды:\n"
                "*старт* - запустить периодическую проверку\n"
                "*стоп* - остановить проверку\n"
                "*статус* - узнать текущий статус\n"
                "*проверить* - выполнить одну проверку сейчас",
                parse_mode='Markdown'
            )
    
    def start_checking(self, update=None, context=None):
        """Запускает периодическую проверку доступности слотов."""
        if self.is_checking:
            if update:
                update.message.reply_text("Проверка уже запущена!")
            return
        
        self.is_checking = True
        self.stop_event.clear()
        
        # Запускаем поток для планировщика
        self.scheduler_thread = threading.Thread(target=self.run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        if update:
            update.message.reply_text(
                f"✅ Проверка запущена! Буду проверять наличие слотов каждые {self.config.CHECK_INTERVAL//60} минут."
            )
        
        logger.info(f"Запущена периодическая проверка слотов с интервалом {self.config.CHECK_INTERVAL} сек.")
    
    def stop_checking(self, update=None, context=None):
        """Останавливает периодическую проверку доступности слотов."""
        if not self.is_checking:
            if update:
                update.message.reply_text("Проверка уже остановлена!")
            return
        
        self.stop_event.set()
        self.is_checking = False
        
        if update:
            update.message.reply_text("❌ Проверка остановлена.")
        
        logger.info("Периодическая проверка слотов остановлена.")
    
    def check_status(self, update, context):
        """Отправляет информацию о текущем статусе проверки."""
        status = "✅ активна" if self.is_checking else "❌ неактивна"
        update.message.reply_text(f"Проверка доступности слотов: {status}")
    
    def check_now(self, update=None, context=None):
        """Выполняет одну проверку доступности слотов."""
        if update:
            update.message.reply_text("🔍 Проверяю наличие доступных слотов...")
        
        # Запускаем проверку в отдельном потоке
        self.check_thread = threading.Thread(target=self.perform_check, args=(update,))
        self.check_thread.daemon = True
        self.check_thread.start()
    
    def perform_check(self, update=None):
        """Выполняет проверку доступности и отправляет результат."""
        try:
            available, details = self.booking_checker.perform_full_check(
                self.config.DEFAULT_FIRST_NAME,
                self.config.DEFAULT_LAST_NAME,
                self.config.DEFAULT_EMAIL
            )
            
            # Записываем результат в базу данных
            check_id = self.db_handler.log_check_result(available, details)
            
            if available:
                # Если есть доступные слоты, отправляем уведомление всем активным пользователям
                self.send_availability_notification(details, check_id)
            elif update:
                # Если это ручная проверка, отправляем ответ пользователю
                update.message.reply_text(f"❌ {details}")
            
            logger.info(f"Проверка завершена: доступность={available}, детали={details}")
        except Exception as e:
            logger.error(f"Ошибка при выполнении проверки: {e}")
            if update:
                update.message.reply_text(f"⚠️ Ошибка при проверке: {str(e)}")
    
    def send_availability_notification(self, details, check_id):
        """Отправляет уведомление о доступных слотах всем активным пользователям."""
        active_users = self.db_handler.get_active_users()
        
        message = (
            "🎉 *ДОСТУПНЫ СЛОТЫ ДЛЯ БРОНИРОВАНИЯ!*\n\n"
            f"{details}\n\n"
            f"🔗 [Перейти на сайт бронирования]({self.config.SITE_URL})"
        )
        
        for user_id in active_users:
            try:
                self.updater.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode='Markdown',
                    disable_web_page_preview=False
                )
                self.db_handler.log_notification(check_id, user_id, delivered=True)
                logger.info(f"Уведомление отправлено пользователю {user_id}")
            except Exception as e:
                self.db_handler.log_notification(check_id, user_id, delivered=False)
                logger.error(f"Ошибка при отправке уведомления пользователю {user_id}: {e}")
    
    def run_scheduler(self):
        """Запускает планировщик для периодической проверки."""
        schedule.every(self.config.CHECK_INTERVAL).seconds.do(self.check_now)
        
        while not self.stop_event.is_set():
            schedule.run_pending()
            time.sleep(1)
        
        # Очищаем все задачи при остановке
        schedule.clear()
    
    def run_background_monitoring(self, update=None, context=None):
        """Запускает мониторинг в фоновом режиме."""
        from booking_monitor import check_booking_availability, save_booking_status, should_send_notification, send_telegram_notification, save_notification_time
        import random
        import time
        
        if self.is_checking:
            if update:
                update.message.reply_text("Мониторинг уже запущен!", parse_mode='Markdown')
            return
        
        self.is_checking = True
        self.stop_event.clear()
        
        # Обновление статуса в базе данных
        if update:
            self.db_handler.update_checking_status(update.effective_user.id, True)
            update.message.reply_text("✅ Мониторинг запущен! Вы получите уведомление, когда появятся доступные слоты.", parse_mode='Markdown')
        
        def monitoring_thread():
            while not self.stop_event.is_set():
                try:
                    # Проверяем доступность
                    browser = BrowserHandler(headless=True)  # В фоне запускаем в headless режиме
                    driver = browser.init_driver()
                    
                    try:
                        logger.info("Запуск проверки доступности слотов...")
                        available, message = browser.run_selenium_side_script(driver)
                        logger.info(f"Результат: Доступность={available}, Сообщение={message}")
                        
                        # Сохраняем результат в историю
                        save_booking_status(available, message)
                        
                        # Проверяем, нужно ли отправлять уведомление
                        if should_send_notification(available, message):
                            # Формируем сообщение
                            notification_text = f"🔔 *Проверка доступности слотов*\n\n"
                            
                            if available:
                                notification_text += f"✅ *НАЙДЕНЫ ДОСТУПНЫЕ СЛОТЫ!*\n\n{message}\n\nСрочно перейдите на сайт бронирования!"
                            else:
                                notification_text += f"❌ Слоты недоступны\n\n{message}"
                                
                            # Отправляем уведомление
                            send_telegram_notification(notification_text)
                            save_notification_time()
                        
                    finally:
                        browser.close(driver)
                        logger.info("Проверка завершена")
                    
                    # Случайный интервал от 2 до 4 минут
                    interval = random.randint(120, 240)
                    logger.info(f"Следующая проверка через {interval} секунд")
                    
                    # Проверяем флаг остановки каждые 5 секунд
                    for _ in range(interval // 5):
                        if self.stop_event.is_set():
                            break
                        time.sleep(5)
                        
                except Exception as e:
                    logger.error(f"Ошибка при выполнении мониторинга: {e}")
                    time.sleep(60)  # При ошибке повторяем через минуту
            
            self.is_checking = False
            logger.info("Мониторинг остановлен")
        
        # Запускаем мониторинг в отдельном потоке
        self.check_thread = threading.Thread(target=monitoring_thread)
        self.check_thread.daemon = True
        self.check_thread.start() 