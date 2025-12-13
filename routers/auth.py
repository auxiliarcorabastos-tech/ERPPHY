from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import SQLModel, Field, select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os

from db import get_async_session

router = APIRouter()

# ======================
# CONFIG
# ======================
SECRET_KEY = os.environ.get("SECRET_KEY", "changeme")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ======================
# MODELS
# ======================
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str
    role: str = Field(default="basic")
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ======================
# UTILS
# ======================
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
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
    result = await session.execute(select(User).where(User.username == username))
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="Usuario ya existe")

    user = User(
        username=username,
        password_hash=hash_password(password),
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
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.password_hash):
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
