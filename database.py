"""Simple JSON-based storage for bot roles"""
import json
import os
from typing import Dict


class RoleStorage:
    """Manages bot roles for different chats"""

    def __init__(self, filename: str = "roles.json"):
        self.filename = filename
        self.roles: Dict[int, str] = self._load()

    def _load(self) -> Dict[int, str]:
        """Load roles from JSON file"""
        # Handle case where file is a directory (Docker volume issue)
        if os.path.isdir(self.filename):
            import shutil
            shutil.rmtree(self.filename)

        if os.path.exists(self.filename) and os.path.isfile(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return {int(k): v for k, v in data.items()}
            except (json.JSONDecodeError, ValueError):
                return {}
        return {}

    def _save(self) -> None:
        """Save roles to JSON file"""
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.roles, f, ensure_ascii=False, indent=2)

    def get_role(self, chat_id: int) -> str:
        """Get role for a chat, returns default if not set"""
        return self.roles.get(
            chat_id,
            "Ты дружелюбный помощник, который комментирует сообщения в групповом чате."
        )

    def set_role(self, chat_id: int, role: str) -> None:
        """Set role for a chat"""
        self.roles[chat_id] = role
        self._save()

    def delete_role(self, chat_id: int) -> bool:
        """Delete role for a chat, returns True if existed"""
        if chat_id in self.roles:
            del self.roles[chat_id]
            self._save()
            return True
        return False


# Global storage instance
role_storage = RoleStorage()
