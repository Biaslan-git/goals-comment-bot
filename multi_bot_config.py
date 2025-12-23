"""Multi-bot configuration management"""
import os
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotConfig(BaseModel):
    """Configuration for a single bot instance"""
    token: str = Field(..., description="Telegram bot token")
    name: str = Field(..., description="Bot display name (for logs)")
    admin_user_ids: str = Field("", description="Comma-separated admin user IDs")
    enable_history: bool = Field(False, description="Enable chat history storage")
    use_reply: bool = Field(False, description="Use reply instead of answer")
    delete_previous: bool = Field(True, description="Delete previous bot messages before sending new ones")
    channel_id: int | None = Field(None, description="Only reply to messages from this channel ID (optional)")

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
    chat_history_limit: int = Field(20, description="Max number of messages to keep in chat history")

    # Bot tokens as comma-separated string
    bot_tokens: str = Field(..., description="Comma-separated bot tokens")

    # Optional: Bot names (comma-separated, must match number of tokens)
    bot_names: str = Field("", description="Comma-separated bot names (optional)")

    # Optional: Admin user IDs (same for all bots or empty)
    admin_user_ids: str = Field("", description="Comma-separated admin user IDs")

    # Optional: Enable history for specific bots (comma-separated true/false, matches bot order)
    bot_enable_history: str = Field("", description="Comma-separated true/false for each bot")

    # Optional: Use reply for specific bots (comma-separated true/false, matches bot order)
    bot_use_reply: str = Field("", description="Comma-separated true/false for each bot")

    # Optional: Delete previous messages for specific bots (comma-separated true/false, matches bot order)
    bot_delete_previous: str = Field("", description="Comma-separated true/false for each bot")

    # Optional: Channel IDs for specific bots (comma-separated channel IDs, matches bot order)
    bot_channel_ids: str = Field("", description="Comma-separated channel IDs for each bot (empty = all messages)")

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

        # Parse enable_history settings (optional)
        enable_history_list = []
        if self.bot_enable_history:
            enable_history_list = [
                s.strip().lower() == "true"
                for s in self.bot_enable_history.split(",")
                if s.strip()
            ]
        # If not provided or count mismatch, use default (False)
        if len(enable_history_list) != len(tokens):
            enable_history_list = [False] * len(tokens)

        # Parse use_reply settings (optional)
        use_reply_list = []
        if self.bot_use_reply:
            use_reply_list = [
                s.strip().lower() == "true"
                for s in self.bot_use_reply.split(",")
                if s.strip()
            ]
        # If not provided or count mismatch, use default (False)
        if len(use_reply_list) != len(tokens):
            use_reply_list = [False] * len(tokens)

        # Parse delete_previous settings (optional)
        delete_previous_list = []
        if self.bot_delete_previous:
            delete_previous_list = [
                s.strip().lower() == "true"
                for s in self.bot_delete_previous.split(",")
                if s.strip()
            ]
        # If not provided or count mismatch, use default (True)
        if len(delete_previous_list) != len(tokens):
            delete_previous_list = [True] * len(tokens)

        # Parse channel_ids settings (optional)
        channel_ids_list = []
        if self.bot_channel_ids:
            for s in self.bot_channel_ids.split(","):
                s = s.strip()
                if s and s.lower() != "none":
                    try:
                        channel_ids_list.append(int(s))
                    except ValueError:
                        channel_ids_list.append(None)
                else:
                    channel_ids_list.append(None)
        # If not provided or count mismatch, use default (None)
        if len(channel_ids_list) != len(tokens):
            channel_ids_list = [None] * len(tokens)

        # Create BotConfig for each token
        bots = []
        for i, token in enumerate(tokens):
            bots.append(BotConfig(
                token=token,
                name=names[i],
                admin_user_ids=self.admin_user_ids,
                enable_history=enable_history_list[i],
                use_reply=use_reply_list[i],
                delete_previous=delete_previous_list[i],
                channel_id=channel_ids_list[i]
            ))

        return bots

    def get_enabled_bots(self) -> list[BotConfig]:
        """Get list of all bots (all are enabled when using env config)"""
        return self.get_bots()


def load_config() -> MultiBotConfig:
    """Load multi-bot configuration from environment variables"""
    return MultiBotConfig()
