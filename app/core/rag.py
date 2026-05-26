from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from app.core.vectorstore import get_retriever
from app.config import settings

LLM_MODEL = "llama-3.1-8b-instant"

RAG_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are a helpful assistant that answers questions about a YouTube video.
Use ONLY the transcript context below to answer the question.
If the answer is not in the context, say "I couldn't find that information in the video."
Always answer in the same language as the question.

Context from video transcript:
{context}

Question: {question}

Answer:"""
)


def get_llm():
    return ChatGroq(
        model=LLM_MODEL,
        temperature=0.3,
        max_tokens=512,
        groq_api_key=settings.GROQ_API_KEY,
    )


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def get_rag_chain(video_id: str):
    retriever = get_retriever(video_id, k=4)
    llm = get_llm()
    chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | RAG_PROMPT
        | llm
        | StrOutputParser()
    )
    return chain, retriever


def ask_question(video_id: str, question: str) -> dict:
    chain, retriever = get_rag_chain(video_id)
    answer = chain.invoke(question)
    docs = retriever.invoke(question)
    return {
        "answer": answer.strip(),
        "sources": [doc.page_content for doc in docs],
    }