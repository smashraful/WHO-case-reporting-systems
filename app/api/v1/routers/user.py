from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.models.user import User
from app.services.user_service import (
    create_user,
    get_users,
    get_user,
    delete_user
)
from app.dependencies.auth import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("", response_model=UserResponse)
def create(user: UserCreate,
db: Session = Depends(get_db)
):
    return create_user(db, user)
    
@router.get("", response_model=list[UserResponse])
def get_all(current_user: User = Depends(get_current_user),db: Session = Depends(get_db)):
    return get_users(db)
     
@router.get("/{user_id}", response_model=UserResponse)
def get_one(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = get_user(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

@router.delete("/{user_id}")
def delete(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = get_user(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    delete_user(db, user)

    return {"message": "User deleted successfully"}
