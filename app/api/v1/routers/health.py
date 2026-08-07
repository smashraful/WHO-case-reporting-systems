from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.dependencies.database import get_db

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)

@router.get("")
def health():
    return {
        "status": "healthy"
    }

@router.get("/version")
def version():
    return {
        "version": "1.0.0"
    }

@router.get("/database")
def database_health(db: Session = Depends(get_db)):
    return {
        "message": "Database connection is healthy"
    }