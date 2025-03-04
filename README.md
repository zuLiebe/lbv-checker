# LBV Appointment Checker Bot

A Telegram bot for automatically checking available appointment slots at LBV (Landesamt für Bürger- und Ordnungsangelegenheiten) in Hamburg.

## Features

- Automatic monitoring of available appointment slots
- Telegram notifications when slots become available
- Flexible check interval configuration
- Detailed logging

## Requirements

- Python 3.8+
- Chrome/Chromium browser
- ChromeDriver

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/lbv-appointment-checker.git
cd lbv-appointment-checker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file in the project root:
```bash
BOT_TOKEN=your_telegram_bot_token
```

## Usage

1. Start the bot:
```bash
python main.py
```

2. Send `/start` command to your bot in Telegram

3. Available commands:
- `/check` - start checking for slots
- `/stop` - stop checking

## Project Structure

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

## License

MIT 