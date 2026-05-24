"""UI strings for Streamlit demo — English (default) and Korean."""

from __future__ import annotations

from typing import Literal

Lang = Literal["en", "ko"]

LANG_OPTIONS: dict[Lang, str] = {
    "en": "English",
    "ko": "한국어",
}

UI: dict[Lang, dict[str, str]] = {
    "en": {
        "page_title": "TradeSmart Demo",
        "title": "TradeSmart V2",
        "subtitle": "Planner Agent · Playbook RAG · Trade Journal RAG · Technicals · Risk Engine",
        "mock_banner": (
            "**Sample demo mode** — illustrative output only, no API calls. "
            "Add `OPENAI_API_KEY` locally for live AI."
        ),
        "sidebar_status": "Status",
        "online": "Online · v{version}",
        "mode_mock": "Mode: **Sample demo** (no API)",
        "mode_direct": "Mode: **Live AI (direct)**",
        "mode_api": "Mode: **Live AI (API)**",
        "playbook_not_ready": "Playbook store not ready.",
        "journal_not_ready": "Journal store not ready.",
        "offline": "Offline.",
        "api_url_label": "API URL (local)",
        "try_example": "**Try an example**",
        "example_queries_link": "Example queries",
        "language_label": "Language",
        "query_label": "Trading question",
        "symbols_label": "Symbols",
        "position_size_label": "Planned position size (% of portfolio)",
        "run_button": "Run V2 Research Agent",
        "empty_query": "Enter a trading question.",
        "system_offline": "System offline. Configure OPENAI_API_KEY.",
        "spinner_mock": "Loading portfolio preview...",
        "spinner_live": "Planner → playbook RAG → journal RAG → market → technicals → risk → LLM...",
        "request_failed": "Request failed: {error}",
        "agent_plan": "**Agent plan:** playbook={playbook} · journal={journal} · market={market} · technicals={technicals} · risk={risk}",
        "thesis": "Thesis",
        "market": "Market",
        "risk_flags": "Risk Flags",
        "technicals": "Technical Indicators",
        "action_items": "Action Items",
        "journal_expander": "Journal matches (episodic RAG)",
        "journal_empty": "No journal matches — try a question about past trades.",
        "playbook_expander": "Playbook matches (rules RAG)",
        "no_market": "No market snapshots returned.",
        "no_technicals": "No technical indicators (planner skipped or unavailable).",
        "no_risk_flags": "No rule-based risk flags triggered.",
        "market_caption": "5d: {change_5d}% | vol: {volume} | 52w: {pos_52w}",
        "market_delta": "{change_1d}% (1d)",
        "tech_line": (
            "**{symbol}** · RSI14={rsi} · MACD={macd}/{signal} · "
            "SMA20={sma20} · SMA50={sma50} · SMA200={sma200} · "
            "ATR14={atr} · 60d DD={dd}%"
        ),
        "severity_prefix": "[{severity}]",
    },
    "ko": {
        "page_title": "TradeSmart 데모",
        "title": "TradeSmart V2",
        "subtitle": "플래너 에이전트 · 플레이북 RAG · 매매일지 RAG · 기술적 지표 · 리스크 엔진",
        "mock_banner": (
            "**샘플 데모 모드** — 예시 출력만 표시됩니다 (API 호출 없음). "
            "실제 AI는 로컬에서 `OPENAI_API_KEY`를 설정하세요."
        ),
        "sidebar_status": "상태",
        "online": "온라인 · v{version}",
        "mode_mock": "모드: **샘플 데모** (API 없음)",
        "mode_direct": "모드: **실시간 AI (직접 실행)**",
        "mode_api": "모드: **실시간 AI (API)**",
        "playbook_not_ready": "플레이북 저장소 준비 안 됨.",
        "journal_not_ready": "매매일지 저장소 준비 안 됨.",
        "offline": "오프라인.",
        "api_url_label": "API URL (로컬)",
        "try_example": "**예시 질문**",
        "example_queries_link": "예시 질문 모음",
        "language_label": "언어",
        "query_label": "트레이딩 질문",
        "symbols_label": "종목",
        "position_size_label": "계획 포지션 크기 (포트폴리오 %)",
        "run_button": "V2 리서치 에이전트 실행",
        "empty_query": "트레이딩 질문을 입력하세요.",
        "system_offline": "시스템 오프라인. OPENAI_API_KEY를 설정하세요.",
        "spinner_mock": "샘플 미리보기 불러오는 중...",
        "spinner_live": "플래너 → 플레이북 RAG → 일지 RAG → 시장 → 기술적 지표 → 리스크 → LLM...",
        "request_failed": "요청 실패: {error}",
        "agent_plan": "**에이전트 계획:** playbook={playbook} · journal={journal} · market={market} · technicals={technicals} · risk={risk}",
        "thesis": "투자 논지",
        "market": "시장",
        "risk_flags": "리스크 플래그",
        "technicals": "기술적 지표",
        "action_items": "액션 아이템",
        "journal_expander": "매매일지 매칭 (에피소드 RAG)",
        "journal_empty": "매매일지 매칭 없음 — 과거 매매에 대한 질문을 시도해 보세요.",
        "playbook_expander": "플레이북 매칭 (규칙 RAG)",
        "no_market": "시장 스냅샷 없음.",
        "no_technicals": "기술적 지표 없음 (플래너가 건너뛰었거나 사용 불가).",
        "no_risk_flags": "규칙 기반 리스크 플래그 없음.",
        "market_caption": "5일: {change_5d}% | 거래량: {volume} | 52주: {pos_52w}",
        "market_delta": "{change_1d}% (1일)",
        "tech_line": (
            "**{symbol}** · RSI14={rsi} · MACD={macd}/{signal} · "
            "SMA20={sma20} · SMA50={sma50} · SMA200={sma200} · "
            "ATR14={atr} · 60일 DD={dd}%"
        ),
        "severity_prefix": "[{severity}]",
    },
}

EXAMPLE_QUERIES: dict[Lang, list[str]] = {
    "en": [
        (
            "SOXL ran from ~68 to ~190. I bought 14 @ 188.89 and 20 @ 168.74, and sold 20 @ 166. "
            "Should I hold or trim? How does this compare to my past trades and RSI?"
        ),
        "How similar is adding SOXL at 188.89 to my past winning vs losing entries?",
        "I sold 20 SOXL at 166 before — should I repeat that trim strategy near 190?",
        "BTC pulled back 3% while QQQ holds above the 50-day — add to BTC sleeve?",
    ],
    "ko": [
        (
            "SOXL이 약 68에서 190까지 올랐어. 188.89에 14주, 168.74에 20주 매수했고 166에 20주 매도했어. "
            "홀드할까 일부 익절할까? 과거 매매·RSI와 비교해줘."
        ),
        "188.89에 SOXL 추가 매수는 과거 수익/손실 진입과 얼마나 비슷해?",
        "전에 SOXL 166에 20주 매도했는데 — 190 근처에서 같은 익절 전략을 반복해야 할까?",
        "BTC는 3% 조정인데 QQQ는 50일선 위 — BTC 비중을 늘려도 될까?",
    ],
}


def normalize_lang(lang: str | None) -> Lang:
    """Return a supported language code (defaults to English)."""
    if lang and lang.lower().startswith("ko"):
        return "ko"
    return "en"


def get_ui(lang: str | None) -> dict[str, str]:
    return UI[normalize_lang(lang)]
