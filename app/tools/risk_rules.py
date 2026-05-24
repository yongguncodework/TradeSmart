"""Deterministic risk rules for BTC, ETFs, and leveraged products like SOXL."""

from __future__ import annotations

from app.api.schemas import MarketSnapshot, RiskFlag, TechnicalSnapshot
from app.config import Settings

LEVERAGED_ETF_SYMBOLS = {"SOXL", "SOXS", "TQQQ", "SQQQ", "UPRO", "SPXU"}
HIGH_VOLATILITY_SYMBOLS = {"BTC-USD", "ETH-USD"}


def evaluate_risk(
    symbols: list[str],
    snapshots: list[MarketSnapshot],
    settings: Settings,
    position_size_pct: float | None = None,
    technicals: list[TechnicalSnapshot] | None = None,
) -> list[RiskFlag]:
    """
    Apply rule-based checks before the LLM synthesizes a research brief.

    These rules encode conservative personal guardrails — not broker constraints.
    """
    flags: list[RiskFlag] = []
    normalized = {s.upper().replace("/", "-") for s in symbols}

    if position_size_pct is not None:
        if position_size_pct > settings.max_position_pct:
            flags.append(
                RiskFlag(
                    severity="high",
                    rule="max_position_pct",
                    message=(
                        f"Planned size {position_size_pct}% exceeds "
                        f"max single-position limit of {settings.max_position_pct}%."
                    ),
                )
            )

        leveraged_hits = normalized & LEVERAGED_ETF_SYMBOLS
        if leveraged_hits and position_size_pct > settings.max_leveraged_etf_pct:
            flags.append(
                RiskFlag(
                    severity="high",
                    rule="max_leveraged_etf_pct",
                    message=(
                        f"Leveraged ETF exposure ({', '.join(leveraged_hits)}) at "
                        f"{position_size_pct}% exceeds cap of "
                        f"{settings.max_leveraged_etf_pct}%."
                    ),
                )
            )

    for snap in snapshots:
        if snap.error:
            continue

        symbol_key = snap.symbol.upper()
        if symbol_key in LEVERAGED_ETF_SYMBOLS and abs(snap.change_pct_1d or 0) >= 8:
            flags.append(
                RiskFlag(
                    severity="medium",
                    rule="leveraged_etf_daily_move",
                    message=(
                        f"{snap.symbol} moved {snap.change_pct_1d}% today — "
                        "leveraged ETFs decay quickly in chop; reduce size or wait."
                    ),
                )
            )

        if symbol_key in HIGH_VOLATILITY_SYMBOLS and abs(snap.change_pct_1d or 0) >= 5:
            flags.append(
                RiskFlag(
                    severity="medium",
                    rule="crypto_daily_move",
                    message=(
                        f"{snap.symbol} daily move {snap.change_pct_1d}% — "
                        "widen stops or cut size for BTC volatility."
                    ),
                )
            )

        if snap.fifty_two_week_position is not None and snap.fifty_two_week_position >= 0.92:
            flags.append(
                RiskFlag(
                    severity="low",
                    rule="extended_price",
                    message=(
                        f"{snap.symbol} is near 52-week highs "
                        f"(position={snap.fifty_two_week_position}). "
                        "Chase risk is elevated."
                    ),
                )
            )

        if snap.volume_ratio is not None and snap.volume_ratio >= 2.5:
            flags.append(
                RiskFlag(
                    severity="low",
                    rule="volume_spike",
                    message=(
                        f"{snap.symbol} volume ratio {snap.volume_ratio}x — "
                        "confirm thesis with broader market context."
                    ),
                )
            )

    if len(normalized) >= 4:
        flags.append(
            RiskFlag(
                severity="low",
                rule="symbol_sprawl",
                message="Query spans many symbols; focus improves execution quality.",
            )
        )

    for tech in technicals or []:
        if tech.error:
            continue
        symbol_key = tech.symbol.upper()
        if tech.rsi_14 is not None and tech.rsi_14 >= 70:
            flags.append(
                RiskFlag(
                    severity="medium",
                    rule="rsi_overbought",
                    message=(
                        f"{tech.symbol} RSI14={tech.rsi_14} — overbought zone; "
                        "trim/add risk is elevated for leveraged products."
                    ),
                )
            )
        if (
            symbol_key in LEVERAGED_ETF_SYMBOLS
            and tech.drawdown_from_60d_high_pct is not None
            and tech.drawdown_from_60d_high_pct > -3
            and (tech.rsi_14 or 0) >= 65
        ):
            flags.append(
                RiskFlag(
                    severity="medium",
                    rule="extended_rally",
                    message=(
                        f"{tech.symbol} is near 60-day highs (drawdown "
                        f"{tech.drawdown_from_60d_high_pct}%) with elevated RSI — "
                        "parabolic rally risk."
                    ),
                )
            )

    return flags


def risk_flags_to_prompt_block(flags: list[RiskFlag]) -> str:
    """Format risk flags for LLM consumption."""
    if not flags:
        return "No rule-based risk flags triggered."
    return "\n".join(f"- [{f.severity.upper()}] {f.rule}: {f.message}" for f in flags)
