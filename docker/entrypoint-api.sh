#!/bin/sh
set -e

echo "Ingesting playbooks into ChromaDB..."
python scripts/ingest_playbooks.py --rebuild

echo "Starting FastAPI on :8000"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
