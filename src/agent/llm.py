"""Utility functions for working with the language model."""

import logging
from langchain_google_genai import ChatGoogleGenerativeAI

from config import settings

logger = logging.getLogger(__name__)

_API_KEYS: list[str] = []
_current_key_idx = 0
MODEL_NAME = "gemini-2.5-flash-preview-05-20"


def _get_api_key() -> str:
    """Return an API key using round-robin selection."""
    global _API_KEYS, _current_key_idx

    if not _API_KEYS:
        keys_str = settings.gemini_api_key.get_secret_value()
        if keys_str:
            _API_KEYS = [k.strip() for k in keys_str.split(",") if k.strip()]
        if not _API_KEYS:
            msg = "Google API keys are not configured or invalid"
            logger.error(msg)
            raise ValueError(msg)

    key = _API_KEYS[_current_key_idx]
    _current_key_idx = (_current_key_idx + 1) % len(_API_KEYS)
    logger.debug("Using Google API key index %s", _current_key_idx)
    return key


def create_llm(
    temperature: float = settings.temperature,
    top_p: float = settings.top_p,
) -> ChatGoogleGenerativeAI:
    """Create a standard LLM instance."""
    return ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=_get_api_key(),
        temperature=temperature,
        top_p=top_p,
        thinking_budget=1024,
    )
    
    
def create_light_llm(temperature: float = settings.temperature, top_p: float = settings.top_p):
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=_get_api_key(),
        temperature=temperature,
        top_p=top_p
    )


def create_precise_llm() -> ChatGoogleGenerativeAI:
    """Return an LLM tuned for deterministic output."""
    return create_llm(temperature=0, top_p=1)
