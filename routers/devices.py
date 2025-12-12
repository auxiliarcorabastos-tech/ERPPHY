
from fastapi import APIRouter
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession
from db import get_async_session
from models import DeviceToken
router = APIRouter()

class DeviceIn(BaseModel):
    user_id: int = None
    token: str
    platform: str = 'android'

@router.post('/register')
async def register_device(d: DeviceIn):
    async with get_async_session() as session:
        dt = DeviceToken(user_id=d.user_id, token=d.token, platform=d.platform)
        session.add(dt)
        await session.commit()
        return {'ok': True}
