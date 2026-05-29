from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from app.core.config import settings

_vectorstore = None

def get_vectorstore() -> Chroma:
    global _vectorstore
    if _vectorstore is None:
        embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL
        )
        _vectorstore = Chroma(
            collection_name=settings.COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=settings.CHROMA_PERSIST_DIR
        )
    return _vectorstore

def retrieve_chunks(question: str) -> list:
    vs = get_vectorstore()
    results = vs.similarity_search_with_score(question, k=settings.TOP_K)
    return results