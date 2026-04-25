import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "TokenForge"
    version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    json_logs: bool = False

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000", "http://localhost:3001", "http://localhost:80"]

    # LLM Adapter: "ollama" | "mock"
    llm_adapter: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma4:latest"
    ollama_timeout: int = 120

    # Embeddings
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_device: str = "cpu"

    # Optimization
    default_mode: str = "balanced"
    max_prompt_length: int = 100_000
    semantic_similarity_threshold: float = 0.85

    # Rate limiting
    rate_limit_requests: int = 60
    rate_limit_window: int = 60


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
