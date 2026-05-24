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

from demo.i18n import EXAMPLE_QUERIES, LANG_OPTIONS, get_ui, normalize_lang

DEFAULT_API_URL = os.getenv("TRADESMART_API_URL", "http://127.0.0.1:8000")
DIRECT_MODE = os.getenv("TRADESMART_DIRECT", "false").lower() in {"1", "true", "yes"}
MOCK_SETTING = os.getenv("TRADESMART_MOCK", "auto").lower()
GITHUB_EXAMPLES = (
    "https://github.com/yongguncodework/TradeSmart/blob/main/docs/EXAMPLE_QUERIES.md"
)

SYMBOL_OPTIONS = ["BTC-USD", "SOXL", "QQQ", "SPY", "SMH"]

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


def render_market_context(items: list[dict], ui: dict[str, str]) -> None:
    if not items:
        st.info(ui["no_market"])
        return
    cols = st.columns(min(len(items), 3))
    for idx, snap in enumerate(items):
        col = cols[idx % len(cols)]
        with col:
            if snap.get("error"):
                st.error(f"{snap['symbol']}: {snap['error']}")
                continue
            delta = None
            if snap.get("change_pct_1d") is not None:
                delta = ui["market_delta"].format(change_1d=snap["change_pct_1d"])
            st.metric(
                label=snap["symbol"],
                value=f"${snap['price']}" if snap.get("price") is not None else "N/A",
                delta=delta,
            )
            st.caption(
                ui["market_caption"].format(
                    change_5d=snap.get("change_pct_5d"),
                    volume=snap.get("volume_ratio"),
                    pos_52w=snap.get("fifty_two_week_position"),
                )
            )


def render_technicals(items: list[dict], ui: dict[str, str]) -> None:
    if not items:
        st.info(ui["no_technicals"])
        return
    for snap in items:
        if snap.get("error"):
            st.error(f"{snap['symbol']}: {snap['error']}")
            continue
        st.markdown(
            ui["tech_line"].format(
                symbol=snap["symbol"],
                rsi=snap.get("rsi_14"),
                macd=snap.get("macd"),
                signal=snap.get("macd_signal"),
                sma20=snap.get("sma_20"),
                sma50=snap.get("sma_50"),
                sma200=snap.get("sma_200"),
                atr=snap.get("atr_14"),
                dd=snap.get("drawdown_from_60d_high_pct"),
            )
        )


def render_risk_flags(flags: list[dict], ui: dict[str, str]) -> None:
    if not flags:
        st.success(ui["no_risk_flags"])
        return
    for flag in flags:
        color = severity_color(flag.get("severity", "low"))
        severity = flag.get("severity", "").upper()
        st.markdown(
            f"<div style='border-left:4px solid {color}; padding:8px 12px; margin-bottom:8px; "
            f"background:#1e293b; border-radius:6px;'>"
            f"<strong>{ui['severity_prefix'].format(severity=severity)}</strong> "
            f"{flag.get('rule')}: {flag.get('message')}"
            f"</div>",
            unsafe_allow_html=True,
        )


def render_results(result: dict, ui: dict[str, str]) -> None:
    plan = result.get("agent_plan") or {}
    if plan:
        st.info(
            ui["agent_plan"].format(
                playbook=plan.get("playbook"),
                journal=plan.get("journal"),
                market=plan.get("market"),
                technicals=plan.get("technicals"),
                risk=plan.get("risk"),
            )
        )

    st.subheader(ui["thesis"])
    st.write(result.get("thesis", ""))

    c1, c2 = st.columns(2)
    with c1:
        st.subheader(ui["market"])
        render_market_context(result.get("market_context", []), ui)
    with c2:
        st.subheader(ui["risk_flags"])
        render_risk_flags(result.get("risk_flags", []), ui)

    st.subheader(ui["technicals"])
    render_technicals(result.get("technical_context", []), ui)

    st.subheader(ui["action_items"])
    for item in result.get("action_items", []):
        st.markdown(f"- {item}")

    with st.expander(ui["journal_expander"], expanded=True):
        journal = result.get("journal_matches", [])
        if not journal:
            st.caption(ui["journal_empty"])
        for match in journal:
            st.markdown(f"**{match.get('source', 'unknown')}**")
            st.code(match.get("content", ""), language="markdown")

    with st.expander(ui["playbook_expander"]):
        for match in result.get("playbook_matches", []):
            st.markdown(f"**{match.get('source', 'unknown')}**")
            st.code(match.get("content", ""), language="markdown")

    st.caption(result.get("disclaimer", ""))


def _init_session_lang() -> str:
    if "lang" not in st.session_state:
        st.session_state["lang"] = "en"
    return st.session_state["lang"]


def main() -> None:
    lang = _init_session_lang()
    ui = get_ui(lang)

    mode, health = resolve_runtime()

    st.title(ui["title"])
    st.caption(ui["subtitle"])

    if mode == "mock":
        st.info(ui["mock_banner"])

    with st.sidebar:
        st.header(ui["sidebar_status"])
        if health:
            st.success(ui["online"].format(version=health.get("version", "?")))
            if mode == "mock":
                st.caption(ui["mode_mock"])
            elif mode.startswith("direct"):
                st.caption(ui["mode_direct"])
            elif mode == "api":
                st.caption(ui["mode_api"])
            if not health.get("vector_store_ready"):
                st.warning(ui["playbook_not_ready"])
            if not health.get("journal_store_ready"):
                st.warning(ui["journal_not_ready"])
        else:
            st.error(ui["offline"])

        if mode != "mock" and not DIRECT_MODE:
            st.text_input(ui["api_url_label"], value=DEFAULT_API_URL, disabled=True)

        st.divider()
        selected_lang = st.selectbox(
            ui["language_label"],
            options=list(LANG_OPTIONS.keys()),
            format_func=lambda code: LANG_OPTIONS[code],
            index=list(LANG_OPTIONS.keys()).index(lang),
            key="lang_select",
        )
        if selected_lang != st.session_state["lang"]:
            st.session_state["lang"] = selected_lang
            st.session_state.pop("query", None)
            st.rerun()

        lang = normalize_lang(st.session_state["lang"])
        ui = get_ui(lang)
        examples = EXAMPLE_QUERIES[lang]

        st.divider()
        st.markdown(ui["try_example"])
        for i, example in enumerate(examples):
            label = example if len(example) <= 72 else example[:72] + "..."
            if st.button(label, use_container_width=True, key=f"ex_{lang}_{i}"):
                st.session_state["query"] = example

        st.markdown(f"[{ui['example_queries_link']}]({GITHUB_EXAMPLES})")

    examples = EXAMPLE_QUERIES[lang]
    default_query = st.session_state.get("query", examples[0])

    query = st.text_area(ui["query_label"], value=default_query, height=120)
    symbols = st.multiselect(ui["symbols_label"], options=SYMBOL_OPTIONS, default=["SOXL", "SMH", "QQQ"])
    position_size = st.slider(ui["position_size_label"], 0.0, 20.0, 10.0, 0.5)

    if st.button(ui["run_button"], type="primary", use_container_width=True):
        if not query.strip():
            st.warning(ui["empty_query"])
            return
        if not health:
            st.error(ui["system_offline"])
            return

        spinner = ui["spinner_mock"] if mode == "mock" else ui["spinner_live"]
        with st.spinner(spinner):
            try:
                result = run_research(
                    {
                        "query": query.strip(),
                        "symbols": symbols,
                        "position_size_pct": position_size if position_size > 0 else None,
                        "response_language": lang,
                    },
                    DEFAULT_API_URL,
                    mode,
                )
            except Exception as exc:  # noqa: BLE001
                st.error(ui["request_failed"].format(error=exc))
                return

        render_results(result, ui)


if __name__ == "__main__":
    main()
