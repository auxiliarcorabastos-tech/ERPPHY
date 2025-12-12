
import os
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.engine import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql+asyncpg://user:pass@localhost:5432/dbname')

engine = create_async_engine(DATABASE_URL, echo=False, future=True)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

def get_async_session() -> AsyncSession:
    return AsyncSession(engine)
