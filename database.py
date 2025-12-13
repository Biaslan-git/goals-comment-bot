"""Simple JSON-based storage for bot role"""
import json
import os
import hashlib


class RoleStorage:
    """Manages bot role (single global role for all chats)"""

    DEFAULT_ROLE = "Ты дружелюбный помощник, который комментирует сообщения в групповом чате."

    def __init__(self, bot_token: str, data_dir: str = "/data"):
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)

        # Use hash of bot token for unique filename
        token_hash = hashlib.md5(bot_token.encode()).hexdigest()[:8]
        self.filename = os.path.join(data_dir, f"role_{token_hash}.json")
        self.role: str = self._load()

    def _load(self) -> str:
        """Load role from JSON file"""
        # Handle case where file is a directory (Docker volume issue)
        if os.path.isdir(self.filename):
            import shutil
            shutil.rmtree(self.filename)

        if os.path.exists(self.filename) and os.path.isfile(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("role", self.DEFAULT_ROLE)
            except (json.JSONDecodeError, ValueError):
                return self.DEFAULT_ROLE
        return self.DEFAULT_ROLE

    def _save(self) -> None:
        """Save role to JSON file"""
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump({"role": self.role}, f, ensure_ascii=False, indent=2)

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


# Global storage instance will be initialized in handlers.py after config is loaded
