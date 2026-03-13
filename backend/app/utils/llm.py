from __future__ import annotations

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

from app.config import get_settings


def get_chat_model():
    settings = get_settings()
    if settings.provider == "anthropic":
        if not settings.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is required when LLM_PROVIDER=anthropic.")
        return ChatAnthropic(model=settings.model_name, temperature=0)
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is required when LLM_PROVIDER=openai.")
    return ChatOpenAI(model=settings.model_name, temperature=0)
