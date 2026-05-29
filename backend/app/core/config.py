from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str
    CHROMA_PERSIST_DIR: str = "./vectorstore"
    DOCUMENTS_DIR: str = "./documents"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    COLLECTION_NAME: str = "sws_ai_policies"
    TOP_K: int = 4

    class Config:
        env_file = ".env"

settings = Settings()