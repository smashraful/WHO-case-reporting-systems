from fastapi import (APIRouter, Depends, HTTPException)

from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_service import login

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/login", response_model = TokenResponse)
def login_user(
    body: LoginRequest,
    db: Session = Depends(get_db)
):
    token = login(db, body.email, body.password)

    if not token:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "access_token": token,
        "token_type": "bearer"
    }