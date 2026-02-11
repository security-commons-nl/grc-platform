from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.core.config import settings

# Runtime engine — uses app user (NOBYPASSRLS) when configured
engine = create_async_engine(settings.APP_DATABASE_URI, echo=True, future=True)

# Alias for clarity in imports
async_engine = engine


async def init_db():
    """
    Initialize database schema and extensions.
    Uses the SUPERUSER engine (SQLALCHEMY_DATABASE_URI) because:
    - CREATE EXTENSION requires superuser
    - CREATE TABLE should be done by the table owner (superuser)
    """
    admin_engine = create_async_engine(
        settings.SQLALCHEMY_DATABASE_URI, echo=False, future=True
    )
    async with admin_engine.begin() as conn:
        from sqlalchemy import text
        # Only enable vector extension for PostgreSQL
        if "postgresql" in settings.SQLALCHEMY_DATABASE_URI:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

        await conn.run_sync(SQLModel.metadata.create_all)

        # Grant permissions to app role if configured
        if settings.POSTGRES_APP_USER:
            await conn.execute(text(
                f"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {settings.POSTGRES_APP_USER}"
            ))
            await conn.execute(text(
                f"GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {settings.POSTGRES_APP_USER}"
            ))
    await admin_engine.dispose()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
