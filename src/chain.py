from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser


def format_docs(docs):
    """Format retrieved documents into a string."""
    return "\n\n".join(doc.page_content for doc in docs)


def build_rag_chain(retriever, llm_model: str = "llama3", ollama_base_url: str = "http://localhost:11434"):
    """Build the RAG chain: retriever -> prompt -> llm -> output."""

    llm = ChatOllama(
        model=llm_model,
        base_url=ollama_base_url,
        temperature=0.7,
    )

    prompt = PromptTemplate(
        template="""You are a helpful assistant answering questions based on the provided context.

Context:
{context}

Question: {question}

Answer:""",
        input_variables=["context", "question"],
    )

    chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain, retriever
