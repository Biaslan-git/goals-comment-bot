from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Bot configuration from environment variables"""

    telegram_bot_token: str
    groq_api_key: str
    admin_user_id: int | None = None
    proxy_url: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


config = Config()
