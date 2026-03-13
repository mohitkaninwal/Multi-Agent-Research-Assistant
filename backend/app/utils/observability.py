from __future__ import annotations

from typing import Any

from app.config import get_settings


def get_langfuse_handler() -> Any | None:
    settings = get_settings()
    if not settings.langfuse_public_key or not settings.langfuse_secret_key:
        return None
    try:
        from langfuse.callback import CallbackHandler
    except Exception:
        return None
    return CallbackHandler(
        secret_key=settings.langfuse_secret_key,
        public_key=settings.langfuse_public_key,
        host=settings.langfuse_host,
    )
