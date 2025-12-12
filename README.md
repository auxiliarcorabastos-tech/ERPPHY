
FastAPI ERP Corabastos - Template for Render deployment
-----------------------------------------------------

What is included:
- main.py: FastAPI app with WebSocket endpoint and routers
- db.py: async SQLModel engine using DATABASE_URL env var
- models.py: SQLModel table definitions (User, DeviceToken, Pedido)
- auth.py: basic register/login (JWT simplified)
- wsmanager.py: WebSocket connection manager and broadcast
- push.py: Firebase push helper (reads FIREBASE_CREDS env var json string)
- routers/: pedidos and devices routers
- requirements.txt
- render.yaml, Dockerfile, README.md

Quick start (local):
1. Create a python venv and activate it.
2. Install dependencies: pip install -r requirements.txt
3. Set env vars (DATABASE_URL, SECRET_KEY). Optionally FIREBASE_CREDS.
4. Run: uvicorn main:app --reload --port 5000
5. Use /docs for API docs (Swagger).

Important security notes:
- Do NOT commit real credentials to git.
- Use Render environment variables for DATABASE_URL and FIREBASE_CREDS.
- For production, consider Redis for websocket broadcast when scaling.
