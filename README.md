# LBV Appointment Checker Bot 🤖

[English](#english) | [Deutsch](#deutsch)

## English

An automated bot for monitoring available appointment slots on the LBV (Landesamt für Bürger- und Ordnungsangelegenheiten) website in Berlin, Germany.

### 🎯 Features

- 🔍 Automatic monitoring of available appointment slots
- 📅 Preferred date range selection (week/two weeks/month)
- 🔔 Instant notifications when slots become available
- 📸 Screenshots of available slots
- 📊 Monitoring via Telegram bot
- 📈 Grafana metrics visualization

### 🛠 Technologies

- Python 3.12+
- Selenium WebDriver
- Telegram Bot API
- SQLite
- Prometheus + Grafana
- Docker & Docker Compose

### ⚙️ Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/lbv-checker.git
cd lbv-checker
```

2. Create virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # for Linux/Mac
# or
venv\Scripts\activate  # for Windows
pip install -r requirements.txt
```

3. Create `.env` file from template:
```bash
cp .env.example .env
```

4. Configure environment variables in `.env`:
```env
# Get token from @BotFather in Telegram
TELEGRAM_TOKEN=your_bot_token_here
USER_FIRSTNAME=your_firstname
USER_LASTNAME=your_lastname
USER_EMAIL=your_email@example.com
```

### 🚀 Launch

#### Local launch
```bash
python start_bot.py
```

#### Docker launch
```bash
docker-compose up -d
```

### 💡 Usage

1. Find your bot in Telegram (using token from settings)
2. Send `/start` command
3. Choose preferred date range for monitoring
4. Bot will start checking for available slots

#### Available commands:
- `/start` - start monitoring
- `/stop` - stop monitoring
- `/status` - check current status
- `check` - perform one-time check

### 🔍 How it works

1. Bot automatically navigates to LBV website
2. Goes through all steps until slot selection page
3. Checks for "auswählen" buttons and associated dates
4. If available slots are found:
   - Within selected range: sends notification with sound
   - Outside range: updates status message
5. Takes screenshots for confirmation

### 📊 Monitoring

- All checks are logged in `logs/bot.log`
- Metrics available through Prometheus
- Visualization in Grafana (port 3000)

### 🔐 Security

- All sensitive data stored in `.env`
- Allowed users list support
- Secure token and credentials storage

### ⚠️ Disclaimer

This bot is intended for personal use and should not be used for automatic booking or creating load on the LBV website.

## Deutsch

[Original German description follows...]

# 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes and create PR

# 📝 License

MIT License. See [LICENSE](LICENSE) file.

# 👥 Support

If you have questions or issues:
1. Create an Issue in repository
2. Describe the problem in detail
3. Attach logs from `logs/bot.log` 