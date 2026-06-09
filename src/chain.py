from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.language_models.chat_models import BaseChatModel


def format_docs(docs):
    """Format retrieved documents into a string."""
    return "\n\n".join(doc.page_content for doc in docs)


def build_rag_chain(retriever, llm: BaseChatModel):
    """Build the RAG chain: retriever -> prompt -> llm -> output."""

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
