from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "IMS API"
    API_V1_STR: str = "/api/v1"

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "ims"
    SQLALCHEMY_DATABASE_URI: str | None = None

    # ==========================================================================
    # AI / LLM Configuration - Multi-Provider Gateway
    # ==========================================================================
    # CRITICAL: All configured providers are EU-based or local.
    # Mistral AI (France), Scaleway (France), Ollama (local).

    # Provider priority (comma-separated): mistral, scaleway, ollama
    AI_PROVIDER_PRIORITY: str = "mistral,scaleway,ollama"

    # Mistral AI (French, GDPR compliant) - https://mistral.ai
    MISTRAL_API_KEY: Optional[str] = None
    MISTRAL_MODEL: str = "mistral-small-latest"
    MISTRAL_API_BASE: str = "https://api.mistral.ai/v1"

    # Scaleway Generative APIs (French cloud) - https://scaleway.com
    SCALEWAY_API_KEY: Optional[str] = None
    SCALEWAY_MODEL: str = "mistral-nemo-instruct-2407"
    SCALEWAY_API_BASE: str = "https://api.scaleway.ai/v1"

    # Local Ollama (offline fallback)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "mistral"

    # Request timeout in seconds
    AI_TIMEOUT: int = 120

    # Legacy settings (kept for backwards compatibility)
    AI_API_BASE: str = "http://localhost:11434"
    AI_MODEL_NAME: str = "mistral"

    # ==========================================================================
    # External Integrations
    # ==========================================================================

    # TopDesk (ITSM)
    TOPDESK_URL: Optional[str] = None
    TOPDESK_USERNAME: Optional[str] = None
    TOPDESK_PASSWORD: Optional[str] = None

    # ServiceNow (ITSM/CMDB)
    SERVICENOW_URL: Optional[str] = None
    SERVICENOW_USERNAME: Optional[str] = None
    SERVICENOW_PASSWORD: Optional[str] = None

    # Proquro (Supplier Management)
    PROQURO_URL: Optional[str] = None
    PROQURO_API_KEY: Optional[str] = None

    # BlueDolphin (Enterprise Architecture)
    BLUEDOLPHIN_URL: Optional[str] = None
    BLUEDOLPHIN_API_KEY: Optional[str] = None

    # Webhook Security
    WEBHOOK_SECRET: Optional[str] = None

    # Langfuse (LLM Observability)
    LANGFUSE_PUBLIC_KEY: Optional[str] = None
    LANGFUSE_SECRET_KEY: Optional[str] = None
    LANGFUSE_HOST: Optional[str] = "https://cloud.langfuse.com"


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.SQLALCHEMY_DATABASE_URI:
            # Use asyncpg driver for async SQLAlchemy
            self.SQLALCHEMY_DATABASE_URI = f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
