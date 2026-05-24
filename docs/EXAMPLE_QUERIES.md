# TradeSmart V2 — Example Queries (RAG + Planner + Technicals)

Use these in the **Streamlit demo** or `POST /api/v1/research`.  
Re-ingest after updating journal: `python scripts/ingest_playbooks.py --rebuild`

---

## Your SOXL trades (stored in journal RAG)

| Action | Shares | Price | Notes |
|--------|--------|-------|-------|
| Buy | 3 | 126.87 | Early accumulation |
| Buy | 1 | 128.11 | Small add |
| Sell | 20 | 166.00 | Profit-taking swing exit |
| Buy | 10 | 187.14 | Momentum re-entry |
| Buy | 20 | 168.74 | Pullback add |
| Buy | 14 | 188.89 | Near-high add |

---

## Best V2 questions (journal RAG + technicals + playbook)

### 1. Hold vs trim after parabolic rally ⭐ (your real scenario)

```text
SOXL recently ran from ~68 to ~190. I also bought 14 shares at 188.89 and 20 at 168.74.
I previously sold 20 at 166 for profit. Should I still hold or start trimming?
What is the impact of this fast rally given RSI and my past trade pattern?
```

**Why it's strong:** triggers planner → journal RAG + technicals + playbook + risk.

---

### 2. Compare to past winning exit

```text
How similar is today's SOXL setup to my past successful sell at 166?
Should I repeat that trim strategy now that price is near 190?
```

**Why:** journal RAG retrieves the 166 sell + compares pattern.

---

### 3. Cost basis / layered entries

```text
I layered SOXL buys at 128, 168.74, 187.14, and 188.89. What is my behavioral pattern
and am I repeating the same mistake of adding near highs?
```

**Why:** journal summary + playbook SOXL sizing rules.

---

### 4. Technical + playbook combo

```text
SOXL RSI looks extended after a 180% run. Based on my playbook and current SMA20/50/200,
is this a trim zone or hold zone?
```

**Why:** technicals + playbook RAG (skips deep journal if you remove past-trade words — still gets playbook).

---

### 5. Past pattern similarity (pure RAG journal)

```text
How similar is this setup to my past winning SOXL trades vs my re-entries near highs?
```

---

### 6. BTC + ETF (non-SOXL)

```text
BTC pulled back 3% while QQQ holds above the 50-day. How does this compare to my playbook
regime filter — should I add BTC or wait?
```

Symbols: `BTC-USD`, `QQQ`, `SPY`

---

## Demo JSON payloads

### SOXL trim question

```json
{
  "query": "SOXL ran from 68 to 190. I bought at 188.89 and 168.74, and sold 20 at 166 before. Should I hold or trim?",
  "symbols": ["SOXL", "SMH", "QQQ"],
  "position_size_pct": 12
}
```

### Journal pattern question

```json
{
  "query": "How similar is adding SOXL at 188.89 to my past trades? Did I usually win when buying near highs?",
  "symbols": ["SOXL"],
  "position_size_pct": null
}
```

---

## What to look for in V2 responses

| Section | Good sign |
|---------|-----------|
| **agent_plan** | `journal: true`, `technicals: true` for SOXL hold/trim questions |
| **journal_matches** | Your 166 sell, 188.89 buy, layered entry summary |
| **technical_context** | RSI, MACD, SMA20/50/200, drawdown from 60d high |
| **risk_flags** | `rsi_overbought`, `extended_rally`, `extended_price` |
| **thesis** | References **your past trim at 166** + **current extension** |

---

## Interview demo script (2 min)

1. Open Streamlit → paste **Question 1**
2. Show **Agent Plan** in API trace (`include_trace=true`) or explain sidebar flow
3. Expand **Journal matches** → "this is episodic memory RAG, not generic LLM"
4. Point at **RSI / drawdown** → "technical tool layer"
5. Close with **risk flags** → "deterministic rules before LLM synthesis"
