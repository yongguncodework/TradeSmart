"""LangGraph node implementations for the TradeSmrt research workflow."""

from __future__ import annotations

import json
import re

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.agent.planner import build_agent_plan
from app.agent.state import AgentState
from app.config import Settings, get_settings
from app.rag.journal_retriever import journal_matches_to_prompt_block, retrieve_journal_context
from app.rag.retriever import playbook_matches_to_prompt_block, retrieve_playbook_context
from app.tools.market_data import fetch_market_context, snapshots_to_prompt_block
from app.tools.risk_rules import evaluate_risk, risk_flags_to_prompt_block
from app.tools.technicals import fetch_technical_context, technicals_to_prompt_block

DISCLAIMER = (
    "Not financial advice. TradeSmrt produces research briefs for personal decision "
    "support only. Verify data independently and respect your own risk limits."
)

SYNTHESIS_SYSTEM_PROMPT = """You are TradeSmrt V2, a disciplined trading research copilot.
You help a trader who focuses on Bitcoin (BTC-USD), broad ETFs (QQQ, SPY), and SOXL.

Rules:
- Never claim certainty or guarantee returns.
- Ground conclusions in market data, technicals, playbooks, journal trades, and risk flags.
- When journal trades are provided, explicitly compare the current setup to past entries/exits.
- Be concise and actionable: thesis, invalidation, sizing notes, and next checks.
- If risk flags are HIGH severity, lead with caution.
- Output valid JSON only with keys: thesis (string), action_items (array of strings).
"""


def _llm(settings: Settings | None = None) -> ChatOpenAI:
    settings = settings or get_settings()
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key or None,
        temperature=0.2,
    )


def plan_tools_node(state: AgentState) -> dict:
    """V2 planner — choose which tools/nodes to run for this question."""
    plan = build_agent_plan(state["query"], state["symbols"])
    return {
        "plan": plan,
        "trace": {
            **state.get("trace", {}),
            "agent_plan": plan,
            "version": "v2",
        },
    }


def retrieve_playbooks_node(state: AgentState) -> dict:
    """RAG node — pull relevant playbook chunks."""
    if not state.get("plan", {}).get("playbook", True):
        return {"playbook_matches": [], "trace": state.get("trace", {})}

    settings = get_settings()
    matches = retrieve_playbook_context(state["query"], settings=settings)
    return {
        "playbook_matches": matches,
        "trace": {**state.get("trace", {}), "playbook_chunks": len(matches)},
    }


def retrieve_journal_node(state: AgentState) -> dict:
    """Journal RAG — retrieve similar past trades and position patterns."""
    if not state.get("plan", {}).get("journal", False):
        return {"journal_matches": [], "trace": state.get("trace", {})}

    settings = get_settings()
    matches = retrieve_journal_context(state["query"], settings=settings)
    return {
        "journal_matches": matches,
        "trace": {**state.get("trace", {}), "journal_chunks": len(matches)},
    }


def fetch_market_node(state: AgentState) -> dict:
    """Tool node — fetch live market snapshots via yfinance."""
    if not state.get("plan", {}).get("market", True):
        return {"market_snapshots": [], "trace": state.get("trace", {})}

    snapshots = fetch_market_context(state["symbols"])
    return {
        "market_snapshots": snapshots,
        "trace": {**state.get("trace", {}), "symbols_fetched": len(snapshots)},
    }


def fetch_technicals_node(state: AgentState) -> dict:
    """Tool node — compute RSI, MACD, SMA, ATR, drawdown."""
    if not state.get("plan", {}).get("technicals", False):
        return {"technical_snapshots": [], "trace": state.get("trace", {})}

    snapshots = fetch_technical_context(state["symbols"])
    return {
        "technical_snapshots": snapshots,
        "trace": {**state.get("trace", {}), "technicals_fetched": len(snapshots)},
    }


def evaluate_risk_node(state: AgentState) -> dict:
    """Deterministic risk engine node."""
    if not state.get("plan", {}).get("risk", True):
        return {"risk_flags": [], "trace": state.get("trace", {})}

    settings = get_settings()
    flags = evaluate_risk(
        symbols=state["symbols"],
        snapshots=state["market_snapshots"],
        settings=settings,
        position_size_pct=state.get("position_size_pct"),
        technicals=state.get("technical_snapshots", []),
    )
    return {
        "risk_flags": flags,
        "trace": {**state.get("trace", {}), "risk_flag_count": len(flags)},
    }


def _parse_synthesis(content: str) -> tuple[str, list[str]]:
    """Parse JSON synthesis from the LLM, with a lightweight fallback."""
    try:
        payload = json.loads(content)
        thesis = str(payload.get("thesis", "")).strip()
        items = payload.get("action_items", [])
        action_items = [str(item).strip() for item in items if str(item).strip()]
        if thesis:
            return thesis, action_items
    except json.JSONDecodeError:
        pass

    cleaned = content.strip()
    return cleaned, ["Review the thesis and confirm against your playbook rules."]


def synthesize_brief_node(state: AgentState) -> dict:
    """LLM node — combine all tool outputs into a research brief."""
    prompt = f"""User query:
{state["query"]}

Planned position size (% of portfolio): {state.get("position_size_pct")}

Agent plan:
{json.dumps(state.get("plan", {}), indent=2)}

Market context:
{snapshots_to_prompt_block(state["market_snapshots"])}

Technical indicators:
{technicals_to_prompt_block(state.get("technical_snapshots", []))}

Retrieved playbooks:
{playbook_matches_to_prompt_block(state["playbook_matches"])}

Similar past trades (journal RAG):
{journal_matches_to_prompt_block(state.get("journal_matches", []))}

Risk flags:
{risk_flags_to_prompt_block(state["risk_flags"])}

Respond with JSON: {{"thesis": "...", "action_items": ["...", "..."]}}
"""
    response = _llm().invoke(
        [
            SystemMessage(content=SYNTHESIS_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]
    )
    content = response.content if isinstance(response.content, str) else str(response.content)
    content = re.sub(r"^```json\s*|\s*```$", "", content.strip())
    thesis, action_items = _parse_synthesis(content)

    return {
        "thesis": thesis,
        "action_items": action_items,
        "messages": [HumanMessage(content=state["query"]), response],
        "trace": {**state.get("trace", {}), "synthesis_model": get_settings().openai_model},
    }
