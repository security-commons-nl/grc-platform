from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "IMS API"
    API_V1_STR: str = "/api/v1"
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "ims"
    SQLALCHEMY_DATABASE_URI: str | None = None

    # AI / LLM Configuration
    # CRITICAL: Default to LOCALHOST to ensure EU Data Sovereignty.
    # Do NOT set this to OpenAI/Anthropic unless you have specific legal clearance.
    AI_API_BASE: str = "http://localhost:11434/v1" # Defaults to local Ollama
    AI_MODEL_NAME: str = "mistral" # Use open weights models


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.SQLALCHEMY_DATABASE_URI:
            # Use asyncpg driver for async SQLAlchemy
            self.SQLALCHEMY_DATABASE_URI = f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
