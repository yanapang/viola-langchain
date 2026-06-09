#!/usr/bin/env python3
import sys
from pathlib import Path

# Allow `python src/app.py` from the project root.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.chain import build_rag_chain
from src.config import load_settings
from src.loader import load_and_chunk_wiki
from src.providers import create_embeddings, create_llm
from src.providers.ollama_health import validate_ollama_models
from src.vectorstore import build_or_load_vectorstore, get_retriever


def _llm_label(settings) -> str:
    if settings.llm_provider == "ollama":
        return settings.ollama_llm_model
    if settings.llm_provider == "huggingface":
        return settings.hf_llm_model
    if settings.llm_provider == "openai":
        return settings.openai_llm_model
    if settings.llm_provider == "cursor":
        return settings.cursor_model
    return "unknown"


def _embed_label(settings) -> str:
    if settings.embed_provider == "ollama":
        return settings.ollama_embed_model
    if settings.embed_provider == "huggingface":
        return settings.hf_embed_model
    return "unknown"


def main():
    settings = load_settings()
    rebuild = "--rebuild" in sys.argv

    validate_ollama_models(settings)
    embeddings = create_embeddings(settings)
    llm = create_llm(settings)

    persist_path = Path(settings.persist_dir)
    if persist_path.exists() and list(persist_path.iterdir()) and not rebuild:
        print("Using cached vectorstore...")
        vectorstore = build_or_load_vectorstore(
            docs=None,
            embeddings=embeddings,
            persist_dir=settings.persist_dir,
        )
    else:
        if rebuild:
            print("Rebuilding vectorstore...")
        print("Loading wiki documents...")
        docs = load_and_chunk_wiki(settings.wiki_dir)
        vectorstore = build_or_load_vectorstore(
            docs=docs,
            embeddings=embeddings,
            persist_dir=settings.persist_dir,
        )

    retriever = get_retriever(vectorstore, k=3)
    chain, _ = build_rag_chain(retriever=retriever, llm=llm)

    print("\n" + "=" * 60)
    print("RAG System Ready!")
    print("=" * 60)
    print(f"Wiki directory: {settings.wiki_dir}")
    print(f"LLM provider: {settings.llm_provider}")
    print(f"LLM model: {_llm_label(settings)}")
    print(f"Embedding provider: {settings.embed_provider}")
    print(f"Embedding model: {_embed_label(settings)}")
    if settings.llm_provider == "ollama" or settings.embed_provider == "ollama":
        print(f"Ollama URL: {settings.ollama_base_url}")
    print("=" * 60)
    print("Type 'exit' to quit\n")

    while True:
        question = input("Ask a question: ").strip()
        if question.lower() == "exit":
            print("Goodbye!")
            break
        if not question:
            continue

        print("\nSearching...\n")
        answer = chain.invoke(question)
        print(f"Answer: {answer}\n")


if __name__ == "__main__":
    main()
