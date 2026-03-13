from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class Settings(BaseModel):
    app_name: str = "AutoResearch API"
    app_env: str = Field(default=os.getenv("APP_ENV", "development"))
    log_level: str = Field(default=os.getenv("LOG_LEVEL", "INFO"))
    provider: Literal["openai", "anthropic"] = Field(
        default=os.getenv("LLM_PROVIDER", "openai")
    )
    model_name: str = Field(
        default=os.getenv("LLM_MODEL", "gpt-4o-mini"),
    )
    tavily_api_key: str | None = Field(default=os.getenv("TAVILY_API_KEY"))
    openai_api_key: str | None = Field(default=os.getenv("OPENAI_API_KEY"))
    anthropic_api_key: str | None = Field(default=os.getenv("ANTHROPIC_API_KEY"))
    langfuse_public_key: str | None = Field(default=os.getenv("LANGFUSE_PUBLIC_KEY"))
    langfuse_secret_key: str | None = Field(default=os.getenv("LANGFUSE_SECRET_KEY"))
    langfuse_host: str = Field(default=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"))
    search_max_results: int = Field(default=int(os.getenv("SEARCH_MAX_RESULTS", "5")))
    search_delay_seconds: float = Field(default=float(os.getenv("SEARCH_DELAY_SECONDS", "0.5")))
    max_subtopics: int = Field(default=int(os.getenv("MAX_SUBTOPICS", "5")))
    critic_loop_limit: int = Field(default=int(os.getenv("CRITIC_LOOP_LIMIT", "1")))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
