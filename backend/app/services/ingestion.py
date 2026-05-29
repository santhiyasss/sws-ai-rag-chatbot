import os
import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from app.core.config import settings

def load_pdfs(documents_dir: str) -> list[Document]:
    docs = []
    for filename in os.listdir(documents_dir):
        if filename.endswith(".pdf"):
            path = os.path.join(documents_dir, filename)
            pdf = fitz.open(path)
            for page_num, page in enumerate(pdf):
                text = page.get_text()
                if text.strip():
                    docs.append(Document(
                        page_content=text,
                        metadata={
                            "source": filename,
                            "page": page_num + 1
                        }
                    ))
            print(f"Loaded: {filename} ({len(pdf)} pages)")
    return docs

def chunk_documents(docs: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = splitter.split_documents(docs)
    print(f"Total chunks created: {len(chunks)}")
    return chunks

def build_vectorstore(chunks: list[Document]) -> Chroma:
    embeddings = HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL
    )
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=settings.COLLECTION_NAME,
        persist_directory=settings.CHROMA_PERSIST_DIR
    )
    print(f"Vector store saved to: {settings.CHROMA_PERSIST_DIR}")
    return vectorstore