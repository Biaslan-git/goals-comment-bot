"""Delete webhook if it was set"""
import asyncio
from aiogram import Bot
from config import config


async def delete_webhook():
    bot = Bot(token=config.telegram_bot_token)
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print("Webhook deleted successfully!")

        # Check webhook info
        webhook_info = await bot.get_webhook_info()
        print(f"Webhook URL: {webhook_info.url}")
        print(f"Pending updates: {webhook_info.pending_update_count}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(delete_webhook())
