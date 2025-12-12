"""Groq LLM API client"""
import aiohttp
from typing import List, Dict


class GroqClient:
    """Client for Groq API (free, fast LLM)"""

    BASE_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile", proxy: str | None = None):
        self.api_key = api_key
        self.model = model
        self.proxy = proxy

    async def generate_comment(self, role: str, message: str) -> str:
        """
        Generate a comment based on the role and message

        Args:
            role: System role/prompt for the bot
            message: User message to comment on

        Returns:
            Generated comment text
        """
        messages = [
            {"role": "system", "content": role},
            {"role": "user", "content": f"Прокомментируй это сообщение: {message}"}
        ]

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500,
        }

        try:
            connector = None
            if self.proxy:
                connector = aiohttp.TCPConnector()

            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(
                    self.BASE_URL,
                    json=payload,
                    headers=headers,
                    proxy=self.proxy if self.proxy else None
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        raise Exception(f"Groq API error: {response.status} - {error_text}")
        except Exception as e:
            raise Exception(f"Failed to generate comment: {str(e)}")
