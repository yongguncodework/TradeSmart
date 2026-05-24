"""Tests for market snapshot formatting."""

from app.api.schemas import MarketSnapshot
from app.tools.market_data import snapshots_to_prompt_block


def test_snapshots_to_prompt_block_includes_symbol():
    snapshots = [
        MarketSnapshot(
            symbol="BTC-USD",
            price=65000.0,
            change_pct_1d=1.2,
            change_pct_5d=3.4,
            volume_ratio=1.5,
            fifty_two_week_position=0.8,
        )
    ]
    block = snapshots_to_prompt_block(snapshots)
    assert "BTC-USD" in block
    assert "65000" in block


def test_error_snapshot_renders_gracefully():
    snapshots = [MarketSnapshot(symbol="SOXL", error="timeout")]
    block = snapshots_to_prompt_block(snapshots)
    assert "unavailable" in block
