from telegram import ReplyKeyboardMarkup, Message

import google.generativeai as generai
import logging

START_CONVERSATION, CHAT, END_CONVERSATION = range(3)

GEMINI_MODEL = generai.GenerativeModel("gemini-1.5-pro-latest")

logger = logging.getLogger(__name__)


async def start(update, context):
    reply_keyboard = [["COMEÇAR"]]

    await update.message.reply_text(
        "<b>Bem vindo ao OctoBot!\n" "Esse eh um chatbot simples, diga oolah!\n</b>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )

    return CHAT


async def chat(update, context):
    await update.message.reply_text(
        "<b>Gerando sua resposta...</b>",
        parse_mode="HTML",
    )
    if update.message:
        response = await GEMINI_MODEL.generate_content_async(
            str(update.message.text),
        )
        logger.info(f"Mensagem enviada: {str(update.message.text)}")
        logger.info(f"Mensagem recebida: {str(response.text)}")

        await update.message.reply_text(
            response.text,
            parse_mode="HTML",
        )
        return CHAT


async def exit(update, context):
    pass
