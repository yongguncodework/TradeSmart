#!/bin/sh
set -e

if [ "$TRADESMART_DIRECT" = "true" ]; then
  echo "Starting Streamlit demo (direct mode) on :8501"
  exec streamlit run streamlit_app.py \
    --server.address=0.0.0.0 \
    --server.port=8501 \
    --browser.gatherUsageStats=false
fi

echo "Starting Streamlit demo (API mode) on :8501"
exec streamlit run demo/streamlit_app.py \
  --server.address=0.0.0.0 \
  --server.port=8501 \
  --browser.gatherUsageStats=false
