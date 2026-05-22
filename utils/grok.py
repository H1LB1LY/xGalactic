"""xAI Grok translation client via AsyncOpenAI-compatible API."""

from __future__ import annotations

import os
from dataclasses import dataclass

from openai import AsyncOpenAI

from utils.security import sanitize_text

SYSTEM_PROMPT = (
    "Translate naturally as a native speaker would say it. "
    "Preserve tone, slang, memes, emojis, and formatting. "
    "Output ONLY the translation."
)

DETECT_PROMPT = (
    "Detect the ISO 639-1 language code of the following text. "
    "Reply with ONLY the two-letter code, nothing else."
)

# Approximate pricing per 1M tokens (update when xAI changes rates)
INPUT_COST_PER_M = 0.20
OUTPUT_COST_PER_M = 0.50


@dataclass
class TranslationResult:
    text: str
    prompt_tokens: int
    completion_tokens: int
    model: str


class GrokClient:
    BASE_URL = "https://api.x.ai/v1"

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self._env_key = os.getenv("XAI_API_KEY")
        self._api_key = api_key or self._env_key
        self.default_model = model or os.getenv("GROK_MODEL", "grok-4.1-fast")
        self._client: AsyncOpenAI | None = None

    def _get_client(self, api_key: str | None = None) -> AsyncOpenAI:
        key = api_key or self._api_key
        if not key:
            raise ValueError(
                "No xAI API key configured. Set XAI_API_KEY in .env or use /config."
            )
        return AsyncOpenAI(api_key=key, base_url=self.BASE_URL)

    async def translate(
        self,
        text: str,
        target_language: str,
        *,
        api_key: str | None = None,
        model: str | None = None,
        style_hint: str | None = None,
    ) -> TranslationResult:
        clean = sanitize_text(text)
        if not clean:
            raise ValueError("Nothing to translate.")

        user_content = f"Translate the following to {target_language}:\n\n{clean}"
        if style_hint:
            user_content = f"Style: {style_hint}\n\n{user_content}"

        client = self._get_client(api_key)
        use_model = model or self.default_model

        response = await client.chat.completions.create(
            model=use_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0.3,
            max_tokens=2048,
        )

        choice = response.choices[0].message.content or ""
        usage = response.usage
        return TranslationResult(
            text=choice.strip(),
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            model=use_model,
        )

    async def detect_language(
        self,
        text: str,
        *,
        api_key: str | None = None,
        model: str | None = None,
    ) -> str:
        clean = sanitize_text(text, max_len=500)
        client = self._get_client(api_key)
        use_model = model or self.default_model

        response = await client.chat.completions.create(
            model=use_model,
            messages=[
                {"role": "system", "content": DETECT_PROMPT},
                {"role": "user", "content": clean},
            ],
            temperature=0,
            max_tokens=10,
        )
        return (response.choices[0].message.content or "en").strip().lower()[:2]

    @staticmethod
    def estimate_cost(prompt_tokens: int, completion_tokens: int) -> float:
        return (
            prompt_tokens * INPUT_COST_PER_M + completion_tokens * OUTPUT_COST_PER_M
        ) / 1_000_000
