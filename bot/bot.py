import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler
from telegram.ext._context import CallbackContext
from loguru import logger
import os
from dotenv import load_dotenv
from .browser import BrowserHandler
import time

# Load environment variables
load_dotenv()

class AppointmentBot:
    def __init__(self):
        self.token = os.getenv('BOT_TOKEN')
        if not self.token:
            raise ValueError("BOT_TOKEN not found in environment variables")
            
        self.browser = BrowserHandler(headless=True)
        self.checking = False
        self.driver = None
        
    async def start(self, update: Update, context: CallbackContext) -> None:
        """Handle /start command"""
        if update.message:
            await update.message.reply_text(
                "Hello! I'm a bot for checking available appointment slots at LBV.\n"
                "Use /check to start checking\n"
                "Use /stop to stop checking"
            )

    async def check_command(self, update: Update, context: CallbackContext) -> None:
        """Handle /check command"""
        if not update.message:
            return
            
        if self.checking:
            await update.message.reply_text("Checking is already running!")
            return
            
        self.checking = True
        await update.message.reply_text("Starting to check for slots...")
        
        try:
            self.driver = self.browser.init_driver()
            while self.checking:
                try:
                    # Open the page
                    self.driver.get("https://www.berlin.de/labo/mobil/dienstleistungen/termin/")
                    
                    # Check slots
                    has_slots, message = self.browser.check_slots(self.driver)
                    
                    if has_slots and update.message:
                        await update.message.reply_text(
                            f"🎉 Available slots found!\n{message}\n"
                            "Go to: https://www.berlin.de/labo/mobil/dienstleistungen/termin/"
                        )
                        break
                    
                    # Wait before next check
                    await asyncio.sleep(60)
                    
                except Exception as e:
                    logger.error(f"Error during check: {e}")
                    if update.message:
                        await update.message.reply_text(f"An error occurred: {str(e)}")
                    break
                    
        finally:
            self.checking = False
            if self.driver:
                self.browser.close(self.driver)
                self.driver = None

    async def stop_command(self, update: Update, context: CallbackContext) -> None:
        """Handle /stop command"""
        if not update.message:
            return
            
        if not self.checking:
            await update.message.reply_text("Checking is not running!")
            return
            
        self.checking = False
        await update.message.reply_text("Stopping the check...")
        
        if self.driver:
            self.browser.close(self.driver)
            self.driver = None

    def run(self):
        """Start the bot"""
        try:
            application = Application.builder().token(self.token).build()
            
            # Register command handlers
            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(CommandHandler("check", self.check_command))
            application.add_handler(CommandHandler("stop", self.stop_command))
            
            # Start the bot
            application.run_polling()
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            print(f"Error starting bot: {str(e)}")

if __name__ == "__main__":
    bot = AppointmentBot()
    bot.run() 