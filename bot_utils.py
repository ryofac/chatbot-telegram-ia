import asyncio
import io
import json
import logging
import time

import google.generativeai as generai
from google.api_core.exceptions import ResourceExhausted
from PIL import Image
from telegram.constants import ParseMode
from telegram.ext import ConversationHandler

import config
from config import MODEL_NAME, MODEL_PROMPT

# Enum de estados
CHAT, REQUEST_IMAGE, PROCESSING_IMAGE = range(3)


logger = logging.getLogger(__name__)

model = generai.GenerativeModel(config.MODEL_NAME)

chat_sessions = {}


def get_user_message_count(history):
    count = 0
    for message in history:
        if message.role == "user":
            count += 1
    return count


async def start(update, context):
    await update.message.reply_text(
        "Bem vindo ao Gobot! \n <b>Sua I.A especializada em Godot Game Engine!</b>\n Para sair digite /end",
        parse_mode=ParseMode.HTML,
    )
    return CHAT


async def error_handler(update, context):
    logger.error(msg="Ocorreu um erro crítico:", exc_info=context.error)
    await update.message.reply_text("Ocorreu um erro. Tente novamente mais tarde")


async def send_message_with_retry(chat_session, prompt, retries=3):
    for attempt in range(retries):
        try:
            response = await asyncio.wait_for(chat_session.send_message_async(prompt), timeout=10)
            return response
        except asyncio.TimeoutError:
            logger.warning(f"Tentativa {attempt + 1} de enviar mensagem excedeu o tempo limite. Reintentando...")
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem na tentativa {attempt + 1}: {e}", exc_info=True)
        except ResourceExhausted as e:
            raise ResourceExhausted(e)

    raise RuntimeError("Falha ao enviar mensagem após várias tentativas.")


def load_data():
    with open(config.FILE_PATH) as file:
        conteudo = json.load(file)
        return "Você sabe SOMENTE dados sobre esses jogos, em JSON: " + json.dumps(conteudo)


def get_or_create_chat_session(user_id):
    chat_session = chat_sessions.get(user_id)
    if chat_session is None:
        chat_session = model.start_chat(
            history=[{"role": "model", "parts": MODEL_PROMPT}, {"role": "model", "parts": load_data()}]
        )
        chat_sessions[user_id] = chat_session
    return chat_session


async def chat(update, context):
    user_id = update.message.from_user.id
    chat_session = get_or_create_chat_session(user_id)
    try:
        if len(update.message.photo) > 0:
            await update.message.reply_text(
                (
                    "<b>Notei que você enviou uma imagem</b>\n"
                    "Digite /image para entrar no modo de processamento de imagens"
                ),
                parse_mode=ParseMode.HTML,
            )
            return CHAT

        user_message = update.message.text.strip() if update.message.text else None

        if not user_message:
            await update.message.reply_text(
                "Desculpe, não entendi sua mensagem. Por favor, tente novamente.",
                parse_mode=ParseMode.HTML,
            )
            return CHAT

        await update.message.reply_text(
            "<b>Gerando sua resposta...</b>",
            parse_mode=ParseMode.HTML,
        )
        start_time = time.time()
        prompt = f"\n Perfira respostas curtas, Aqui está a mensagem do usuário: {user_message}"
        response = await send_message_with_retry(chat_session, prompt)
        elapsed_time = time.time() - start_time

        logger.info(f"Mensagem enviada: {user_message}")
        logger.info(f"Mensagem recebida: {response.text}")
        logger.info(f"Tempo de resposta do modelo: {elapsed_time:.2f} segundos")

        await update.message.reply_text(
            response.text,
            parse_mode=ParseMode.MARKDOWN,
        )

        await update.message.reply_text(
            f"Tempo de resposta do modelo: {elapsed_time:.2f} segundos",
        )

    except ResourceExhausted as e:
        await update.message.reply_text(
            f"Limite de quota alcançado : {e}",
        )

    except Exception as e:
        logger.error(
            f"Ocorreu um erro ao gerar a resposta: {e}",
            exc_info=True,
        )
        await update.message.reply_text(
            "Ocorreu um erro ao processar sua mensagem. Por favor, tente novamente mais tarde.",
            parse_mode=ParseMode.HTML,
        )
        logger.info(chat_sessions)

    return CHAT


async def request_image(update, context):
    await update.message.reply_text(
        "Processamento de imagem \n Mande uma imagem com descrição (ou não) para eu processar"
    )
    return PROCESSING_IMAGE


async def process_image(update, context):
    try:
        user_images = update.message.photo
        image_description = update.message.caption
        logger.info(f"Imagens do usuário: {str(user_images)}")

        if not user_images:
            return REQUEST_IMAGE

        logger.info("Processando imagem")
        chat_session = get_or_create_chat_session(update.message.from_user.id)
        file = await update.message.photo[0].get_file()
        file_bytes = await file.download_as_bytearray()
        image_file = Image.open(io.BytesIO(file_bytes))

        await update.message.reply_text(
            "Processando imagem...",
            parse_mode=ParseMode.HTML,
        )

        # Pegar o input do user ou mandar só a imagem
        response = await chat_session.send_message_async(
            [
                image_file,
                MODEL_PROMPT + (image_description if image_description else "Gere uma descrição para essa imagem:"),
            ]
        )

        await update.message.reply_text(
            (
                "Enviando pergunta: " + f"<b>{image_description}</b>"
                if image_description
                else "Nenhuma descrição detectada"
            ),
            parse_mode=ParseMode.HTML,
        )

        await update.message.reply_text(
            response.text,
            parse_mode=ParseMode.MARKDOWN,
        )

        return CHAT

    except Exception as e:
        logger.error(f"Erro crítico ao processar imagem: {str(e)}")
        await update.message.reply_text(
            "Erro ao processar imagem, voltando ao chat",
            parse_mode=ParseMode.MARKDOWN,
        )
        return CHAT


async def exit(update, context):
    await update.message.reply_text(
        "<b>Obrigado por utilizar o Gobot \n Para mais conversas digite /start</b>",
        parse_mode=ParseMode.HTML,
    )

    chat_sessions.pop(update.message.from_user.id, None)

    return ConversationHandler.END


async def get_info(update, context):
    chat_session = chat_sessions.get(update.message.from_user.id, None)

    if not chat_session:
        await update.message.reply_text("Não consegui obter informações de conversa, converse comigo primeiro")
        return CHAT

    data = (
        "<b> Informações gerais sobre o Gobot </b>\n\n"
        f"* Nome do modelo: {MODEL_NAME}\n\n"
        f"* Prompt de geração: {MODEL_PROMPT}\n\n"
        f"* Quantidade de mensagens enviadas: {get_user_message_count(chat_session.history)}"
    )

    await update.message.reply_text(data, parse_mode=ParseMode.HTML)
    await update.message.reply_text("Aguarde, obtendo informações sobre nossa conversa...")

    try:
        chat_overview_response = await send_message_with_retry(
            chat_session, "Gere um historico da nossa conversa, em topicos"
        )
        await update.message.reply_text(chat_overview_response.text, parse_mode=ParseMode.HTML)

    except Exception as e:
        print(e)
        await update.message.reply_text(
            "Não consegui obter informações sobre o histórico da nossa conversa mas sei que foi bem legal"
        )
