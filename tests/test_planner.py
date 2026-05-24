"""Tests for V2 planner tool selection."""

from app.agent.planner import build_agent_plan


def test_planner_enables_journal_for_past_trade_question():
    plan = build_agent_plan(
        "How similar is this SOXL setup to my past winning trades?",
        ["SOXL"],
    )
    assert plan["journal"] is True


def test_planner_enables_technicals_for_trim_question():
    plan = build_agent_plan(
        "SOXL ran from 68 to 190 — should I trim or hold? RSI looks high.",
        ["SOXL"],
    )
    assert plan["technicals"] is True
    assert plan["journal"] is True


def test_planner_always_keeps_playbook_and_risk():
    plan = build_agent_plan("Quick check", ["QQQ"])
    assert plan["playbook"] is True
    assert plan["risk"] is True
