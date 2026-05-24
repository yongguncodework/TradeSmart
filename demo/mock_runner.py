"""Zero-cost portfolio preview — returns a saved sample response (no OpenAI)."""

from __future__ import annotations

import json
from pathlib import Path

from demo.i18n import normalize_lang

DEMO_DIR = Path(__file__).resolve().parent
SAMPLE_PATH = DEMO_DIR / "sample_response.json"


def sample_path_for_lang(lang: str | None) -> Path:
    code = normalize_lang(lang)
    if code == "ko":
        ko_path = DEMO_DIR / "sample_response.ko.json"
        if ko_path.exists():
            return ko_path
    return SAMPLE_PATH


def load_sample_response(lang: str | None = None) -> dict:
    path = sample_path_for_lang(lang)
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def mock_health() -> dict:
    return {
        "status": "ok",
        "version": "0.2.0-preview",
        "vector_store_ready": True,
        "journal_store_ready": True,
        "mock": True,
    }


def run_research_mock(payload: dict) -> dict:
    """Return canned demo output instantly — $0 API cost."""
    lang = payload.get("response_language")
    sample = load_sample_response(lang)
    sample["query"] = payload.get("query") or sample["query"]
    return sample
