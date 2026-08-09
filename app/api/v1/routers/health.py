from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.dependencies.database import get_db

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
def health():
    return {"status": "healthy"}


@router.get("/version")
def version():
    return {"version": settings.APP_VERSION}


@router.get("/database")
def database_health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(
            status_code=503, detail="Database connection is unhealthy"
        )
    return {"status": "healthy", "message": "Database connection is healthy"}
