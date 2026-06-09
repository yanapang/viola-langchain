#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from src.loader import load_and_chunk_wiki
from src.vectorstore import build_or_load_vectorstore, get_retriever
from src.chain import build_rag_chain

load_dotenv()

WIKI_DIR = os.getenv("WIKI_DIR", "./wiki")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3")
PERSIST_DIR = ".chroma"


def main():
    # Check if we need to rebuild
    rebuild = "--rebuild" in sys.argv

    # Load or build vectorstore
    persist_path = Path(PERSIST_DIR)
    if persist_path.exists() and list(persist_path.iterdir()) and not rebuild:
        print("Using cached vectorstore...")
        vectorstore = build_or_load_vectorstore(
            docs=None,
            embed_model=EMBED_MODEL,
            ollama_base_url=OLLAMA_BASE_URL,
            persist_dir=PERSIST_DIR,
        )
    else:
        if rebuild:
            print("Rebuilding vectorstore...")
        print("Loading wiki documents...")
        docs = load_and_chunk_wiki(WIKI_DIR)
        vectorstore = build_or_load_vectorstore(
            docs=docs,
            embed_model=EMBED_MODEL,
            ollama_base_url=OLLAMA_BASE_URL,
            persist_dir=PERSIST_DIR,
        )

    # Build RAG chain
    retriever = get_retriever(vectorstore, k=3)
    chain, _ = build_rag_chain(
        retriever=retriever,
        llm_model=LLM_MODEL,
        ollama_base_url=OLLAMA_BASE_URL,
    )

    print("\n" + "=" * 60)
    print("RAG System Ready!")
    print("=" * 60)
    print(f"Wiki directory: {WIKI_DIR}")
    print(f"LLM model: {LLM_MODEL}")
    print(f"Embedding model: {EMBED_MODEL}")
    print(f"Ollama URL: {OLLAMA_BASE_URL}")
    print("=" * 60)
    print("Type 'exit' to quit\n")

    # Interactive loop
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
