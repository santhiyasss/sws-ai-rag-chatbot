import sys, os
sys.path.append(os.path.dirname(__file__))

from app.services.ingestion import load_pdfs, chunk_documents, build_vectorstore
from app.core.config import settings

if __name__ == "__main__":
    print("Starting document ingestion...")
    docs = load_pdfs(settings.DOCUMENTS_DIR)
    print(f"Loaded {len(docs)} pages total")
    chunks = chunk_documents(docs)
    build_vectorstore(chunks)
    print("Ingestion complete! Vector store is ready.")