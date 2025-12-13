"""Bot message handlers"""
from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.enums import ChatType
import logging

from database import RoleStorage
from llm_client import GroqClient
from config import config

logger = logging.getLogger(__name__)
router = Router()

# Initialize storage and LLM client
role_storage = RoleStorage(bot_token=config.telegram_bot_token, data_dir=config.data_dir)
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
    """Set bot role (works in private chat only)"""
    if not command.args:
        await message.answer(
            "Использование: /setrole &lt;текст роли&gt;\n\n"
            "Пример:\n"
            "/setrole Ты опытный психолог, который дает мотивирующие комментарии к целям людей"
        )
        return

    role = command.args
    role_storage.set_role(role)

    await message.answer(f"Роль установлена для всех чатов!\n\n{role}")
    logger.info(f"Role set: {role[:50]}...")


@router.message(Command("getrole"))
async def cmd_get_role(message: Message):
    """Get current bot role"""
    role = role_storage.get_role()
    await message.answer(f"Текущая роль:\n\n{role}")


@router.message(Command("deleterole"))
async def cmd_delete_role(message: Message):
    """Reset to default role"""
    role_storage.delete_role()
    await message.answer("Роль сброшена на стандартную.")


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
    role = role_storage.get_role()
    user_message = message.text

    try:
        # Generate comment using LLM
        comment = await llm_client.generate_comment(role, user_message)

        # Send comment as regular message (not reply)
        await message.answer(comment)
        logger.info(f"Commented in chat {chat_id}")

    except Exception as e:
        logger.error(f"Error generating comment: {e}", exc_info=True)
        await message.answer("Извини, произошла ошибка при генерации комментария.")


@router.message(
    F.chat.type == ChatType.PRIVATE,
    F.text
)
async def handle_private_message(message: Message):
    """Handle messages in private chat"""
    if message.text and message.text.startswith("/"):
        return

    await message.answer(
        "Я работаю в групповых чатах! Добавь меня в группу, "
        "чтобы я комментировал сообщения.\n\n"
        "Используй /start для списка команд."
    )
