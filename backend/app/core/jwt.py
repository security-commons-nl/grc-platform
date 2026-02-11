"""
JWT token creation and verification for API authentication.
"""
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt

from app.core.config import settings


def create_access_token(
    user_id: int,
    tenant_id: int | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token."""
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.JWT_EXPIRE_MINUTES))
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    if tenant_id is not None:
        payload["tid"] = tenant_id
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode and verify a JWT token. Raises JWTError on failure."""
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
