"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Central settings for TradeSmrt."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    chroma_persist_dir: str = str(PROJECT_ROOT / "data" / "chroma")
    playbooks_dir: str = str(PROJECT_ROOT / "data" / "playbooks")
    journal_path: str = str(PROJECT_ROOT / "data" / "journal" / "trades.jsonl")
    rag_top_k: int = 4

    max_position_pct: float = 15.0
    max_leveraged_etf_pct: float = 8.0
    max_daily_loss_pct: float = 3.0

    @property
    def tracked_symbols(self) -> list[str]:
        """Default watchlist aligned with the project focus."""
        return ["BTC-USD", "SOXL", "QQQ", "SPY", "SMH"]


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
