from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # PostgreSQL
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "rag_db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    # Ollama
    ollama_base_url: str = "http://localhost:11434"

    # Application
    app_env: str = "development"
    secret_key: str = "change-me-in-production"

    # LLM
    llm_provider: str = "ollama"
    ollama_model: str = "qwen2.5:7b"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str = "https://api.openai.com/v1"

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@localhost:5432/{self.postgres_db}"

    class Config:
        env_file = ".env"


settings = Settings()
