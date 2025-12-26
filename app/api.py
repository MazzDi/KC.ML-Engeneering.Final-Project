import os
from pathlib import Path

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles

from routes.auth import router as auth_router
from routes.clients import router as clients_router
from routes.health import router as health_router
from routes.managers import router as managers_router
from routes.ui_api import router as ui_api_router
from routes.ui_pages import router as ui_pages_router
from routes.users import router as users_router

app = FastAPI(title="Credit Scoring API")

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY", "dev-secret"))

STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(health_router)
app.include_router(ui_pages_router)
app.include_router(auth_router)
app.include_router(ui_api_router)
app.include_router(users_router)
app.include_router(clients_router)
app.include_router(managers_router)


