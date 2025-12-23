"""Simple JSON-based storage for bot role"""
import json
import os
import hashlib
from typing import List, Dict


class RoleStorage:
    """Manages bot role (single global role for all chats) and last message IDs"""

    DEFAULT_ROLE = "Ты дружелюбный помощник, который комментирует сообщения в групповом чате."

    def __init__(self, bot_token: str, data_dir: str = "/data", history_limit: int = 20):
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)

        # Use hash of bot token for unique filename
        token_hash = hashlib.md5(bot_token.encode()).hexdigest()[:8]
        self.filename = os.path.join(data_dir, f"role_{token_hash}.json")
        self.role: str = self.DEFAULT_ROLE
        self.last_message_ids: dict[int, int] = {}  # chat_id -> message_id
        self.chat_histories: dict[int, List[Dict[str, str]]] = {}  # chat_id -> list of messages
        self.history_limit = history_limit
        self._load()

    def _load(self) -> None:
        """Load role, last message IDs, and chat histories from JSON file (backward compatible)"""
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

                    # Load last_message_ids with integer keys (backward compatible)
                    last_msg_ids = data.get("last_message_ids", {})
                    self.last_message_ids = {int(k): v for k, v in last_msg_ids.items()} if last_msg_ids else {}

                    # Load chat_histories with integer keys (new field, backward compatible)
                    chat_hists = data.get("chat_histories", {})
                    self.chat_histories = {int(k): v for k, v in chat_hists.items()} if chat_hists else {}
            except (json.JSONDecodeError, ValueError):
                self.role = self.DEFAULT_ROLE
                self.last_message_ids = {}
                self.chat_histories = {}

    def _save(self) -> None:
        """Save role, last message IDs, and chat histories to JSON file"""
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump({
                "role": self.role,
                "last_message_ids": self.last_message_ids,
                "chat_histories": self.chat_histories
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

    def get_chat_history(self, chat_id: int) -> List[Dict[str, str]]:
        """Get chat history for a specific chat"""
        return self.chat_histories.get(chat_id, [])

    def add_message_to_history(self, chat_id: int, role: str, content: str) -> None:
        """Add a message to chat history and maintain limit"""
        if chat_id not in self.chat_histories:
            self.chat_histories[chat_id] = []

        # Add new message
        self.chat_histories[chat_id].append({"role": role, "content": content})

        # Trim history if it exceeds limit
        if len(self.chat_histories[chat_id]) > self.history_limit:
            self.chat_histories[chat_id] = self.chat_histories[chat_id][-self.history_limit:]

        self._save()

    def clear_chat_history(self, chat_id: int) -> None:
        """Clear chat history for a specific chat"""
        if chat_id in self.chat_histories:
            del self.chat_histories[chat_id]
            self._save()


# Global storage instance will be initialized in handlers.py after config is loaded
