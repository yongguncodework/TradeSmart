"""Trade journal RAG retrieval."""

from __future__ import annotations

from langchain_core.documents import Document

from app.api.schemas import JournalMatch
from app.config import Settings, get_settings
from app.rag.journal_store import get_journal_retriever


def retrieve_journal_context(
    query: str,
    settings: Settings | None = None,
    top_k: int | None = None,
) -> list[JournalMatch]:
    settings = settings or get_settings()
    retriever = get_journal_retriever(settings, top_k=top_k)
    docs: list[Document] = retriever.invoke(query)

    matches: list[JournalMatch] = []
    for doc in docs:
        matches.append(
            JournalMatch(
                source=str(doc.metadata.get("source", "journal:unknown")),
                content=doc.page_content.strip(),
                symbol=doc.metadata.get("symbol"),
                action=doc.metadata.get("action"),
            )
        )
    return matches


def journal_matches_to_prompt_block(matches: list[JournalMatch]) -> str:
    if not matches:
        return "No similar past trades found in journal."
    blocks: list[str] = []
    for idx, match in enumerate(matches, start=1):
        blocks.append(f"[{idx}] Source: {match.source}\n{match.content}")
    return "\n\n".join(blocks)
