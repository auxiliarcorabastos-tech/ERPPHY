import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from db import init_db
from wsmanager import manager

# Importar routers DIRECTAMENTE (evita ciclos)
from routers.auth import router as auth_router
from routers.pedidos import router as pedidos_router
from routers.devices import router as devices_router

app = FastAPI(
    title="ERP Corabastos",
    version="1.0.0"
)

# CORS (web + móvil)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # luego se puede limitar
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear tablas al iniciar
@app.on_event("startup")
async def startup():
    await init_db()

# Rutas
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(pedidos_router, prefix="/pedidos", tags=["Pedidos"])
app.include_router(devices_router, prefix="/devices", tags=["Devices"])

# WebSocket (actualización en vivo)
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)

# Health check
@app.get("/")
async def root():
    return {"status": "ERP Corabastos API running"}

# Solo local (Render usa su propio comando)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=False
    )


