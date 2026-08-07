from fastapi import FastAPI

from app.core.config import settings

from app.api.v1.routers.health import router as health_router
from app.api.v1.routers.info import router as info_router
from app.api.v1.routers.user import router as user_router
from app.api.v1.routers.auth import router as auth_router

from app.db.database import engine
from app.models import *
from app.models.base import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)
app.include_router(health_router)
app.include_router(info_router)
app.include_router(user_router)
app.include_router(auth_router)

@app.get("/")

def root():
    return {
        "message": "WHO case reporting api"
    }