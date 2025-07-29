print("Bot script started...")
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)



from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Replace with your actual bot token
TOKEN = "8443616015:AAFUC514DzToapTz8XCgtvYaekw-YkC9GwQ"

# Define a simple start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔒 Security Screening Bot is Active!")

def main():
    # Build the application
    app = ApplicationBuilder().token(TOKEN).build()

    # Add the start command handler
    app.add_handler(CommandHandler("start", start))

    # Start the bot
    app.run_polling()

if __name__ == "__main__":
    main()
