from fastapi import FastAPI

from routes.clients import router as clients_router
from routes.health import router as health_router
from routes.managers import router as managers_router
from routes.users import router as users_router

app = FastAPI(title="Credit Scoring API")

app.include_router(health_router)
app.include_router(users_router)
app.include_router(clients_router)
app.include_router(managers_router)


