from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os

from db import get_async_session
from models import User   # ✅ IMPORTAR, NO DEFINIR

router = APIRouter()

# ======================
# CONFIG
# ======================
SECRET_KEY = os.environ.get("SECRET_KEY", "changeme")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ======================
# UTILS
# ======================
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ======================
# ROUTES
# ======================
@router.post("/register")
async def register(
    username: str,
    password: str,
    role: str = "basic",
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        select(User).where(User.username == username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Usuario ya existe")

    user = User(
        username=username,
        hashed_password=hash_password(password),
        role=role
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return {"msg": "Usuario creado", "id": user.id}


@router.post("/login")
async def login(
    username: str,
    password: str,
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )

    token = create_access_token(
        data={"sub": user.username, "role": user.role}
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role
    }

