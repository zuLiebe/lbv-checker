from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from loguru import logger
import threading
import time
import random
import schedule
from browser_manager.browser import BrowserHandler
from utils.notification import send_telegram_notification, load_last_message_ids, save_last_message_ids, send_photo_with_caption, load_chat_ids
from booking_monitor import check_booking_availability, save_booking_status, should_send_notification, save_notification_time
import os

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
        
        # Добавляем обработчик для CallbackQuery (нажатия на inline-кнопки)
        dp.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Добавляем обработчик ошибок
        dp.add_error_handler(self.error_handler)
        
        # Запускаем бота
        self.updater.start_polling()
        logger.info("Telegram бот запущен и готов к работе")
    
    def stop(self):
        """Останавливает Telegram бота."""
        if self.updater:
            self.updater.stop()
            logger.info("Telegram бот остановлен")
        
        self.stop_checking()
        
        # Сохраняем ID последних сообщений
        save_last_message_ids()
    
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
        from config.config import add_chat_id
        add_chat_id(user.id)
        
        message = (
            f"👋 Здравствуйте, {user.first_name}!\n\n"
            f"Я бот для проверки доступности слотов бронирования на сайте LBV.\n\n"
            f"Команды:\n"
            f"*старт* - запустить мониторинг\n"
            f"*стоп* - остановить мониторинг\n"
            f"*статус* - проверить статус мониторинга\n"
            f"*проверить* - выполнить однократную проверку\n\n"
            f"Я буду уведомлять вас, когда появятся доступные слоты для бронирования."
        )
        
        update.message.reply_text(message, parse_mode='Markdown')
    
    def cmd_help(self, update: Update, context: CallbackContext):
        """Обрабатывает команду /help."""
        message = (
            "🔍 *Как пользоваться ботом:*\n\n"
            "1. Отправьте команду *старт* для запуска периодической проверки\n"
            "2. Выберите предпочтительный диапазон дат:\n"
            "   - Любые даты\n"
            "   - В течение недели\n"
            "   - В течение 2 недель\n"
            "   - В течение месяца\n"
            "3. Бот будет проверять наличие слотов каждые 4-7 минут\n"
            "4. При обнаружении доступных слотов вы получите уведомление\n"
            "5. Для остановки проверки отправьте *стоп*\n\n"
            "Дополнительные команды:\n"
            "*проверить* - проверить доступность слотов сейчас\n"
            "*статус* - узнать, активны ли проверки\n"
        )
        
        update.message.reply_text(message, parse_mode='Markdown')
    
    def handle_message(self, update: Update, context: CallbackContext):
        """Обрабатывает текстовые сообщения."""
        try:
            message = update.message.text.lower().strip()
            user_id = update.effective_user.id
            
            logger.info(f"Получено сообщение от {user_id}: {message}")
            
            # Обновляем время последней активности пользователя
            try:
                self.db_handler.update_user_activity(user_id)
            except Exception as e:
                logger.warning(f"Не удалось обновить активность пользователя: {e}")
            
            # Проверяем команды
            if message in ['старт', 'start', 'запустить', 'начать']:
                update.message.reply_text("Запускаю мониторинг в видимом режиме...", parse_mode='Markdown')
                self.run_background_monitoring(update, context)
                
            elif message in ['стоп', 'stop', 'остановить', 'хватит']:
                self.stop_checking(update, context)
                
            elif message in ['статус', 'status']:
                self.check_status(update, context)
                
            elif message in ['проверить', 'check', 'тест', 'test']:
                update.message.reply_text("Запускаю проверку в видимом режиме...", parse_mode='Markdown')
                self.run_single_check(update, context)
                
            else:
                update.message.reply_text(
                    "Не понимаю команду. Доступные команды:\n"
                    "*старт* - запустить мониторинг\n"
                    "*стоп* - остановить мониторинг\n"
                    "*статус* - проверить статус мониторинга\n"
                    "*проверить* - выполнить однократную проверку",
                    parse_mode='Markdown'
                )
        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения: {e}")
            try:
                update.message.reply_text(f"Произошла ошибка: {str(e)}")
            except:
                pass
    
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
    
    def run_single_check(self, update=None, context=None):
        """Выполняет одну проверку доступности слотов."""
        if update:
            update.message.reply_text("🔍 Проверяю наличие доступных слотов...")
        
        # Запускаем проверку в отдельном потоке
        thread = threading.Thread(target=self.perform_single_check, args=(update,))
        thread.daemon = True
        thread.start()
    
    def perform_single_check(self, update, context):
        """Выполняет проверку доступности слотов по запросу пользователя."""
        chat_id = update.effective_chat.id
        
        # Обновляем активность пользователя
        try:
            self.db_handler.update_user_activity(update.effective_user.id)
        except Exception as e:
            logger.warning(f"Не удалось обновить активность пользователя: {e}")
        
        message = update.message.reply_text("🔍 Проверяю наличие доступных слотов...", parse_mode='Markdown')
        
        try:
            # Инициализируем браузер с большим таймаутом
            browser = BrowserHandler(headless=False, timeout=60)
            driver = browser.init_driver()
            
            # Запускаем проверку
            available, msg = browser.run_selenium_side_script(driver, [chat_id])  # Передаем chat_id списком
            logger.info(f"Результат: Доступность={available}, Сообщение={msg}")
            
            if available:
                # Найдены доступные слоты
                update.message.reply_text(f"✅ *{msg}*", parse_mode='Markdown')
                logger.info(f"Найдены доступные слоты! Отправляем уведомление пользователям: [{chat_id}]")
                
                # Отправляем уведомление с фото текущему пользователю
                send_telegram_notification(
                    chat_id,
                    f"🚨 *{msg}*",
                    "current_state.png",
                    self.config['TELEGRAM_TOKEN']
                )
            else:
                # Слоты не найдены
                update.message.reply_text(f"❌ {msg}", parse_mode='Markdown')
            
            # Закрываем браузер
            browser.close(driver)
            return available, msg
        except Exception as e:
            update.message.reply_text(f"❌ Ошибка при проверке: {str(e)}")
    
    def run_background_monitoring(self, update, context):
        """Запускает мониторинг в фоновом режиме."""
        chat_id = update.effective_chat.id
        
        # Проверяем, не запущен ли уже мониторинг
        if self.is_checking:
            update.message.reply_text("⚠️ Мониторинг уже запущен.")
            return
        
        # Запрашиваем предпочтительный диапазон дат
        self.ask_date_range(update, context)
        
        # Сохраняем контекст для callback-обработчика
        context.user_data['starting_monitoring'] = True
    
    def ask_date_range(self, update: Update, context: CallbackContext):
        """Запрашивает предпочтительный диапазон дат для мониторинга."""
        keyboard = [
            [InlineKeyboardButton("Любые даты", callback_data='date_range_any')],
            [InlineKeyboardButton("В течение недели", callback_data='date_range_week')],
            [InlineKeyboardButton("В течение 2 недель", callback_data='date_range_two_weeks')],
            [InlineKeyboardButton("В течение месяца", callback_data='date_range_month')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.message.reply_text(
            "Выберите предпочтительный диапазон дат для мониторинга.\n\n"
            "Вы получите <b>срочное</b> уведомление только если появятся слоты в выбранном диапазоне.",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    def error_handler(self, update, context):
        """Обработчик ошибок для диспетчера."""
        logger.error(f"Ошибка при обработке обновления {update}: {context.error}")
        
        # Если можем отправить сообщение пользователю
        if update and update.effective_chat:
            try:
                update.effective_message.reply_text(
                    "Произошла ошибка при обработке запроса. Попробуйте позже."
                )
            except:
                pass
    
    def button_callback(self, update: Update, context: CallbackContext):
        """Обрабатывает нажатия на inline-кнопки."""
        query = update.callback_query
        query.answer()  # Отвечаем на callback, чтобы убрать "часики" на кнопке
        
        callback_data = query.data
        chat_id = query.message.chat_id
        
        if callback_data.startswith('date_range_'):
            # Обрабатываем выбор диапазона дат
            date_range = callback_data.replace('date_range_', '')
            
            if date_range == 'any':
                message = "Вы выбрали мониторинг для <b>любых дат</b>.\n\nЗапускаю проверку..."
                readable_range = "любые даты"
            elif date_range == 'week':
                message = "Вы выбрали мониторинг для дат <b>в течение недели</b>.\n\nЗапускаю проверку..."
                readable_range = "в течение недели"
            elif date_range == 'two_weeks':
                message = "Вы выбрали мониторинг для дат <b>в течение 2 недель</b>.\n\nЗапускаю проверку..."
                readable_range = "в течение 2 недель"
            elif date_range == 'month':
                message = "Вы выбрали мониторинг для дат <b>в течение месяца</b>.\n\nЗапускаю проверку..."
                readable_range = "в течение месяца"
            else:
                message = "Неизвестный диапазон. Выбраны <b>любые даты</b>.\n\nЗапускаю проверку..."
                date_range = 'any'
                readable_range = "любые даты"
            
            query.edit_message_text(
                text=message,
                parse_mode='HTML'
            )
            
            # Обновляем предпочтительный диапазон дат пользователя
            self.db_handler.update_user_preferred_dates(chat_id, date_range)
            
            # Запускаем мониторинг с выбранным диапазоном
            self.start_monitoring_with_range(chat_id, date_range)
    
    def start_monitoring_with_range(self, chat_id, date_range):
        """Запускает мониторинг с выбранным диапазоном дат."""
        # Включаем флаг проверки в базе данных
        self.db_handler.update_checking_status(chat_id, True)
        
        # Останавливаем предыдущий поток если есть
        self.stop_event.set()
        if self.check_thread and self.check_thread.is_alive():
            self.check_thread.join(1)
        self.stop_event.clear()
        
        self.is_checking = True
        
        def monitoring_thread():
            """Функция мониторинга, запускаемая в отдельном потоке."""
            current_chat_id = chat_id  # Сохраняем ID чата, откуда пришла команда
            max_errors = 3
            consecutive_errors = 0
            first_run = True
            
            # Загружаем ID последних сообщений, если они были сохранены
            load_last_message_ids()
            
            # Получаем chat_ids для обновления скриншотов
            chat_ids = [current_chat_id]  # Используем ID текущего чата
            
            # Получаем токен из конфига правильно
            from config.config import TELEGRAM_TOKEN
            token = TELEGRAM_TOKEN
            
            while not self.stop_event.is_set():
                try:
                    if consecutive_errors >= max_errors:
                        logger.warning(f"Достигнут лимит последовательных ошибок ({max_errors}). Остановка мониторинга.")
                        send_telegram_notification(
                            current_chat_id,
                            "⚠️ *Мониторинг остановлен из-за повторяющихся ошибок*\n\nПожалуйста, перезапустите командой 'старт'",
                            None,
                            token
                        )
                        break
                    
                    # Инициализируем браузер
                    browser = BrowserHandler(headless=False, timeout=60)
                    driver = browser.init_driver()
                    
                    try:
                        # Передаем chat_ids для обновления скриншотов в процессе
                        result = browser.run_selenium_side_script(driver, [current_chat_id])  # Передаем ID чата в списке
                        
                        # Правильно обрабатываем возвращаемое значение
                        if isinstance(result, tuple) and len(result) == 2:
                            available, message = result
                        else:
                            available, message = False, "Неизвестный результат проверки"
                        
                        # Сбрасываем счетчик ошибок при успешном выполнении
                        consecutive_errors = 0
                        
                        # Сохраняем результат в базу данных
                        self.db_handler.save_check_result(available, message)
                        
                        logger.info(f"Проверка завершена: доступность={available}, сообщение={message}")
                        
                        # После первого запуска сообщаем, что мониторинг работает
                        if first_run:
                            send_telegram_notification(
                                current_chat_id,
                                "✅ *Мониторинг запущен и работает*\n\nВы получите уведомление при появлении слотов в выбранном диапазоне.",
                                None,
                                token
                            )
                            first_run = False
                        
                    finally:
                        # Закрываем браузер
                        browser.close(driver)
                    
                    # ВСЕГДА делаем паузу между проверками, независимо от результата
                    wait_time = random.randint(240, 420)  # 4-7 минут между проверками
                    logger.info(f"Ожидание {wait_time} секунд до следующей проверки")
                    
                    for _ in range(wait_time):
                        if self.stop_event.is_set():
                            break
                        time.sleep(1)
                
                except Exception as e:
                    logger.error(f"Ошибка в цикле мониторинга: {e}")
                    consecutive_errors += 1
                    time.sleep(30)  # Короткий интервал при ошибке
            
            # После завершения цикла
            self.is_checking = False
            self.db_handler.update_checking_status(current_chat_id, False)
            logger.info("Мониторинг завершен")
        
        # Запускаем мониторинг в отдельном потоке
        self.check_thread = threading.Thread(target=monitoring_thread)
        self.check_thread.daemon = True
        self.check_thread.start()
        logger.info(f"Фоновый мониторинг запущен для пользователя {chat_id} с диапазоном дат {date_range}") 