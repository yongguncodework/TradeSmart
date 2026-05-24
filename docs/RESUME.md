# TradeSmart — Resume & Portfolio Snippets

Use these blocks on your resume, LinkedIn, cover letter, or portfolio site.  
Repo: **https://github.com/yongguncodework/TradeSmart**

---

## Project Title (pick one)

- **TradeSmart — AI Trading Research Copilot**
- **TradeSmart — RAG + LangGraph Agent for Pre-Trade Research**

---

## One-liner (English)

Personal AI agent that generates structured pre-trade research briefs for Bitcoin, ETFs, and SOXL by combining RAG over custom playbooks, live market data, and deterministic risk guardrails.

---

## One-liner (Korean)

Bitcoin·ETF·SOXL 매매 전 리서치를 자동화하는 AI agent. 개인 playbook RAG, 실시간 시장 데이터, 규칙 기반 risk engine, LLM synthesis를 하나의 API/Demo UI로 통합.

---

## Resume — Project Block (English)

**TradeSmart — AI Trading Research Copilot** | Personal Project  
GitHub: github.com/yongguncodework/TradeSmart

- Built a **FastAPI + LangGraph** agent that automates pre-trade research for **BTC, ETFs, and SOXL** (not auto-trading).
- Implemented **RAG** with **LangChain + ChromaDB** over personal markdown playbooks for grounded, repeatable decision support.
- Integrated **yfinance** market snapshots and a **deterministic Python risk engine** (position caps, leveraged ETF limits, volatility flags).
- Delivered **Streamlit demo UI**, **Docker Compose** deployment, typed **Pydantic** schemas, **pytest** coverage, and OpenAPI docs.

**Stack:** Python, FastAPI, LangGraph, LangChain, ChromaDB, OpenAI, yfinance, Streamlit, Docker

---

## Resume — Bullet-only version (copy 3–4 lines)

- Designed a hybrid AI pipeline: **RAG retrieval → market data tools → rule-based risk checks → LLM synthesis**
- Exposed the agent via **REST API** with health checks, structured JSON responses, and Swagger documentation
- Containerized API + demo with **Docker Compose** for one-command local deployment and portfolio demos
- Applied responsible AI patterns: no execution layer, explicit disclaimers, auditable deterministic rules before LLM output

---

## LinkedIn — Featured Project Description

**TradeSmart | AI Trading Research Copilot**

I built TradeSmart to solve a problem I hit every week as an active trader: before entering BTC, ETF, or SOXL positions, I need to cross-check my playbook rules, current market context, and risk limits — fast.

Instead of a generic chatbot, TradeSmart uses a **LangGraph agent** with four explicit steps:
1) RAG over my personal playbooks (ChromaDB)  
2) Live market snapshots (yfinance)  
3) Deterministic risk guardrails (Python rules)  
4) LLM synthesis into a structured research brief

The project includes a **Streamlit demo**, **Docker Compose** setup, unit tests, and full API documentation. It is designed as **decision support**, not financial advice or automated trading.

Tech: FastAPI · LangGraph · LangChain · ChromaDB · OpenAI · Streamlit · Docker

---

## Korean Resume Block

**TradeSmart — AI 트레이딩 리서치 Copilot** | 개인 프로젝트  
GitHub: github.com/yongguncodework/TradeSmart

- **FastAPI + LangGraph** 기반 agent로 BTC·ETF·SOXL **매매 전 리서치** 자동화 (자동 매매 아님)
- **LangChain + ChromaDB RAG**로 개인 trading playbook 기반 grounded response 구현
- **yfinance** 시장 데이터 + **Python rule engine** (포지션 cap, SOXL 레버리지 한도, 변동성 flag)
- **Streamlit demo UI**, **Docker Compose**, Pydantic schema, pytest, OpenAPI docs 제공

**기술 스택:** Python, FastAPI, LangGraph, LangChain, ChromaDB, OpenAI, Streamlit, Docker

---

## Interview — 60-second script (English)

> "TradeSmart is a personal project I built around how I actually trade BTC, ETFs, and SOXL. It's not a trading bot — it's a pre-trade research copilot.
>
> I use LangGraph to orchestrate four nodes: RAG over my markdown playbooks, a yfinance market data tool, a deterministic risk engine for position and leverage limits, and finally an LLM step that synthesizes a structured brief with a thesis and action items.
>
> I intentionally separated execution from research. The risk rules are pure Python so they're testable and reproducible, and RAG keeps the model grounded in my own rules instead of generic advice.
>
> For portfolio demos, I added a Streamlit UI and Docker Compose so interviewers can run the full stack with one command."

---

## Interview — 60-second script (Korean)

> "TradeSmart는 제가 실제로 거래하는 BTC, ETF, SOXL의 **매매 전 리서치**를 자동화한 개인 프로젝트입니다. 자동 매매 봇이 아니라 research copilot입니다.
>
> LangGraph로 4단계 pipeline을 만들었습니다. playbook RAG, yfinance 시장 데이터, Python risk rule engine, LLM synthesis 순서입니다.
>
> LLM에 모든 판단을 맡기지 않고, 규칙 기반 레이어와 RAG로 grounding한 hybrid AI design이 핵심입니다.
>
> 면접 demo를 위해 Streamlit UI와 Docker Compose까지 포함했습니다."

---

## Skills to tag on resume / LinkedIn

`Python` · `FastAPI` · `LangGraph` · `LangChain` · `RAG` · `ChromaDB` · `OpenAI API` · `Agentic AI` · `Docker` · `Streamlit` · `REST APIs` · `Pydantic` · `pytest`

---

## Demo talking points (live interview)

1. Open **Streamlit** → ask an SOXL question → show thesis + risk flags
2. Expand **Playbook matches** → "this came from my RAG knowledge base, not generic LLM memory"
3. Mention **risk flag** triggered by SOXL size or daily move → "deterministic rules ran before LLM"
4. Optional: show **Swagger** at `/docs` for API-first design

---

## What NOT to say

- ❌ "AI trading bot that makes money"
- ❌ "Guaranteed signals" / "automated profit system"
- ✅ "Pre-trade research automation"
- ✅ "Hybrid AI: RAG + tools + rules + LLM"
- ✅ "Responsible decision-support design"
