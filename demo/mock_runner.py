"""Zero-cost portfolio preview — returns a saved sample response (no OpenAI)."""

from __future__ import annotations

import json
from pathlib import Path

SAMPLE_PATH = Path(__file__).resolve().parent / "sample_response.json"


def load_sample_response() -> dict:
    with SAMPLE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def mock_health() -> dict:
    return {
        "status": "ok",
        "version": "0.2.0-preview",
        "vector_store_ready": True,
        "journal_store_ready": True,
        "mock": True,
    }


def run_research_mock(_payload: dict) -> dict:
    """Return canned demo output instantly — $0 API cost."""
    sample = load_sample_response()
    sample["query"] = _payload.get("query") or sample["query"]
    return sample
