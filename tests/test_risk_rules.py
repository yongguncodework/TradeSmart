"""Tests for deterministic risk rules."""

from app.api.schemas import MarketSnapshot
from app.config import Settings
from app.tools.risk_rules import evaluate_risk


def test_leveraged_etf_size_cap():
    settings = Settings(max_leveraged_etf_pct=8.0, max_position_pct=15.0)
    flags = evaluate_risk(
        symbols=["SOXL"],
        snapshots=[],
        settings=settings,
        position_size_pct=10.0,
    )
    assert any(f.rule == "max_leveraged_etf_pct" for f in flags)


def test_large_daily_move_flags_leveraged_etf():
    settings = Settings()
    snap = MarketSnapshot(symbol="SOXL", price=50.0, change_pct_1d=9.5)
    flags = evaluate_risk(
        symbols=["SOXL"],
        snapshots=[snap],
        settings=settings,
        position_size_pct=None,
    )
    assert any(f.rule == "leveraged_etf_daily_move" for f in flags)


def test_no_flags_for_small_benign_snapshot():
    settings = Settings()
    snap = MarketSnapshot(
        symbol="QQQ",
        price=400.0,
        change_pct_1d=0.5,
        fifty_two_week_position=0.5,
        volume_ratio=1.1,
    )
    flags = evaluate_risk(
        symbols=["QQQ"],
        snapshots=[snap],
        settings=settings,
        position_size_pct=5.0,
    )
    assert flags == []
