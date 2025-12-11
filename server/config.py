"""
LexAI Configuration Management
"""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Settings
    app_name: str = "LexAI"
    app_version: str = "2.0.0"  # Hedge Fund Edition
    debug: bool = True
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database URLs
    postgres_url: str = "postgresql://lexai:lexai@localhost:5432/lexai"
    redis_url: str = "redis://localhost:6379"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    
    # Vector DB
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    use_mock_vector_db: bool = False  # Production mode
    
    # LLM Settings
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    llm_model: str = "gpt-4o"  # Production model
    llm_provider: str = "openai"  # openai or anthropic
    use_mock_llm: bool = True  # Set False when API key provided
    
    # Data Source APIs
    courtlistener_api_key: str = ""
    sec_edgar_user_agent: str = "LexAI HedgeFund contact@lexai.fund"
    pacer_username: str = ""
    pacer_password: str = ""
    
    # Search Settings
    embedding_model: str = "all-MiniLM-L6-v2"
    search_top_k: int = 10
    rerank_top_k: int = 5
    
    # Trading Settings
    broker: str = "interactive_brokers"
    paper_trading: bool = True  # Always start with paper trading
    max_position_pct: float = 0.05  # 5% max position
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

