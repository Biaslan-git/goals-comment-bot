"""Bot message handlers"""
from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.enums import ChatType
import logging

from database import role_storage
from llm_client import GroqClient
from config import config

logger = logging.getLogger(__name__)
router = Router()

# Initialize LLM client
llm_client = GroqClient(api_key=config.groq_api_key, proxy=config.proxy_url)


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command"""
    await message.answer(
        "Привет! Я бот, который комментирует сообщения в группах.\n\n"
        "Команды:\n"
        "/setrole &lt;текст роли&gt; - установить роль для этого чата\n"
        "/getrole - посмотреть текущую роль\n"
        "/deleterole - удалить роль (вернуться к стандартной)\n\n"
        "Добавь меня в группу, и я буду комментировать сообщения!"
    )


@router.message(Command("setrole"))
async def cmd_set_role(message: Message, command: CommandObject):
    """Set bot role for current chat"""
    if not command.args:
        await message.answer(
            "Использование: /setrole &lt;текст роли&gt;\n\n"
            "Пример:\n"
            "/setrole Ты опытный психолог, который дает мотивирующие комментарии к целям людей"
        )
        return

    chat_id = message.chat.id
    role = command.args
    role_storage.set_role(chat_id, role)

    await message.answer(f"Роль установлена!\n\n{role}")
    logger.info(f"Role set for chat {chat_id}: {role[:50]}...")


@router.message(Command("getrole"))
async def cmd_get_role(message: Message):
    """Get current bot role for this chat"""
    chat_id = message.chat.id
    role = role_storage.get_role(chat_id)
    await message.answer(f"Текущая роль:\n\n{role}")


@router.message(Command("deleterole"))
async def cmd_delete_role(message: Message):
    """Delete custom role for this chat"""
    chat_id = message.chat.id
    if role_storage.delete_role(chat_id):
        await message.answer("Роль удалена. Использую стандартную роль.")
    else:
        await message.answer("Роль не была установлена.")


@router.message(
    F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}),
    F.text
)
async def handle_group_message(message: Message):
    """Handle messages in groups"""
    # Skip if message is a command
    if message.text and message.text.startswith("/"):
        return

    # Skip if message is from a bot
    if message.from_user and message.from_user.is_bot:
        return

    chat_id = message.chat.id
    role = role_storage.get_role(chat_id)
    user_message = message.text

    try:
        # Generate comment using LLM
        comment = await llm_client.generate_comment(role, user_message)

        # Reply to the message
        await message.reply(comment)
        logger.info(f"Commented in chat {chat_id}")

    except Exception as e:
        logger.error(f"Error generating comment: {e}", exc_info=True)
        await message.reply("Извини, произошла ошибка при генерации комментария.")


@router.message(F.text)
async def handle_private_message(message: Message):
    """Handle messages in private chat"""
    if message.text and message.text.startswith("/"):
        return

    await message.answer(
        "Я работаю в групповых чатах! Добавь меня в группу, "
        "чтобы я комментировал сообщения.\n\n"
        "Используй /start для списка команд."
    )
