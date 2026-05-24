"""Trade journal vector store and ingestion."""

from __future__ import annotations

import json
from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from app.config import Settings, get_settings
from app.rag.vectorstore import _delete_collection_if_exists, _embeddings

JOURNAL_COLLECTION = "tradesmrt_journal"


def _journal_to_text(entry: dict) -> str:
    """Render a journal record as searchable narrative text."""
    parts = [
        f"Symbol: {entry.get('symbol', 'UNKNOWN')}",
        f"Action: {entry.get('action', 'unknown')}",
    ]
    if entry.get("shares") is not None:
        parts.append(f"Shares: {entry['shares']}")
    if entry.get("price") is not None:
        parts.append(f"Price: {entry['price']}")
    if entry.get("date"):
        parts.append(f"Date: {entry['date']}")
    if entry.get("setup_tag"):
        parts.append(f"Setup: {entry['setup_tag']}")
    if entry.get("outcome_pct") is not None:
        parts.append(f"Outcome: {entry['outcome_pct']}%")
    if entry.get("notes"):
        parts.append(f"Notes: {entry['notes']}")
    if entry.get("tags"):
        parts.append(f"Tags: {', '.join(entry['tags'])}")
    return "\n".join(parts)


def load_journal_documents(journal_path: str | Path) -> list[Document]:
    path = Path(journal_path)
    if not path.exists():
        raise FileNotFoundError(f"Journal file not found: {path}")

    documents: list[Document] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entry = json.loads(line)
        documents.append(
            Document(
                page_content=_journal_to_text(entry),
                metadata={
                    "source": f"journal:{entry.get('id', entry.get('symbol', 'trade'))}",
                    "symbol": entry.get("symbol"),
                    "action": entry.get("action"),
                    "trade_id": entry.get("id"),
                },
            )
        )
    return documents


def build_journal_store(
    settings: Settings | None = None,
    *,
    force_rebuild: bool = False,
) -> Chroma:
    settings = settings or get_settings()
    persist_dir = Path(settings.chroma_persist_dir)
    persist_dir.mkdir(parents=True, exist_ok=True)
    embedding = _embeddings(settings)

    if force_rebuild:
        _delete_collection_if_exists(persist_dir, JOURNAL_COLLECTION)
    else:
        try:
            store = Chroma(
                collection_name=JOURNAL_COLLECTION,
                persist_directory=str(persist_dir),
                embedding_function=embedding,
            )
            if store._collection.count() > 0:  # noqa: SLF001
                return store
        except Exception:
            pass

    documents = load_journal_documents(settings.journal_path)
    if not documents:
        raise ValueError("No journal documents found to ingest.")

    return Chroma.from_documents(
        documents=documents,
        embedding=embedding,
        collection_name=JOURNAL_COLLECTION,
        persist_directory=str(persist_dir),
    )


def get_journal_retriever(settings: Settings | None = None, top_k: int | None = None):
    settings = settings or get_settings()
    store = build_journal_store(settings)
    return store.as_retriever(search_kwargs={"k": top_k or settings.rag_top_k})
