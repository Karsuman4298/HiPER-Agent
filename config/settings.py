import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # LLM Configuration
    LLM_PROVIDER: str = "ollama"  # or "openai", "anthropic", "groq", "google"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "llama3"  
    
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo"
    
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-opus-20240229"

    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama3-70b-8192"

    GOOGLE_API_KEY: Optional[str] = None
    GOOGLE_MODEL: str = "gemini-1.5-flash"
    
    # Memory Configuration
    QDRANT_PATH: str = "memory/qdrant_storage"
    EXPERIENCE_DB_PATH: str = "memory/experience.db"
    
    # Tool Configuration
    SEARCH_API_KEY: Optional[str] = None  # DuckDuckGo doesn't strictly need one
    
    # App Settings
    APP_NAME: str = "HYPER-Agent"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
