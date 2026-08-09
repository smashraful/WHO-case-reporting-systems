from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.rbac import require_roles
from app.schemas.user import UserCreate, UserResponse
from app.models.enums import UserRole
from app.models.user import User
from app.services.user_service import (
    create_user,
    get_users,
    get_user,
    delete_user,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.admin))],
)
def create(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)


@router.get("", response_model=list[UserResponse])
def get_all(
    _: User = Depends(require_roles(UserRole.admin, UserRole.program_manager)),
    db: Session = Depends(get_db),
):
    return get_users(db)


@router.get("/{user_id}", response_model=UserResponse)
def get_one(
    user_id: int,
    _: User = Depends(require_roles(UserRole.admin, UserRole.program_manager)),
    db: Session = Depends(get_db),
):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", dependencies=[Depends(require_roles(UserRole.admin))])
def delete(user_id: int, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    delete_user(db, user)
    return {"message": "User deleted successfully"}
