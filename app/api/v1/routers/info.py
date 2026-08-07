from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(
    prefix="/info",
    tags=["Info"]
)

@router.get("")
def info():
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "debug": settings.DEBUG
    }