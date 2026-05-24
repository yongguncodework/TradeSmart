"""Market data tools backed by yfinance."""

from __future__ import annotations

from typing import Any

import yfinance as yf

from app.api.schemas import MarketSnapshot


def _safe_pct(current: float | None, previous: float | None) -> float | None:
    if current is None or previous in (None, 0):
        return None
    return round(((current - previous) / previous) * 100, 2)


def _week_position(current: float, low: float, high: float) -> float | None:
    if high <= low:
        return None
    return round((current - low) / (high - low), 3)


def fetch_market_snapshot(symbol: str, period: str = "1mo") -> MarketSnapshot:
    """
    Fetch a compact snapshot for a ticker.

    Uses daily history to compute short-term momentum and 52-week positioning.
    """
    try:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period=period, interval="1d")
        if history.empty:
            return MarketSnapshot(symbol=symbol, error="No market data returned.")

        closes = history["Close"]
        volumes = history["Volume"]
        latest = float(closes.iloc[-1])
        prev_close = float(closes.iloc[-2]) if len(closes) > 1 else None
        five_day_ref = float(closes.iloc[-6]) if len(closes) > 5 else None
        avg_volume = float(volumes.tail(20).mean()) if len(volumes) >= 5 else None
        latest_volume = float(volumes.iloc[-1])

        info = ticker.info or {}
        low_52 = info.get("fiftyTwoWeekLow") or info.get("regularMarketDayLow")
        high_52 = info.get("fiftyTwoWeekHigh") or info.get("regularMarketDayHigh")
        week_pos = None
        if low_52 and high_52:
            week_pos = _week_position(latest, float(low_52), float(high_52))

        volume_ratio = None
        if avg_volume and avg_volume > 0:
            volume_ratio = round(latest_volume / avg_volume, 2)

        return MarketSnapshot(
            symbol=symbol,
            price=round(latest, 4),
            change_pct_1d=_safe_pct(latest, prev_close),
            change_pct_5d=_safe_pct(latest, five_day_ref),
            volume_ratio=volume_ratio,
            fifty_two_week_position=week_pos,
        )
    except Exception as exc:  # noqa: BLE001 — surface as structured API error
        return MarketSnapshot(symbol=symbol, error=str(exc))


def fetch_market_context(symbols: list[str]) -> list[MarketSnapshot]:
    """Fetch snapshots for multiple symbols."""
    return [fetch_market_snapshot(symbol) for symbol in symbols]


def snapshots_to_prompt_block(snapshots: list[MarketSnapshot]) -> str:
    """Format market data for LLM consumption."""
    lines: list[str] = []
    for snap in snapshots:
        if snap.error:
            lines.append(f"- {snap.symbol}: unavailable ({snap.error})")
            continue
        lines.append(
            f"- {snap.symbol}: price={snap.price}, 1d={snap.change_pct_1d}%, "
            f"5d={snap.change_pct_5d}%, vol_ratio={snap.volume_ratio}, "
            f"52w_pos={snap.fifty_two_week_position}"
        )
    return "\n".join(lines)


def market_summary_dict(snapshots: list[MarketSnapshot]) -> dict[str, Any]:
    """Serialize snapshots for API responses."""
    return [snap.model_dump() for snap in snapshots]  # type: ignore[return-value]
