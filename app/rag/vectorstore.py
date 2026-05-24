"""Vector store setup and playbook ingestion for RAG."""

from __future__ import annotations

from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import Settings, get_settings


def _delete_collection_if_exists(persist_dir: Path, collection_name: str) -> None:
    try:
        import chromadb

        client = chromadb.PersistentClient(path=str(persist_dir))
        client.delete_collection(collection_name)
    except Exception:
        pass


def _embeddings(settings: Settings | None = None) -> OpenAIEmbeddings:
    settings = settings or get_settings()
    return OpenAIEmbeddings(
        model=settings.openai_embedding_model,
        api_key=settings.openai_api_key or None,
    )


def load_playbook_documents(playbooks_dir: str | Path):
    """Load markdown/text playbooks from disk."""
    path = Path(playbooks_dir)
    if not path.exists():
        raise FileNotFoundError(f"Playbooks directory not found: {path}")

    documents = []
    for pattern in ("**/*.md", "**/*.txt"):
        loader = DirectoryLoader(
            str(path),
            glob=pattern,
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
            show_progress=False,
            use_multithreading=True,
        )
        documents.extend(loader.load())
    return documents


def build_vector_store(
    settings: Settings | None = None,
    *,
    force_rebuild: bool = False,
) -> Chroma:
    """
    Create or load a persisted Chroma collection from playbooks.

    Call with force_rebuild=True to re-embed all playbook documents.
    """
    settings = settings or get_settings()
    persist_dir = Path(settings.chroma_persist_dir)
    persist_dir.mkdir(parents=True, exist_ok=True)

    embedding = _embeddings(settings)
    collection_name = "tradesmrt_playbooks"

    if force_rebuild:
        _delete_collection_if_exists(persist_dir, collection_name)
    elif any(persist_dir.iterdir()):
        return Chroma(
            collection_name=collection_name,
            persist_directory=str(persist_dir),
            embedding_function=embedding,
        )

    documents = load_playbook_documents(settings.playbooks_dir)
    if not documents:
        raise ValueError("No playbook documents found to ingest.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=120,
        separators=["\n## ", "\n### ", "\n", " "],
    )
    chunks = splitter.split_documents(documents)

    return Chroma.from_documents(
        documents=chunks,
        embedding=embedding,
        collection_name=collection_name,
        persist_directory=str(persist_dir),
    )


def get_retriever(settings: Settings | None = None, top_k: int | None = None):
    """Return a similarity retriever over playbook chunks."""
    settings = settings or get_settings()
    store = build_vector_store(settings)
    return store.as_retriever(search_kwargs={"k": top_k or settings.rag_top_k})
