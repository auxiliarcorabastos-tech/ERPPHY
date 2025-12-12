
import os
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from db import init_db
from wsmanager import manager
from routers import auth, pedidos, devices
import uvicorn

app = FastAPI(title="ERP Corabastos - FastAPI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    # initialize DB (create tables)
    await init_db()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(pedidos.router, prefix="/pedidos", tags=["pedidos"])
app.include_router(devices.router, prefix="/devices", tags=["devices"])

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            # echo back or ignore; clients listen to broadcasts
    except WebSocketDisconnect:
        manager.disconnect(ws)

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get('PORT',5000)), reload=False)
