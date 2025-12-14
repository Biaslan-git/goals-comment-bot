"""
Multi-bot Telegram bot manager - runs multiple bots in a single process
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, BotCommandScopeDefault

from multi_bot_config import load_config, BotConfig
from multi_bot_handlers import BotHandlers
from llm_client import GroqClient


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def setup_bot_commands(bot: Bot, bot_name: str):
    """Set bot commands for better UX"""
    commands = [
        BotCommand(command="start", description="Информация о боте"),
        BotCommand(command="setrole", description="Установить роль бота"),
        BotCommand(command="getrole", description="Посмотреть текущую роль"),
        BotCommand(command="deleterole", description="Удалить роль"),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
    logger.info(f"[{bot_name}] Commands set successfully")


async def run_bot(bot_config: BotConfig, groq_client: GroqClient, data_dir: str):
    """Run a single bot instance"""
    logger.info(f"[{bot_config.name}] Starting bot...")

    # Initialize bot and dispatcher
    bot = Bot(
        token=bot_config.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Create handlers for this bot
    bot_handlers = BotHandlers(bot_config, groq_client, data_dir)

    # Register router with handlers
    dp.include_router(bot_handlers.router)

    # Set bot commands
    await setup_bot_commands(bot, bot_config.name)

    # Start polling
    try:
        logger.info(f"[{bot_config.name}] Bot started successfully!")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"[{bot_config.name}] Error: {e}", exc_info=True)
    finally:
        await bot.session.close()
        logger.info(f"[{bot_config.name}] Bot stopped")


async def main():
    """Start all bots"""
    logger.info("=" * 60)
    logger.info("Multi-Bot Manager Starting")
    logger.info("=" * 60)

    # Load configuration from environment variables
    try:
        config = load_config()
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}", exc_info=True)
        return

    enabled_bots = config.get_enabled_bots()

    if not enabled_bots:
        logger.error("No enabled bots found in configuration")
        return

    logger.info(f"Loaded configuration for {len(enabled_bots)} enabled bot(s)")
    for bot in enabled_bots:
        logger.info(f"  - {bot.name}")

    # Create shared Groq client
    groq_client = GroqClient(api_key=config.groq_api_key, proxy=config.proxy_url)
    logger.info("Groq client initialized")

    # Create tasks for all bots
    tasks = [
        run_bot(bot_config, groq_client, config.data_dir)
        for bot_config in enabled_bots
    ]

    logger.info("=" * 60)
    logger.info(f"Starting {len(tasks)} bot instance(s)...")
    logger.info("=" * 60)

    # Run all bots concurrently
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        logger.info("All bots stopped")


if __name__ == "__main__":
    asyncio.run(main())
