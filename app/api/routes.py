"""FastAPI route handlers."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app import __version__
from app.agent.graph import research_agent
from app.agent.nodes import get_disclaimer
from app.api.schemas import AgentPlan, HealthResponse, ResearchRequest, ResearchResponse
from app.config import get_settings
from app.rag.journal_store import build_journal_store
from app.rag.vectorstore import build_vector_store

router = APIRouter()


def _vector_store_ready() -> bool:
    settings = get_settings()
    if not settings.openai_api_key:
        return False
    try:
        build_vector_store(settings)
        return True
    except Exception:  # noqa: BLE001
        return False


def _journal_store_ready() -> bool:
    settings = get_settings()
    if not settings.openai_api_key:
        return False
    try:
        build_journal_store(settings)
        return True
    except Exception:  # noqa: BLE001
        return False


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Liveness and dependency check."""
    return HealthResponse(
        status="ok",
        version=__version__,
        vector_store_ready=_vector_store_ready(),
        journal_store_ready=_journal_store_ready(),
    )


@router.post("/research", response_model=ResearchResponse)
async def run_research(
    payload: ResearchRequest,
    include_trace: bool = Query(default=False, description="Include agent debug trace."),
) -> ResearchResponse:
    """
    Run the LangGraph V2 research agent for a trading question.

    Combines planner-driven tool selection, dual RAG (playbooks + journal),
    market data, technical indicators, risk rules, and LLM synthesis.
    """
    settings = get_settings()
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=503,
            detail="OPENAI_API_KEY is not configured. Copy .env.example to .env and set your key.",
        )

    initial_state = {
        "query": payload.query,
        "symbols": payload.symbols,
        "position_size_pct": payload.position_size_pct,
        "response_language": payload.response_language,
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

    try:
        result = research_agent.invoke(initial_state)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {exc}") from exc

    plan_data = result.get("plan") or {}
    agent_plan = AgentPlan(**plan_data) if plan_data else None

    return ResearchResponse(
        query=payload.query,
        thesis=result.get("thesis", ""),
        agent_plan=agent_plan,
        market_context=result.get("market_snapshots", []),
        technical_context=result.get("technical_snapshots", []),
        playbook_matches=result.get("playbook_matches", []),
        journal_matches=result.get("journal_matches", []),
        risk_flags=result.get("risk_flags", []),
        action_items=result.get("action_items", []),
        disclaimer=get_disclaimer(payload.response_language),
        raw_trace=result.get("trace") if include_trace else None,
    )
