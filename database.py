"""Simple JSON-based storage for bot role"""
import json
import os
import hashlib


class RoleStorage:
    """Manages bot role (single global role for all chats) and last message IDs"""

    DEFAULT_ROLE = "Ты дружелюбный помощник, который комментирует сообщения в групповом чате."

    def __init__(self, bot_token: str, data_dir: str = "/data"):
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)

        # Use hash of bot token for unique filename
        token_hash = hashlib.md5(bot_token.encode()).hexdigest()[:8]
        self.filename = os.path.join(data_dir, f"role_{token_hash}.json")
        self.role: str = self.DEFAULT_ROLE
        self.last_message_ids: dict[int, int] = {}  # chat_id -> message_id
        self._load()

    def _load(self) -> None:
        """Load role and last message IDs from JSON file (backward compatible)"""
        # Handle case where file is a directory (Docker volume issue)
        if os.path.isdir(self.filename):
            import shutil
            shutil.rmtree(self.filename)

        if os.path.exists(self.filename) and os.path.isfile(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    data = json.load(f)

                    # Load role (backward compatible)
                    self.role = data.get("role", self.DEFAULT_ROLE)

                    # Load last_message_ids with integer keys (new field, backward compatible)
                    last_msg_ids = data.get("last_message_ids", {})
                    self.last_message_ids = {int(k): v for k, v in last_msg_ids.items()} if last_msg_ids else {}
            except (json.JSONDecodeError, ValueError):
                self.role = self.DEFAULT_ROLE
                self.last_message_ids = {}

    def _save(self) -> None:
        """Save role and last message IDs to JSON file"""
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump({
                "role": self.role,
                "last_message_ids": self.last_message_ids
            }, f, ensure_ascii=False, indent=2)

    def get_role(self) -> str:
        """Get current role"""
        return self.role

    def set_role(self, role: str) -> None:
        """Set new role"""
        self.role = role
        self._save()

    def delete_role(self) -> None:
        """Reset to default role"""
        self.role = self.DEFAULT_ROLE
        self._save()

    def get_last_message_id(self, chat_id: int) -> int | None:
        """Get last message ID for a chat"""
        return self.last_message_ids.get(chat_id)

    def set_last_message_id(self, chat_id: int, message_id: int) -> None:
        """Set last message ID for a chat"""
        self.last_message_ids[chat_id] = message_id
        self._save()

    def clear_last_message_id(self, chat_id: int) -> None:
        """Clear last message ID for a chat"""
        if chat_id in self.last_message_ids:
            del self.last_message_ids[chat_id]
            self._save()


# Global storage instance will be initialized in handlers.py after config is loaded
