import asyncio
import logging
import time

import google.generativeai as generai
from google.api_core.exceptions import ResourceExhausted
from telegram.ext import ConversationHandler

import config
from config import MODEL_PROMPT

# Enum de estados
START_CONVERSATION, CHAT, END_CONVERSATION = range(3)


logger = logging.getLogger(__name__)

model = generai.GenerativeModel(config.MODEL_NAME)

chat_sessions = {}


async def start(update, context):
    await update.message.reply_text(
        "Bem vindo ao OctoBot!\n <b>Esse é o chatbot mais gatão do planeta!</b>\n Para sair digite /end",
        parse_mode="HTML",
    )
    return CHAT


async def error_handler(update, context):
    logger.error(msg="Ocorreu um erro crítico:", exc_info=context.error)
    await update.message.reply_text("Ocorreu um erro. Tente novamente mais tarde!")


async def send_message_with_retry(chat_session, prompt, retries=3):
    for attempt in range(retries):
        try:
            response = await asyncio.wait_for(chat_session.send_message_async(prompt), timeout=10)
            return response
        except asyncio.TimeoutError:
            logger.warning(f"Tentativa {attempt + 1} de enviar mensagem excedeu o tempo limite. Reintentando...")
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem na tentativa {attempt + 1}: {e}", exc_info=True)
    raise RuntimeError("Falha ao enviar mensagem após várias tentativas.")


async def chat(update, context):
    user_id = update.message.from_user.id
    chat_session = chat_sessions.get(user_id)

    if chat_session is None:
        chat_session = model.start_chat()
        chat_sessions[user_id] = chat_session

    try:
        user_message = update.message.text.strip() if update.message else None

        if not user_message:
            await update.message.reply_text(
                "Desculpe, não entendi sua mensagem. Por favor, tente novamente.",
                parse_mode="HTML",
            )
            return CHAT

        await update.message.reply_text(
            "<b>Gerando sua resposta...</b>",
            parse_mode="HTML",
        )
        start_time = time.time()
        prompt = MODEL_PROMPT + f"\n Perfira respostas curtas, Aqui está a mensagem do usuário: {user_message}"
        response = await send_message_with_retry(chat_session, prompt)
        elapsed_time = time.time() - start_time

        logger.info(f"Mensagem enviada: {user_message}")
        logger.info(f"Mensagem recebida: {response.text}")
        logger.info(f"Tempo de resposta do modelo: {elapsed_time:.2f} segundos")

        await update.message.reply_text(
            response.text,
            parse_mode="MARKDOWN",
        )

        await update.message.reply_text(
            f"Tempo de resposta do modelo: {elapsed_time:.2f} segundos",
        )

    except ResourceExhausted as e:
        await update.message.reply_text(
            f"Limite de quota alcançado! : {e}",
        )

    except Exception as e:
        logger.error(
            f"Ocorreu um erro ao gerar a resposta: {e}",
            exc_info=True,
        )
        await update.message.reply_text(
            "Ocorreu um erro ao processar sua mensagem. Por favor, tente novamente mais tarde.",
            parse_mode="HTML",
        )
        logger.info(chat_sessions)

    return CHAT


async def exit(update, context):
    await update.message.reply_text(
        "<b>Obrigado por utilizar o otobot! \n Para mais conversas digite /start!</b>",
        parse_mode="HTML",
    )

    return ConversationHandler.END
