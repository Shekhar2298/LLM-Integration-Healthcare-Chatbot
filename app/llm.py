from typing import Protocol

import httpx

from app.config import Settings
from app.safety import SYSTEM_POLICY


class LLMError(RuntimeError):
    """Raised when an LLM provider cannot produce a response."""


class LLMClient(Protocol):
    async def complete(self, user_message: str) -> str:
        ...


class MockLLMClient:
    """Deterministic provider used for local development and automated tests."""

    async def complete(self, user_message: str) -> str:
        del user_message
        return (
            "I can share general health education, but I cannot diagnose or prescribe. "
            "For a useful conversation with a clinician, note when the concern started, "
            "what makes it better or worse, and any medicines or conditions your clinician "
            "already knows about."
        )


class OpenAICompatibleClient:
    def __init__(self, settings: Settings) -> None:
        if not settings.llm_api_key or not settings.llm_model:
            raise LLMError(
                "LLM_API_KEY and LLM_MODEL are required when LLM_PROVIDER is not 'mock'"
            )
        self._settings = settings
        self._endpoint = settings.llm_base_url.rstrip("/") + "/chat/completions"

    async def complete(self, user_message: str) -> str:
        payload = {
            "model": self._settings.llm_model,
            "messages": [
                {"role": "system", "content": SYSTEM_POLICY},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.2,
            "max_tokens": 450,
        }
        headers = {
            "Authorization": f"Bearer {self._settings.llm_api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self._settings.llm_timeout_seconds) as client:
                response = await client.post(self._endpoint, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise LLMError("The configured LLM provider is unavailable") from exc

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError("The LLM provider returned an unexpected response") from exc

        if not isinstance(content, str) or not content.strip():
            raise LLMError("The LLM provider returned an empty response")
        return content.strip()


def create_llm_client(settings: Settings) -> LLMClient:
    if settings.llm_provider.lower() == "mock":
        return MockLLMClient()
    return OpenAICompatibleClient(settings)