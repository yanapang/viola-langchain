import os
from pathlib import Path
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain.schema import Document


def build_or_load_vectorstore(
    docs: list[Document] | None = None,
    embed_model: str = "nomic-embed-text",
    ollama_base_url: str = "http://localhost:11434",
    persist_dir: str = ".chroma",
) -> Chroma:
    """Build a new vectorstore from docs or load existing one."""

    embeddings = OllamaEmbeddings(
        model=embed_model,
        base_url=ollama_base_url,
    )

    persist_path = Path(persist_dir)

    if persist_path.exists() and list(persist_path.iterdir()):
        print(f"Loading existing vectorstore from {persist_dir}")
        vectorstore = Chroma(
            persist_directory=str(persist_path),
            embedding_function=embeddings,
        )
    else:
        if docs is None or len(docs) == 0:
            raise ValueError("No documents provided and no existing vectorstore found")
        print(f"Building new vectorstore from {len(docs)} chunks...")
        vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=embeddings,
            persist_directory=str(persist_path),
        )
        vectorstore.persist()
        print(f"Vectorstore persisted to {persist_dir}")

    return vectorstore


def get_retriever(vectorstore: Chroma, k: int = 3):
    """Get a retriever from the vectorstore."""
    return vectorstore.as_retriever(search_kwargs={"k": k})
