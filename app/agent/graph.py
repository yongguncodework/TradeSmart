"""LangGraph workflow assembly — V2 planner-driven pipeline."""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from app.agent.nodes import (
    evaluate_risk_node,
    fetch_market_node,
    fetch_technicals_node,
    plan_tools_node,
    retrieve_journal_node,
    retrieve_playbooks_node,
    synthesize_brief_node,
)
from app.agent.state import AgentState


def build_research_graph():
    """
    Build the TradeSmrt V2 research agent graph.

    Flow:
        START -> plan_tools -> playbook RAG -> journal RAG -> market -> technicals
             -> risk -> synthesis -> END

    Each node checks the planner flags and no-ops when a tool is not needed.
    This keeps a single graph while enabling dynamic tool selection per question.
    """
    graph = StateGraph(AgentState)

    graph.add_node("plan_tools", plan_tools_node)
    graph.add_node("retrieve_playbooks", retrieve_playbooks_node)
    graph.add_node("retrieve_journal", retrieve_journal_node)
    graph.add_node("fetch_market", fetch_market_node)
    graph.add_node("fetch_technicals", fetch_technicals_node)
    graph.add_node("evaluate_risk", evaluate_risk_node)
    graph.add_node("synthesize_brief", synthesize_brief_node)

    graph.add_edge(START, "plan_tools")
    graph.add_edge("plan_tools", "retrieve_playbooks")
    graph.add_edge("retrieve_playbooks", "retrieve_journal")
    graph.add_edge("retrieve_journal", "fetch_market")
    graph.add_edge("fetch_market", "fetch_technicals")
    graph.add_edge("fetch_technicals", "evaluate_risk")
    graph.add_edge("evaluate_risk", "synthesize_brief")
    graph.add_edge("synthesize_brief", END)

    return graph.compile()


research_agent = build_research_graph()
