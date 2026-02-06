from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.security import verify_password
from app.core.crud import CRUDBase
from app.models.core_models import User, UserRead

router = APIRouter()
crud_user = CRUDBase(User)


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login", response_model=UserRead)
async def login(
    credentials: LoginRequest,
    session: AsyncSession = Depends(get_session),
):
    """Validate credentials against database and return user data."""
    user = await crud_user.get_by_field(session, "username", credentials.username)
    if not user:
        raise HTTPException(status_code=401, detail="Ongeldige gebruikersnaam of wachtwoord")

    if not user.is_active:
        raise HTTPException(status_code=401, detail="Account is gedeactiveerd")

    if not user.password_hash:
        raise HTTPException(status_code=401, detail="Geen wachtwoord ingesteld voor dit account")

    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Ongeldige gebruikersnaam of wachtwoord")

    # Update last_login
    user.last_login = datetime.utcnow()
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user
