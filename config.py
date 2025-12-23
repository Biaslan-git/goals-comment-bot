from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Config(BaseSettings):
    """Bot configuration from environment variables"""

    telegram_bot_token: str
    groq_api_key: str
    admin_user_ids: str = ""  # Comma-separated list of admin user IDs
    proxy_url: str | None = None
    data_dir: str = "/data"  # Directory for persistent data
    chat_history_limit: int = 20  # Max number of messages to keep in chat history
    delete_previous_messages: bool = True  # Delete previous bot messages before sending new ones

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    @property
    def admin_ids_list(self) -> list[int]:
        """Parse admin_user_ids string into list of integers"""
        if not self.admin_user_ids:
            return []
        try:
            return [int(uid.strip()) for uid in self.admin_user_ids.split(",") if uid.strip()]
        except ValueError:
            return []


config = Config()
