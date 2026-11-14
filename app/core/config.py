from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    app_name: str = "IT Support Agentic RAG Copilot"
    app_env: str = "development"
    gemini_api_key: str = ""
    tavily_api_key: str = ""
    pinecone_api_key: str = ""
    pinecone_index_name: str = "it-support-agentic-rag"
    pinecone_namespace: str = "company-it-kb"
    gemini_model: str = "gemini-3.5-flash-lite"
    embeddings_model: str = "gemini-embedding-001"
    top_k: int = 4
    max_reties: int = 1
    admin_api_key: str = "admin-secret-key"
    audit_db_path: str = str(BASE_DIR / "data" / "audit.db")
    uploads_dir: str = str(BASE_DIR / "uploads")
    sample_kb_dir: str = str(BASE_DIR / "data" / "sample_kb")
    
    model_config = SettingsConfigDict(env_file=(BASE_DIR / ".env"), extra="allow")    
    
    
@lru_cache
def get_settings() -> Settings:
    return Settings()
