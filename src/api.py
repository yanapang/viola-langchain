#!/usr/bin/env python3
"""FastAPI server that exposes the RAG chain over HTTP."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.chain import build_rag_chain
from src.config import load_settings
from src.loader import load_and_chunk_wiki
from src.providers import create_embeddings, create_llm
from src.providers.ollama_health import validate_ollama_models
from src.vectorstore import build_or_load_vectorstore, get_retriever

# ──────────────────────────────────────────────
# Helpers (reused from app.py)
# ──────────────────────────────────────────────

def _embed_label(settings) -> str:
    if settings.embed_provider == "ollama":
        return settings.ollama_embed_model
    if settings.embed_provider == "huggingface":
        return settings.hf_embed_model
    return "unknown"


def _embed_meta_path(persist_dir: str) -> Path:
    return Path(persist_dir) / ".embed_model"


def _needs_rebuild(settings, persist_path: Path, rebuild: bool) -> bool:
    if rebuild:
        return True
    if not persist_path.exists() or not any(persist_path.iterdir()):
        return True
    meta_path = _embed_meta_path(settings.persist_dir)
    if not meta_path.exists():
        return True
    current = f"{settings.embed_provider}:{_embed_label(settings)}"
    stored = meta_path.read_text(encoding="utf-8").strip()
    return stored != current


def _save_embed_meta(settings) -> None:
    meta_path = _embed_meta_path(settings.persist_dir)
    meta_path.write_text(
        f"{settings.embed_provider}:{_embed_label(settings)}",
        encoding="utf-8",
    )


# ──────────────────────────────────────────────
# App-level state
# ──────────────────────────────────────────────

_chain = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the RAG chain once at startup."""
    global _chain

    print("Initializing RAG system...")
    settings = load_settings()

    validate_ollama_models(settings)
    embeddings = create_embeddings(settings)
    llm = create_llm(settings)

    persist_path = Path(settings.persist_dir)
    if _needs_rebuild(settings, persist_path, rebuild=False):
        print("Loading wiki documents and building vectorstore...")
        docs = load_and_chunk_wiki(settings.wiki_dir)
        vectorstore = build_or_load_vectorstore(
            docs=docs,
            embeddings=embeddings,
            persist_dir=settings.persist_dir,
            rebuild=True,
        )
        _save_embed_meta(settings)
    else:
        print("Using cached vectorstore...")
        vectorstore = build_or_load_vectorstore(
            docs=None,
            embeddings=embeddings,
            persist_dir=settings.persist_dir,
        )

    retriever = get_retriever(vectorstore, k=3)
    _chain, _ = build_rag_chain(
        retriever=retriever,
        llm=llm,
        response_language=settings.response_language,
    )
    print("RAG system ready.")
    yield


# ──────────────────────────────────────────────
# FastAPI app
# ──────────────────────────────────────────────

app = FastAPI(title="Wiki RAG API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# Request / Response schemas
# ──────────────────────────────────────────────

class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str


# ──────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────

@app.get("/")
async def root():
    return {"message": "Wiki RAG API is running. POST /ask to query."}


@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    """Return a complete answer for the given question."""
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="question must not be empty")
    if _chain is None:
        raise HTTPException(status_code=503, detail="RAG chain not initialized")

    answer = _chain.invoke(req.question)
    return AskResponse(answer=answer)


@app.post("/ask/stream")
async def ask_stream(req: AskRequest):
    """Stream the answer token-by-token using Server-Sent Events."""
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="question must not be empty")
    if _chain is None:
        raise HTTPException(status_code=503, detail="RAG chain not initialized")

    def token_generator():
        for token in _chain.stream(req.question):
            # SSE format: data: <payload>\n\n
            yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(token_generator(), media_type="text/event-stream")
