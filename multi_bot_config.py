"""Multi-bot configuration management"""
import os
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotConfig(BaseModel):
    """Configuration for a single bot instance"""
    token: str = Field(..., description="Telegram bot token")
    name: str = Field(..., description="Bot display name (for logs)")
    admin_user_ids: str = Field("", description="Comma-separated admin user IDs")

    @property
    def admin_ids_list(self) -> list[int]:
        """Parse admin_user_ids string into list of integers"""
        if not self.admin_user_ids:
            return []
        try:
            return [int(uid.strip()) for uid in self.admin_user_ids.split(",") if uid.strip()]
        except ValueError:
            return []


class MultiBotConfig(BaseSettings):
    """Configuration for all bots loaded from environment variables"""

    groq_api_key: str = Field(..., description="Groq API key (shared by all bots)")
    proxy_url: str | None = Field(None, description="Proxy URL (shared by all bots)")
    data_dir: str = Field("/data", description="Directory for persistent data")

    # Bot tokens as comma-separated string
    bot_tokens: str = Field(..., description="Comma-separated bot tokens")

    # Optional: Bot names (comma-separated, must match number of tokens)
    bot_names: str = Field("", description="Comma-separated bot names (optional)")

    # Optional: Admin user IDs (same for all bots or empty)
    admin_user_ids: str = Field("", description="Comma-separated admin user IDs")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    @field_validator('bot_tokens')
    @classmethod
    def validate_bot_tokens_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("BOT_TOKENS must contain at least one bot token")
        return v

    def get_bots(self) -> list[BotConfig]:
        """Parse environment variables into list of BotConfig objects"""
        # Parse tokens
        tokens = [t.strip() for t in self.bot_tokens.split(",") if t.strip()]

        # Parse names (optional)
        names = []
        if self.bot_names:
            names = [n.strip() for n in self.bot_names.split(",") if n.strip()]

        # If names not provided or count mismatch, generate default names
        if len(names) != len(tokens):
            names = [f"Bot{i+1}" for i in range(len(tokens))]

        # Create BotConfig for each token
        bots = []
        for i, token in enumerate(tokens):
            bots.append(BotConfig(
                token=token,
                name=names[i],
                admin_user_ids=self.admin_user_ids
            ))

        return bots

    def get_enabled_bots(self) -> list[BotConfig]:
        """Get list of all bots (all are enabled when using env config)"""
        return self.get_bots()


def load_config() -> MultiBotConfig:
    """Load multi-bot configuration from environment variables"""
    return MultiBotConfig()
