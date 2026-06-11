from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.language_models.chat_models import BaseChatModel


def format_docs(docs):
    """Format retrieved documents into a string."""
    return "\n\n".join(doc.page_content for doc in docs)


def _prompt_for_language(language: str) -> PromptTemplate:
    if language == "ko":
        template = """제공된 맥락만을 바탕으로 질문에 답하세요.
절대 중국어로 답하지 마세요. 한국어 또는 영어로만 답하세요.
맥락에 답이 없으면 모른다고 한국어로 답하세요.

맥락:
{context}

질문: {question}

답변:"""
    else:
        template = """You are a helpful assistant answering questions based on the provided context.
If the context does not contain the answer, say you do not know. Answer in English. Do not answer in Chinese.

Context:
{context}

Question: {question}

Answer:"""

    return PromptTemplate(
        template=template,
        input_variables=["context", "question"],
    )


def build_rag_chain(
    retriever, llm: BaseChatModel, response_language: str = "ko"
):
    """Build the RAG chain: retriever -> prompt -> llm -> output."""

    prompt = _prompt_for_language(response_language)

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
