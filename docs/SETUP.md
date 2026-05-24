# Setup & Run Guide

Step-by-step install for **Windows**, **macOS/Linux**, and **Docker**.

---

## Prerequisites

| Requirement | Notes |
|-------------|--------|
| **Python 3.11+** | Check: `python --version` |
| **Git** | To clone the repo |
| **OpenAI API key** | Only for **live AI** mode ([platform.openai.com](https://platform.openai.com/api-keys)) |
| **Docker** (optional) | For containerized run |

---

## Two run modes

| Mode | API key needed? | Cost | Use case |
|------|-----------------|------|----------|
| **Sample demo** | No | Free | See UI flow, README-style output |
| **Live agent** | Yes | OpenAI usage | Real RAG + market data + LLM |

Sample demo:

```powershell
# Windows PowerShell
$env:TRADESMART_MOCK="true"
streamlit run streamlit_app.py
```

Live agent: follow full setup below.

---

## Windows (recommended path)

### 1. Clone and enter project

```powershell
git clone https://github.com/yongguncodework/TradeSmart.git
cd TradeSmart
```

### 2. Virtual environment

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

You should see `(.venv)` in your prompt.

### 3. Environment file

```powershell
copy .env.example .env
```

Edit `.env` and set:

```env
OPENAI_API_KEY=sk-your-real-key
```

> Never commit `.env` — it is gitignored.

### 4. Ingest knowledge bases (required once)

```powershell
python scripts/ingest_playbooks.py --rebuild
```

Expected output:

```text
Playbook chunks: 8
Journal chunks:  7
Ingestion complete.
```

If you see `No module named 'app'`, run from the project root (folder containing `app/`).

### 5. Start API (terminal 1)

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000/docs — Swagger UI should load.

Health check: http://127.0.0.1:8000/api/v1/health  
Both `vector_store_ready` and `journal_store_ready` should be `true`.

### 6. Start UI (terminal 2)

```powershell
cd TradeSmart
.venv\Scripts\activate
streamlit run streamlit_app.py
```

Open http://127.0.0.1:8501

- First Streamlit launch may ask for email → **press Enter to skip**
- Sidebar should show **API online**

### 7. Try a query

Use the default SOXL question or paste from [EXAMPLE_QUERIES.md](EXAMPLE_QUERIES.md), then click **Run V2 Research Agent**.

---

## macOS / Linux

```bash
git clone https://github.com/yongguncodework/TradeSmart.git
cd TradeSmart

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env → OPENAI_API_KEY=sk-...

python scripts/ingest_playbooks.py --rebuild

# Terminal 1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2
streamlit run streamlit_app.py
```

---

## Docker

```bash
cp .env.example .env
# add OPENAI_API_KEY for live mode

docker compose up --build
```

| URL | Service |
|-----|---------|
| http://127.0.0.1:8000/docs | API |
| http://127.0.0.1:8501 | Streamlit UI |

---

## API-only (no UI)

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/research" \
  -H "Content-Type: application/json" \
  -d '{"query": "Should I trim SOXL after a large rally?", "symbols": ["SOXL","SMH"], "position_size_pct": 10}'
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `No module named 'app'` | Run commands from project root; use `python scripts/ingest_playbooks.py` |
| `OPENAI_API_KEY is not configured` | Create `.env` from `.env.example` and restart API |
| `Vector store not ready` | Run `python scripts/ingest_playbooks.py --rebuild` |
| Streamlit `API unreachable` | Start uvicorn in terminal 1 first |
| `initial_sidebar_expanded` error | Update Streamlit: `pip install -U streamlit` |
| Ingest finds 0 playbooks (Windows) | Fixed in V2 — pull latest; uses `**/*.md` glob |
| OpenAI 401 / invalid key | Regenerate key at OpenAI dashboard |
| Slow first query | Normal — RAG + market fetch + LLM on first run |

---

## Verify tests (no API key)

```bash
pytest -q
```

---

## Customize data

1. Edit `data/playbooks/*.md` — trading rules  
2. Edit `data/journal/trades.jsonl` — your trade log (one JSON object per line)  
3. Re-ingest: `python scripts/ingest_playbooks.py --rebuild`

---

## Limitations

- Market data via **yfinance** — not real-time broker feed  
- LLM output can still hallucinate — risk engine + RAG reduce but do not eliminate this  
- **Not** for automated order execution  
- Sample demo mode returns **canned output**, not live analysis
