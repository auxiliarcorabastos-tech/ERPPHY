# db.py
import os
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.engine import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

# Ejemplo de DATABASE_URL async:
# postgresql+asyncpg://user:pass@host/dbname

# Si Render te da un URL sin "+asyncpg", lo convertimos:
if DATABASE_URL and "postgresql://" in DATABASE_URL and "+asyncpg" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_async_session():
    async with SessionLocal() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

