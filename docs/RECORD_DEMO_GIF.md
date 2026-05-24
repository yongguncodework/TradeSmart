# Record a Demo GIF (Windows, free)

One-time screen recording → embed in README → **$0 forever**.

---

## Quick method — Xbox Game Bar (built into Windows)

1. Run mock demo locally (no API cost):

```powershell
$env:TRADESMART_MOCK="true"
streamlit run streamlit_app.py
```

2. Open http://localhost:8501
3. Press **Win + Alt + R** to start recording
4. Click **Run V2 Research Agent** and scroll through:
   - Agent plan
   - Thesis
   - Market / Risk / Technicals
   - Journal RAG (your SOXL trades)
5. Press **Win + Alt + R** to stop
6. Clip saves to `Videos/Captures/`

---

## Convert to GIF (optional, smaller for GitHub)

Use **[ScreenToGif](https://www.screentogif.com/)** (free):

1. Import the MP4 clip
2. Trim to ~15–30 seconds
3. Export as `docs/demo-preview.gif`
4. Keep file **under 10 MB** for GitHub

---

## Add to README

```markdown
## Demo preview

![TradeSmart V2 demo](docs/demo-preview.gif)

*[Live preview app](https://your-app.streamlit.app)* — sample output, no API cost.
```

---

## What to show in the GIF (30 sec script)

1. SOXL question pre-filled
2. Click **Run V2 Research Agent**
3. Highlight **Journal matches** (166 sell, 188.89 buy)
4. Highlight **RSI / risk flags**
5. Show **action items**

That answers "how does it work?" without live AI costs.
