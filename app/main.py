"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.routes import router
from app.config import get_settings
from app.rag.journal_store import build_journal_store
from app.rag.vectorstore import build_vector_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Warm up the vector store on startup when credentials are present."""
    settings = get_settings()
    if settings.openai_api_key:
        try:
            build_vector_store(settings)
            build_journal_store(settings)
        except Exception:
            pass
    yield


app = FastAPI(
    title="TradeSmrt",
    description=(
        "AI trading research copilot for Bitcoin, ETFs, and SOXL. "
        "Combines RAG, LangGraph agents, market data tools, and risk guardrails."
    ),
    version=__version__,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1", tags=["research"])


@app.get("/")
async def root():
    """Root redirect to interactive docs."""
    return {
        "service": "TradeSmrt",
        "docs": "/docs",
        "health": "/api/v1/health",
        "research": "POST /api/v1/research",
    }
