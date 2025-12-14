"""Bot message handlers for multi-bot setup"""
from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.enums import ChatType
import logging

from database import RoleStorage
from llm_client import GroqClient
from multi_bot_config import BotConfig

logger = logging.getLogger(__name__)


class BotHandlers:
    """Handler factory for individual bot instances"""

    def __init__(self, bot_config: BotConfig, groq_client: GroqClient, data_dir: str):
        self.bot_config = bot_config
        self.groq_client = groq_client
        self.router = Router()

        # Each bot has its own storage
        self.role_storage = RoleStorage(
            bot_token=bot_config.token,
            data_dir=data_dir
        )

        # Register handlers
        self._register_handlers()

    def _is_admin(self, user_id: int) -> bool:
        """Check if user is admin for this bot"""
        admin_ids = self.bot_config.admin_ids_list
        # If no admins configured, allow everyone
        if not admin_ids:
            return True
        return user_id in admin_ids

    def _register_handlers(self):
        """Register all message handlers for this bot"""

        @self.router.message(Command("start"))
        async def cmd_start(message: Message):
            """Handle /start command"""
            await message.answer(
                f"Привет! Я {self.bot_config.name} - бот, который комментирует сообщения в группах.\n\n"
                "Команды:\n"
                "/setrole &lt;текст роли&gt; - установить роль для этого бота\n"
                "/getrole - посмотреть текущую роль\n"
                "/deleterole - удалить роль (вернуться к стандартной)\n\n"
                "Добавь меня в группу, и я буду комментировать сообщения!"
            )

        @self.router.message(Command("setrole"))
        async def cmd_set_role(message: Message, command: CommandObject):
            """Set bot role (admin only)"""
            if not self._is_admin(message.from_user.id):
                await message.answer("У вас нет прав для выполнения этой команды.")
                logger.warning(
                    f"[{self.bot_config.name}] Unauthorized setrole attempt from user {message.from_user.id}"
                )
                return

            if not command.args:
                await message.answer(
                    "Использование: /setrole &lt;текст роли&gt;\n\n"
                    "Пример:\n"
                    "/setrole Ты опытный психолог, который дает мотивирующие комментарии к целям людей"
                )
                return

            role = command.args
            self.role_storage.set_role(role)

            await message.answer(f"Роль установлена!\n\n{role}")
            logger.info(f"[{self.bot_config.name}] Role set by user {message.from_user.id}: {role[:50]}...")

        @self.router.message(Command("getrole"))
        async def cmd_get_role(message: Message):
            """Get current bot role"""
            role = self.role_storage.get_role()
            await message.answer(f"Текущая роль {self.bot_config.name}:\n\n{role}")

        @self.router.message(Command("deleterole"))
        async def cmd_delete_role(message: Message):
            """Reset to default role (admin only)"""
            if not self._is_admin(message.from_user.id):
                await message.answer("У вас нет прав для выполнения этой команды.")
                logger.warning(
                    f"[{self.bot_config.name}] Unauthorized deleterole attempt from user {message.from_user.id}"
                )
                return

            self.role_storage.delete_role()

            await message.answer("Роль сброшена на стандартную.")
            logger.info(f"[{self.bot_config.name}] Role deleted by user {message.from_user.id}")

        @self.router.message(
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
            role = self.role_storage.get_role()
            user_message = message.text

            try:
                # Delete previous bot comment if it exists
                last_message_id = self.role_storage.get_last_message_id(chat_id)
                if last_message_id:
                    try:
                        await message.bot.delete_message(chat_id=chat_id, message_id=last_message_id)
                        logger.info(
                            f"[{self.bot_config.name}] Deleted previous comment "
                            f"(message_id={last_message_id}) in chat {chat_id}"
                        )
                    except Exception as e:
                        logger.warning(
                            f"[{self.bot_config.name}] Could not delete previous message "
                            f"{last_message_id} in chat {chat_id}: {e}"
                        )
                        # Clear the stored message_id if deletion failed
                        self.role_storage.clear_last_message_id(chat_id)

                # Generate comment using LLM
                comment = await self.groq_client.generate_comment(role, user_message)

                # Send comment as regular message (not reply)
                sent_message = await message.answer(comment)

                # Store the message ID of the new comment
                self.role_storage.set_last_message_id(chat_id, sent_message.message_id)

                logger.info(
                    f"[{self.bot_config.name}] Commented in chat {chat_id} "
                    f"(message_id={sent_message.message_id})"
                )

            except Exception as e:
                logger.error(f"[{self.bot_config.name}] Error generating comment: {e}", exc_info=True)
                await message.answer("Извини, произошла ошибка при генерации комментария.")

        @self.router.message(
            F.chat.type == ChatType.PRIVATE,
            F.text
        )
        async def handle_private_message(message: Message):
            """Handle messages in private chat"""
            if message.text and message.text.startswith("/"):
                return

            await message.answer(
                f"Я {self.bot_config.name} и работаю в групповых чатах! "
                "Добавь меня в группу, чтобы я комментировал сообщения.\n\n"
                "Используй /start для списка команд."
            )
