# LBV Appointment Checker Bot

Telegram бот для автоматической проверки доступных слотов записи в LBV (Landesamt für Bürger- und Ordnungsangelegenheiten) в Берлине.

## Особенности

- Автоматическая проверка доступных слотов
- Уведомления через Telegram при появлении свободных мест
- Гибкая настройка интервала проверки
- Подробное логирование

## Требования

- Python 3.8+
- Chrome/Chromium браузер
- ChromeDriver

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/lbv-appointment-checker.git
cd lbv-appointment-checker
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` в корневой директории проекта:
```bash
BOT_TOKEN=your_telegram_bot_token
```

## Использование

1. Запустите бота:
```bash
python main.py
```

2. В Telegram отправьте команду `/start` вашему боту

3. Используйте следующие команды:
- `/check` - начать проверку слотов
- `/stop` - остановить проверку

## Структура проекта

```
clean_version/
├── bot/
│   ├── __init__.py
│   ├── bot.py
│   └── browser.py
├── config/
│   ├── __init__.py
│   └── config.py
├── utils/
│   ├── __init__.py
│   └── logger.py
├── tests/
├── .env
├── main.py
├── requirements.txt
└── README.md
```

## Лицензия

MIT 