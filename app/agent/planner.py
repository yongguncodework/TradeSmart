"""Rule-based planner — decides which tools the agent runs (V2)."""

from __future__ import annotations

import re

JOURNAL_KEYWORDS = (
    "past",
    "similar",
    "history",
    "historical",
    "my trade",
    "my trades",
    "bought",
    "sold",
    "cost basis",
    "average",
    "avg cost",
    "winning",
    "losing",
    "journal",
    "before",
    "last time",
    "prior",
    "pattern",
    "168",
    "188",
    "166",
    "128",
    "187",
    "holdings",
    "my position",
    "my soxl",
)

TECHNICAL_KEYWORDS = (
    "rsi",
    "macd",
    "sma",
    "atr",
    "drawdown",
    "overbought",
    "oversold",
    "technical",
    "indicator",
    "moving average",
    "trim",
    "take profit",
    "sell",
    "hold",
    "180",
    "190",
    "rally",
    "run",
    "extended",
    "momentum",
    "pullback",
    "support",
    "resistance",
)


def build_agent_plan(query: str, symbols: list[str]) -> dict:
    """
    Lightweight planner — selects tools without an extra LLM call.

    Returns flags consumed by conditional LangGraph nodes.
    """
    q = query.lower()
    has_symbols = bool(symbols)

    need_journal = any(k in q for k in JOURNAL_KEYWORDS) or bool(
        re.search(r"\b(1[2-9]\d|190)\b", q)
    )
    need_technicals = any(k in q for k in TECHNICAL_KEYWORDS) or any(
        word in q for word in ("should i", "still hold", "start to sell", "take profit")
    )
    need_market = has_symbols or any(
        k in q for k in ("price", "market", "volume", "52-week", "52w", "btc", "soxl", "qqq")
    )

    # Playbook + risk are almost always useful for trading questions.
    need_playbook = True
    need_risk = True

    steps = []
    if need_playbook:
        steps.append("playbook RAG")
    if need_journal:
        steps.append("trade journal RAG")
    if need_market:
        steps.append("market snapshots")
    if need_technicals:
        steps.append("technical indicators")
    if need_risk:
        steps.append("risk engine")

    rationale = (
        f"Planner selected: {', '.join(steps)}."
        if steps
        else "Planner selected minimal path."
    )

    return {
        "playbook": need_playbook,
        "journal": need_journal,
        "market": need_market,
        "technicals": need_technicals,
        "risk": need_risk,
        "rationale": rationale,
    }
