from __future__ import annotations

from langchain_groq import ChatGroq

from app.config import get_settings


def get_chat_model():
    settings = get_settings()
    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY is required to run the LLM.")
    return ChatGroq(model=settings.model_name, temperature=0, api_key=settings.groq_api_key)
