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

    # JWT Authentication
    JWT_SECRET: str = "CHANGE_ME_IN_PRODUCTION_use_openssl_rand_hex_32"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 480  # 8 hours

    # App-level DB user (non-superuser, RLS enforced)
    # If not set, falls back to POSTGRES_USER (superuser — RLS bypassed!)
    POSTGRES_APP_USER: str | None = None
    POSTGRES_APP_PASSWORD: str | None = None
    APP_DATABASE_URI: str | None = None

    # ==========================================================================
    # AI / LLM Configuration - Multi-Provider Gateway
    # ==========================================================================
    # CRITICAL: All configured providers are EU-based or local.
    # Mistral AI (France), Scaleway (France), Ollama (local).

    # Provider priority (comma-separated): mistral, scaleway
    AI_PROVIDER_PRIORITY: str = "mistral,scaleway"

    # Mistral AI (French, GDPR compliant) - https://mistral.ai
    MISTRAL_API_KEY: Optional[str] = None
    MISTRAL_MODEL: str = "mistral-small-latest"
    MISTRAL_API_BASE: str = "https://api.mistral.ai/v1"

    # Scaleway Generative APIs (French cloud) - https://scaleway.com
    SCALEWAY_API_KEY: Optional[str] = None
    SCALEWAY_MODEL: str = "mistral-nemo-instruct-2407"
    SCALEWAY_API_BASE: str = "https://api.scaleway.ai/v1"

    # Request timeout in seconds
    AI_TIMEOUT: int = 120

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

    # Default admin password (used by seed_data to create demo users)
    DEFAULT_ADMIN_PASSWORD: str = "changeme"

    # Langfuse (LLM Observability)
    # IMPORTANT: For EU data sovereignty, Langfuse must be self-hosted.
    # Do NOT use the US-hosted cloud.langfuse.com - set LANGFUSE_HOST to your self-hosted instance.
    LANGFUSE_PUBLIC_KEY: Optional[str] = None
    LANGFUSE_SECRET_KEY: Optional[str] = None
    LANGFUSE_HOST: Optional[str] = None  # Set to self-hosted instance URL in production


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.SQLALCHEMY_DATABASE_URI:
            # Use asyncpg driver for async SQLAlchemy
            self.SQLALCHEMY_DATABASE_URI = f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
        
        if not self.APP_DATABASE_URI:
            if self.POSTGRES_APP_USER and self.POSTGRES_APP_PASSWORD:
                # Non-superuser for runtime (RLS enforced)
                self.APP_DATABASE_URI = f"postgresql+asyncpg://{self.POSTGRES_APP_USER}:{self.POSTGRES_APP_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
            else:
                # Fallback: use superuser (RLS bypassed!)
                self.APP_DATABASE_URI = self.SQLALCHEMY_DATABASE_URI

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"

settings = Settings()
