# Try TradeSmart without installing

## Streamlit Cloud (browser demo)

1. Open [share.streamlit.io](https://share.streamlit.io)
2. New app → repo **`yongguncodework/TradeSmart`** → file **`streamlit_app.py`**
3. Leave secrets empty (or set `TRADESMART_MOCK=true`)
4. Deploy

Runs in **sample mode** — no OpenAI key, no cost. Shows the same UI flow as the README preview.

## Record a GIF for README (optional)

See [RECORD_DEMO_GIF.md](RECORD_DEMO_GIF.md) — save as `docs/demo-preview.gif` and add to README.

## Live mode (your machine only)

Add `OPENAI_API_KEY` to `.env` and run locally. See README **Run locally**.
