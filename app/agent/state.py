"""LangGraph agent state definition."""

from typing import Annotated, Any, TypedDict

from langgraph.graph.message import add_messages

from app.api.schemas import (
    JournalMatch,
    MarketSnapshot,
    PlaybookMatch,
    RiskFlag,
    TechnicalSnapshot,
)


class AgentState(TypedDict):
    """Shared state passed between LangGraph nodes."""

    query: str
    symbols: list[str]
    position_size_pct: float | None
    plan: dict[str, Any]
    playbook_matches: list[PlaybookMatch]
    journal_matches: list[JournalMatch]
    market_snapshots: list[MarketSnapshot]
    technical_snapshots: list[TechnicalSnapshot]
    risk_flags: list[RiskFlag]
    thesis: str
    action_items: list[str]
    messages: Annotated[list, add_messages]
    trace: dict
