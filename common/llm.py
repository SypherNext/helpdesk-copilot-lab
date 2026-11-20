"""Talks to the local Ollama server. This is the only module that knows its API."""
import httpx

from common import config


class OllamaClient:
    def __init__(self, base_url=config.OLLAMA_URL, model=config.MODEL):
        self.base_url = base_url
        self.model = model

    def chat(self, messages, tools=None):
        """Send the conversation, return the assistant message as a dict.

        The returned dict has "content" (text) and, when the model wants to
        use a tool, "tool_calls".
        """
        body = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            # Small models answer faster and more directly with thinking off.
            "think": False,
            "options": config.MODEL_OPTIONS,
        }
        if tools:
            body["tools"] = tools
        response = httpx.post(
            f"{self.base_url}/api/chat", json=body, timeout=config.MODEL_TIMEOUT_SECONDS
        )
        response.raise_for_status()
        return response.json()["message"]
