"""Streamlit demo UI for TradeSmart V2 — local API or cloud direct mode."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import httpx
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_API_URL = os.getenv("TRADESMART_API_URL", "http://127.0.0.1:8000")
DIRECT_MODE = os.getenv("TRADESMART_DIRECT", "false").lower() in {"1", "true", "yes"}
MOCK_SETTING = os.getenv("TRADESMART_MOCK", "auto").lower()
GITHUB_EXAMPLES = (
    "https://github.com/yongguncodework/TradeSmart/blob/main/docs/EXAMPLE_QUERIES.md"
)

SYMBOL_OPTIONS = ["BTC-USD", "SOXL", "QQQ", "SPY", "SMH"]
EXAMPLE_QUERIES = [
    (
        "SOXL ran from ~68 to ~190. I bought 14 @ 188.89 and 20 @ 168.74, and sold 20 @ 166. "
        "Should I hold or trim? How does this compare to my past trades and RSI?"
    ),
    "How similar is adding SOXL at 188.89 to my past winning vs losing entries?",
    "I sold 20 SOXL at 166 before — should I repeat that trim strategy near 190?",
    "BTC pulled back 3% while QQQ holds above the 50-day — add to BTC sleeve?",
]

st.set_page_config(
    page_title="TradeSmart Demo",
    page_icon="📊",
    layout="wide",
)


@st.cache_resource(show_spinner="Bootstrapping RAG knowledge bases (first load)...")
def _bootstrap_direct() -> bool:
    from demo.agent_runner import ensure_knowledge_bases

    ensure_knowledge_bases()
    return True


def check_health_api(api_url: str) -> dict | None:
    try:
        response = httpx.get(f"{api_url}/api/v1/health", timeout=10.0)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError:
        return None


def _use_mock_mode() -> bool:
    """Portfolio preview — no OpenAI calls, $0 cost."""
    if MOCK_SETTING in {"1", "true", "yes"}:
        return True
    if MOCK_SETTING == "false":
        return False
    # auto: mock when no API key (safe for public Streamlit deploy)
    return not bool(os.getenv("OPENAI_API_KEY"))


def resolve_runtime() -> tuple[str, dict | None]:
    """Pick mock (free), direct (cloud), or API mode (local/docker)."""
    if _use_mock_mode():
        from demo.mock_runner import mock_health

        return "mock", mock_health()

    if DIRECT_MODE:
        _bootstrap_direct()
        from demo.agent_runner import direct_health

        return "direct", direct_health()

    health = check_health_api(DEFAULT_API_URL)
    if health:
        return "api", health

    if os.getenv("OPENAI_API_KEY"):
        try:
            _bootstrap_direct()
            from demo.agent_runner import direct_health

            return "direct-fallback", direct_health()
        except Exception:
            pass

    from demo.mock_runner import mock_health

    return "mock", mock_health()


def run_research(payload: dict, api_url: str, mode: str) -> dict:
    if mode == "mock":
        from demo.mock_runner import run_research_mock

        return run_research_mock(payload)

    if mode.startswith("direct"):
        from demo.agent_runner import run_research_direct

        return run_research_direct(payload)

    response = httpx.post(
        f"{api_url}/api/v1/research?include_trace=true",
        json=payload,
        timeout=120.0,
    )
    response.raise_for_status()
    return response.json()


def severity_color(severity: str) -> str:
    return {"high": "#ef4444", "medium": "#f59e0b", "low": "#3b82f6"}.get(severity, "#6b7280")


def render_market_context(items: list[dict]) -> None:
    if not items:
        st.info("No market snapshots returned.")
        return
    cols = st.columns(min(len(items), 3))
    for idx, snap in enumerate(items):
        col = cols[idx % len(cols)]
        with col:
            if snap.get("error"):
                st.error(f"{snap['symbol']}: {snap['error']}")
                continue
            st.metric(
                label=snap["symbol"],
                value=f"${snap['price']}" if snap.get("price") is not None else "N/A",
                delta=f"{snap.get('change_pct_1d')}% (1d)" if snap.get("change_pct_1d") is not None else None,
            )
            st.caption(
                f"5d: {snap.get('change_pct_5d')}% | vol: {snap.get('volume_ratio')} | "
                f"52w: {snap.get('fifty_two_week_position')}"
            )


def render_technicals(items: list[dict]) -> None:
    if not items:
        st.info("No technical indicators (planner skipped or unavailable).")
        return
    for snap in items:
        if snap.get("error"):
            st.error(f"{snap['symbol']}: {snap['error']}")
            continue
        st.markdown(
            f"**{snap['symbol']}** · RSI14={snap.get('rsi_14')} · "
            f"MACD={snap.get('macd')}/{snap.get('macd_signal')} · "
            f"SMA20={snap.get('sma_20')} · SMA50={snap.get('sma_50')} · "
            f"SMA200={snap.get('sma_200')} · ATR14={snap.get('atr_14')} · "
            f"60d DD={snap.get('drawdown_from_60d_high_pct')}%"
        )


def render_risk_flags(flags: list[dict]) -> None:
    if not flags:
        st.success("No rule-based risk flags triggered.")
        return
    for flag in flags:
        color = severity_color(flag.get("severity", "low"))
        st.markdown(
            f"<div style='border-left:4px solid {color}; padding:8px 12px; margin-bottom:8px; "
            f"background:#1e293b; border-radius:6px;'>"
            f"<strong>[{flag.get('severity', '').upper()}]</strong> "
            f"{flag.get('rule')}: {flag.get('message')}"
            f"</div>",
            unsafe_allow_html=True,
        )


def render_results(result: dict) -> None:
    plan = result.get("agent_plan") or {}
    if plan:
        st.info(
            f"**Agent plan:** playbook={plan.get('playbook')} · journal={plan.get('journal')} · "
            f"market={plan.get('market')} · technicals={plan.get('technicals')} · "
            f"risk={plan.get('risk')}"
        )

    st.subheader("Thesis")
    st.write(result.get("thesis", ""))

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Market")
        render_market_context(result.get("market_context", []))
    with c2:
        st.subheader("Risk Flags")
        render_risk_flags(result.get("risk_flags", []))

    st.subheader("Technical Indicators")
    render_technicals(result.get("technical_context", []))

    st.subheader("Action Items")
    for item in result.get("action_items", []):
        st.markdown(f"- {item}")

    with st.expander("Journal matches (episodic RAG)", expanded=True):
        journal = result.get("journal_matches", [])
        if not journal:
            st.caption("No journal matches — try a question about past trades.")
        for match in journal:
            st.markdown(f"**{match.get('source', 'unknown')}**")
            st.code(match.get("content", ""), language="markdown")

    with st.expander("Playbook matches (rules RAG)"):
        for match in result.get("playbook_matches", []):
            st.markdown(f"**{match.get('source', 'unknown')}**")
            st.code(match.get("content", ""), language="markdown")

    st.caption(result.get("disclaimer", ""))


def main() -> None:
    mode, health = resolve_runtime()

    st.title("TradeSmart V2")
    st.caption("Planner Agent · Playbook RAG · Trade Journal RAG · Technicals · Risk Engine")

    if mode == "mock":
        st.info(
            "**Sample demo mode** — illustrative output only, no API calls. "
            "Add `OPENAI_API_KEY` locally for live AI."
        )

    with st.sidebar:
        st.header("Status")
        if health:
            st.success(f"Online · v{health.get('version', '?')}")
            if mode == "mock":
                st.caption("Mode: **Sample demo** (no API)")
            elif mode.startswith("direct"):
                st.caption("Mode: **Live AI (direct)**")
            elif mode == "api":
                st.caption("Mode: **Live AI (API)**")
            if not health.get("vector_store_ready"):
                st.warning("Playbook store not ready.")
            if not health.get("journal_store_ready"):
                st.warning("Journal store not ready.")
        else:
            st.error("Offline.")

        if mode != "mock" and not DIRECT_MODE:
            st.text_input("API URL (local)", value=DEFAULT_API_URL, disabled=True)

        st.divider()
        st.markdown("**Try an example**")
        for i, example in enumerate(EXAMPLE_QUERIES):
            label = example if len(example) <= 72 else example[:72] + "..."
            if st.button(label, use_container_width=True, key=f"ex_{i}"):
                st.session_state["query"] = example

        st.markdown(f"[Example queries]({GITHUB_EXAMPLES})")

    query = st.text_area(
        "Trading question",
        value=st.session_state.get("query", EXAMPLE_QUERIES[0]),
        height=120,
    )
    symbols = st.multiselect("Symbols", options=SYMBOL_OPTIONS, default=["SOXL", "SMH", "QQQ"])
    position_size = st.slider("Planned position size (% of portfolio)", 0.0, 20.0, 10.0, 0.5)

    if st.button("Run V2 Research Agent", type="primary", use_container_width=True):
        if not query.strip():
            st.warning("Enter a trading question.")
            return
        if not health:
            st.error("System offline. Configure OPENAI_API_KEY.")
            return

        spinner = (
            "Loading portfolio preview..."
            if mode == "mock"
            else "Planner → playbook RAG → journal RAG → market → technicals → risk → LLM..."
        )
        with st.spinner(spinner):
            try:
                result = run_research(
                    {
                        "query": query.strip(),
                        "symbols": symbols,
                        "position_size_pct": position_size if position_size > 0 else None,
                    },
                    DEFAULT_API_URL,
                    mode,
                )
            except Exception as exc:  # noqa: BLE001
                st.error(f"Request failed: {exc}")
                return

        render_results(result)


if __name__ == "__main__":
    main()
