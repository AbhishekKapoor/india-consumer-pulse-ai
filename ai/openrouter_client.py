"""
OpenRouter API Client — India Consumer Pulse AI

All AI calls in this project route through this module.
Do NOT import openai or call OpenRouter from app.py or dashboard files.

OpenRouter uses the OpenAI-compatible API spec.
Docs: https://openrouter.ai/docs
"""

import json
import logging
import re
import time
from typing import Any, Optional

from openai import OpenAI, RateLimitError, APIError

from config.settings import settings

logger = logging.getLogger(__name__)

_HEADERS = {
    "HTTP-Referer": "https://india-consumer-pulse-ai.local",
    "X-Title": "India Consumer Pulse AI",
}


class OpenRouterClient:
    def __init__(self) -> None:
        if not settings.openrouter_configured:
            logger.warning("OPENROUTER_API_KEY not set — AI calls will use fallback mode")
            self._client = None
        else:
            self._client = OpenAI(
                base_url=settings.OPENROUTER_BASE_URL,
                api_key=settings.OPENROUTER_API_KEY,
                default_headers=_HEADERS,
            )

    @property
    def is_available(self) -> bool:
        return self._client is not None

    def chat(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> Optional[str]:
        """Send a chat request and return the response text, or None on failure."""
        if not self.is_available:
            return None

        model = model or settings.OPENROUTER_MODEL

        for attempt in range(3):
            try:
                response = self._client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content
            except RateLimitError:
                wait = 2 ** attempt * 5
                logger.warning(f"OpenRouter rate limit — waiting {wait}s (attempt {attempt + 1})")
                time.sleep(wait)
            except APIError as e:
                logger.error(f"OpenRouter API error (model={model}): {e}")
                return None
            except Exception as e:
                logger.error(f"Unexpected error calling OpenRouter (model={model}): {e}")
                return None

        return None

    def chat_json(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1500,
    ) -> Optional[Any]:
        """Send a chat request expecting JSON back. Returns parsed object or None."""
        raw = self.chat(messages, model=model, temperature=temperature, max_tokens=max_tokens)
        if raw is None:
            return None
        return _parse_json(raw)


# ── Module-level singleton ────────────────────────────────────

_client: Optional[OpenRouterClient] = None


def get_client() -> OpenRouterClient:
    global _client
    if _client is None:
        _client = OpenRouterClient()
    return _client


# ── JSON parsing utility ──────────────────────────────────────

def _parse_json(text: str) -> Optional[Any]:
    """Try multiple strategies to extract valid JSON from LLM output."""
    # Strip reasoning model think-blocks (<think>...</think>) before parsing
    text = re.sub(r"<think>[\s\S]*?</think>", "", text, flags=re.IGNORECASE).strip()

    # 1. Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2. Extract from markdown code block
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # 3. Extract first JSON array
    match = re.search(r"(\[[\s\S]*\])", text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # 4. Extract first JSON object
    match = re.search(r"(\{[\s\S]*\})", text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    preview = text[:120].replace("\n", " ")
    logger.warning(f"Could not parse JSON from OpenRouter response. Preview: {preview!r}")
    return None
