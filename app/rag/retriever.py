"""RAG retrieval helpers."""

from __future__ import annotations

from langchain_core.documents import Document

from app.api.schemas import PlaybookMatch
from app.config import Settings, get_settings
from app.rag.vectorstore import get_retriever


def retrieve_playbook_context(
    query: str,
    settings: Settings | None = None,
    top_k: int | None = None,
) -> list[PlaybookMatch]:
    """Retrieve the most relevant playbook chunks for a user query."""
    settings = settings or get_settings()
    retriever = get_retriever(settings, top_k=top_k)
    docs: list[Document] = retriever.invoke(query)

    matches: list[PlaybookMatch] = []
    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        matches.append(
            PlaybookMatch(
                source=str(source),
                content=doc.page_content.strip(),
                score=doc.metadata.get("score"),
            )
        )
    return matches


def playbook_matches_to_prompt_block(matches: list[PlaybookMatch]) -> str:
    """Format retrieved playbook excerpts for LLM consumption."""
    if not matches:
        return "No matching playbook content found."
    blocks: list[str] = []
    for idx, match in enumerate(matches, start=1):
        blocks.append(f"[{idx}] Source: {match.source}\n{match.content}")
    return "\n\n".join(blocks)
