"""CLI helper to ingest playbooks and trade journal into Chroma."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import get_settings
from app.rag.journal_store import build_journal_store
from app.rag.vectorstore import build_vector_store


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest TradeSmrt knowledge bases into ChromaDB.")
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Force rebuild of all vector stores from scratch.",
    )
    args = parser.parse_args()

    settings = get_settings()
    playbook_store = build_vector_store(settings, force_rebuild=args.rebuild)
    journal_store = build_journal_store(settings, force_rebuild=args.rebuild)

    playbook_count = playbook_store._collection.count()  # noqa: SLF001
    journal_count = journal_store._collection.count()  # noqa: SLF001

    print(f"Playbook chunks: {playbook_count}")
    print(f"Journal chunks:  {journal_count}")
    print(f"Persist directory: {settings.chroma_persist_dir}")
    print("Ingestion complete.")


if __name__ == "__main__":
    main()
