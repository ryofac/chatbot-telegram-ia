import logging
import os
from dotenv import load_dotenv
import asyncio
from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from utils.utils import start, chat, START_CONVERSATION, CHAT, END_CONVERSATION, exit

import google.generativeai as generai


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    load_dotenv()

    generai.configure(api_key=os.getenv("API_KEY_GEMINI"))
    app = Application.builder().token(os.getenv("BOT_TOKEN")).build()
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={CHAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, chat)]},
        fallbacks=[CommandHandler('end', exit)],
    )
    app.add_handler(conversation_handler)

    # Handle the case when a user sends /start but they're not in a conversation
    app.add_handler(CommandHandler('start', start))

    app.run_polling()


if __name__ == "__main__":
    main()
