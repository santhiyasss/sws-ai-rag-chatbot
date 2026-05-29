from langchain_anthropic import ChatAnthropic
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

    llm = ChatAnthropic(
        model="claude-3-haiku-20240307",
        anthropic_api_key=settings.ANTHROPIC_API_KEY,
        max_tokens=1024
    )

    chain = prompt | llm
    response = chain.invoke({"context": context, "question": question})

    return {
        "answer": response.content,
        "sources": list(sources)
    }