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
role_storage = RoleStorage(
    bot_token=config.telegram_bot_token,
    data_dir=config.data_dir,
    history_limit=config.chat_history_limit
)
llm_client = GroqClient(api_key=config.groq_api_key, proxy=config.proxy_url)


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    admin_ids = config.admin_ids_list
    # If no admins configured, allow everyone
    if not admin_ids:
        return True
    return user_id in admin_ids


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
    """Set bot role (admin only)"""
    # Check admin access
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет прав для выполнения этой команды.")
        logger.warning(f"Unauthorized setrole attempt from user {message.from_user.id}")
        return

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
    logger.info(f"Role set by user {message.from_user.id}: {role[:50]}...")


@router.message(Command("getrole"))
async def cmd_get_role(message: Message):
    """Get current bot role"""
    role = role_storage.get_role()
    await message.answer(f"Текущая роль:\n\n{role}")


@router.message(Command("deleterole"))
async def cmd_delete_role(message: Message):
    """Reset to default role (admin only)"""
    # Check admin access
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет прав для выполнения этой команды.")
        logger.warning(f"Unauthorized deleterole attempt from user {message.from_user.id}")
        return

    role_storage.delete_role()
    await message.answer("Роль сброшена на стандартную.")
    logger.info(f"Role deleted by user {message.from_user.id}")


@router.message(
    F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}),
    F.text
)
async def handle_group_message(message: Message):
    """Handle messages in groups"""
    # Skip if message is a command
    if message.text and message.text.startswith("/"):
        return

    # Skip if message is from a bot user (not channel)
    # Allow messages from channels (sender_chat is set but from_user might be None or a bot)
    if message.from_user and message.from_user.is_bot and not message.sender_chat:
        return

    chat_id = message.chat.id
    role = role_storage.get_role()
    user_message = message.text

    # Log message source for debugging
    if message.sender_chat:
        logger.info(f"Processing message from channel/chat: {message.sender_chat.title} (id={message.sender_chat.id})")
    elif message.from_user:
        logger.info(f"Processing message from user: {message.from_user.username or message.from_user.id}")

    try:
        # Delete previous bot comment if it exists
        last_message_id = role_storage.get_last_message_id(chat_id)
        if last_message_id:
            try:
                await message.bot.delete_message(chat_id=chat_id, message_id=last_message_id)
                logger.info(f"Deleted previous comment (message_id={last_message_id}) in chat {chat_id}")
            except Exception as e:
                logger.warning(f"Could not delete previous message {last_message_id} in chat {chat_id}: {e}")
                # Clear the stored message_id if deletion failed (message might have been deleted manually)
                role_storage.clear_last_message_id(chat_id)

        # Get chat history for context
        chat_history = role_storage.get_chat_history(chat_id)

        # Generate comment using LLM with chat history
        comment = await llm_client.generate_comment(role, user_message, chat_history)

        # Send comment as reply to the user's message
        sent_message = await message.reply(comment)

        # Add user message and bot response to chat history
        role_storage.add_message_to_history(chat_id, "user", user_message)
        role_storage.add_message_to_history(chat_id, "assistant", comment)

        # Store the message ID of the new comment
        role_storage.set_last_message_id(chat_id, sent_message.message_id)

        logger.info(f"Commented in chat {chat_id} (message_id={sent_message.message_id})")

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
