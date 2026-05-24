"""Run the research agent in-process (for Streamlit Cloud / single-service deploy)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import __version__
from app.agent.graph import research_agent
from app.agent.nodes import DISCLAIMER
from app.api.schemas import AgentPlan
from app.config import get_settings
from app.rag.journal_store import build_journal_store
from app.rag.vectorstore import build_vector_store


def _model_dump(item) -> dict:
    if hasattr(item, "model_dump"):
        return item.model_dump()
    return dict(item)


def ensure_knowledge_bases() -> None:
    """Build or load Chroma collections (playbooks + journal)."""
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    playbook = build_vector_store(settings, force_rebuild=False)
    journal = build_journal_store(settings, force_rebuild=False)

    if playbook._collection.count() == 0:  # noqa: SLF001
        build_vector_store(settings, force_rebuild=True)
    if journal._collection.count() == 0:  # noqa: SLF001
        build_journal_store(settings, force_rebuild=True)


def direct_health() -> dict | None:
    settings = get_settings()
    if not settings.openai_api_key:
        return None
    try:
        playbook = build_vector_store(settings)
        journal = build_journal_store(settings)
        return {
            "status": "ok",
            "version": __version__,
            "vector_store_ready": playbook._collection.count() > 0,  # noqa: SLF001
            "journal_store_ready": journal._collection.count() > 0,  # noqa: SLF001
        }
    except Exception:
        return None


def run_research_direct(payload: dict) -> dict:
    """Invoke LangGraph agent and return API-compatible JSON."""
    ensure_knowledge_bases()

    initial_state = {
        "query": payload["query"],
        "symbols": payload["symbols"],
        "position_size_pct": payload.get("position_size_pct"),
        "plan": {},
        "playbook_matches": [],
        "journal_matches": [],
        "market_snapshots": [],
        "technical_snapshots": [],
        "risk_flags": [],
        "thesis": "",
        "action_items": [],
        "messages": [],
        "trace": {},
    }

    result = research_agent.invoke(initial_state)
    plan_data = result.get("plan") or {}

    return {
        "query": payload["query"],
        "thesis": result.get("thesis", ""),
        "agent_plan": AgentPlan(**plan_data).model_dump() if plan_data else None,
        "market_context": [_model_dump(x) for x in result.get("market_snapshots", [])],
        "technical_context": [_model_dump(x) for x in result.get("technical_snapshots", [])],
        "playbook_matches": [_model_dump(x) for x in result.get("playbook_matches", [])],
        "journal_matches": [_model_dump(x) for x in result.get("journal_matches", [])],
        "risk_flags": [_model_dump(x) for x in result.get("risk_flags", [])],
        "action_items": result.get("action_items", []),
        "disclaimer": DISCLAIMER,
        "raw_trace": result.get("trace"),
    }
