"""Pydantic schemas for API requests and responses."""

from typing import Any, Literal

from pydantic import BaseModel, Field

ResponseLanguage = Literal["en", "ko"]


class ResearchRequest(BaseModel):
    """User query for the trading research agent."""

    query: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        examples=[
            "SOXL ran from 68 to 190 — should I trim? How does this compare to my past trades?"
        ],
    )
    symbols: list[str] = Field(
        default_factory=lambda: ["BTC-USD", "SOXL", "QQQ"],
        description="Tickers to pull market context for.",
    )
    position_size_pct: float | None = Field(
        default=None,
        ge=0,
        le=100,
        description="Optional planned position size as % of portfolio.",
    )
    response_language: ResponseLanguage = Field(
        default="en",
        description="Language for thesis and action items (en or ko).",
    )


class AgentPlan(BaseModel):
    """Tool selection plan produced by the V2 planner node."""

    playbook: bool = True
    journal: bool = False
    market: bool = True
    technicals: bool = False
    risk: bool = True
    rationale: str = ""


class RiskFlag(BaseModel):
    """Structured risk warning emitted by the risk engine."""

    severity: str
    rule: str
    message: str


class PlaybookMatch(BaseModel):
    """Relevant playbook excerpt retrieved by RAG."""

    source: str
    content: str
    score: float | None = None


class JournalMatch(BaseModel):
    """Relevant past trade retrieved from journal RAG."""

    source: str
    content: str
    symbol: str | None = None
    action: str | None = None
    score: float | None = None


class MarketSnapshot(BaseModel):
    """Compact market data for a single symbol."""

    symbol: str
    price: float | None = None
    change_pct_1d: float | None = None
    change_pct_5d: float | None = None
    volume_ratio: float | None = None
    fifty_two_week_position: float | None = Field(
        default=None,
        description="0 = at 52w low, 1 = at 52w high.",
    )
    error: str | None = None


class TechnicalSnapshot(BaseModel):
    """Technical indicator bundle for a symbol."""

    symbol: str
    price: float | None = None
    rsi_14: float | None = None
    macd: float | None = None
    macd_signal: float | None = None
    sma_20: float | None = None
    sma_50: float | None = None
    sma_200: float | None = None
    atr_14: float | None = None
    drawdown_from_60d_high_pct: float | None = None
    price_vs_sma200_pct: float | None = None
    error: str | None = None


class ResearchResponse(BaseModel):
    """Final structured output from the LangGraph agent."""

    query: str
    thesis: str
    agent_plan: AgentPlan | None = None
    market_context: list[MarketSnapshot]
    technical_context: list[TechnicalSnapshot] = Field(default_factory=list)
    playbook_matches: list[PlaybookMatch]
    journal_matches: list[JournalMatch] = Field(default_factory=list)
    risk_flags: list[RiskFlag]
    action_items: list[str]
    disclaimer: str
    raw_trace: dict[str, Any] | None = Field(
        default=None,
        description="Optional debug trace from the agent graph.",
    )


class HealthResponse(BaseModel):
    """Service health payload."""

    status: str
    version: str
    vector_store_ready: bool
    journal_store_ready: bool = False
