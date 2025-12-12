
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
import uuid, asyncio
from sqlmodel.ext.asyncio.session import AsyncSession
from db import get_async_session
from models import Pedido, DeviceToken
from wsmanager import manager
from sqlmodel import select

router = APIRouter()

class PedidoIn(BaseModel):
    nit: str
    fundacion: str
    total: float = 0.0
    peaje: float = 0.0
    trans: float = 0.0

@router.post('/create')
async def create_pedido(payload: PedidoIn):
    async with get_async_session() as session:
        uid = "PED-" + str(uuid.uuid4())[:8]
        p = Pedido(uid=uid, nit=payload.nit, fundacion=payload.fundacion, total=payload.total, peaje=payload.peaje, trans=payload.trans)
        session.add(p)
        await session.commit()
        await session.refresh(p)

        # broadcast via websocket
        await manager.broadcast({'type':'new_pedido','pedido':{'uid':p.uid,'nit':p.nit,'fundacion':p.fundacion,'total':p.total}})

        # send push in background if tokens exist
        q = await session.exec(select(DeviceToken.token))
        tokens = [r for r in q.all()]
        if tokens:
            from push import send_push_to_token
            loop = asyncio.get_event_loop()
            for t in tokens:
                loop.run_in_executor(None, send_push_to_token, t, f"Nuevo pedido {p.uid}", f"Fundación: {p.fundacion}", {'pedido_id':p.uid})

        return {'ok': True, 'uid': p.uid}
