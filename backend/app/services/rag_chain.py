from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.services.retriever import retrieve_chunks
from app.core.config import settings

SYSTEM_PROMPT = """You are an HR assistant for SWS AI. Answer employee questions using ONLY the provided company policy documents.

Rules:
- Answer only from the context below. Be concise and specific.
- If the answer is not in the documents, say exactly: "I don't have that information in the company documents."
- Never make up policies or numbers.

Context:
{context}
"""

def run_rag(question: str) -> dict:
    results = retrieve_chunks(question)

    context_parts = []
    sources = set()
    for doc, score in results:
        context_parts.append(doc.page_content)
        sources.add(doc.metadata.get("source", "Unknown"))

    context = "\n\n---\n\n".join(context_parts)

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{question}")
    ])

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        groq_api_key=settings.GROQ_API_KEY,
        temperature=0
    )

    chain = prompt | llm
    response = chain.invoke({"context": context, "question": question})

    return {
        "answer": response.content,
        "sources": list(sources)
    }