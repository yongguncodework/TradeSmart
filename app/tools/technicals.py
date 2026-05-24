"""Technical indicator tools (RSI, MACD, SMA, ATR, drawdown)."""

from __future__ import annotations

import yfinance as yf

from app.api.schemas import TechnicalSnapshot


def _ema(series, span: int):
    return series.ewm(span=span, adjust=False).mean()


def _compute_rsi(closes, period: int = 14) -> float | None:
    if len(closes) < period + 1:
        return None
    delta = closes.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    last_loss = float(loss.iloc[-1])
    if last_loss == 0:
        return 100.0
    rs = float(gain.iloc[-1]) / last_loss
    return round(100 - (100 / (1 + rs)), 2)


def _compute_macd(closes) -> tuple[float | None, float | None]:
    if len(closes) < 35:
        return None, None
    ema12 = _ema(closes, 12)
    ema26 = _ema(closes, 26)
    macd_line = ema12 - ema26
    signal = _ema(macd_line, 9)
    return round(float(macd_line.iloc[-1]), 4), round(float(signal.iloc[-1]), 4)


def _compute_atr(history, period: int = 14) -> float | None:
    if len(history) < period + 1:
        return None
    high = history["High"]
    low = history["Low"]
    close = history["Close"]
    prev_close = close.shift(1)
    tr = (high - low).combine((high - prev_close).abs(), max).combine(
        (low - prev_close).abs(), max
    )
    atr = tr.rolling(period).mean()
    return round(float(atr.iloc[-1]), 4)


def fetch_technical_snapshot(symbol: str, period: str = "1y") -> TechnicalSnapshot:
    """Compute common technical indicators from daily OHLCV history."""
    try:
        history = yf.Ticker(symbol).history(period=period, interval="1d")
        if history.empty or len(history) < 30:
            return TechnicalSnapshot(symbol=symbol, error="Insufficient history for indicators.")

        closes = history["Close"]
        latest = float(closes.iloc[-1])

        sma20 = float(closes.tail(20).mean()) if len(closes) >= 20 else None
        sma50 = float(closes.tail(50).mean()) if len(closes) >= 50 else None
        sma200 = float(closes.tail(200).mean()) if len(closes) >= 200 else None

        high_60d = float(closes.tail(60).max()) if len(closes) >= 60 else float(closes.max())
        drawdown = round(((latest - high_60d) / high_60d) * 100, 2) if high_60d else None

        price_vs_sma200 = None
        if sma200 and sma200 > 0:
            price_vs_sma200 = round(((latest - sma200) / sma200) * 100, 2)

        rsi = _compute_rsi(closes)
        macd, macd_signal = _compute_macd(closes)
        atr = _compute_atr(history)

        return TechnicalSnapshot(
            symbol=symbol,
            price=round(latest, 4),
            rsi_14=rsi,
            macd=macd,
            macd_signal=macd_signal,
            sma_20=round(sma20, 4) if sma20 else None,
            sma_50=round(sma50, 4) if sma50 else None,
            sma_200=round(sma200, 4) if sma200 else None,
            atr_14=atr,
            drawdown_from_60d_high_pct=drawdown,
            price_vs_sma200_pct=price_vs_sma200,
        )
    except Exception as exc:  # noqa: BLE001
        return TechnicalSnapshot(symbol=symbol, error=str(exc))


def fetch_technical_context(symbols: list[str]) -> list[TechnicalSnapshot]:
    return [fetch_technical_snapshot(symbol) for symbol in symbols]


def technicals_to_prompt_block(snapshots: list[TechnicalSnapshot]) -> str:
    lines: list[str] = []
    for snap in snapshots:
        if snap.error:
            lines.append(f"- {snap.symbol}: unavailable ({snap.error})")
            continue
        lines.append(
            f"- {snap.symbol}: price={snap.price}, RSI14={snap.rsi_14}, "
            f"MACD={snap.macd}/{snap.macd_signal}, SMA20={snap.sma_20}, "
            f"SMA50={snap.sma_50}, SMA200={snap.sma_200}, ATR14={snap.atr_14}, "
            f"drawdown_60d={snap.drawdown_from_60d_high_pct}%, "
            f"vs_SMA200={snap.price_vs_sma200_pct}%"
        )
    return "\n".join(lines)
